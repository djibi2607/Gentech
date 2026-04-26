from app.schemas.UserSchema import CreateUser
from sqlalchemy.orm import Session 
from app.models.UserModel import User
from fastapi import HTTPException
from sqlalchemy import or_
from app.utils.Hashing import hashPassword
from app.models.WalletModel import Wallet

async def signup (db: Session, data : CreateUser):
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

        