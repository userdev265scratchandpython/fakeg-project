print("Importing pathlib... ", end="")
try:
    from pathlib import Path
    import sys
    print("Done")
except Exception:
    print("Failed")
    sys.exit(1)

try:
    print("Loading file... ", end="")
    path = Path(".venv/lib/python3.12/site-packages/atom/http_core.py")
    print("Reading... ", end="")
    file = path.read_text()
    print("Done")
except Exception as e:
    print(f"Failed: {e}")
    sys.exit(1)

try:
    print("Setting patterns... ", end="")
    old = "from . import http.client as httplib"
    new = "import http.client as httplib"
    print("Done")
except Exception as e:
    print(f"Failed: {e}")
    sys.exit(1)

try:
    print("Checking pattern and patching... ", end="")
    if old in file:
        path.write_text(file.replace(old, new))
        print("Patched atom/http_core.py")
    elif new in file:
        print("atom/http_core.py is already patched")
    else:
        raise RuntimeError(
            "Could not find the expected import in atom/http_core.py"
        )
except Exception as e:
    print(f"Failed: {e}")
    sys.exit(1)
