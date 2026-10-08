import hashlib
import secrets

import bcrypt


class PasswordService:
    @staticmethod
    def hash_pwd(password: str) -> str:
        salt = bcrypt.gensalt()
        pwd_bytes: bytes = password.encode(encoding="utf-8")
        hashed_pwd_bytes = bcrypt.hashpw(pwd_bytes, salt)
        return hashed_pwd_bytes.decode(encoding="utf-8")

    @staticmethod
    def verify(password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            password=password.encode(encoding="utf-8"),
            hashed_password=hashed_password.encode(encoding="utf-8"),
        )


class HashService:
    @classmethod
    def hash_data(cls, token: str) -> str:
        bytes_ = token.encode("utf-8")
        return hashlib.sha256(bytes_).hexdigest()

    @classmethod
    def verify(cls, value: str, to_compare: str) -> bool:
        return secrets.compare_digest(value, to_compare)
