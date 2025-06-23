"""Stub generator that turns `spec.yaml` into a dummy Python module.

Replace the body of `generate()` with real LLM calls later.
"""

from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SPEC_PATH = REPO_ROOT / "spec.yaml"
GENERATED_DIR = REPO_ROOT / "generated"
GENERATED_DIR.mkdir(exist_ok=True)

def generate(spec_path: Path | None = None):
    spec_file = spec_path or SPEC_PATH
    spec = yaml.safe_load(spec_file.read_text())

    # Create/overwrite __init__.py
    (GENERATED_DIR / "__init__.py").write_text(
        "# Auto‑generated package – do not edit by hand\n"
    )

    # Dummy example: create a CPU module with one add() function
    cpu_code = f'''"""Generated CPU module from spec v{spec.get("version", "0.x")}"""

def add(a: int, b: int) -> int:
    return a + b
'''
    (GENERATED_DIR / "cpu.py").write_text(cpu_code)
    return True

if __name__ == "__main__":
    generate()
