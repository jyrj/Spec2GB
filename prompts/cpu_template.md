Write a Python class named `CPU` that simulates a GameBoy-style processor.

Requirements:

- Implement a `reset()` method that initializes:
  - registers A, F, PC to 0,
  - RAM as a list of 256 bytes,
  - stack as an empty list,
  - Interrupt Master Enable flag (`IME`) as `False`,
  - timer registers `DIV`, `TIMA`, `TMA`, and `TAC` as 8-bit values initialized to 0.

- Implement a `step()` method that:
  - fetches the next instruction from `self.memory` using the program counter (`PC`),
  - executes the instruction,
  - increments the PC by 1 unless the instruction modifies PC directly (e.g. JP, JR, CALL, RET).

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
  - {"op": "DI"}
  - {"op": "EI"}

- Supported operations:

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
  - CALL           → push current PC + 1 to stack, then PC ← addr
  - RET            → pop PC from stack
  - DI             → IME ← False (disable interrupts)
  - EI             → IME ← True (enable interrupts)

- Other notes:

  - Registers A, F, and timers (DIV, TIMA, TMA, TAC) are 8-bit; PC is 16-bit.
  - The `IME` (Interrupt Master Enable) is a boolean flag initialized to `False`.
  - Registers are stored in a dictionary `self.registers`.
  - Code instructions are stored in `self.memory`.
  - Data memory (RAM) is stored in `self.ram`.
  - The call stack is stored as a Python list `self.stack`.
  - `step()` executes the instruction at PC and updates PC accordingly.
  - Timer logic can be stubbed (no actual timer counting required yet).
  - Add inline comments explaining the code and each operation.
