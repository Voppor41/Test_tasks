from pydantic import BaseModel
from datetime import datetime

class TronRequestCreate(BaseModel):
    address: str

class TronRequestResponse(BaseModel):
    id: int
    address: str
    balance: float
    bandwidth: int
    energy: int
    timestamp: datetime

    class Config:
        from_attributes = True