<!-- Copy-paste this into your favorite LLM chat window -->

**TASK**  
Generate a Python class that implements the ADD and SUB opcodes for the
Game Boy-CPU according to the YAML spec below.  
The class must be pure-Python, no external deps, and expose:

* `reset()` – sets all registers to zero
* `step(opcode, *operands)` – executes one instruction and updates registers

Return only valid Python (no markdown fences).

```yaml
<< paste spec.yaml here >>

(Feel free to add more prompt templates.)
```
