from pydantic import BaseModel, Field
from decimal import Decimal

class DepWith (BaseModel):
    amount : Decimal = Field (gt = 0, lt = 10001, decimal_places = 2)
    description : str | None = None

class Transfer (BaseModel):
    amount: Decimal = Field (gt = 0, lt = 10001, decimal_places = 2)
    description : str | None = None
    receiver_email : str | None = None
    receiver_phone : str | None = None
