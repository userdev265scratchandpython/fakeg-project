#!/usr/bin/bash
clear
rm -rf server.build/ server.dist testcli.build/ testcli.dist/ .pytest_cache/ .venv/ __pycache__/
./fix.sh
source .venv/bin/activate
./fix.sh
uv run python -m nuitka testcli.py --standalone
uv run python -m nuitka server.py --standalone
clear
echo ========
echo == run testcli.dist/testcli.bin to launch client.
echo ========
server.dist/server.bin
