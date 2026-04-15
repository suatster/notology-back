import bcrypt
import hashlib

def hash_password(password: str) -> str:
    pwd_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_hash.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_hash = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
    return bcrypt.checkpw(
        pwd_hash.encode("utf-8"), 
        hashed_password.encode("utf-8")
    )
