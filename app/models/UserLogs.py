from app.database import base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, DateTime, func, ForeignKey

class UserLogs (base):
    __tablename__= "user_logs"

    id = Column (Integer, primary_key = True, index = True)

    user_id = Column (Integer, ForeignKey("users.user_id"))

    action = Column (String, nullable = False)

    executedAt =  Column (DateTime(timezone = True), server_default = func.now())

    country = Column (String, nullable = True)

    city = Column (String, nullable = True)

    longitude = Column (String, nullable = True)

    latitude = Column (String, nullable = True)

    device = Column (String, nullable = True)

    os = Column (String, nullable = True)

    browser = Column (String, nullable = True)

    userConnection = relationship ("User", back_populates = "userLogs", uselist = False)