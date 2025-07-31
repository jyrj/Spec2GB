import pytest
from generated.cartridge import Cartridge
from generated.memory import Memory


def make_memory():
    rom = bytearray([0x00] * 0x8000)
    ram = bytearray([0x00] * 0x2000)
    cart = Cartridge(rom=rom, ram=ram)
    return Memory(cartridge=cart)

def test_invalid_write_address():
    memory = make_memory()
    # 0xEFFF is outside all defined memory regions in your MemoryRegion enum
    with pytest.raises(ValueError):
        memory.write(0xEFFF, 0x42)  # Invalid address

def test_invalid_write_value():
    memory = make_memory()
    with pytest.raises(ValueError):
        memory.write(0xA000, 300)  # Not a byte

def test_invalid_read_address():
    memory = make_memory()
    with pytest.raises(ValueError):
        memory.read(0x123456)  # Invalid address

def test_known_regions():
    assert get_memory_region(0x0000) == "ROM0"
    assert get_memory_region(0x8000) == "VRAM"
    assert get_memory_region(0xC000) == "WRAM0"
    assert get_memory_region(0xD000) == "WRAMX"
    assert get_memory_region(0xFE00) == "OAM"
    assert get_memory_region(0xFF80) == "HRAM"

def test_unknown_addresses():
    assert get_memory_region(0xFFFF) == "UNKNOWN"
    assert get_memory_region(-1) == "UNKNOWN"
    assert get_memory_region(0x10000) == "UNKNOWN"
