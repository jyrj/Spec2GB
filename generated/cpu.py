class CPU:
    def __init__(self):
        self.reset()

    # ------------------------------------------------------------------
    # state
    # ------------------------------------------------------------------
    def reset(self):
        # 8-bit A, F and 16-bit PC
        self.registers = {"A": 0, "F": 0, "PC": 0}

        # Optional instruction memory (original code path)
        self.memory = []

        # 256-byte RAM
        self.ram = [0] * 256

        # Stack for CALL / RET
        self.stack = []

    # ------------------------------------------------------------------
    # public registers (needed by the test)
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # single-step
    # ------------------------------------------------------------------
    def step(self, instr=None):
        """
        • If `instr` (decoded) is supplied, execute it directly
          (used by the test harness).
        • Otherwise fetch from self.memory using PC
          (your original behaviour).
        """
        if instr is not None:
            # convert harness format -> existing format
            if "mnemonic" in instr:           # harness dict
                op = instr["mnemonic"]
                n  = instr.get("operand")
                instr = {"op": op}
                if n is not None:
                    instr.update({"imm8": n, "n8": n, "addr": n, "offset": n})
            self._execute(instr)
            return

        # -------- original memory-based flow ----------
        pc = self.registers["PC"]
        if pc >= len(self.memory):
            return                            # nothing to run

        instr = self.memory[pc]
        self._execute(instr)
        self.registers["PC"] += 1             # auto-increment PC

    # ------------------------------------------------------------------
    # executor (unchanged except for HALT support)
    # ------------------------------------------------------------------
    def _execute(self, instr):
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
            self.registers["A"] &= imm8
            self._update_zero_flag()

        elif op == "OR_A_n8":
            imm8 = instr["imm8"]
            self.registers["A"] |= imm8
            self._update_zero_flag()

        elif op == "XOR_A_n8":
            imm8 = instr["imm8"]
            self.registers["A"] ^= imm8
            self._update_zero_flag()

        elif op == "INC_A":
            self.registers["A"] = (self.registers["A"] + 1) & 0xFF
            self._update_zero_flag()

        elif op == "DEC_A":
            self.registers["A"] = (self.registers["A"] - 1) & 0xFF
            self._update_zero_flag()

        # --- Load / Store ---
        elif op == "LD_r_r":
            r1, r2 = instr["r1"], instr["r2"]
            self.registers[r1] = self.registers[r2]

        elif op == "LD_A_n8_ptr":
            addr = instr["n8"]
            self.registers["A"] = self.ram[addr]
            self._update_zero_flag()

        elif op == "LD_n8_A_ptr":
            addr = instr["n8"]
            self.ram[addr] = self.registers["A"]

        # --- Control flow ---
        elif op == "JP":
            self.registers["PC"] = instr["addr"]
            return

        elif op == "JR":
            self.registers["PC"] = (self.registers["PC"] + instr["offset"]) & 0xFFFF
            return

        elif op == "CALL":
            self.stack.append(self.registers["PC"] + 1)
            self.registers["PC"] = instr["addr"]
            return

        elif op == "RET":
            if self.stack:
                self.registers["PC"] = self.stack.pop()
            return

        elif op == "HALT":
            # nothing else needed for the tiny test ROM
            return

        else:
            raise ValueError(f"Unknown operation: {op}")

    # ------------------------------------------------------------------
    # flag helper
    # ------------------------------------------------------------------
    def _update_zero_flag(self):
        if self.registers["A"] == 0:
            self.registers["F"] |= 0b10000000
        else:
            self.registers["F"] &= 0b01111111
