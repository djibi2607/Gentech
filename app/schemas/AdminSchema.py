from pydantic import BaseModel 
from datetime import datetime

class Promote (BaseModel):
    email : str | None = None
    phone : str | None = None

class AgentLogFilters (BaseModel):
    agent_id : int | None = None
    date_from : datetime | None = None
    date_to : datetime | None = None

class DeleteUser (BaseModel):
    user_id : int

class CirculationSchema (BaseModel):
    date_from : datetime | None = None
    date_to: datetime | None = None
    trans_type : str | None = None

class Code (BaseModel):
    code : str 
