import sys
import os

# Fix import path to load generated/memory.py and generated/cpu.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../generated')))

from generated.memory import Memory
from generated.cpu import CPU

def main():
    # Instantiate memory and CPU
    mem = Memory()
    cpu = CPU(memory=mem)  # Pass memory into CPU

    # --- Task 1: Test 1: Memory write/read directly in WRAM0 ---
    test_addr = 0xC000  # WRAM0 start address
    test_value = 0x42
    mem.write(test_addr, test_value)
    read_value = mem.read(test_addr)
    print(f"Memory write/read test: wrote {test_value:#04x}, read {read_value:#04x}")
    assert read_value == test_value, "Memory read/write test failed!"

    # --- Task 1: Test 2: CPU writes to memory, then reads back ---
    cpu.A = 0x77
    cpu.step({"op": "LD_n8_A_ptr", "n8": 0xC080})  # write A to WRAM0[0xC080]
    cpu.A = 0x00  # clear register
    cpu.step({"op": "LD_A_n8_ptr", "n8": 0xC080})  # read from WRAM0[0xC080] into A
    print(f"CPU memory write/read test: value in A is {cpu.A:#04x}")
    assert cpu.A == 0x77, "CPU memory read/write test failed!"

    # --- Task 2: Test read-only region (ROM0) ---
    rom_addr = 0x0000
    try:
        mem.write(rom_addr, 0x99)
        print("ERROR: Write to ROM0 should have failed but didn't!")
    except ValueError:
        print("Correctly prevented write to ROM0 (read-only)")

    # Read from ROM0 should work (usually contains initial data)
    rom_val = mem.read(rom_addr)
    print(f"ROM0 read test at {rom_addr:#06x}: value = {rom_val:#04x}")

    # --- Task 3: Test write to VRAM (writable) ---
    vram_addr = 0x8000
    vram_val = 0xAB
    mem.write(vram_addr, vram_val)
    assert mem.read(vram_addr) == vram_val, "VRAM write/read failed"
    print(f"VRAM write/read test passed at {vram_addr:#06x} with value {vram_val:#04x}")

    # --- Task 4: Test writing outside any writable region ---
    illegal_addr = 0xFFFF  # Assuming this is outside writable memory
    try:
        mem.write(illegal_addr, 0x01)
        print("ERROR: Write outside writable regions should have failed but didn't!")
    except ValueError:
        print(f"Correctly prevented write outside writable regions at {illegal_addr:#06x}")

if __name__ == "__main__":
    main()

