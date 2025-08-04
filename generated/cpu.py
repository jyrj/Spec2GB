class CPU:
    INSTRUCTION_CYCLES = {
        "ADD_A_n8": 8,
        "SUB_A_n8": 8,
        "AND_A_n8": 8,
        "OR_A_n8": 8,
        "XOR_A_n8": 8,
        "INC_A": 4,
        "DEC_A": 4,
        "LD_r_r": 4,
        "LD_A_n8_ptr": 8,
        "LD_n8_A_ptr": 8,
        "LDH_a8_A": 8,
        "LDH_A_a8": 8,  # ✅ Added
        "JP": 16,
        "JR": 12,
        "CALL": 24,
        "RET": 16,
        "DI": 4,
        "EI": 4,
        "HALT": 4,
    }

    def __init__(self, memory):
        self.memory = memory
        self.timer = self.memory.timer
        self.reset()

    def reset(self):
        self.registers = {"A": 0, "F": 0, "PC": 0}
        self.memory_instructions = []
        self.stack = []
        self.IME = False
        self.DIV = 0
        self.TIMA = 0
        self.TMA = 0
        self.TAC = 0

    @property
    def A(self):
        return self.registers["A"]

    @A.setter
    def A(self, val):
        self.registers["A"] = val & 0xFF

    @property
    def F(self):
        return self.registers["F"]

    @F.setter
    def F(self, val):
        self.registers["F"] = val & 0xFF

    @property
    def PC(self):
        return self.registers["PC"]

    @PC.setter
    def PC(self, val):
        self.registers["PC"] = val & 0xFFFF

    @property
    def bus(self):
        # Add this to fix the test, so cpu.bus.read8(addr) works
        return self.memory

    def read_memory(self, addr):
        return self.memory.read(addr)

    def write_memory(self, addr, val):
        self.memory.write(addr, val)

    def step(self, instr=None):
        if instr is not None:
            if "mnemonic" in instr:
                op = instr["mnemonic"]
                n = instr.get("operand")
                instr = {"op": op}
                if n is not None:
                    instr.update({"imm8": n, "n8": n, "addr": n, "offset": n, "a8": n})
            cycles = self._execute(instr)
            self.timer.step(cycles)
            return

        pc = self.registers["PC"]
        if pc >= len(self.memory_instructions):
            return

        instr = self.memory_instructions[pc]
        cycles = self._execute(instr)
        if instr["op"] not in ("JP", "JR", "CALL", "RET"):
            self.registers["PC"] += 1

        self.timer.step(cycles)

    def _execute(self, instr):
        op = instr["op"]

        if op == "ADD_A_n8":
            self.registers["A"] = (self.registers["A"] + instr["imm8"]) & 0xFF
            self._update_zero_flag()

        elif op == "SUB_A_n8":
            self.registers["A"] = (self.registers["A"] - instr["imm8"]) & 0xFF
            self._update_zero_flag()

        elif op == "AND_A_n8":
            self.registers["A"] &= instr["imm8"]
            self._update_zero_flag()

        elif op == "OR_A_n8":
            self.registers["A"] |= instr["imm8"]
            self._update_zero_flag()

        elif op == "XOR_A_n8":
            self.registers["A"] ^= instr["imm8"]
            self._update_zero_flag()

        elif op == "INC_A":
            self.registers["A"] = (self.registers["A"] + 1) & 0xFF
            self._update_zero_flag()

        elif op == "DEC_A":
            self.registers["A"] = (self.registers["A"] - 1) & 0xFF
            self._update_zero_flag()

        elif op == "LD_r_r":
            self.registers[instr["r1"]] = self.registers[instr["r2"]]

        elif op == "LD_A_n8_ptr":
            self.registers["A"] = self.read_memory(instr["n8"])
            self._update_zero_flag()

        elif op == "LD_n8_A_ptr":
            self.write_memory(instr["n8"], self.registers["A"])

        elif op == "LDH_a8_A":
            addr = 0xFF00 + instr["a8"]
            self.write_memory(addr, self.registers["A"])

        elif op == "LDH_A_a8":
            addr = 0xFF00 + instr["a8"]
            self.registers["A"] = self.read_memory(addr)
            self._update_zero_flag()

        elif op == "JP":
            self.registers["PC"] = instr["addr"]

        elif op == "JR":
            offset = instr["offset"]
            if offset & 0x80:
                offset -= 0x100
            self.registers["PC"] = (self.registers["PC"] + offset) & 0xFFFF

        elif op == "CALL":
            self.stack.append((self.registers["PC"] + 1) & 0xFFFF)
            self.registers["PC"] = instr["addr"]

        elif op == "RET":
            if self.stack:
                self.registers["PC"] = self.stack.pop()

        elif op == "DI":
            self.IME = False

        elif op == "EI":
            self.IME = True

        elif op == "HALT":
            pass

        else:
            raise ValueError(f"Unknown operation: {op}")

        return self.INSTRUCTION_CYCLES.get(op, 4)

    def _update_zero_flag(self):
        if self.registers["A"] == 0:
            self.registers["F"] |= 0b10000000
        else:
            self.registers["F"] &= 0b01111111
