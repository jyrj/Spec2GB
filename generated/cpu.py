class CPU:
    def __init__(self):
        self.reset()

    # ------------------------------------------------------------------
    # state
    # ------------------------------------------------------------------
    def reset(self):
        # 8-bit A, F and 16-bit PC registers
        self.registers = {"A": 0, "F": 0, "PC": 0}

        # Optional instruction memory (code)
        self.memory = []

        # 256-byte RAM (data)
        self.ram = [0] * 256

        # Stack for CALL / RET instructions
        self.stack = []

        # Interrupt Master Enable flag (IME)
        self.IME = False

        # Timer registers (all 8-bit, stubbed)
        self.DIV = 0
        self.TIMA = 0
        self.TMA = 0
        self.TAC = 0

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
    # single-step execution
    # ------------------------------------------------------------------
    def step(self, instr=None):
        """
        If `instr` is supplied, execute it directly (used by tests).
        Otherwise fetch instruction from self.memory at PC and execute.
        """
        if instr is not None:
            # Convert test harness format to internal format if needed
            if "mnemonic" in instr:
                op = instr["mnemonic"]
                n = instr.get("operand")
                instr = {"op": op}
                if n is not None:
                    # Set all possible operand keys with n to support all ops
                    instr.update({"imm8": n, "n8": n, "addr": n, "offset": n})
            self._execute(instr)
            return

        pc = self.registers["PC"]
        if pc >= len(self.memory):
            return  # No instruction to execute

        instr = self.memory[pc]
        self._execute(instr)
        # Increment PC only if instruction did not alter PC explicitly
        if instr["op"] not in ("JP", "JR", "CALL", "RET"):
            self.registers["PC"] += 1

    # ------------------------------------------------------------------
    # execute instruction
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

        elif op == "JR":
            # Signed offset, so add and mask to 16-bit
            offset = instr["offset"]
            if offset & 0x80:  # if negative (signed 8-bit)
                offset -= 0x100
            self.registers["PC"] = (self.registers["PC"] + offset) & 0xFFFF

        elif op == "CALL":
            # Push address of next instruction to stack
            self.stack.append((self.registers["PC"] + 1) & 0xFFFF)
            self.registers["PC"] = instr["addr"]

        elif op == "RET":
            if self.stack:
                self.registers["PC"] = self.stack.pop()
            else:
                # Stack empty, halt or error - for now do nothing
                pass

        # --- Interrupts ---
        elif op == "DI":
            self.IME = False

        elif op == "EI":
            self.IME = True

        # --- HALT ---
        elif op == "HALT":
            # Placeholder for HALT instruction (no operation here)
            pass

        else:
            raise ValueError(f"Unknown operation: {op}")

    # ------------------------------------------------------------------
    # flag helper: update zero flag in F register (bit 7)
    # ------------------------------------------------------------------
    def _update_zero_flag(self):
        if self.registers["A"] == 0:
            self.registers["F"] |= 0b10000000  # Set zero flag
        else:
            self.registers["F"] &= 0b01111111  # Clear zero flag
