from app.database import base
from sqlalchemy import Column, String, Integer, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship

class RefreshToken (base):
    __tablename__ = "refresh_tokens"

    id = Column (Integer, primary_key = True, index = True)

    token = Column (String, nullable = False, index = True, unique = True)

    createdAt = Column (DateTime(timezone = True), server_default = func.now(), nullable = False)

    isRevoked = Column (Boolean, default = False, nullable = False)

    expiresAt = Column (DateTime(timezone = True), nullable = False)

    user_id = Column (Integer, ForeignKey("users.user_id"), nullable = False)

    userRefresh = relationship ("User", back_populates = "refresh")