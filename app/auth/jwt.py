from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(rounds=10)
    ).decode("utf-8")


def verify_password(plain: str, hashed: str, db=None, user=None) -> bool:
    is_valid = bcrypt.checkpw(
        plain.encode("utf-8"),
        hashed.encode("utf-8")
    )

    # silently rehash if stored hash used fewer than 12 rounds
    if is_valid and db and user and not hashed.startswith("$2b$12$"):
        user.password_hash = hash_password(plain)
        db.commit()

    return is_valid


def create_access_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)  # ✅ was minutes
    payload.update({"exp": expire})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None