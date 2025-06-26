 <!-- TODO -->
Write a Python class named `CPU` that models a simplified GameBoy CPU.

- It should have 8-bit registers: A (accumulator) and F (flags), and a 16-bit PC (program counter).
- Implement a method `reset()` that sets all registers to 0.
- Implement a method `step()` that accepts a dictionary like:
  {"mnemonic": "ADD_A_n8", "operand": 5}
- In `step()`, support two operations:
  - ADD_A_n8: A ← A + operand
  - SUB_A_n8: A ← A – operand
- If A becomes 0 after an operation, set the Zero flag (bit 7 of F).
- You can ignore other flags for now.

Use Python’s `@dataclass` to define the CPU class.
