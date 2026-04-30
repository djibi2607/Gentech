from fastapi import APIRouter, Depends, Request
from app.schemas.UserSchema import CreateUser, Login, refreshTok, UpdateEmail, UpdatePassword, UpdatePhone
from app.database import get_db
from app.services import UserServices
from sqlalchemy.orm import Session
from app.utils.Auth import get_current_user
from app.models.UserModel import User
from app.schemas.TransactionSchema import DepWith, Transfer
from fastapi_cache.decorator import cache
from app.utils.Caching import user_key_builder
from app.main import limiter

router = APIRouter(prefix = "/api/users")

@router.post("/signup")
@limiter.limit("2/minute")
async def signup (request: Request, data:CreateUser, db: Session = Depends (get_db)):
    return await UserServices.signup(db, data)

@router.post("/login")
@limiter.limit("3/minute")
async def login (request: Request, data : Login, db:Session = Depends(get_db)):
    return await UserServices.login(db,data)

@router.post("/refresh_token")
@limiter.limit("2/minute")
async def refreshToken (request: Request, data: refreshTok, db: Session = Depends (get_db)):
    return await UserServices.refreshToken (data, db)

# @router.post("/deposit")
# async def deposit (request: Request, data: DepWith, db: Session = Depends (get_db), current_user: User = Depends(get_current_user)):
    # return await UserServices.deposit(data, db, current_user)

# @router.post ("/withdraw")
# async def deposit (request: Request, data: DepWith, db: Session = Depends (get_db), current_user:User = Depends (get_current_user)):
    # return await UserServices.withdraw(db,data,current_user)

@router.post("/transfer")
@limiter.limit("3/minute")
async def transfer (request: Request, data: Transfer, db: Session = Depends (get_db), current_user: User = Depends (get_current_user)):
    return await UserServices.transfer(db, data, current_user)

@router.patch ("/update-email")
@limiter.limit("1/minute")
async def updateEmail (request: Request, data : UpdateEmail, db: Session = Depends (get_db), current_user : User = Depends(get_current_user)):
    return await UserServices.update_email(db,data,current_user)

@router.patch ("/update-phone")
@limiter.limit("1/minute")
async def updatePhone (request: Request, data: UpdatePhone, db: Session = Depends(get_db), current_user:User = Depends(get_current_user)):
    return await UserServices.update_phone(db, data, current_user)

@router.patch ("/update-password")
@limiter.limit("1/minute")
async def updatePassword (request: Request, data: UpdatePassword, db: Session = Depends(get_db), current_user:User = Depends(get_current_user)):
    return await UserServices.update_password(db,data,current_user)

@router.delete ("delete-account")
async def deleteAccount (request: Request, db:Session = Depends(get_db), current_user:User = Depends(get_current_user)):
    return await UserServices.delete_account(db, current_user)

@router.get("/get-balance")
@cache(key_builder = user_key_builder, expire = 86400)
async def getBalance (request: Request, current_user : User = Depends (get_current_user)):
    return await UserServices.getBalance(current_user)