import re

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def validate_signup_form(email: str, nickname: str, password: str):
    if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
        raise ValueError("Invalid email format")
    if not re.match(r"^[\uAC00-\uD7A3a-zA-Z0-9]{1,20}$", nickname):
        raise ValueError("Invalid nickname format or length")
    if not re.match(r"^(?=.*[a-zA-Z])(?=.*[!@#$%^*+=-])(?=.*[0-9]).{10,25}$", password):
        raise ValueError("Invalid password format or length")
