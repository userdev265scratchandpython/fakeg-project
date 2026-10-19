#!/usr/bin/bash
clear
source .venv/bin/activate
./fix.sh
python testcli.py
