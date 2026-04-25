from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, DECIMAL, func
from app.database import base
from sqlalchemy.orm import relationship

class Transaction(base):
    __tablename__ = "transactions"

    trans_id = Column(Integer, primary_key = True, index = True)

    amount = Column(DECIMAL(10,2), nullable = False)

    trans_type = Column (String, nullable = False)

    description = Column (String, nullable = True)

    sender_id =  Column (Integer, ForeignKey("users.user_id"), nullable = False)

    receiver_id = Column (Integer, ForeignKey("users.user_id"), nullable = False)

    initiatedAt = Column (DateTime(timezone = True), server_default = func.now())

    wallet_id = Column (Integer, ForeignKey("wallets.wallet_id"), nullable = False)

    wallet = relationship ("Wallet", back_populates = "transactions")

    sender = relationship ("User", foreign_keys = [sender_id])
    
    receiver = relationship ("User", foreign_keys = [receiver_id])

