from sqlalchemy.orm import Session
from app.schemas.AdminSchema import Promote
from app.models.UserModel import User
from fastapi import HTTPException
from sqlalchemy import or_

async def promote_agent (db: Session, data: Promote, current_user: User):
    
    try:
        if current_user.role != "admin":
            raise HTTPException (status_code = 401, detail = "Access restricted")
        
        user = db.query (User).filter (or_(User.email == data.email, User.phone == data.phone), User.isDeleted == False, User.isFlagged == False).one_or_none()

        if not user:
            raise HTTPException (status_code= 404, detail = "User not found")
        
        user.role = "agent"

        db.commit()
        db.refresh (user)

    except HTTPException:
        raise 
    
    except Exception:
        db.rollback()
        raise HTTPException (status_code = 500, detail = "Something went wrong. Please try again")

    return {"Notice": f"{user.name} has successfully been promoted to agent"}

