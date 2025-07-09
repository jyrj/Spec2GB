class CPU:
    def __init__(self):
        self.reset()

    def reset(self):
        # Initialize registers A, F (8-bit), and PC (16-bit)
        self.registers = {
            "A": 0,
            "F": 0,
            "PC": 0
        }

        # Instruction memory
        self.memory = []

        # Data RAM (256 bytes)
        self.ram = [0] * 256

        # Stack for CALL/RET
        self.stack = []

    def step(self):
        pc = self.registers["PC"]

        if pc >= len(self.memory):
            return  # No instruction to execute

        instr = self.memory[pc]
        op = instr["op"]

        # --- ALU Operations ---
        if op == "ADD_A_n8":
            imm8 = instr["imm8"]
            self.registers["A"] = (self.registers["A"] + imm8) & 0xFF
            self._update_zero_flag()

        elif op == "SUB_A_n8":
            imm8 = instr["imm8"]
            self.registers["A"] = (self.registers["A"] - imm8) & 0xFF
            self._update_zero_flag()

        elif op == "AND_A_n8":
            imm8 = instr["imm8"]
            self.registers["A"] = self.registers["A"] & imm8
            self._update_zero_flag()

        elif op == "OR_A_n8":
            imm8 = instr["imm8"]
            self.registers["A"] = self.registers["A"] | imm8
            self._update_zero_flag()

        elif op == "XOR_A_n8":
            imm8 = instr["imm8"]
            self.registers["A"] = self.registers["A"] ^ imm8
            self._update_zero_flag()

        elif op == "INC_A":
            self.registers["A"] = (self.registers["A"] + 1) & 0xFF
            self._update_zero_flag()

        elif op == "DEC_A":
            self.registers["A"] = (self.registers["A"] - 1) & 0xFF
            self._update_zero_flag()

        # --- Load/Store Operations ---
        elif op == "LD_r_r":
            r1 = instr["r1"]
            r2 = instr["r2"]
            self.registers[r1] = self.registers[r2]

        elif op == "LD_A_n8_ptr":
            addr = instr["n8"]
            self.registers["A"] = self.ram[addr]
            self._update_zero_flag()

        elif op == "LD_n8_A_ptr":
            addr = instr["n8"]
            self.ram[addr] = self.registers["A"]

        # --- Control Flow Operations ---
        elif op == "JP":
            addr = instr["addr"]
            self.registers["PC"] = addr
            return  # Don't auto-increment PC

        elif op == "JR":
            offset = instr["offset"]
            self.registers["PC"] = (self.registers["PC"] + offset) & 0xFFFF
            return

        elif op == "CALL":
            addr = instr["addr"]
            self.stack.append(self.registers["PC"] + 1)
            self.registers["PC"] = addr
            return

        elif op == "RET":
            if self.stack:
                self.registers["PC"] = self.stack.pop()
            return

        else:
            raise ValueError(f"Unknown operation: {op}")

        # Auto-increment PC unless a jump/control op occurred
        self.registers["PC"] += 1

    def _update_zero_flag(self):
        # Set Zero flag (bit 7 of F) if A == 0
        if self.registers["A"] == 0:
            self.registers["F"] |= 0b10000000
        else:
            self.registers["F"] &= 0b01111111
