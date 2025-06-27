import pytest
from generated.ppu import PPU

REG_ADDRS = [
    0xFF40,  # LCDC
    0xFF41,  # STAT
    0xFF42,  # SCY
    0xFF43,  # SCX
    0xFF44,  # LY
    0xFF4A,  # WY
    0xFF4B,  # WX
]

@pytest.mark.parametrize("addr", REG_ADDRS)
def test_write_then_read(addr):
    ppu = PPU()
    ppu.write(addr, 0xAB)           # write an arbitrary byte
    assert ppu.read(addr) == 0xAB   # must read back the same byte
