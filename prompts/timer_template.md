# Timer Component Specification

Implement a `Timer` class that simulates the Game Boy timer hardware. It should have the following properties:

## Timer Registers (8-bit)

- `DIV` (Divider Register): Address 0xFF04  
  - Increments at a fixed rate: increases by 1 every 256 CPU cycles.  
  - Wraps around to 0 after 0xFF.

- `TIMA` (Timer Counter): Address 0xFF05  
  - Increments based on the timer speed selected in `TAC`.  
  - When `TIMA` overflows (goes from 0xFF to 0x00), it triggers a timer interrupt (not implemented here, just reset to `TMA`).

- `TMA` (Timer Modulo): Address 0xFF06  
  - Holds the value to reset `TIMA` to after overflow.

- `TAC` (Timer Control): Address 0xFF07  
  - Bits 0 and 1 select the timer speed:  
    - 00: 4096 Hz (cycle period: 1024 CPU cycles)  
    - 01: 262144 Hz (cycle period: 16 CPU cycles)  
    - 10: 65536 Hz (cycle period: 64 CPU cycles)  
    - 11: 16384 Hz (cycle period: 256 CPU cycles)  
  - Bit 2: Timer Enable (0=off, 1=on).

## Methods

- `read(addr)`: Return the value of the timer register at `addr`.
- `write(addr, val)`: Write `val` to the timer register at `addr`.
- `step(cycles)`: Advance the timer state by `cycles` CPU cycles. This updates `DIV` automatically and increments `TIMA` if timer enabled.

## Behavior

- `DIV` increments every 256 cycles, wraps at 0xFF.
- When enabled, `TIMA` increments according to selected speed.
- On `TIMA` overflow, reset `TIMA` to `TMA`.
- `step()` should be called regularly with the number of CPU cycles elapsed.

---

Please implement all timer logic inside the `Timer` class.
