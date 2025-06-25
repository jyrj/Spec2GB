
---


# Roadmap

| Week | Mentee | Focus | Concrete Deliverables |
|------|--------|-------|-----------------------|
| **1** | **A** (Spec Owner) | ⚙️  **Spec Evolution** <br>• Expand `spec.yaml` with four more ALU ops (AND, OR, XOR, INC) and 4 kB RAM.<br>• Add YAML comments that clarify each field. | PR: updated `spec.yaml` + short `docs/spec_notes.md`. |
|      | **B** (Prompt Engineer) | 📝 **Prompt Templates & Gen** <br>• Create `prompts/cpu_template.md` that converts *current* spec into a Python `CPU` class.<br>• Use ChatGPT (or another LLM) to generate code, paste into `generated/cpu.py`.<br>• Add/update `tests/test_cpu_smoke.py` that instantiates the class and calls `add()` / `sub()`. | PR: prompt + generated code + passing tests. |
|      | **C** (Harness Builder) | 🕹️ **PyBoy Integration** <br>• `cosim/pyboy_harness.py` that loads *Tetris.gb* ROM, steps 50 instructions, returns `A`, `F`, `PC`.<br>• Example script `examples/run_pyboy.py` prints those values. | PR: harness + example (no dependency on B’s code yet). |
| **2** | **A** | Extend spec with basic PPU registers (`LCDC`, `STAT`, `LY`) and Joypad block. | PR: `spec.yaml` v0.2 + changelog in `docs/`. |
|      | **B** | Update prompt/template to new spec, regenerate `generated/*.py`, keep tests green. | PR: regenerated code + extended tests. |
|      | **C** | Write `tests/test_alu_vs_pyboy.py`:<br>1. Executes one ADD and one SUB via PyBoy harness.<br>2. Executes same ops on `generated.cpu.CPU`.<br>3. Asserts register match. | PR: new test (CI passes). |

### Daily cadence

* Only the README and spec may change in ways that affect others; keep them small and well-commented.



---

