from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
from jose import jwt, JWTError
from app.utils.Config import SECRET_KEY, ALGORITHM
from app.database import SessionLocal
from app.models.UserModel import User
from fastapi.responses import JSONResponse
from app.models.BannedIps import BannedIps
from datetime import datetime, timezone

async def _rate_limit_exceeded_custom (request : Request, exc: RateLimitExceeded):

    try: 

        db = SessionLocal()

        request_ip = request.client.host

        new_banned_ip = BannedIps(
            ip = request_ip,
            addedAt = datetime.now(timezone.utc)
        )
        db.add(new_banned_ip)

        token = request.headers.get("Authorization")

        if not token or not token.startswith("Bearer "):
            return JSONResponse(status_code=429, content={"Notice": "Too many requests"})
        
        cleanToken = token.split (" ") [1]

        try: 
            to_decode = jwt.decode (cleanToken, SECRET_KEY, algorithms= [ALGORITHM])

            user_id : str = to_decode.get("sub")

            if not user_id:
                return JSONResponse(status_code=429, content={"Notice": "Too many requests"})
            
            user = db.query(User).filter(User.user_id ==  int (user_id), User.isDeleted == False).one_or_none()

            user.isFlagged = True

            db.commit()
            db.refresh(new_banned_ip)

            return JSONResponse(status_code=429,content={"Notice": "Your account has been flagged. Please contact support"})
        
        except HTTPException:
            raise 
        except JWTError:
            return JSONResponse(status_code=429, content={"Notice": "Too many requests"})  
    
    finally: 
        db.close()