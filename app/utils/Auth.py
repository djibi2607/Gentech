from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session 
from app.database import get_db
from jose import jwt, JWTError
from app.utils.Config import SECRET_KEY, ALGORITHM
from app.models.UserModel import User

async def get_current_user (credentials : HTTPAuthorizationCredentials = Depends (HTTPBearer()), db: Session = Depends (get_db)):

    try: 
        token = credentials.credentials

        to_decode = jwt.decode(token, SECRET_KEY, algorithms =[ALGORITHM])

        user_id : str = to_decode.get("sub")

        if not user_id:
            raise HTTPException (status_code = 401, detail = "Incorrect credentials")
        
        user = db.query(User).filter(User.user_id == int (user_id), User.isDeleted == False).one_or_none()

        if not user:
            raise HTTPException (status_code = 404, detail = "Authentication failed")
        
        return user
    
    except HTTPException:
        raise
    except JWTError:
        raise HTTPException (status_code = 500, detail = "Something went wrong, try again")

    
async def get_current_agent (current_user: User = Depends (get_current_user)):
    
    roles = ["admin", "agent"]

    if current_user.role not in roles:
        raise HTTPException (status_code = 401, detail = "Access restricted to agents")
    
    return current_user