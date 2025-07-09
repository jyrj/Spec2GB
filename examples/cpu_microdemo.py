from generated.cpu import CPU  # adjust path if needed

def main():
    cpu = CPU()
    cpu.reset()

    cpu.memory = [
        {"op": "ADD_A_n8", "imm8": 5},
        {"op": "INC_A"},
        {"op": "XOR_A_n8", "imm8": 0xFF},
        {"op": "AND_A_n8", "imm8": 0xF0},
        {"op": "OR_A_n8", "imm8": 0x0F},
        {"op": "SUB_A_n8", "imm8": 100},
        {"op": "INC_A"},
        {"op": "INC_A"},
        {"op": "XOR_A_n8", "imm8": 0xAA},
        {"op": "ADD_A_n8", "imm8": 1}
    ]

    for _ in range(10):
        cpu.step()

    print("A:", cpu.registers["A"])
    print("F:", cpu.registers["F"])
    print("PC:", cpu.registers["PC"])

if __name__ == "__main__":
    main()
