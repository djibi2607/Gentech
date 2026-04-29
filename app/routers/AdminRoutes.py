from fastapi import APIRouter, Depends
from app.schemas.AdminSchema import AgentLogFilters, DeleteUser
from app.database import get_db
from app.utils.Auth import get_current_admin
from app.models.UserModel import User
from app.services import AdminServices
from sqlalchemy.orm import Session
from app.schemas.AdminSchema import CirculationSchema
from app.schemas.AdminSchema import Code
from app.utils.Auth import get_current_user

router = APIRouter(prefix="/api/admin")

@router.post("/agent-logs")
async def getAgentLogs(data: AgentLogFilters, page: int = 1, limit: int = 10, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    return await AdminServices.get_agent_logs(db, data, current_admin, page, limit)

@router.post("/all-users-info")
async def getAllUsersInfo(page: int = 1, limit: int = 10, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    return await AdminServices.get_all_users_info(db, current_admin, page, limit)

@router.delete ("/softdelete")
async def delete_user (data : DeleteUser, db: Session = Depends(get_db), current_admin : User = Depends (get_current_admin)):
    return await AdminServices.delete_user(db,current_admin,data)

@router.post("/circulation/wallet")
async def getWalletCirculation(data: CirculationSchema, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    return await AdminServices.getCirculation(db, current_admin, data)

@router.post("/circulation/transactions")
async def getTransactionCirculation(data: CirculationSchema, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    return await AdminServices.getTransactionCirculation(db, current_admin, data)

@router.patch("/become-admin")
async def becomeAdmin(data: Code, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await AdminServices.becomeAdmin(db, current_user, data)