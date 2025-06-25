
---


# Roadmap

| Week | Mentee | Area owned | Goals & Deliverables |
|------|--------|-----------|----------------------|
| **1** | **A** | `cpu` spec + prompt | • Expand `cpu.alu_ops` to include AND, OR, XOR, INC.<br>• Fill `prompts/cpu_template.md` so it emits a Python `CPU` class with `reset()` and `step()` (ADD & SUB only).<br>• Run template through ChatGPT, paste result into `generated/cpu.py`.<br>• Add `tests/test_cpu_smoke.py` that instantiates `CPU` and calls `add()` / `sub()`. |
|      | **B** | `memory` spec + prompt | • Flesh out `memory.regions` to cover ROM, VRAM, WRAM, OAM (addresses & sizes only).<br>• Write `prompts/memory_template.md` that yields a simple `Memory` class supporting `read(addr)` / `write(addr,val)` with bounds checking.<br>• Generate code → `generated/memory.py`.<br>• Add `tests/test_mem_bounds.py` (write outside region raises `ValueError`). |
|      | **C** | `ppu` spec + prompt | • Add 5 more PPU registers (`STAT`,`SCY`,`SCX`,`WY`,`WX`).<br>• Create `prompts/ppu_template.md` that outputs a skeletal `PPU` class storing those registers.<br>• Generate code → `generated/ppu.py`.<br>• Add `tests/test_ppu_regs.py` that writes & reads each register. |
| **2** | **A** | Prompt iteration | • Update `cpu_template.md` to generate all 6 ALU ops.<br>• Regenerate `cpu.py`, extend tests to cover new ops. |
|      | **B** | PyBoy harness | • Build `cosim/pyboy_harness.py` that steps a ROM 50 instructions and returns (A, F, PC).<br>• Example script in `examples/run_pyboy.py`. |
|      | **C** | Integration tests | • Write `tests/test_cpu_vs_pyboy.py`: run one ADD via PyBoy harness; run same ADD on our `CPU`; assert A & flags match. |


At the end of Week 2 we will have:

* Expanded YAML spec with **clearly separated sections**.  
* Three prompt templates and generated Python modules.  
* Basic unit tests plus the first PyBoy comparison harness.

Cosimulation with mGBA can then be Phase 3 once the Python model grows.

---

