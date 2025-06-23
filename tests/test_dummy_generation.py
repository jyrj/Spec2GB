import importlib, sys
from generator.generate import generate

def test_generation_pipeline():
    # should succeed without exceptions
    assert generate()

    # dynamic import after generation
    mod = importlib.import_module("generated.cpu")
    assert mod.add(2, 3) == 5
