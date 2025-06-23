# Spec2GB

**Spec2GB** is a teaching-oriented research prototype that shows how an LLM‑powered *spec‑to‑code* agent can synthesize a cycle‑accurate Python model of the Nintendo ® Game Boy, and then co‑simulate that model against a *known‑good* open‑source emulator (mGBA).

> **Status:** Scaffold only – everything inside `generated/` is produced automatically by the generator.  
> **Goal for interns:** iterate on the `spec.yaml` and the prompt templates so that `generator/` can create an ever more complete Game Boy model.

---

## Repo layout

```
Spec2GB/
├── generator/          # Agent harness & prompt templates
│   └── generate.py     # stub that 'builds' a dummy module from spec
├── generated/          # ⚠️ auto‑generated – do not edit by hand
├── cosim/              # hooks for driving mGBA & comparing traces
├── spec.yaml           # machine‑readable architectural spec (tiny stub)
├── tests/              # pytest suite that proves the pipeline works
└── .github/workflows/  # CI (runs tests on every push)
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

### How does the “generation” work?

For now, **it doesn’t** – `generator/generate.py` pretends to read `spec.yaml` and just creates a trivial `add()` function. You’ll replace that with real OpenAI / Ollama / Llama.cpp calls later. The important bit is:

* **Never** touch files under `generated/` by hand.  
* Tests import from `generated.*`; if they fail, your agent broke the contract.

Happy hacking!

