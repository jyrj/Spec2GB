class Timer:
    def __init__(self):
        self.DIV = 0          # Divider register (0xFF04)
        self.TIMA = 0         # Timer counter (0xFF05)
        self.TMA = 0          # Timer modulo (0xFF06)
        self.TAC = 0          # Timer control (0xFF07)

        self.div_counter = 0  # Internal counter for DIV increments
        self.tima_counter = 0 # Internal counter for TIMA increments

    def read(self, addr):
        if addr == 0xFF04:
            return self.DIV
        elif addr == 0xFF05:
            return self.TIMA
        elif addr == 0xFF06:
            return self.TMA
        elif addr == 0xFF07:
            return self.TAC
        else:
            raise ValueError(f"Timer read: invalid address {hex(addr)}")

    def write(self, addr, val):
        val &= 0xFF
        if addr == 0xFF04:
            self.DIV = 0
            self.div_counter = 0
        elif addr == 0xFF05:
            self.TIMA = val
        elif addr == 0xFF06:
            self.TMA = val
        elif addr == 0xFF07:
            self.TAC = val & 0x07  # Only lower 3 bits used
        else:
            raise ValueError(f"Timer write: invalid address {hex(addr)}")

    def step(self, cycles):
        # Update DIV every 256 cycles
        self.div_counter += cycles
        while self.div_counter >= 256:
            self.div_counter -= 256
            self.DIV = (self.DIV + 1) & 0xFF

        # Check if timer is enabled
        if (self.TAC & 0x04) == 0:
            return  # Timer disabled

        # Timer input clock select
        speed = self.TAC & 0x03
        if speed == 0:
            period = 1024
        elif speed == 1:
            period = 16
        elif speed == 2:
            period = 64
        elif speed == 3:
            period = 256
        else:
            period = 1024  # default fallback

        # Update TIMA
        self.tima_counter += cycles
        while self.tima_counter >= period:
            self.tima_counter -= period
            self.TIMA += 1
            if self.TIMA > 0xFF:
                self.TIMA = self.TMA  # Reset TIMA on overflow
                # Normally trigger timer interrupt here (not implemented)
