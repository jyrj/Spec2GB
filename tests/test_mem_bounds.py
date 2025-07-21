import pytest
from generated.memory import get_memory_region

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
