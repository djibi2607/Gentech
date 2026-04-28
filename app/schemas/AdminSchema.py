from pydantic import BaseModel 
from app.database import base
from datetime import date
class Promote (base):
    email : str | None = None
    phone : str | None = None

class AgentLogFilters (base):
    agent_id : int | None = None
    date_from : date | None = None
    date_to : date | None = None

class DeleteUser (base):
    user_id : int