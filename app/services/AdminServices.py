from sqlalchemy.orm import Session
from app.schemas.AdminSchema import Promote
from app.models.UserModel import User
from fastapi import HTTPException
from sqlalchemy import or_
from app.schemas.AdminSchema import AgentLogFilters, DeleteUser, CirculationSchema, Code
from app.models.AgentLogs import AgentLogs
from sqlalchemy import func
from app.schemas.Responses import LogResponse, AdminAllUsers
from app.models.WalletModel import Wallet
from app.models.TransactionModel import Transaction
import os

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
    
async def get_all_users_info (db: Session, current_admin:User, page: int = 1, limit : int = 10):
    try: 

        offset = (page - 1) * limit

        users = db.query(User).offset(offset).limit(limit).all()

        return [AdminAllUsers.model_validate(user) for user in users]

    except Exception as e:
        print (e)
        
async def delete_user(db: Session, current_admin : User, data: DeleteUser):
    try: 

        user = db.query(User).filter(User.user_id == data.user_id).one_or_none()

        if not user:
            raise  HTTPException (status_code = 404, detail = "User not found")

        if user.isDeleted:
            return {"Notice" : "User already deleted"}
        
        user.isDeleted = True
        db.commit()
        return {"Notice": f"{user.name} has been successfully deleted"}

    except HTTPException:
        raise 

    except Exception as e:
        print (e)
        db.rollback()
        raise HTTPException (status_code = 500, detail = "Something went wrong. Try again")
    
async def getCirculation (db: Session, current_admin : User, data:CirculationSchema):

    try: 
        query = db.query(func.sum(Wallet.balance))

        if data.date_from:
            query = query.filter(func.date(Wallet.updatedAt) >= data.date_from)

        if data.date_to:
            query = query.filter(func.date(Wallet.updatedAt) <= data.date_to)

        circulation = query.scalar() or 0

        return {"Notice" : f"The total amount in Gentech is {circulation}"}
    
    except HTTPException:
        raise 

    except Exception:
        raise HTTPException (status_code = 500, detail = "Something went wrong")
    
async def getTransactionCirculation (db: Session, current_admin: User, data:CirculationSchema):
    
    try:
        types = ["Deposit", "Withdraw", "Transfer In", "Transfer Out"]

        if data.trans_type and data.trans_type not in types:
            raise HTTPException (status_code = 400, detail = "Wrong transaction_type")
        
        query = db.query (func.sum(Transaction.amount))

        count_query = db.query(Transaction)

        if data.date_from:
            query = query.filter(func.date(Transaction.initiatedAt) >= data.date_from)

            count_query = count_query.filter(func.date(Transaction.initiatedAt) >= data.date_from)

        if data.date_to:
            query = query.filter (func.date(Transaction.initiatedAt) <= data.date_to)

            count_query = count_query.filter(func.date(Transaction.initiatedAt) <= data.date_to)

        if data.trans_type:
            query = query.filter(Transaction.trans_type == data.trans_type)

            count_query = count_query.filter(Transaction.trans_type == data.trans_type)

        if not data.trans_type:
            query = query.filter (Transaction.trans_type.in_(["Deposit", "Withdraw", "Transfer Out"]))

            count_query = count_query.filter(Transaction.trans_type.in_(["Deposit", "Withdraw", "Transfer In"]))

        circulations = query.scalar() or 0
        
        circulations_count = count_query.count() or 0

        if data.date_from and data.date_to:
            return {"Analytics" : f"The amount circulating from {data.date_from} to {data.date_to} is ${circulations} and the number of transactions made is {circulations_count}"}
        else:
            return {"Analytics" : f"The amount circulating is $ {circulations} and the number of transactions made is {circulations_count}"}
        

    except HTTPException:
        raise

    except Exception as e:
        print (e)
        raise HTTPException (status_code = 500, detail = "Something went wrong. Try again")

async def becomeAdmin (db: Session, current_user : User, data: Code):
    
    try:

        if current_user.isFlagged == True:
            raise HTTPException (status_code = 400, detail = "Access restricted")
        
        existing_admin = db.query(User).filter(User.role == "admin").first()

        if existing_admin:
            raise HTTPException (status_code = 401, detail =  "Access Restricted")
        
        ADMIN_CODE  = os.getenv("ADMIN_CODE")

        if not ADMIN_CODE:
            raise HTTPException(status_code=500, detail="Admin code not configured")
        
        if data.code != ADMIN_CODE:
            current_user.isFlagged
            current_user.flag_reason = f"Try to become admin"
            db.commit()
            raise HTTPException (status_code = 400, detail = "Incorrect code")
        else:
            current_user.role = "admin"
            db.commit()
            return {"Notice" : "You are now admin of gentech"}

    except HTTPException:
        raise 

    except Exception:
        db.rollback()
        raise HTTPException (status_code = 500, detail = "Something went wrong")