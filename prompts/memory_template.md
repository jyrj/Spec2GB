Output a single Python file. Code only. No explanations. No ellipses. No truncation.
Include TODO comments for unimplemented parts.
Do not include markdown or comments about what the code does.
All code must be importable and self-contained.

You're helping with a Game Boy emulator. Please write simple Python 3.13.5 code.

# Step 1: Plan
Make a file `generated/memory.py` with an `Enum` class called `MemoryRegion`.

Each enum entry should have:
- a start address
- an end address
- a banked flag (True/False)

Add a method `.contains(addr)` to check if a given address falls within the region's range.

Also write a function `get_memory_region(addr)` that:
- returns the name of the matching memory region
- returns `"UNKNOWN"` if the address doesn't belong to any region

# Step 2: Edge Cases
If the address is invalid or outside all regions, return `"UNKNOWN"`.

# Step 3: Code
Use this table to define the regions:

| Name   | Start  | End    | Banked |
|--------|--------|--------|--------|
| ROM0   | 0x0000 | 0x3FFF | False  |
| ROMX   | 0x4000 | 0x7FFF | True   |
| VRAM   | 0x8000 | 0x9FFF | True   |
| WRAM0  | 0xC000 | 0xCFFF | False  |
| WRAMX  | 0xD000 | 0xDFFF | True   |
| OAM    | 0xFE00 | 0xFE9F | False  |
| HRAM   | 0xFF80 | 0xFFFE | False  |
