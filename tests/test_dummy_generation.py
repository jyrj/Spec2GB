def test_generation_pipeline():
    from generated.cpu import CPU

    cpu = CPU()
    cpu.memory = [{"op": "ADD_A_n8", "imm8": 3}, {"op": "ADD_A_n8", "imm8": 2}]
    cpu.reset()
    cpu.step()  # A = 0 + 3
    cpu.step()  # A = 3 + 2
    assert cpu.registers["A"] == 5
