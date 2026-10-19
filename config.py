from configbackend import MAX_REQUEST_SIZE, ALLOW_LOGS_CLEAR, GETQUEUE
from logger import print
for elem in GETQUEUE():
    print(elem)
