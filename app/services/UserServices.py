from app.schemas.UserSchema import CreateUser, Login, refreshTok
from sqlalchemy.orm import Session 
from app.models.UserModel import User
from fastapi import HTTPException
from sqlalchemy import or_
from app.utils.Hashing import hashPassword, verifyPassword
from app.models.WalletModel import Wallet
from app.utils.Jwt import create_access_token, create_refresh_token
from app.models.RefreshModel import RefreshToken
from datetime import datetime, timedelta, timezone
from app.utils import Resend
from app.models.TransactionModel import Transaction
from app.utils.DailyLimit import checkDailyLimits
from app.schemas.TransactionSchema import DepWith

async def signup (db: Session, data : CreateUser) -> dict:
    try:
        if data.email is None and data.phone is None:
            raise HTTPException (status_code = 400, detail = "You must provide an email or phone number")
    
        existing_user = db.query(User).filter(or_(User.email == data.email, User.phone == data.phone), User.isDeleted == False).first()

        if existing_user:
            raise HTTPException (status_code = 409, detail = "An account with these credentials already exists")
    
        newUser = User (
            email = data.email,
            phone = data.phone,
            name = data.name,
            password = hashPassword(data.password)
        )
        db.add(newUser)
        db.flush()

        newWallet = Wallet (
            user_id = newUser.user_id
        )
        db.add(newWallet)
        if data.email:
            Resend.sendWelcomeEmail(data.name)
        db.commit()
        db.refresh(newUser)
        db.refresh(newWallet)

        return {"Status" : f"Welcome, {data.name}, your account has successfully been created, you can now proceed to login"}
    
    except HTTPException:
        raise
    except Exception as e:
        print (e)
        db.rollback()
        raise HTTPException (status_code = 500, detail = "Something went wrong, Please try again")

async def login (db: Session, data: Login) -> dict:
    try:
        if not data.email and not data.phone:
            raise HTTPException (status_code = 400, detail = "You must enter your phone or email")
        
        user : User = db.query (User).filter (or_(User.email == data.email, User.phone == data.phone), User.isDeleted == False).one_or_none()

        if not user:
            raise HTTPException (status_code = 404, detail = "Your account has not been found. Please signup first")
        
        if not verifyPassword(data.password, user.password):
            raise HTTPException (status_code = 401, detail = "Incorrect password")
        
        accessToken = create_access_token (data = {"sub" : str (user.user_id)})

        refreshValue = create_refresh_token()

        newRefreshToken = RefreshToken(
            user_id = user.user_id,
            token = refreshValue,
            expiresAt = datetime.now(timezone.utc) + timedelta (hours = 1)
        )

        db.add (newRefreshToken)
        db.commit()
        db.refresh(newRefreshToken)

        return {"Notice" : f"You have been successfully logged in {user.name}",
                "Access Token" : accessToken,
                "Refresh Token" : refreshValue,
                "Token type" : "Bearer"
        }

    except HTTPException:
        raise 

    except Exception :
        
        db.rollback()
        raise HTTPException (status_code = 500, detail = "Something went wrong, Please try again")
    
async def refreshToken (data: refreshTok, db: Session):

    try: 
        storedToken = db.query(RefreshToken).filter(RefreshToken.token == data.token).one_or_none()

        if not storedToken:
            raise HTTPException (status_code = 401, detail = "Token not found")

        if storedToken.isRevoked:
            storedToken.userRefresh.isFlagged = True
            db.commit()
            raise HTTPException (status_code = 401, detail = "Invalid token")
        
        if storedToken.expiresAt < datetime.now(timezone.utc):
            storedToken.userRefresh.isFlagged = True
            db.commit()
            raise HTTPException (status_code = 401, detail = "Invalid Token")
        
        storedToken.isRevoked = True 

        newAccess = create_access_token(data = {"sub" : str (storedToken.user_id)})

        newRefreshvalue = create_refresh_token()

        newRefresh = RefreshToken (
            user_id = storedToken.user_id,
            token = newRefreshvalue,
            expiresAt = datetime.now(timezone.utc) + timedelta (hours = 1)
        )
        db.add(newRefresh)
        db.commit()
        db.refresh (newRefresh)

        return {"Access Token" : newAccess,
                "Refresh Token" : newRefreshvalue,
                "Token type" : "Bearer"
        }
    
    except HTTPException:
        raise 
    except Exception:
        db.rollback()
        raise HTTPException (status_code = 500, detail = "Something went wrong. Please try again")
    

async def deposit (data: DepWith, db: Session, current_user : User):

    try: 
        if data.description is None:
            data.description = "Unspecified"

        if current_user.isFlagged:
            raise HTTPException (status_code = 401, detail = "Unable to deposit due to suspicious activities. Please contact support")
        
        await checkDailyLimits (db, current_user.user_id, data.amount)
        
        current_user.wallet.balance += data.amount
        
        newTrans = Transaction (
           amount = data.amount,
            trans_type = "Deposit",
            description = data.description,
            wallet_id = current_user.wallet.wallet_id
        )

        db.add(newTrans)
        Resend.sendDepositEmail(current_user.name, data.amount)
        db.commit()
        db.refresh(newTrans)
        db.refresh(current_user.wallet)
        return {"Notice" : f"The amount of {data.amount} has successfully been deposited into your account"}
    
    except HTTPException:
        raise 
    
    except Exception as e:
        print (e)
        db.rollback()
        raise HTTPException (status_code = 500, detail = "Something went wrong, try again")

async def withdraw (db:Session, data : DepWith, current_user: User):
    
    try: 
        if data.description is None:
            data.description = "Unspecified"

        if current_user.isFlagged:
            raise HTTPException (status_code = 401, detail = "Unable to withdraw due to suspicious activities. Please contact support")
        
        if current_user.wallet.balance < data.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")

        await checkDailyLimits (db, current_user.user_id, data.amount)
        
        current_user.wallet.balance -= data.amount
        
        newTrans = Transaction (
           amount = data.amount,
            trans_type = "Withdraw",
            description = data.description,
            wallet_id = current_user.wallet.wallet_id
        )

        db.add(newTrans)
        Resend.sendWithdrawEmail(current_user.name, data.amount)
        db.commit()
        db.refresh(newTrans)
        db.refresh(current_user.wallet)

        return {"Notice" : f"The amount of {data.amount} has successfully been withdrawn from your account"}

    except HTTPException:
        raise 

    except Exception:
        db.rollback()
        raise HTTPException (status_code = 500, detail = "Something went wrong, try again")
    

        