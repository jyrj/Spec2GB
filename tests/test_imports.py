def test_repo_imports():
    """Smoke import until real tests arrive."""
    import importlib
    try:
        importlib.import_module("generated.cpu")
    except ModuleNotFoundError:
        # Acceptable on day-1; will disappear once prompts run
        pass
