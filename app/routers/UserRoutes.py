from fastapi import APIRouter, Depends
from app.schemas.UserSchema import CreateUser, Login, refreshTok, UpdateEmail, UpdatePassword, UpdatePhone
from app.database import get_db
from app.services import UserServices
from sqlalchemy.orm import Session
from app.utils.Auth import get_current_user
from app.models.UserModel import User
from app.schemas.TransactionSchema import DepWith, Transfer
from fastapi_cache.decorator import cache
from app.utils.Caching import user_key_builder
router = APIRouter(prefix = "/api/users")

@router.post("/signup")
async def signup (data:CreateUser, db: Session = Depends (get_db)):
    return await UserServices.signup(db, data)

@router.post("/login")
async def login (data : Login, db:Session = Depends(get_db)):
    return await UserServices.login(db,data)

@router.post("/refresh_token")
async def refreshToken (data: refreshTok, db: Session = Depends (get_db)):
    return await UserServices.refreshToken (data, db)

# @router.post("/deposit")
# async def deposit (data: DepWith, db: Session = Depends (get_db), current_user: User = Depends(get_current_user)):
    # return await UserServices.deposit(data, db, current_user)

# @router.post ("/withdraw")
# async def deposit (data: DepWith, db: Session = Depends (get_db), current_user:User = Depends (get_current_user)):
    # return await UserServices.withdraw(db,data,current_user)

@router.post("/transfer")
async def transfer (data: Transfer, db: Session = Depends (get_db), current_user: User = Depends (get_current_user)):
    return await UserServices.transfer(db, data, current_user)

@router.patch ("/update-email")
async def updateEmail (data : UpdateEmail, db: Session = Depends (get_db), current_user : User = Depends(get_current_user)):
    return await UserServices.update_email(db,data,current_user)

@router.patch ("/update-phone")
async def updatePhone (data: UpdatePhone, db: Session = Depends(get_db), current_user:User = Depends(get_current_user)):
    return await UserServices.update_phone(db, data, current_user)

@router.patch ("/update-password")
async def updatePassword (data: UpdatePassword, db: Session = Depends(get_db), current_user:User = Depends(get_current_user)):
    return await UserServices.update_password(db,data,current_user)

@router.delete ("/delete-account")
async def deleteAccount (db:Session = Depends(get_db), current_user:User = Depends(get_current_user)):
    return await UserServices.delete_account(db, current_user)

@router.get("/get-balance")
@cache(key_builder = user_key_builder, expire = 86400)
async def getBalance (current_user : User = Depends (get_current_user)):
    return await UserServices.getBalance(current_user)