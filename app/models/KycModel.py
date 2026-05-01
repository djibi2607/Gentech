from app.database import base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Kycs(base):
    __tablename__ = "kyc"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.user_id"))

    document_type = Column(String, nullable=False)

    document_key = Column(String, nullable=False)

    selfie_key = Column(String, nullable=False)

    status = Column(String, default="Pending")

    createdAt = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="kyc")