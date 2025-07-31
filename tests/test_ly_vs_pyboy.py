# tests/test_ly_vs_pyboy.py
import os, tempfile
from pyboy import PyBoy

from generated.ppu import PPU
from tests.test_cpu_vs_pyboy import build_rom      # reuse the tiny ROM

# ────────────────────────────────────────────────────────────────────────────
def _spawn_pyboy(rom_path: str) -> PyBoy:
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    return PyBoy(rom_path, window="null", sound_emulated=False, no_input=True)

def _peek_ly(pb: PyBoy) -> int:
    # PyBoy ≥ 2.0 exposes .memory (fast); fall back to helpers for 1.x
    if hasattr(pb, "memory"):
        return pb.memory[0xFF44]
    if hasattr(pb, "get_memory_value"):
        return pb.get_memory_value(0xFF44)
    return pb.get_memory()[0xFF44]

# ────────────────────────────────────────────────────────────────────────────
def test_ly_vs_pyboy():
    # --- build a throw‑away ROM ------------------------------------------------
    rom_bytes = build_rom()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".gb") as tmp:
        tmp.write(rom_bytes); tmp.flush(); rom_path = tmp.name

    # --- reference (PyBoy) -----------------------------------------------------
    pyboy = _spawn_pyboy(rom_path)

    # --- device‑under‑test (our PPU) ------------------------------------------
    ppu   = PPU()

    # We’ll run for two full frames: 2 × 154 × 456 = 140 448 CPU cycles
    total_cycles = 2 * PPU.TOTAL_SCANLINES * PPU.CYCLES_PER_SCANLINE

    for cyc in range(total_cycles):
        pyboy.tick()     # 1 CPU cycle
        ppu.tick()       # feed the same cycle to our PPU

        # check LY exactly at the end of every scan‑line
        if (cyc + 1) % PPU.CYCLES_PER_SCANLINE == 0:
            assert _peek_ly(pyboy) == ppu.read(0xFF44), (
                f"LY mismatch after {cyc+1} cycles"
            )

    pyboy.stop()