from dataclasses import dataclass

@dataclass
class CPU:
    A: int = 0  # Accumulator (8-bit)
    F: int = 0  # Flag register (Z N H C)
    PC: int = 0  # Program Counter (16-bit)

    def reset(self):
        self.A = 0
        self.F = 0
        self.PC = 0

    def step(self, instruction):
        mnemonic = instruction.get("mnemonic")
        operand = instruction.get("operand", 0)

        if mnemonic == "ADD_A_n8":
            self.A = (self.A + operand) & 0xFF
        elif mnemonic == "SUB_A_n8":
            self.A = (self.A - operand) & 0xFF
        else:
            raise ValueError(f"Unsupported instruction: {mnemonic}")

        # Set Zero flag (bit 7) if A is zero
        if self.A == 0:
            self.F |= 0b10000000
        else:
            self.F &= 0b01111111
