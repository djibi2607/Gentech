from pydantic import BaseModel 

class CustomerInfo (BaseModel):
    email: str | None = None 
    phone : str | None = None 

class UnflagUser (BaseModel):
    phone : str 
    email : str 