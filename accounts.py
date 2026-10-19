import hashlib
import hmac
import os
import secrets

from logger import print
print("accounts module loaded")

class AccountStore:
    def __init__(self):
        print("Accounts module storage initialized")
        self._accounts = {}
        self._dummy_salt = secrets.token_bytes(16)
        self._dummy_hash = self._hash_password(
            "not-a-real-password",
            self._dummy_salt,
        )

    @staticmethod
    def _hash_password(password, salt):
        r = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            180_000,
        )
        print(f"Hashed {password} -> {r}")
        return r

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
        print(f"Registered {email} :: {password}")

    def authenticate(self, email, password):
        email = email.strip().lower()
        account = self._accounts.get(email)

        # Perform a password hash even for unknown accounts, so the
        # simplest username-enumeration timing difference is reduced.
        if account is None:
            candidate = self._hash_password(password, self._dummy_salt)
            hmac.compare_digest(candidate, self._dummy_hash)
            r = False
        else:
            candidate = self._hash_password(password, account["salt"])
            r = hmac.compare_digest(
                candidate,
                account["password_hash"],
            )
        print(f"Authenticated {account} :: {password} -> {r}")
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

        accounts.add_account(email, password)
        return accounts
