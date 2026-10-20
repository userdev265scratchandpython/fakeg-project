
import hashlib
import hmac
import json
import os
import secrets
from threading import Lock

from logger import print

print("accounts module loaded")


class AccountStore:
    def __init__(self, storage_path="accounts.wdb"):
        print("Accounts module storage initialized")
        self._lock = Lock()

        self.storage_path = storage_path
        self._accounts = {}

        # Used for authentication attempts with unknown accounts.
        self._dummy_salt = secrets.token_bytes(16)
        self._dummy_hash = self._hash_password(
            "fakeg-dummy-password",
            self._dummy_salt,
        )

        self.load()

    @staticmethod
    def _hash_password(password, salt):
        return hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            180_000,
        )

    def load(self):
        """Load accounts from disk on startup."""
        if not os.path.exists(self.storage_path):
            print("No account storage found; starting empty")
            return

        with open(self.storage_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        accounts = {}

        for email, account in data.items():
            email = email.strip().lower()

            accounts[email] = {
                "salt": bytes.fromhex(account["salt"]),
                "password_hash": bytes.fromhex(
                    account["password_hash"]
                ),
            }

        self._accounts = accounts
        print(f"Loaded {len(self._accounts)} accounts")

    def write(self):
        """Write account data to disk."""
        data = {
            email: {
                "salt": account["salt"].hex(),
                "password_hash": account["password_hash"].hex(),
            }
            for email, account in self._accounts.items()
        }

        directory = os.path.dirname(
            os.path.abspath(self.storage_path)
        )
        os.makedirs(directory, exist_ok=True)

        temp_path = self.storage_path + ".tmp"

        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
                f.flush()
                os.fsync(f.fileno())

            os.replace(temp_path, self.storage_path)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

        print(f"Wrote {len(self._accounts)} accounts")

    def add_account(self, email, password):
        email = email.strip().lower()

        if not email or not password:
            raise ValueError("Email and password must not be empty")

        salt = secrets.token_bytes(16)
        password_hash = self._hash_password(password, salt)

        self._accounts[email] = {
            "salt": salt,
            "password_hash": password_hash,
        }

        self.write()
    
    def register_account(self, email, password):
        with self._lock:
            if email in self._accounts:
                return False

        # Only create the account after the duplicate check.
        salt = secrets.token_bytes(16)
        password_hash = self._hash_password(password, salt)

        self._accounts[email] = {
            "salt": salt,
            "password_hash": password_hash,
        }

        self.write()
        return True

    def authenticate(self, email, password):
        email = email.strip().lower()
        account = self._accounts.get(email)

        # Perform a password hash even for unknown accounts, so the
        # simplest username-enumeration timing difference is reduced.
        if account is None:
            candidate = self._hash_password(
                password,
                self._dummy_salt,
            )
            hmac.compare_digest(candidate, self._dummy_hash)
            r = False
        else:
            candidate = self._hash_password(
                password,
                account["salt"],
            )
            r = hmac.compare_digest(
                candidate,
                account["password_hash"],
            )

        return r

    @classmethod
    def for_local_development(cls):
        accounts = cls()

        email = os.environ.get(
            "FAKEG_DEMO_EMAIL",
            "demo@example.test",
        )
        password = os.environ.get(
            "FAKEG_DEMO_PASSWORD",
            "fakeg-demo-password",
        )

        email = email.strip().lower()

        # Seed the demo account only when it doesn't already exist.
        # This preserves the existing password across restarts.
        if email not in accounts._accounts:
            accounts.add_account(email, password)

        return accounts

