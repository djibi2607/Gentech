from pydantic import BaseModel
from datetime import datetime

class WalletResponse(BaseModel):
    wallet_id: int
    createdAt: datetime
    updatedAt: datetime | None = None

    class Config:
        from_attributes = True

class TransactionResponse(BaseModel):
    trans_id: int
    amount: float
    trans_type: str
    description: str | None = None
    initiatedAt: datetime

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    user_id: int
    name: str
    email: str | None = None
    phone: str | None = None
    isFlagged: bool
    isDeleted: bool
    createdAt: datetime
    transactions_sent: list[TransactionResponse] = []
    transactions_received: list[TransactionResponse] = []
    wallet : WalletResponse
    
    class Config:
        from_attributes = True