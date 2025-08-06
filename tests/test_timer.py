from generated.timer import Timer

def test_div_increments():
    timer = Timer()
    initial_div = timer.DIV
    timer.step(256)
    assert timer.DIV == (initial_div + 1) & 0xFF, "DIV did not increment properly after 256 cycles"

def test_tima_increments_when_enabled():
    timer = Timer()
    timer.TAC = 0x05  # Timer enabled, speed = 01 (16 cycles per increment)
    initial_tima = timer.TIMA
    timer.step(16)
    assert timer.TIMA == (initial_tima + 1) & 0xFF, "TIMA did not increment properly when enabled"

def test_tima_resets_on_overflow():
    timer = Timer()
    timer.TAC = 0x05  # Timer enabled
    timer.TMA = 0x42
    timer.TIMA = 0xFF
    timer.step(16)
    assert timer.TIMA == 0x42, "TIMA did not reset to TMA on overflow"
