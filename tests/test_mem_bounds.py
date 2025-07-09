import pytest
from generated.memory import get_memory_region

def test_rom0():
    assert get_memory_region(0x0000) == "ROM0"
    assert get_memory_region(0x3FFF) == "ROM0"

def test_romx():
    assert get_memory_region(0x4000) == "ROMX"
    assert get_memory_region(0x7FFF) == "ROMX"

def test_vram():
    assert get_memory_region(0x8000) == "VRAM"

def test_unknown():
    assert get_memory_region(0xFFFF) == "UNKNOWN"
