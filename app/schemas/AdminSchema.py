from pydantic import BaseModel 
from app.database import base

class Promote (base):
    email : str | None = None
    phone : str | None = None
