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
| RAMX   | 0xA000 | 0xBFFF | True   |
| VRAM   | 0x8000 | 0x9FFF | True   |
| WRAM0  | 0xC000 | 0xCFFF | False  |
| WRAMX  | 0xD000 | 0xDFFF | True   |
| OAM    | 0xFE00 | 0xFE9F | False  |
| TIMER  | 0xFF04 | 0xFF07 | True   |
| IO     | 0xFF00 | 0xFF7F | True   |
| HRAM   | 0xFF80 | 0xFFFE | False  |

# Step 4: Cartridge ROM and RAM Mapping (MBC0)
Update the `Memory` class so it accepts a `cartridge` object with:

- `cartridge.rom`: a `bytes` object with 32KB ROM data
- `cartridge.ram`: an optional `bytearray` for external RAM (usually 8KB)

The Memory class should:

- Map `ROM0` (0x0000–0x3FFF) and `ROMX` (0x4000–0x7FFF) to `cartridge.rom`
- Map `RAMX` (0xA000–0xBFFF) to `cartridge.ram` if present, or fallback to internal RAM
- All other regions (e.g. WRAM, VRAM, HRAM, etc.) use internal bytearrays
- The TIMER region should call `self.timer.read()` or `self.timer.write()` as appropriate

Implement `read(addr)` and `write(addr, val)`:

- ROM region reads return data from `cartridge.rom`
- RAM region reads/writes access `cartridge.ram` or fallback
- Writes to ROM should raise `ValueError`
- Invalid or unmapped addresses should raise `ValueError`

# Step 5: Add read8 alias
Add `read8(addr)` method that returns `self.read(addr)`.

This allows CPU bus calls like `bus.read8(pc)` to work without error.
