Output a single Python file. Code only. No explanations. No ellipses. No truncation.
Include TODO comments for unimplemented parts.
Do not include markdown or comments about what the code does.
All code must be importable and self-contained.

# APU Template

Implement a Python class `APU` that contains audio control registers used by the Game Boy hardware. This is a stub implementation: actual audio behavior is not required.

## Requirements
- Registers: NR10–NR14, NR52, and wave RAM (0xFF30–0xFF3F).
- On `read(addr)`, return the current register value if known, otherwise 0xFF.
- On `write(addr, value)`, store the value in internal register map.
- Provide a `reset()` method that sets all values to 0.

Stub only: no sound generation, timers, or waveform logic required.

Class signature:
```python
class APU:
    def reset(self): ...
    def read(self, addr: int) -> int: ...
    def write(self, addr: int, value: int): ...
