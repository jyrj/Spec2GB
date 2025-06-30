 <!-- TODO -->
Write a Python class named `CPU` that simulates a GameBoy-style processor.

Requirements:
- Implement a `reset()` method that initializes the registers A, F, PC to 0.
- Implement a `step()` method that fetches and executes the next instruction from memory.
- Instructions are dictionaries like:
  - {"op": "ADD_A_n8", "imm8": 5}
  - {"op": "INC_A"}
- Supported operations are:
  - ADD_A_n8 → A ← A + imm8
  - SUB_A_n8 → A ← A – imm8
  - AND_A_n8 → A ← A & imm8
  - OR_A_n8  → A ← A | imm8
  - XOR_A_n8 → A ← A ^ imm8
  - INC_A    → A ← A + 1
- The `A` and `F` registers are 8-bit. The `PC` (program counter) is 16-bit.
- Registers should be stored in a dictionary.
- `step()` should fetch the instruction at `PC`, execute it, and then increment PC.
- Assume instructions are stored in a list called `self.memory`.
- Add inline comments to explain the code.
