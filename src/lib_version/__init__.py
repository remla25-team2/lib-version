try:
    from ._version import __version__
except ImportError:
    try:
        import json
        import os
        with open(os.path.join(os.path.dirname(__file__), "version.json")) as f:
            __version__ = json.load(f)["version"]
    except (ImportError, FileNotFoundError, KeyError):
        __version__ = "0.0.0"