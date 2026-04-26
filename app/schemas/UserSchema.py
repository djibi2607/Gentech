from pydantic import BaseModel, field_validator
import re

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
    
