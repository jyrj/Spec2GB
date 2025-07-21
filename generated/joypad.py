class Joypad:
    def __init__(self):
        self.reset()

    def reset(self):
        # Initialize joypad register P1 (0xFF00) to 0xFF (no button pressed)
        self.P1 = 0xFF

        # 4-directional buttons: Down, Up, Left, Right
        # Action buttons: Start, Select, B, A
        self.buttons = {
            "right": False,
            "left": False,
            "up": False,
            "down": False,
            "a": False,
            "b": False,
            "select": False,
            "start": False
        }

        # 0: pressed, 1: not pressed (active low)
        self.select_directions = True  # Bit 4 = 0 means direction keys selected
        self.select_buttons = True     # Bit 5 = 0 means button keys selected

    def read(self):
        result = 0xCF  # Upper 4 bits = 1, bits 4 and 5 = select lines

        if not self.select_buttons:
            # Action buttons
            result &= ~(0x01 if self.buttons["a"] else 0x00)
            result &= ~(0x02 if self.buttons["b"] else 0x00)
            result &= ~(0x04 if self.buttons["select"] else 0x00)
            result &= ~(0x08 if self.buttons["start"] else 0x00)

        if not self.select_directions:
            # Directional buttons
            result &= ~(0x01 if self.buttons["right"] else 0x00)
            result &= ~(0x02 if self.buttons["left"] else 0x00)
            result &= ~(0x04 if self.buttons["up"] else 0x00)
            result &= ~(0x08 if self.buttons["down"] else 0x00)

        return result

    def write(self, value):
        # Only bits 4 and 5 are writable
        self.select_buttons = not (value & (1 << 5))
        self.select_directions = not (value & (1 << 4))

    def press(self, key):
        if key in self.buttons:
            self.buttons[key] = True

    def release(self, key):
        if key in self.buttons:
            self.buttons[key] = False
