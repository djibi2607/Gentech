from app.database import base
from sqlalchemy import Column, DECIMAL, Integer, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship

class Wallet(base):
    __tablename__ = "wallets"

    wallet_id = Column (Integer, primary_key= True, index = True)

    balance = Column (DECIMAL(10,2), default= 0.0, nullable = False)

    createdAt = Column (DateTime(timezone=True), server_default = func.now())

    updatedAt = Column (DateTime(timezone=True), onupdate = func.now())
    
    user_id = Column (Integer, ForeignKey("users.user_id"), unique = True, nullable = False)

    user = relationship ("User", back_populates = "wallet", uselist = False)
    
    transactions = relationship ("Transaction", back_populates = "wallet")