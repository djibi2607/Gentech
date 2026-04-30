from sqlalchemy import Column, String, Integer, DateTime
from app.database import base

class BannedIps (base):
    __tablename__ = "banned_ips"

    id = Column (Integer, primary_key = True, index = True)

    ip = Column (String, nullable = False)

    addedAt = Column (DateTime(timezone = True), nullable = False)