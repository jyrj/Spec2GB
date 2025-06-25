# Spec2GB

**Spec2GB** is a teaching-oriented research prototype that shows how an LLM‑powered *spec‑to‑code* agent can synthesize a Python model of the Nintendo ® Game Boy, and then co‑simulate that model against a *known‑good* open‑source emulator (mGBA).

The long–term vision is to co-simulate selective components against a trusted
reference emulator (mGBA), but we’ll start with quick checks using **PyBoy**.


> **Status:** Bare-bones scaffold.  
> **Intern Goal (summer 2025):** grow `spec.yaml`, refine prompt templates, and
> keep committing the LLM-generated code under `generated/`.


---

## Repo layout

```
Spec2GB/
├── prompts/           # example prompt templates (LLM copy-&-paste)
├── generator/         # helper script that writes generated/ stubs
│   └── generate.py    # placeholder generator
├── generated/         # ⚠️ LLM-created code – never hand-edit
├── cosim/             # glue to run PyBoy / mGBA comparisons
├── spec.yaml          # single source of truth for the architecture
├── tests/             # pytest suites
└── .github/
    └── workflows/     # CI: lint + tests on every push

```

See `CONTRIBUTING.md` (coming soon) for coding style, branching and commit rules.

---

## Quick‑start

```bash
# clone
git clone https://github.com/jyrj/spec2gb
cd spec2gb
# install deps
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# run the generator (creates generated/*.py)
python -m generator.generate

# run tests
pytest -q
```

On every push, GitHub Actions executes the same steps to keep `main` green.

---

Happy hacking!

