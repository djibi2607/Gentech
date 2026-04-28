from fastapi import APIRouter, Depends
from app.schemas.AdminSchema import AgentLogFilters
from app.database import get_db
from app.utils.Auth import get_current_admin
from app.models.UserModel import User
from app.services import AdminServices
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/admin")

@router.post("/agent-logs")
async def getAgentLogs(data: AgentLogFilters, page: int = 1, limit: int = 10, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    return await AdminServices.get_agent_logs(db, data, current_admin, page, limit)