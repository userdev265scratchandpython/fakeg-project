import inspect
import os
import builtins
import shutil
from datetime import datetime, timezone
from configbackend import SHOW_PRC_TS, SHOW_LGC, SHOW_TS

if SHOW_TS:
    if SHOW_PRC_TS:
        def tstamp():
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    else:
        def tstamp():
            return datetime.now().strftime("%Y-%m-%d %H:%M")
else:
    def tstamp():
        return ""

def clearlogs():
    if os.path.isfile("logs"):
        os.remove("logs")
    else:
        shutil.rmtree("logs")

startt = str(tstamp())

hasp = 1
log = ["// Winst FakeG log\n"]

def print(message):
    frame = inspect.currentframe().f_back
    caller = os.path.basename(frame.f_globals.get("__file__", "<unknown>")).rstrip(".py").center(12)

    if SHOW_LGC:
        if SHOW_TS:
            if hasp == 1:
                l = f"\n{tstamp()} : [{caller}] {message}".rstrip("\n")
            else:
                l = f"{tstamp()} : [{caller}] {message}".rstrip("\n")
        else:
            if hasp == 1:
                l = f"\n[{caller}] {message}".rstrip("\n")
            else:
                l = f"[{caller}] {message}".rstrip("\n")
    else:
        if SHOW_TS:
            if hasp == 1:
                l = f"\n{tstamp()} : {message}".rstrip("\n")
            else:
                l = f"{tstamp()} : {message}".rstrip("\n")
        else:
            if hasp == 1:
                l = f"\n{message}".rstrip("\n")
            else:
                l = f" {message}".rstrip("\n")
    log.append(l)
    builtins.print(l, end="")

hasp = 0
print("Logger module initialized")
hasp = 1

def writelog():
    if os.path.isfile("logs"):
        os.remove("logs")

    os.makedirs("logs", exist_ok=True)

    print("Writing log.")
    with open(f"logs/{startt}.log", "w") as f:
        for line in log:
            f.write(f"{line}")
