from passlib.context import CryptContext  # password hashing library
from jose import jwt, JWTError  # JWT token handling
from datetime import datetime, timedelta  # time handling for token expiry
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = "secret123"  # secret key for JWT encoding
ALGORITHM = "HS256"  # hashing algorithm used for JWT
ACCESS_TOKEN_EXPIRE_HOURS = 2  # token validity time

security = HTTPBearer()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # bcrypt password context


def hash_password(password: str) -> str:
    return pwd_context.hash(password)  # convert plain password to hashed password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)  # compare passwords safely


def create_token(data: dict):
    to_encode = data.copy()  # copy data to encode in token

    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)  # set expiry time
    to_encode.update({"exp": expire})  # add expiry to token payload

    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # generate JWT token
    return token  # return encoded token


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    return {"user_id": user_id}