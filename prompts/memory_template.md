<!-- TODO -->
You're helping with a Game Boy emulator. Please write simple Python 3.13.5 code.

# Step 1: Plan
Make a file `generated/memory.py` with an `Enum` class for memory regions. Each region should have a start and end address, and a banked flag (True/False). Add a `.contains(addr)` method to check if the address is in the region. Also write a `get_memory_region(addr)` function that returns the region name, or "UNKNOWN".

# Step 2: Edge Cases
Skip bad addresses or ones that don’t match.

# Step 3: Code
Use this table:

| Name   | Start  | End    | Banked |
|--------|--------|--------|--------|
| ROM0   | 0x0000 | 0x3FFF | False  |
| ROMX   | 0x4000 | 0x7FFF | True   |
| VRAM   | 0x8000 | 0x9FFF | True   |
| WRAM0  | 0xC000 | 0xCFFF | False  |
| WRAMX  | 0xD000 | 0xDFFF | True   |
| OAM    | 0xFE00 | 0xFE9F | False  |