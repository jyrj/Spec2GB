#!/usr/bin/env python3
# subset_compare.py
# ---------------------------------------------------------------------------
# Compare the tiny‑subset CPU implementation against PyBoy, instruction by
# instruction, using a purpose‑built ROM containing only the supported
# opcodes.
# ---------------------------------------------------------------------------
import logging
import csv, datetime, os
from pathlib import Path
from typing import Dict

from generated.cpu import CPU                      # our reference core

from pyboy import PyBoy, PyBoyRegisterFile
from spec2gb.pyboy_bridge import get_mb, tick_cpu  

# ---------------------------------------------------------------------------
#                               1.  ROM Builder
# ---------------------------------------------------------------------------
class ROMBuilder:
    """Builds a 32 KiB test ROM limited to the tiny‑subset instructions."""

    BANK   = 0x4000              # 16 KiB (single bank size)
    SIZE   = 0x8000              # 32 KiB total (2 banks)

    LOGO = bytes([
        0xCE, 0xED, 0x66, 0x66, 0xCC, 0x0D, 0x00, 0x0B,
        0x03, 0x73, 0x00, 0x83, 0x00, 0x0C, 0x00, 0x0D,
        0x00, 0x08, 0x11, 0x1F, 0x88, 0x89, 0x00, 0x0E,
        0xDC, 0xCC, 0x6E, 0xE6, 0xDD, 0xDD, 0xD9, 0x99,
        0xBB, 0xBB, 0x67, 0x63, 0x6E, 0x0E, 0xEC, 0xCC,
        0xDD, 0xDC, 0x99, 0x9F, 0xBB, 0xB9, 0x33, 0x3E
    ])

    def build(self, path: Path):
        # ------------------------------------------------------------------
        # 1. Allocate fixed‑size ROM buffer
        # ------------------------------------------------------------------
        rom = bytearray(self.SIZE)             # exactly 32 768 bytes, all 0

        # ------------------------------------------------------------------
        # 2. Header (mostly boiler‑plate)
        # ------------------------------------------------------------------
        rom[0x0104:0x0104 + 48] = self.LOGO
        rom[0x0134:0x0134 + 11] = b"SUBSETTEST"       # Title (≤ 11 B)
        rom[0x0143] = 0x00                            # CGB flag
        rom[0x0144] = rom[0x0145] = 0x00              # New licensee
        rom[0x0146] = 0x00                            # SGB flag
        rom[0x0147] = 0x01                            # Cart type = ROM only
        rom[0x0148] = 0x00                            # ROM size = 32 KiB
        rom[0x0149] = 0x00                            # RAM size = none
        rom[0x014A] = 0x00                            # Destination = Japan
        rom[0x014B] = 0x33                            # Old licensee
        rom[0x014C] = 0x00                            # ROM version

        # Header checksum (x = −(Σ[0134‑014C] + 1))
        chk = 0
        for b in rom[0x0134:0x014D]:
            chk = (chk - b - 1) & 0xFF
        rom[0x014D] = chk

        # Leave global checksum 0000 (PyBoy ignores it)
        rom[0x014E:0x0150] = b"\x00\x00"

                # ------------------------------------------------------------------
        # 3. Program data (tiny-subset opcodes only)
        # ------------------------------------------------------------------
        # Main program placed at 0x0100
        main = [
            0xE0, 0x10,             # 0100: LDH (FF10),A
            0x3C,                   # 0102: INC A
            0xE0, 0x11,             # 0103: LDH (FF11),A
            0xC6, 0x05,             # 0105: ADD A,05
            0xD6, 0x03,             # 0107: SUB A,03
            0xE6, 0x0F,             # 0109: AND A,0F
            0xF6, 0x20,             # 010B: OR  A,20
            0xEE, 0xFF,             # 010D: XOR A,FF
            0xCD, 0x00, 0x02,       # 010F: CALL 0200
            0xC3, 0x00, 0x01,       # 0112: JP   0100
        ]
        rom[0x0100 : 0x0100 + len(main)] = bytes(main)

        # Sub-routine placed at 0x0200
        subr = [
            0xE0, 0x12,             # 0200: LDH (FF12),A
            0xC9                    # 0202: RET
        ]
        rom[0x0200 : 0x0200 + len(subr)] = bytes(subr)


        # ------------------------------------------------------------------
        # 4. **Safety padding / assertion**
        # ------------------------------------------------------------------
        if len(rom) % self.BANK != 0:
            padding = self.BANK - (len(rom) % self.BANK)
            rom.extend(b"\x00" * padding)
        assert len(rom) == self.SIZE, f"ROM final size is {len(rom)}"

        # ------------------------------------------------------------------
        # 5. Save to disk
        # ------------------------------------------------------------------
        path.write_bytes(rom)
        print(f"ROM written to: {path.resolve()}  ({len(rom)} bytes)")


# ---------------------------------------------------------------------------
#                            2.  My‑CPU Harness
# ---------------------------------------------------------------------------
class MyCPUHarness:
    """Loads the ROM, decodes supported opcodes, and steps the custom CPU."""

    _DECODERS = {
        0xE0: ("LDH_a8_A", 2, ("a8",)),
        0xF0: ("LDH_A_a8", 2, ("a8",)),
        0x3C: ("INC_A",    1, ()),
        0x3D: ("DEC_A",    1, ()),
        0xC6: ("ADD_A_n8", 2, ("imm8",)),
        0xD6: ("SUB_A_n8", 2, ("imm8",)),
        0xE6: ("AND_A_n8", 2, ("imm8",)),
        0xF6: ("OR_A_n8",  2, ("imm8",)),
        0xEE: ("XOR_A_n8", 2, ("imm8",)),
        0x18: ("JR_r8",    2, ("rel8",)),
        0xC3: ("JP_a16",   3, ("addr",)),
        0xCD: ("CALL_a16", 3, ("addr",)),
        0xC9: ("RET",      1, ()),
    }

    def __init__(self, rom: bytes, initial_state: Dict[str, int]):
        self.cpu = CPU()
        # Mirror PyBoy's power‑on state
        for r, v in initial_state.items():
            setattr(self.cpu, r, v)

        # Decode ROM to dicts that the CPU class expects
        self._decode_rom(rom)

    # ------------- stepping & state dump -------------------
    def step(self):
        self.cpu.step()

    def state(self) -> Dict[str, int]:
        return {
            "A": self.cpu.A, "F": self.cpu.F,
            "B": self.cpu.B, "C": self.cpu.C,
            "D": self.cpu.D, "E": self.cpu.E,
            "H": self.cpu.H, "L": self.cpu.L,
            "SP": self.cpu.SP, "PC": self.cpu.PC
        }

    # ------------- decoding helper -------------------------
    def _decode_rom(self, rom: bytes):
        pc = 0
        while pc < len(rom):
            opcode = rom[pc]
            if opcode not in self._DECODERS:
                pc += 1
                continue                       # ignore unsupported bytes
            mnem, length, fields = self._DECODERS[opcode]
            operands = {}
            if length == 2:
                val = rom[pc + 1]
            elif length == 3:
                val = rom[pc + 1] | (rom[pc + 2] << 8)
            else:
                val = None

            if fields:
                operands[fields[0]] = val

            self.cpu.code[pc] = {"op": mnem, **operands, "len": length}
            pc += length

# ---------------------------------------------------------------------------
#                       3.  PyBoy Harness  (works on v2.x)
# ---------------------------------------------------------------------------
from pathlib import Path
from typing import Dict

class PyBoyHarness:
    """
    Boots PyBoy head‑less, bypasses the Nintendo boot‑ROM, and allows stepping
    one CPU *instruction* at a time.  Tested with PyBoy 2.0‑2.6.
    """
    
    # ─── opcode-length table for the tiny subset ────────────────────────
    _LEN = {
        0x3C: 1, 0x3D: 1, 0xC9: 1,                 # 1-byte opcodes
        0xE0: 2, 0xF0: 2, 0xC6: 2, 0xD6: 2,
        0xE6: 2, 0xF6: 2, 0xEE: 2, 0x18: 2,        # 2-byte opcodes
        0xC3: 3, 0xCD: 3,                          # 3-byte opcodes
    }
    _CONTROL = {0x18, 0xC3, 0xCD, 0xC9}            # alter PC internally
    
    def __init__(self, rom_path: Path):
        # 1) start PyBoy without a window
        self.pyboy = PyBoy(
            str(rom_path),
            window="null",          # head-less backend
            bootrom=None,           # don't load external boot ROM
            sound_emulated=False,
            no_input=True,
            log_level="ERROR",
        )

        # 2) unmap the internal boot ROM and reset registers
        self.pyboy.memory[0xFF50] = 1              # disable boot ROM

        rf: PyBoyRegisterFile = self.pyboy.register_file
        rf.PC = 0x0100
        rf.SP = 0xFFFE
        rf.A = rf.B = rf.C = rf.D = rf.E = rf.F = 0
        rf.HL = 0
        
    # ------------------------------------------------------------------
    # execute exactly one instruction
    # ------------------------------------------------------------------
        # ------------------------------------------------------------------
    # execute exactly one instruction
    # ------------------------------------------------------------------
        # ------------------------------------------------------------------
    # execute exactly one instruction
    # ------------------------------------------------------------------
    def step(self) -> None:
        """
        Tick PyBoy’s CPU until the current instruction is complete.
        We advance 4 T-cycles per iteration (one machine cycle) because the
        PC is updated only at machine-cycle granularity.
        """
        rf       = self.pyboy.register_file
        start_pc = rf.PC
        opcode   = self.pyboy.memory[start_pc]
        length   = self._LEN.get(opcode, 1)

        while True:
            tick_cpu(self.pyboy, 4)                 # 4 T-cycles = 1 M-cycle
            delta = (rf.PC - start_pc) & 0xFFFF     # bytes advanced

            # Control-flow ops (JP/JR/CALL/RET) finish at first PC change
            if opcode in self._CONTROL:
                if delta != 0:
                    break
            # All others finish when full opcode length has been fetched
            else:
                if delta >= length:
                    break



    # ------------------------------------------------------------------
    # dump CPU state as dict of 8-bit regs plus PC/SP
    # ------------------------------------------------------------------
    def state(self) -> Dict[str, int]:
        rf = self.pyboy.register_file
        hl = rf.HL
        return {
            "A": rf.A,
            "F": rf.F,
            "B": rf.B,
            "C": rf.C,
            "D": rf.D,
            "E": rf.E,
            "H": (hl >> 8) & 0xFF,
            "L": hl & 0xFF,
            "SP": rf.SP,
            "PC": rf.PC,
        }

# ---------------------------------------------------------------------------
#                        4.  Comparison Driver
# ---------------------------------------------------------------------------
class CompareDriver:
    def __init__(self, steps=40):
        self.steps = steps
        self.logger = self._setup_logger()
        
        self.csv_path = Path("mismatch_log.csv")
        self.csv_file = self.csv_path.open("w", newline="")
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(
            ["cycle", "pc_ref", "a_ref", "f_ref",
             "pc_pyboy", "a_pyboy", "f_pyboy"]
        )


        rom_path = Path("subset_test.gb")
        ROMBuilder().build(rom_path)

        # --- Start PyBoy and snapshot initial state ---------------------
        self.pyboy_h = PyBoyHarness(rom_path)
        init_state = self.pyboy_h.state()

        # --- My‑CPU with identical power‑on state ----------------------
        rom_bytes = rom_path.read_bytes()
        self.mycpu_h = MyCPUHarness(rom_bytes, init_state)

    # ------------------------------------------------------------------
    def run(self):
        self.logger.info("Step |     PC |      A F |   MATCH")
        self.logger.info("-----------------------------------------")

        for step_idx in range(1, self.steps + 1):
            # --- Execute one instruction on both cores ---------------
            self.pyboy_h.step()
            self.mycpu_h.step()

            # --- Gather states ---------------------------------------
            state_py  = self.pyboy_h.state()
            state_ref = self.mycpu_h.state()

            # --- Compare --------------------------------------------
            match = state_py == state_ref
            tag   = "MATCH" if match else "DIFF "

            self.logger.info("%4d | %04X | %02X %02X | %s",
                             step_idx,
                             state_ref["PC"],
                             state_ref["A"], state_ref["F"],
                             tag)

            if not match:
                # log the mismatch row
                self.csv_writer.writerow(
                    [
                        step_idx,
                        f"{state_ref['PC']:04X}", f"{state_ref['A']:02X}", f"{state_ref['F']:02X}",
                        f"{state_py['PC']:04X}",  f"{state_py['A']:02X}",  f"{state_py['F']:02X}",
                    ]
                )
                self.logger.error(
                    "Register diff at step %d\n  PyBoy: %s\n  Mine : %s",
                    step_idx, state_py, state_ref
                )
                break


        self.logger.info("Comparison finished.")
        
        self.logger.info("Comparison finished.")
        self.csv_file.close()
        self.logger.info("Mismatch log: %s", self.csv_path.resolve())


    # ------------------------------------------------------------------
    def _setup_logger(self):
        logging.basicConfig(level=logging.INFO,
                            format="%(message)s",
                            handlers=[logging.StreamHandler()])
        return logging.getLogger("compare")


# ---------------------------------------------------------------------------
#                                entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    CompareDriver().run()
