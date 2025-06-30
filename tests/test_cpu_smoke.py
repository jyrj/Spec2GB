from generated.cpu import CPU  # Adjust this if CPU is in a different location

def test_addition_and_subtraction():
    cpu = CPU()
    cpu.reset()
    
    cpu.memory = [
        {"op": "ADD_A_n8", "imm8": 3},  # A = 0 + 3 = 3
        {"op": "ADD_A_n8", "imm8": 2},  # A = 3 + 2 = 5
    ]

    cpu.step()
    cpu.step()

    assert cpu.registers["A"] == 5, f"Expected A to be 5, got {cpu.registers['A']}"

class CPU:
    def __init__(self):
        self.reset()

    def reset(self):
        # Initialize 8-bit registers A (accumulator) and F (flags), and 16-bit PC (program counter)
        self.registers = {
            "A": 0,
            "F": 0,
            "PC": 0
        }
        # Memory holds a list of instructions
        self.memory = []

    def step(self):
        pc = self.registers["PC"]

        # Check if we've reached the end of memory
        if pc >= len(self.memory):
            return  # No instruction to execute

        instr = self.memory[pc]  # Fetch instruction at current PC
        op = instr["op"]         # Operation mnemonic

        # Handle supported operations
        if op == "ADD_A_n8":
            # A ← A + imm8
            imm8 = instr["imm8"]
            self.registers["A"] = (self.registers["A"] + imm8) & 0xFF  # Ensure 8-bit wraparound

        elif op == "SUB_A_n8":
            # A ← A – imm8
            imm8 = instr["imm8"]
            self.registers["A"] = (self.registers["A"] - imm8) & 0xFF

        elif op == "AND_A_n8":
            # A ← A & imm8
            imm8 = instr["imm8"]
            self.registers["A"] = self.registers["A"] & imm8

        elif op == "OR_A_n8":
            # A ← A | imm8
            imm8 = instr["imm8"]
            self.registers["A"] = self.registers["A"] | imm8

        elif op == "XOR_A_n8":
            # A ← A ^ imm8
            imm8 = instr["imm8"]
            self.registers["A"] = self.registers["A"] ^ imm8

        elif op == "INC_A":
            # A ← A + 1
            self.registers["A"] = (self.registers["A"] + 1) & 0xFF

        else:
            raise ValueError(f"Unknown operation: {op}")

        # Increment the program counter (PC) after executing instruction
        self.registers["PC"] += 1
