#!/usr/bin/env bash
uv lock
uv sync
uv run pylint .venv/lib/python3.12/site-packages/atom .venv/lib/python3.12/site-packages/gdata --verbose
2to3 -w .venv/lib/python3.12/site-packages/atom --verbose
2to3 -w .venv/lib/python3.12/site-packages/gdata --verbose
python fix.py
uv run pylint --disable=E --errors-only server.py auth.py accounts.py logger.py config.py fix.py testcli.py tcli2.py tcli.py .venv/lib/python3.12/site-packages/atom .venv/lib/python3.12/site-packages/gdata
