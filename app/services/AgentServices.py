from app.utils.Auth import get_current_agent
from app.schemas.TransactionSchema import AgentDepwith
from sqlalchemy.orm import Session
from app.models.UserModel import User
from fastapi import HTTPException
from app.models.WalletModel import Wallet
from app.utils.DailyLimit import checkDailyLimits
from app.models.TransactionModel import Transaction
from app.utils import Resend
from app.schemas.AgentSchema import CustomerInfo, UnflagUser
from sqlalchemy import or_
from app.models.AgentLogs import AgentLogs
from app.schemas.Responses import UserResponse, WalletResponse, TransactionResponse

async def getUserCredientials (data: CustomerInfo, db: Session, current_agent : User):
        
    try: 

        if data.email is None and data.phone is None:
            raise HTTPException (status_code = 400, detail = "Enter an identifier")
            
        user = db.query(User).filter (or_(User.email == data.email, User.phone == data.phone)).one_or_none()

        if not user: 
            raise HTTPException (status_code = 400, detail = "User not found")
        
        if user.isFlagged: 
            return {"Notice" : "User is flagged"}
            
        if user.isDeleted:
            return {"Notice" : "Account is deleted"}
        
        if user.role == "admin" and current_agent.role != "admin":
            current_agent.isFlagged = True 
            db.commit()
            raise HTTPException (status_code = 403, detail = "Your account has been flagged")

        newlog = AgentLogs (
            description = f"Agent {current_agent.name} / {current_agent.email} / {current_agent.phone} got {user.email} / {user.phone} credientials",
            agent_id = current_agent.user_id
        )

        db.add(newlog)
        db.commit()
        db.refresh(newlog)

        return {
            "User" : UserResponse.model_validate(user)
        }
    
    except HTTPException:
        raise 

    except Exception:
        db.rollback()
        raise HTTPException (status_code = 500, detail = "Something went wrong")

async def AgentDeposit (data: AgentDepwith, db: Session, current_agent : User):

    try: 
        if data.description is None:
            data.description = "Unspecified"

        customer_wallet = db.query(Wallet).filter (Wallet.wallet_id == data.customer_wallet_id).with_for_update().one_or_none()

        if not customer_wallet:
            raise HTTPException (status_code = 400, detail = "Wallet not found")
        
        
        await checkDailyLimits (db, customer_wallet.user.user_id, data.amount)
        
        customer_wallet.balance += data.amount
        
        newTrans = Transaction (
           amount = data.amount,
            trans_type = "In person deposit",
            description = data.description,
            wallet_id = customer_wallet.wallet_id
        )

        db.add(newTrans)

        newlogs = AgentLogs(
            description = f"Agent {current_agent.name} / {current_agent.email} / {current_agent.phone} deposited ${data.amount} in {customer_wallet.user.email} / {customer_wallet.user.phone} account",
            amount = data.amount,
            agent_id = current_agent.user_id
        )
        db.add(newlogs)

        try: 
            Resend.sendDepositEmail(customer_wallet.user.name, data.amount)
        except: 
            pass 

        db.commit()
        db.refresh(newTrans)
        db.refresh(customer_wallet)

        return {"Notice" : f"The amount of ${data.amount} has successfully been deposited into {customer_wallet.user.name} wallet"}
    
    except HTTPException:
        raise 
    
    except Exception as e:
        print (e)
        db.rollback()
        raise HTTPException (status_code = 500, detail = "Something went wrong, try again")

async def AgentWithdrawal (data : AgentDepwith, db:Session, current_agent:User):
    try:
        if data.description is None:
            data.description = "Unpecified"
        
        customer_wallet = db.query (Wallet).filter (Wallet.wallet_id == data.customer_wallet_id).with_for_update().one_or_none()

        if not customer_wallet:
            raise HTTPException (status_code = 400, detail = "Wallet not found")

        if customer_wallet.balance < data.amount:
            raise HTTPException (status_code = 400, detail = "Insufficient funds")

        await checkDailyLimits (db, customer_wallet.user.user_id, data.amount)

        customer_wallet.balance -= data.amount 

        newTrans = Transaction (
            amount = data.amount,
            trans_type = "In person withdrawal",
            description = data.description,
            wallet_id = customer_wallet.wallet_id
        )
        db.add(newTrans)

        newLogs = AgentLogs (
            description = f"Agent {current_agent.name} / {current_agent.email} / {current_agent.phone} withdrew ${data.amount} in {customer_wallet.user.email} / {customer_wallet.user.phone} account",
            amount = data.amount,
            agent_id = current_agent.user_id
        )
        db.add(newLogs)

        try:
            Resend.sendWithdrawEmail(customer_wallet.user.name, data.amount)
        except: 
            pass 

        db.commit()
        db.refresh(newTrans)
        db.refresh(newLogs)

        return {"Notice": f"The amount of ${data.amount} has been withdrew from {customer_wallet.user.name} account"}

    except HTTPException:
        raise
    
    except Exception:
        db.rollback()
        raise HTTPException (status_code = 500, detail = "Something went wrong. Please try again")

async def unflagUser (db:Session, current_agent:User, data: UnflagUser):
    try: 
        if not data.phone and not data.email:
            raise HTTPException (status_code = 400, detail = "You must enter the user's credientials")
        
        customer = db.query(User).filter(or_(User.email == data.email, User.phone == data.phone), User.isDeleted == False, User.isFlagged == True).one_or_none()

        if not customer:
            raise HTTPException (status_code = 404, detail = "The flagged user has not been found")
        
        if customer.role != "user":
            current_agent.isFlagged = True
            
            newLogs = AgentLogs (
                description = f"Agent {current_agent.user_id} / {current_agent.name} / {current_agent.email} attempted unflagging agent/admin {customer.user_id}/ {customer.name}",
                agent_id = current_agent.user_id
            )
            db.add(newLogs)
            db.commit()
            db.refresh(newLogs)

            return {"Your account has been flagged due to suspicious activities"}
        
        customer.isFlagged = False

        newAgentLogs = AgentLogs (
            description = f"Agent {current_agent.user_id}/{current_agent.name} successfully unflagged {customer.user_id}/ {customer.name}",
            agent_id = current_agent.user_id
        )

        db.add(newAgentLogs)
        db.commit()
        db.refresh(newAgentLogs)

        return {"Notice" : f"{customer.name} has successfully been unflagged"}
    
    except HTTPException:
        raise
    
    except Exception:
        db.rollback()
        raise HTTPException (status_code = 500, detail = "Something went wrong")
