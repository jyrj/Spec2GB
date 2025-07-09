Write a Python class named `CPU` that simulates a GameBoy-style processor.

Requirements:

- Implement a `reset()` method that initializes the registers A, F, PC to 0, and sets up RAM as a list of 256 bytes.
- Implement a `step()` method that fetches and executes the next instruction from memory.
- Instructions are dictionaries like:
  - {"op": "ADD_A_n8", "imm8": 5}
  - {"op": "SUB_A_n8", "imm8": 2}
  - {"op": "AND_A_n8", "imm8": 0xF0}
  - {"op": "OR_A_n8", "imm8": 0x0F}
  - {"op": "XOR_A_n8", "imm8": 0xFF}
  - {"op": "INC_A"}
  - {"op": "DEC_A"}
  - {"op": "LD_r_r", "r1": "A", "r2": "F"}
  - {"op": "LD_A_n8_ptr", "n8": 42}
  - {"op": "LD_n8_A_ptr", "n8": 42}
  - {"op": "JP", "addr": 10}
  - {"op": "JR", "offset": -2}
  - {"op": "CALL", "addr": 20}
  - {"op": "RET"}

Supported operations:

- ADD_A_n8 → A ← A + imm8
- SUB_A_n8 → A ← A – imm8
- AND_A_n8 → A ← A & imm8
- OR_A_n8  → A ← A | imm8
- XOR_A_n8 → A ← A ^ imm8
- INC_A    → A ← A + 1
- DEC_A    → A ← A - 1
- LD_r_r         → r1 ← r2
- LD_A_n8_ptr    → A ← RAM[n8]
- LD_n8_A_ptr    → RAM[n8] ← A
- JP             → PC ← addr (no auto-increment)
- JR             → PC ← PC + offset (signed byte)
- CALL           → Push PC to stack, then PC ← addr
- RET            → Pop PC from stack

Other notes:

- A, F are 8-bit registers; PC is a 16-bit register.
- Registers should be stored in a dictionary called `self.registers`.
- Memory should be stored in `self.memory` (for code) and `self.ram` (for data).
- The stack is a list called `self.stack`, where `CALL` pushes and `RET` pops.
- `step()` should fetch the instruction at PC, execute it, and increment PC by 1, unless the instruction modifies PC directly (e.g. JP, JR, CALL, RET).
- Add inline comments to explain each operation.
