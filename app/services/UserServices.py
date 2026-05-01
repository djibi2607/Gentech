from app.schemas.UserSchema import CreateUser, Login, refreshTok, UpdateEmail, UpdatePassword, UpdatePhone, Verify
from sqlalchemy.orm import Session 
from app.models.UserModel import User
from fastapi import HTTPException, Request
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
from app.models.BannedIps import BannedIps
from app.utils.GeoipUtil import get_location
from app.utils.User_agent import getUserAgent
from app.models.UserLogs import UserLogs
from app.utils import Kyc
from app.models.KycModel import Kycs
from fastapi import UploadFile
from app.utils.Auth import create_code

async def signup (request : Request, db: Session, data : CreateUser) -> dict:
    
    try:


        request_ip = request.client.host
        ua = getUserAgent(request.headers.get("user-agent"))
                          
        banned_ips = db.query (BannedIps).filter(BannedIps.ip == request_ip).first()

        if banned_ips:
            raise HTTPException (status_code = 403, detail = "You have been disabled to signup")

        location = get_location(request_ip)

        country_allowed = ["Guinea", "United States"]

        if location["Country"] not in country_allowed:
            raise HTTPException (status_code = 403, detail = "Service not allowed in your location")

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

        newUserLog = UserLogs (
            user_id = newUser.user_id,
            action = f"User created his gentech account",
            country = location["Country"],
            city = location ["City"],
            longitude = location["Longitude"],
            latitude = location ["Latitude"],
            device = ua["Device"],
            os = ua["os"],
            browser = ua["browser"]
        )
        db.add(newUserLog)
        try: 
            if data.email:
                Resend.sendWelcomeEmail(data.name)
        except: 
            pass

        db.commit()
        db.refresh(newUser)
        db.refresh(newWallet)
        db.refresh(newUserLog)

        return {"Status" : f"Welcome, {data.name}, your account has successfully been created, you can now proceed to login"}
    
    except HTTPException:
        raise
    except Exception as e:
        print (e)
        db.rollback()
        raise HTTPException (status_code = 500, detail = "Something went wrong, Please try again")

async def login (request : Request, db: Session, data: Login) -> dict:
    try:
        request_ip = request.client.host

        ua = getUserAgent(request.headers.get("user-agent"))

        location = get_location(request_ip)

        banned_ips = db.query (BannedIps).filter(BannedIps.ip == request_ip).first()

        if banned_ips:
            raise HTTPException (status_code = 403, detail = "You have been disabled to login")

        if not data.email and not data.phone:
            raise HTTPException (status_code = 400, detail = "You must enter your phone or email")
        
        country_allowed = ["Guinea", "United States"]

        if location["Country"] not in country_allowed:
            raise HTTPException (status_code = 403, detail = "Service not allowed in your location")
        
        user : User = db.query (User).filter (or_(User.email == data.email, User.phone == data.phone), User.isDeleted == False).one_or_none()

        if not user:
            raise HTTPException (status_code = 404, detail = "Your account has not been found. Please signup first")
        
        if not verifyPassword(data.password, user.password):
            newUserLog = UserLogs(
            user_id=user.user_id,
            action="Failed login attempt",
            country=location["Country"],
            city=location["City"],
            longitude=location["Longitude"],
            latitude=location["Latitude"],
            device=ua["Device"],
            os=ua["os"],
            browser=ua["browser"]
            )
            db.add(newUserLog)
            db.commit()
            raise HTTPException (status_code = 401, detail = "Incorrect password")
        
        if user.enabled_2fa == True and user.email != None:
            code = await create_code(user, db)
            try: 
                Resend.sendEmailCode(user.name, code)
            except:
                pass
            return {"Notice" : f"A code has been sent to your email"}
    
        
        accessToken = create_access_token (data = {"sub" : str (user.user_id)})

        refreshValue = create_refresh_token()

        newRefreshToken = RefreshToken(                     
            user_id = user.user_id,
            token = refreshValue,
            expiresAt = datetime.now(timezone.utc) + timedelta (hours = 1)
        )
        newUserLog = UserLogs (
            user_id = user.user_id,
            action = f"User logged in",
            country = location["Country"],
            city = location ["City"],
            longitude = location["Longitude"],
            latitude = location ["Latitude"],
            device = ua["Device"],
            os = ua["os"],
            browser = ua["browser"]
        )
        db.add(newUserLog)
        db.add (newRefreshToken)
        db.commit()
        db.refresh(newRefreshToken)
        db.refresh(newUserLog)

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
    

async def verify_code (request: Request, data : Verify, db: Session):
    try:
        request_ip = request.client.host
        location = get_location(request_ip)
        ua = getUserAgent(request.headers.get("user-agent"))

        user = db.query (User).filter (User.email == data.email, User.isDeleted == False).one_or_none()

        if not user: 
            raise HTTPException (status_code = 400, detail = "User not found")
        
        if datetime.now(timezone.utc) > user.expired_code:
            raise HTTPException(status_code=400, detail="Code has expired, please login again")
        
        if user.code_2fa != data.code:
            newUserLog = UserLogs(
            user_id=user.user_id,
            action="Failed login attempt because of incorrect code",
            country=location["Country"],
            city=location["City"],
            longitude=location["Longitude"],
            latitude=location["Latitude"],
            device=ua["Device"],
            os=ua["os"],
            browser=ua["browser"]
            )
            db.add(newUserLog)
            db.commit()
            raise HTTPException (status_code = 400, detail = "Incorrect code")
        
        accessToken = create_access_token (data = {"sub" : str (user.user_id)})

        refreshValue = create_refresh_token()

        newRefreshToken = RefreshToken(                     
            user_id = user.user_id,
            token = refreshValue,
            expiresAt = datetime.now(timezone.utc) + timedelta (hours = 1)
        )
        newUserLog = UserLogs (
            user_id = user.user_id,
            action = f"User logged in",
            country = location["Country"],
            city = location ["City"],
            longitude = location["Longitude"],
            latitude = location ["Latitude"],
            device = ua["Device"],
            os = ua["os"],
            browser = ua["browser"]
        )
        
        user.code_2fa = None
        user.expired_code = None
        db.add(newUserLog)
        db.add (newRefreshToken)
        db.commit()
        db.refresh(newRefreshToken)
        db.refresh(newUserLog)
        db.refresh(user)
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


async def refreshToken (request : Request, data: refreshTok, db: Session):

    try: 
        request_ip = request.client.host

        banned_ips = db.query (BannedIps).filter(BannedIps.ip == request_ip).first()

        if banned_ips:
            raise HTTPException (status_code = 403, detail = "You have been disabled to login")

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
    

async def deposit (request : Request, data: DepWith, db: Session, current_user : User):

    try: 
        if data.description is None:
            data.description = "Unspecified"

        if current_user.isFlagged:
            raise HTTPException (status_code = 401, detail = "Unable to deposit due to suspicious activities. Please contact support")
        
        await checkDailyLimits (db, current_user.user_id, data.amount)

        sender_wallet = db.query(Wallet).filter(Wallet.wallet_id == current_user.wallet.wallet_id).with_for_update().one_or_none()
        
        current_user.wallet.balance += data.amount
        
        newTrans = Transaction (
            amount = data.amount,
            trans_type = "Deposit",
            description = data.description,
            wallet_id = current_user.wallet.wallet_id
        )

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

async def withdraw (request : Request, db:Session, data : DepWith, current_user: User):
    
    try: 
        if data.description is None:
            data.description = "Unspecified"

        if current_user.isFlagged:
            raise HTTPException (status_code = 401, detail = "Unable to withdraw due to suspicious activities. Please contact support")
        
        if current_user.wallet.balance < data.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")

        await checkDailyLimits (db, current_user.user_id, data.amount)
        
        sender_wallet = db.query(Wallet).filter(Wallet.wallet_id == current_user.wallet.wallet_id).with_for_update().one_or_none()

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
    
async def transfer (request : Request, db: Session, data: Transfer, current_user : User):

    try:
        location = get_location(request.client.host)

        ua = getUserAgent(request.headers.get("user-agent"))

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
        
        sender_wallet = db.query(Wallet).filter(Wallet.wallet_id == current_user.wallet.wallet_id).with_for_update().one_or_none()

        receiver_wallet = db.query(Wallet).filter(Wallet.wallet_id == receiver.wallet.wallet_id).with_for_update().one_or_none()
        
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

        newUserLog = UserLogs (
            user_id = current_user.user_id,
            action = f"User made a transfer of {data.amount} to receiver_id : {receiver.user_id}",
            country = location["Country"],
            city = location ["City"],
            longitude = location["Longitude"],
            latitude = location ["Latitude"],
            device = ua["Device"],
            os = ua["os"],
            browser = ua["browser"]
        )
        db.add(newUserLog)
        
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
        db.refresh(newUserLog)
        return {"Notice" : f"Your transfer of ${data.amount} is being processed. We will notify you after getting processed"}
    
    except HTTPException:
        raise 

    except Exception:
        db.rollback()
        raise HTTPException (status_code = 500, detail = "Something went wrong, try again")
    
async def update_email (request : Request, db: Session, data:UpdateEmail, current_user:User):

    try: 
        location = get_location(request.client.host)
        ua = getUserAgent(request.headers.get("user-agent"))

        if not verifyPassword(data.password, current_user.password):
            raise HTTPException (status_code = 400, detail = "Incorrect password")
    
        if current_user.email == data.email:
            raise HTTPException (status_code = 409, detail = "New email can't be the same as old one")
    
        current_user.email = data.email

        newUserLog = UserLogs (
            user_id = current_user.user_id,
            action = f"User updated his email",
            country = location["Country"],
            city = location ["City"],
            longitude = location["Longitude"],
            latitude = location ["Latitude"],
            device = ua["Device"],
            os = ua["os"],
            browser = ua["browser"]
        )
        db.add(newUserLog)
        db.commit()
        db.refresh(newUserLog)

        return {"Notice" : "New email registered"}
    
    except HTTPException:
        raise 
    
    except Exception:
        db.rollback()
        raise HTTPException (status_code = 500, detail = "Something went wrong. Please try again")

async def update_phone (request : Request, db: Session, data: UpdatePhone, current_user : User):

    try: 
        location = get_location(request.client.host)
        ua = getUserAgent(request.headers.get("user-agent"))

        if not verifyPassword (data.password, current_user.password):
            raise HTTPException (status_code = 400, detail = "Incorrect password")
        
        if current_user.phone == data.phone:
            raise HTTPException (status_code = 409, detail = "New phone can't be the same as old one")
        
        current_user.phone = data.phone
        newUserLog = UserLogs (
            user_id = current_user.user_id,
            action = f"User updated his phone number",
            country = location["Country"],
            city = location ["City"],
            longitude = location["Longitude"],
            latitude = location ["Latitude"],
            device = ua["Device"],
            os = ua["os"],
            browser = ua["browser"]
        )
        db.add(newUserLog)
        db.commit()
        db.refresh(newUserLog)

        return {"Notice" :  "New phone registered"}
    
    except HTTPException:
        raise 

    except Exception:
        db.rollback()
        raise HTTPException (status_code = 500, detail = "Something went wrong. Please try again")

async def update_password (request : Request, db: Session, data:UpdatePassword, current_user :User):
    try:
        location = get_location(request.client.host)
        ua = getUserAgent(request.headers.get("user-agent"))

        if not verifyPassword(data.old_password, current_user.password):
            raise HTTPException (status_code = 400, detail = "Incorrect password")
        
        if data.old_password == data.new_password:
            raise HTTPException (status_code = 409, detail = "New password can't be the same as old one")
        
        current_user.password = hashPassword(data.new_password)
        newUserLog = UserLogs (
            user_id = current_user.user_id,
            action = f"User updated his password",
            country = location["Country"],
            city = location ["City"],
            longitude = location["Longitude"],
            latitude = location ["Latitude"],
            device = ua["Device"],
            os = ua["os"],
            browser = ua["browser"]
        )
        db.add(newUserLog)
        db.commit()
        db.refresh(newUserLog)

        return {"Notice" : "New password registered"}
    
    except HTTPException:
        raise 

    except Exception:
        db.rollback()
        raise HTTPException (status_code = 500, detail = "Something went wrong. Try again")
    
async def delete_account (request : Request, db: Session, current_user: User):

    try:
        location = get_location(request.client.host)
        ua = getUserAgent(request.headers.get("user-agent"))

        current_user.isDeleted = True
        newUserLog = UserLogs (
            user_id = current_user.user_id,
            action = f"User deleted his account",
            country = location["Country"],
            city = location ["City"],
            longitude = location["Longitude"],
            latitude = location ["Latitude"],
            device = ua["Device"],
            os = ua["os"],
            browser = ua["browser"]
        )
        db.add(newUserLog)
        db.commit()
        db.refresh(newUserLog)

        return {"Notice": "Account is deleted"}

    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Something went wrong. Try again")
    
async def getBalance (current_user:User):
    return {"Balance" : current_user.wallet.balance}


async def uploadFiletoS3 (request: Request, document_type : str, file : UploadFile, selfie : UploadFile, db: Session, current_user: User):
    
    try: 
        location = get_location(request.client.host)
        ua = getUserAgent(request.headers.get("user-agent"))

        existing_kyc = db.query(Kycs).filter (Kycs.user_id == current_user.user_id).first()

        if existing_kyc:
            raise HTTPException (status_code = 400, detail = "File already uploaded")
        
        allowed_types = ["passport", "national_id", "driver_license"]

        if document_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Invalid document type")
        
        allowed_extensions = ["jpg", "jpeg", "png", "pdf"]

        file_ext = file.filename.split(".")[-1].lower()
        selfies_ext = selfie.filename.split(".")[-1].lower()

        if file_ext not in allowed_extensions or selfies_ext not in allowed_extensions:
            raise HTTPException (status_code = 400, detail = "Files must be in jpg, jpeg, png or pdf")
        
        doc_key = Kyc.uploadFiletoS3(file.file, current_user.user_id, file.filename, "Id")
        self_key = Kyc.uploadFiletoS3 (selfie.file, current_user.user_id, selfie.filename, "selfies")

        newKyc = Kycs(
            user_id=current_user.user_id,
            document_type=document_type,
            document_key=doc_key,
            selfie_key=self_key
        )
        db.add(newKyc)

        newUserLog = UserLogs (
            user_id = current_user.user_id,
            action = f"User uploaded Kyc",
            country = location["Country"],
            city = location ["City"],
            longitude = location["Longitude"],
            latitude = location ["Latitude"],
            device = ua["Device"],
            os = ua["os"],
            browser = ua["browser"]
        )
        db.add(newUserLog)
        db.commit()
        db.refresh(newKyc)
        db.refresh(newUserLog)

        return {"Notice": "KYC submitted successfully, pending review"}

    except HTTPException:
        raise

    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=500, detail="Something went wrong. Please try again")