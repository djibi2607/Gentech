from sqlalchemy import Column, String, Integer, Boolean, DateTime, func
from app.database import base
from sqlalchemy.orm import relationship

class User (base):
    __tablename__ = "users"

    user_id = Column (Integer, primary_key= True, index = True)

    name = Column (String, nullable= False)

    phone = Column (String, index = True, nullable = True, unique = True)

    email = Column (String, index = True, nullable = True, unique = True)

    password = Column (String, nullable = False)

    isDeleted = Column (Boolean, default = False)

    isFlagged = Column (Boolean, default = False)

    createdAt = Column (DateTime(timezone=True), server_default = func.now())

    updatedAt = Column (DateTime(timezone=True), onupdate = func.now())

    wallet = relationship ("Wallet", back_populates = "user", uselist = False)

    transactions_sent = relationship ("Transaction", foreign_keys = "Transaction.sender_id", back_populates = "sender")

    transactions_received = relationship ("Transaction", foreign_keys = "Transaction.receiver_id", back_populates = "receiver")

    refresh = relationship ("RefreshToken", back_populates = "userRefresh")

    role = Column (String, nullable = False, server_default = "user")

    agent = relationship ("AgentLogs", back_populates = "userAgent")

    userLogs = relationship("UserLogs", back_populates = "userConnection")