from fastapi import APIRouter, Depends
from app.models.UserModel import User
from app.utils.Auth import get_current_agent
from app.database import get_db
from app.services import AgentServices
from app.schemas.TransactionSchema import AgentDepwith
from app.schemas.AgentSchema import CustomerInfo, UnflagUser
from sqlalchemy.orm import Session

router = APIRouter(prefix = "/api/agent")

@router.get("/get-customer")
async def getCustomer(data: CustomerInfo, db: Session = Depends(get_db), current_agent: User = Depends(get_current_agent)):
    return await AgentServices.getUserCredentials(data, db, current_agent)

@router.post("/deposit")
async def deposit(data: AgentDepwith, db: Session = Depends(get_db), current_agent: User = Depends(get_current_agent)):
    return await AgentServices.AgentDeposit(data, db, current_agent)

@router.post("/withdraw")
async def withdraw(data: AgentDepwith, db: Session = Depends(get_db), current_agent: User = Depends(get_current_agent)):
    return await AgentServices.AgentWithdrawal(data, db, current_agent)

@router.patch("/unflag")
async def unflag(data: UnflagUser, db: Session = Depends(get_db), current_agent: User = Depends(get_current_agent)):
    return await AgentServices.unflagUser(db, current_agent, data)

