from datetime import datetime, timezone, timedelta
from app.utils.Config import EXPIRES_IN_MIN, SECRET_KEY, ALGORITHM
from jose import jwt, JWTError
from fastapi import HTTPException
import secrets

def create_access_token (data:dict):
    try:
        to_encode = data.copy()

        expire = datetime.now(timezone.utc) + timedelta (minutes = EXPIRES_IN_MIN)

        to_encode.update ({"exp" : expire})

        return jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)
    
    except JWTError:
        raise HTTPException (status_code = 500, detail = "Something went wrong, Retry")
    

def create_refresh_token() -> str:
    return secrets.token_urlsafe(64)