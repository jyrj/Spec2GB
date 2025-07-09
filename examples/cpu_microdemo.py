from generated.cpu import CPU  # adjust path if needed

def main():
    cpu = CPU()
    cpu.reset()

    # Program with ALU ops + load/store + INC/DEC
    cpu.memory = [
        # ALU ops from original demo
        {"op": "ADD_A_n8", "imm8": 5},
        {"op": "INC_A"},
        {"op": "XOR_A_n8", "imm8": 0xFF},
        {"op": "AND_A_n8", "imm8": 0xF0},
        {"op": "OR_A_n8", "imm8": 0x0F},
        {"op": "SUB_A_n8", "imm8": 100},

        # Load/store + INC/DEC ops
        {"op": "INC_A"},                      # Increment A
        {"op": "INC_A"},
        {"op": "XOR_A_n8", "imm8": 0xAA},    # Just for variation
        {"op": "ADD_A_n8", "imm8": 1},

        {"op": "LD_n8_A_ptr", "n8": 20},     # Store A into RAM[20]
        {"op": "LD_A_n8_ptr", "n8": 20},     # Load A from RAM[20]
        {"op": "DEC_A"},                      # Decrement A

        {"op": "LD_r_r", "r1": "F", "r2": "A"}  # Copy A into F register
    ]

    # Initialize RAM address 20 to 0 explicitly
    cpu.ram[20] = 0

    # Run all instructions
    for _ in range(len(cpu.memory)):
        cpu.step()

    print("A:", cpu.registers["A"])
    print("F: {:08b}".format(cpu.registers["F"]))  # binary flags
    print("PC:", cpu.registers["PC"])

if __name__ == "__main__":
    main()