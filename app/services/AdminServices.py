from sqlalchemy.orm import Session
from app.schemas.AdminSchema import Promote
from app.models.UserModel import User
from fastapi import HTTPException
from sqlalchemy import or_
from app.schemas.AdminSchema import AgentLogFilters
from app.models.AgentLogs import AgentLogs
from datetime import datetime, timedelta, timezone
from sqlalchemy import func
from app.schemas.Responses import LogResponse
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

async def get_agent_logs (db: Session, data: AgentLogFilters, current_admin : User, page : int = 1, limit : int = 10):

    offset = (page - 1) * limit

    try: 
        if data.agent_id is None and data.date_from is None and data.date_to is None:
            raise HTTPException (status_code = 400, detail = "You must enter filters")
        
        query = db.query (AgentLogs)

        if data.agent_id:
            query = query.filter(AgentLogs.agent_id == data.agent_id)

        if data.date_from:
            query = query.filter(func.date(AgentLogs.executedAt) >= data.date_from)

        if data.date_to:
            query = query.filter (func.date(AgentLogs.executedAt)  <= data.date_to)

        logs = query.offset(offset).limit(limit).all()

        return [LogResponse.model_validate(log) for log in logs]
    
    except HTTPException:
        raise 

    except Exception:
        db.rollback()
        raise HTTPException (status_code = 500, detail = "Something went wrong")