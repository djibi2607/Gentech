from pydantic import BaseModel, Field
from decimal import Decimal

class DepWith (BaseModel):
    amount : Decimal = Field (gt = 0, lt = 10000, decimal_places = 2)
    description : str | None = None
