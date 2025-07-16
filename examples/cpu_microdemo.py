from generated.cpu import CPU  # adjust if needed

def main():
    cpu = CPU()
    cpu.reset()

    cpu.registers["F"] = 42  # Set F to some value to test LD_r_r

    cpu.memory = [
        {"op": "ADD_A_n8", "imm8": 5},          # A = 5
        {"op": "LD_n8_A_ptr", "n8": 10},        # RAM[10] = A (5)
        {"op": "LD_A_n8_ptr", "n8": 10},        # A = RAM[10] = 5
        {"op": "INC_A"},                        # A = 6
        {"op": "DEC_A"},                        # A = 5
        {"op": "LD_r_r", "r1": "A", "r2": "F"}, # A = F = 42
        {"op": "XOR_A_n8", "imm8": 0xFF},       # A ^= 0xFF
        {"op": "DI"},                           # IME = False
        {"op": "EI"},                           # IME = True
        {"op": "JP", "addr": 12},               # PC jumps forward (skips next line)
        {"op": "ADD_A_n8", "imm8": 1},          # Skipped
        {"op": "CALL", "addr": 14},             # Push PC, jump to 14
        {"op": "ADD_A_n8", "imm8": 2},          # Executed after RET
        {"op": "RET"},                          # Return to 12
    ]

    # Run all 13 steps
    for _ in range(13):
        cpu.step()

    # Print result
    print("A:", cpu.registers["A"])
    print("F:", cpu.registers["F"])
    print("PC:", cpu.registers["PC"])
    print("IME:", cpu.IME)
    print("RAM[10]:", cpu.ram[10])
    print("Stack:", cpu.stack)

if __name__ == "__main__":
    main()
