from app.schemas.UserSchema import CreateUser, Login, refreshTok, UpdateEmail, UpdatePassword, UpdatePhone
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
from app.schemas.TransactionSchema import DepWith, Transfer
from fastapi_cache import FastAPICache

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

        try: 
            if data.email:
                Resend.sendWelcomeEmail(data.name)
        except: 
            pass

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

    except Exception  as e:
        print (e)
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
        await FastAPICache.clear()

        db.add(newTrans)

        try: 
            Resend.sendDepositEmail(current_user.name, data.amount)
        except: 
            pass 

        await FastAPICache.clear(namespace = f"Balance:{current_user.user_id}")
        
        db.commit()
        db.refresh(newTrans)
        db.refresh(current_user.wallet)
        return {"Notice" : f"The amount of ${data.amount} has successfully been deposited into your account"}
    
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

        try: 
            Resend.sendWithdrawEmail(current_user.name, data.amount)
        except: 
            pass

        await FastAPICache.clear(namespace = f"Balance:{current_user.user_id}")

        db.commit()
        db.refresh(newTrans)
        db.refresh(current_user.wallet)

        return {"Notice" : f"The amount of ${data.amount} has successfully been withdrawn from your account"}

    except HTTPException:
        raise 

    except Exception:
        db.rollback()
        raise HTTPException (status_code = 500, detail = "Something went wrong, try again")
    
async def transfer (db: Session, data: Transfer, current_user : User):

    try:
        
        if current_user.isFlagged:
            raise HTTPException (status_code = 401, detail = "Unable to transfer due to suspicious activities. Please contact our support")

        if data.description is None:
            data.description = "Unspecified"

        if data.receiver_email is None and data.receiver_phone is None:
            raise HTTPException (status_code = 400, detail = "You must provide the recepient email or phone")
        
        if data.amount > current_user.wallet.balance:
            raise HTTPException (status_code = 400, detail = "Insufficient funds")
        
        
        receiver = db.query (User).filter (or_(User.email == data.receiver_email, User.phone == data.receiver_phone), User.isDeleted == False).one_or_none()

        if not receiver:
            raise HTTPException (status_code = 404, detail = "Receipient not found")
        
        if current_user.user_id == receiver.user_id:
            raise HTTPException (status_code = 400, detail = "You cannot make a transaction to your bank account")
        
        await checkDailyLimits(db, current_user.user_id, data.amount)

        receiverTrans = Transaction (
            amount = data.amount,
            trans_type = "Transfer In",
            description = data.description,
            sender_id = current_user.user_id,
            wallet_id = receiver.wallet.wallet_id
        )
        db.add(receiverTrans)

        senderTrans = Transaction (
            amount = data.amount,
            trans_type = "Transfer Out",
            description = data.description,
            receiver_id = receiver.user_id,
            wallet_id = current_user.wallet.wallet_id
        )
        db.add (senderTrans)
        
        current_user.wallet.balance -= data.amount
        receiver.wallet.balance += data.amount

        try: 
            Resend.sendTransferEmailReceiver (receiver.name, data.amount, current_user.name, current_user.email, current_user.phone)
            Resend.sendTransferEmailSender (current_user.name, data.amount, receiver.name, receiver.email)
        except: 
            pass
        
        await FastAPICache.clear(namespace = f"Balance:{current_user.user_id}")
        await FastAPICache.clear(namespace = f"Balance:{receiver.user_id}")

        db.commit()
        db.refresh(receiverTrans)
        db.refresh(senderTrans)

        return {"Notice" : f"Your transfer of ${data.amount} is being processed. We will notify you after getting processed"}
    
    except HTTPException:
        raise 

    except Exception:
        db.rollback()
        raise HTTPException (status_code = 500, detail = "Something went wrong, try again")
    
async def update_email (db: Session, data:UpdateEmail, current_user:User):

    try: 

        if not verifyPassword(data.password, current_user.password):
            raise HTTPException (status_code = 400, detail = "Incorrect password")
    
        if current_user.email == data.email:
            raise HTTPException (status_code = 409, detail = "New email can't be the same as old one")
    
        current_user.email = data.email
        db.commit()
    
        return {"Notice" : "New email registered"}
    
    except HTTPException:
        raise 
    
    except Exception:
        db.rollback()
        raise HTTPException (status_code = 500, detail = "Something went wrong. Please try again")

async def update_phone (db: Session, data: UpdatePhone, current_user : User):

    try: 
        if not verifyPassword (data.password, current_user.password):
            raise HTTPException (status_code = 400, detail = "Incorrect password")
        
        if current_user.phone == data.phone:
            raise HTTPException (status_code = 409, detail = "New phone can't be the same as old one")
        
        current_user.phone = data.phone
        db.commit()

        return {"Notice" :  "New phone registered"}
    
    except HTTPException:
        raise 

    except Exception:
        db.rollback()
        raise HTTPException (status_code = 500, detail = "Something went wrong. Please try again")

async def update_password (db: Session, data:UpdatePassword, current_user :User):
    try:
        if not verifyPassword(data.old_password, current_user.password):
            raise HTTPException (status_code = 400, detail = "Incorrect password")
        
        if data.old_password == data.new_password:
            raise HTTPException (status_code = 409, detail = "New password can't be the same as new one")
        
        current_user.password = hashPassword(data.new_password)
        db.commit()

        return {"Notice" : "New password registered"}
    
    except HTTPException:
        raise 

    except Exception:
        db.rollback()
        raise HTTPException (status_code = 500, detail = "Something went wrong. Try again")
    
async def delete_account (db: Session, current_user: User):

    try:
        current_user.isDeleted = True
        db.commit()
        return {"Notice": "Account is deleted"}

    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Something went wrong. Try again")
    
async def getBalance (current_user:User):
    return {"Balance" : current_user.wallet.balance}