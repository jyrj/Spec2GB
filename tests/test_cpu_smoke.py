from generated.cpu import CPU

def test_add():
    cpu = CPU()
    cpu.reset()
    cpu.step({"mnemonic": "ADD_A_n8", "operand": 7})
    assert cpu.A == 7
    assert (cpu.F & 0b10000000) == 0  # Zero flag should NOT be set

def test_sub_to_zero():
    cpu = CPU()
    cpu.reset()
    cpu.step({"mnemonic": "ADD_A_n8", "operand": 3})
    cpu.step({"mnemonic": "SUB_A_n8", "operand": 3})
    assert cpu.A == 0
    assert (cpu.F & 0b10000000) != 0  # Zero flag should be set
