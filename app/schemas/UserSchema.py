from pydantic import BaseModel, field_validator, Field
import re
from decimal import Decimal

class CreateUser(BaseModel):
    name : str
    email : str | None = None
    phone : str | None = None
    password: str 

    @field_validator("password")
    @classmethod
    def checkPassword (cls, value):
        if not re.search(r"[!@#$%*()?]", value):
            raise ValueError ("Password must contain a symbol")
        return value
    
class Login (BaseModel):
    email : str | None = None
    phone : str | None = None 
    password : str 

class refreshTok (BaseModel):
    token : str 
    password : str 

class UpdatePhone(BaseModel):
    phone : str 
    password : str 

class UpdateEmail(BaseModel):
    email : str 

class UpdatePassword(BaseModel): 
    old_password : str 
    new_password : str 

class Verify (BaseModel):
    code : str 
    email : str 