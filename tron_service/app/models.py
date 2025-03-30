from sqlalchemy import Column, Integer, String, DateTime, func
from .database import Base

class TronRequest(Base):
    __tablename__ = "tron_requests"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, nullable=False)
    timestamp = Column(DateTime, default=func.now())
