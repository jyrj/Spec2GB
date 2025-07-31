import sys
sys.path.insert(0, "./generated")

from cartridge import Cartridge
from generated.memory import Memory
from generated.cpu import CPU

def main():
    # Load a dummy ROM with a jump instruction at the start
    rom_data = bytearray(0x8000)  # 32 KB ROM size for MBC0
    # Place a jump instruction at 0x0100 to address 0x0150 (JP 0x0150)
    rom_data[0x0100] = 0xC3  # Opcode for JP a16
    rom_data[0x0101] = 0x50  # Low byte of address
    rom_data[0x0102] = 0x01  # High byte of address

    # Create Cartridge with ROM data, no RAM for MBC0
    cartridge = Cartridge(rom=rom_data)

    # Create Memory with cartridge
    memory = Memory(cartridge)

    # Create CPU with memory
    cpu = CPU(memory)

    # Set PC to 0x0100 where program starts
    cpu.PC = 0x0100

    # Load the ROM into CPU's instruction memory for execution
    # For simplicity, we just store instructions manually
    cpu.memory_instructions = [
        {"op": "JP", "addr": 0x0150}  # Jump to 0x0150
    ]

    # Step CPU once to execute the jump
    cpu.step()

    # Print CPU PC to confirm jump
    print(f"CPU PC after jump: {hex(cpu.PC)}")

if __name__ == "__main__":
    main()