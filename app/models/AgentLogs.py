from app.database import base 
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, DECIMAL
from sqlalchemy.orm import relationship

class AgentLogs (base):
    __tablename__ = "agent_logs"

    id = Column (Integer, primary_key = True, index = True)

    description = Column (String, nullable = False)

    agent_id = Column (Integer, ForeignKey ("users.user_id"))

    executedAt = Column (DateTime(timezone=True), server_default = func.now())

    amount = Column (DECIMAL(10,2), nullable = True)

    userAgent = relationship ("User", back_populates = "agent", uselist = False)