"""
Real code is produced manually via LLM prompts:
  1. Edit spec.yaml
  2. Ask the LLM for Python that matches the new spec
  3. Paste the answer into generated/<component>.py
This script only drops in a trivial CPU stub so that imports succeed
on a fresh clone.
"""

from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "spec.yaml"
OUT = ROOT / "generated"
OUT.mkdir(exist_ok=True)

def generate(spec_path: Path | None = None) -> bool:
    spec_yaml = yaml.safe_load((spec_path or SPEC).read_text())

    # Always (over)write __init__.py
    (OUT / "__init__.py").write_text(
        "# Auto-generated – do not hand-edit\n"
    )

    # Provide a minimal CPU class if one is not yet generated
    cpu_py = OUT / "cpu.py"
    if not cpu_py.exists():
        cpu_py.write_text(
            f'''"""
Trivial CPU placeholder generated from spec v{spec_yaml.get("version",'0.x')}.
Replace me with real LLM-generated code.
"""
class CPU:
    def add(self, a: int, b: int) -> int:
        return a + b
'''
        )
    return True

if __name__ == "__main__":
    generate()
