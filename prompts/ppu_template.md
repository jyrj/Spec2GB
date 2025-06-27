 <!-- TODO -->
 You are a senior Gameboy emulator engineer, please write concise Python 3.13.5 code.

 Here is the current PPU register from spec.yaml:

 "
 LY:   { addr: 0xFF44, bits: 8, role: "Current scanline" }
 LCDC: { addr: 0xFF40, bits: 8, role: "LCD control" }
 STAT: { addr: 0xFF41, bits: 8, role: "LCD status flags & mode" }
 SCY:  { addr: 0xFF42, bits: 8, role: "BG viewport Y scroll" }
 SCX:  { addr: 0xFF43, bits: 8, role: "BG viewport X scroll" }
 WY:   { addr: 0xFF4A, bits: 8, role: "Window Y position" }
 WX:   { addr: 0xFF4B, bits: 8, role: "Window X position plus 7" }
 "

 # Step 1: Plan (<= 120 words)
 Create an outline of "generated/ppu.py" that stores these registers and supports "read" / "write"

 # Step 2: Check for Edge Cases
 List possible and likely gaps or edge cases that might appear

 # Step 3: Implement
 Output ONE python file only
 1. Define "Register8" which includes read and write
 2. Define a class called PPU with one "Register8" for every register and also read/write, raising ValueError on unknown regions
 3. insert "# TODO" comments for timing or interrupt logic
 4. must be less than or equal to 120 words

 Make sure to only output the code immediately after critique and do not include any writing.