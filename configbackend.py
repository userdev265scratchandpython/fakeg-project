MAX_REQUEST_SIZE = 64 * 1024
ALLOW_LOGS_CLEAR = False
SHOW_PRC_TS = True
SHOW_LGC = True
SHOW_TS = True
IP = "0.0.0.0"
PORT = 8080

printqueue = []
def print(text):
    printqueue.append(text)

import os, shutil

if os.path.exists("fakeg.winstconfig"):
    if not os.path.isfile("fakeg.winstconfig"):
        shutil.rmtree("fakeg.winstconfig")
        print("Removed bad FS entry that was named like config")

haderrs = 0

if os.path.exists("fakeg.winstconfig"):
    with open("fakeg.winstconfig", "r") as f:
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
                elif key == "MAX_REQ_SZ":
                    try:
                        MAX_REQUEST_SIZE = int(val) * 1024
                    except:
                        print("Max request size must be INT. skipping.")
                        haderrs = 1
                elif key == "ALLOW_LOGSCLR_ONLOAD":
                    if val.lower() == "true":
                        ALLOW_LOGS_CLEAR = True
                    elif val.lower() == "false":
                        ALLOW_LOGS_CLEAR = False
                    else:
                        print("Allow Logs Clear Onload must be BOOL. skipping.")
                        haderrs = 1
                elif key == "SHOW_PRECISE_TS":
                    if val.lower() == "true":
                        SHOW_PRC_TS = True
                    elif val.lower() == "false":
                        SHOW_PRC_TS = False
                    else:
                        print("Show precise timestamp must be BOOL. skipping.")
                        haderrs = 1
                elif key == "SHOW_LOG_COMP":
                    if val.lower() == "true":
                        SHOW_LGC = True
                    elif val.lower() == "false":
                        SHOW_LGC = False
                    else:
                        print("Show logger component must be BOOL. skipping.")
                        haderrs = 1
                elif key == "SHOW_TIMESTAMP":
                    if val.lower() == "true":
                        SHOW_TS = True
                    elif val.lower() == "false":
                        SHOW_TS = False
                    else:
                        print("Show logger component must be BOOL. skipping.")
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
    with open("fakeg.winstconfig", "w") as f:
        f.write(f"MAX_REQ_SZ : {str(int(MAX_REQUEST_SIZE / 1024))}\nALLOW_LOGSCLR_ONLOAD : false\nSHOW_LOG_COMP : true\nSHOW_TIMESTAMP : true\nSHOW_PRECISE_TS : true\n")
    print("Wrote config successfully")

if not SHOW_TS:
    if SHOW_PRC_TS:
        print("Disabled showing precise timestamp: showing timestamp is disabled")
        SHOW_PRC_TS = False

print(f"Max request size        : {str(MAX_REQUEST_SIZE)}")
print(f"Allow log clear on load : {str(ALLOW_LOGS_CLEAR)}")
print(f"Show logger component   : {str(SHOW_LGC)}")
print(f"Show timestamp          : {str(SHOW_TS)}")
print(f"Show precise timestamp  : {str(SHOW_PRC_TS)}")
print(f"IP and port             : {IP}:{PORT}")

def GETQUEUE():
    return printqueue
