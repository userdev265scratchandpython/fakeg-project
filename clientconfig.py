IP = "0.0.0.0"
PORT = "8080"

import os, shutil

if os.path.exists("fakeg_cli.winstconfig"):
    if not os.path.isfile("fakeg_cli.winstconfig"):
        shutil.rmtree("fakeg.winstconfig")
        print("Removed bad FS entry that was named like config")

haderrs = 0

if os.path.exists("fakeg_cli.winstconfig"):
    with open("fakeg_cli.winstconfig", "r") as f:
        for line in f.readlines():
            data = str(line).rstrip("\r").rstrip("\n").split(" : ")
            if line[0] == "#":
                pass
            elif len(data) == 2:
                key = data[0]
                val = data[1]
                val = val.lower()
                if key == "IP":
                    IP = val
                elif key == "PORT":
                    try:
                        port = str(int(port))
                    except Exception:
                        print(f"Bad config: port cannoy be {port}")
                        haderrs = 1
                else:
                    haderrs = 1
                    print(f"Unknown key : {key} ; Cannot apply value {val}")
            else:
                print(f"Malformed line : \"{line!r}\"")
    if haderrs == 0:
        print("Read config successfully")
    else:
        print("Read config with errors")
else:
    with open("fakeg_cli.winstconfig", "w") as f:
        f.write(f"IP : 0.0.0.0\nPORT : 8080")
    print("Wrote config successfully")
