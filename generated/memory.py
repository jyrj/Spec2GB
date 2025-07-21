from enum import Enum

class MemoryRegion(Enum):
    ROM0 = (0x0000, 0x3FFF, False)
    ROMX = (0x4000, 0x7FFF, True)
    VRAM = (0x8000, 0x9FFF, True)
    WRAM0 = (0xC000, 0xCFFF, False)
    WRAMX = (0xD000, 0xDFFF, True)
    OAM = (0xFE00, 0xFE9F, False)

    def contains(self, addr):
        return self.value[0] <= addr <= self.value[1]

def get_memory_region(addr):
    for region in MemoryRegion:
        if region.contains(addr):
            return region.name
    return "UNKNOWN"
