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

    wallet = relationship ("Wallet", back_populates = "user")