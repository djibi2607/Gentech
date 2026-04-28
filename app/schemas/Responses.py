from pydantic import BaseModel
from datetime import date, datetime
from decimal import Decimal
class WalletResponse(BaseModel):
    wallet_id: int
    createdAt: date
    updatedAt: date | None = None

    class Config:
        from_attributes = True

class TransactionResponse(BaseModel):
    trans_id: int
    amount: float
    trans_type: str
    description: str | None = None
    initiatedAt: date

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    user_id: int
    name: str
    email: str | None = None
    phone: str | None = None
    isFlagged: bool
    isDeleted: bool
    createdAt: date
    transactions_sent: list[TransactionResponse] = []
    transactions_received: list[TransactionResponse] = []
    wallet : WalletResponse
    
    class Config:
        from_attributes = True

class LogResponse (BaseModel):
    id: int 
    description : str 
    agent_id : int 
    executedAt : datetime 

    class Config:
        from_attributes = True


class AdminTransactionResponse (BaseModel):
    trans_id: int
    amount: float
    trans_type: str
    description: str | None = None
    initiatedAt: date
    sender_id : int | None = None
    receiver_id : int | None = None

    class Config: 
        from_attributes = True

class AdminWalletResponse (BaseModel):
    wallet_id: int
    createdAt: date
    updatedAt: date | None = None
    balance: Decimal 

    class Config:
        from_attributes = True

class AdminAllUsers (BaseModel):
    user_id : int
    name : str 
    phone : str | None = None
    email : str | None = None
    isFlagged: bool
    isDeleted: bool
    createdAt: date
    transactions_sent : list [AdminTransactionResponse] = []
    transactions_received : list [AdminTransactionResponse] = []
    wallet : AdminWalletResponse

    class Config:
        from_attributes = True