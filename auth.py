
import secrets
import threading
import os
import shutil

from logger import print

print("auth module loaded.")

stored = {}

if os.path.exists("authdata"):
    if os.path.isfile("authdata"):
        print("authentication data: removed (should not be a file)")
        os.remove("authdata")
        os.makedirs("authdata")
    else:
        print("authentication data: OK")
else:
    print("authentication data: not created")
    os.makedirs("authdata")

for file in os.listdir("authdata"):
    path = os.path.join("authdata", file)

    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            stored[file] = f.read().strip().splitlines()


class TokenStore:
    def __init__(self):
        print("Auth module store initialized.")
        self._tokens = {}
        self._lock = threading.Lock()

        for key, value in stored.items():
            for token in value:
                self._tokens[token] = {"email": key.strip().lower()}
                print(f"Re-activated a token for {key.strip().lower()}")

    def _save(self, email, token):
        path = os.path.join("authdata", email.strip().lower())

        with open(path, "a", encoding="utf-8") as f:
            f.write(token + "\n")

    def issue(self, email):
        token = secrets.token_urlsafe(32)

        with self._lock:
            self._tokens[token] = {
                "email": email.strip().lower(),
            }

        return token

    def validate(self, token):
        if not token:
            print("Cannot validate empty token.")
            return None

        with self._lock:
            record = self._tokens.get(token)

            if record is None:
                print("Invalid token.")
                return None

            result = dict(record)

        print(f"Validated token for {result['email']}")
        return result

    def revoke(self, token):
        if not token:
            print("Cannot revoke empty token.")
            return False

        with self._lock:
            record = self._tokens.pop(token, None)

            if record is not None:
                path = os.path.join("authdata", record["email"])
                if os.path.isfile(path):
                    with open(path, "r", encoding="utf-8") as f:
                        tokens = f.read().splitlines()

                    with open(path, "w", encoding="utf-8") as f:
                        for saved_token in tokens:
                            if saved_token != token:
                                f.write(saved_token + "\n")

        print(f"Token revoked: {record is not None}")
        return record is not None

    def clear(self):
        with self._lock:
            os.makedirs("authdata", exist_ok=True)

            # Group tokens by account.
            stored = {}
            for token, record in self._tokens.items():
                email = record["email"]
                stored.setdefault(email, []).append(token)

            # Write the current state to disk.
            for file in os.listdir("authdata"):
                path = os.path.join("authdata", file)
                if os.path.isfile(path):
                    os.remove(path)
                    print(f"removed outdated status: {path}")

            for email, tokens in stored.items():
                path = os.path.join("authdata", email)
                with open(path, "w", encoding="utf-8") as f:
                    f.write("\n".join(tokens) + "\n")
                    print(f"wrote up-to-date status: {path}")
            if self._tokens:
                cl = 1
                print("Clearing tokens...")
            else:
                cl = 0
                print("No tokens to clear")

        if cl == 1:
                while self._tokens:
                    token = next(iter(self._tokens))
                    self._tokens.pop(token)
                    print(f"Unloaded a token.")
                print(f"Cleared tokens")
