from pydantic import BaseModel 
from datetime import date

class Promote (BaseModel):
    email : str | None = None
    phone : str | None = None

class AgentLogFilters (BaseModel):
    agent_id : int | None = None
    date_from : date | None = None
    date_to : date | None = None

class DeleteUser (BaseModel):
    user_id : int

class CirculationSchema (BaseModel):
    date_from : date | None = None
    date_to: date | None = None
    trans_type : str | None = None

class Code (BaseModel):
    code : str 
