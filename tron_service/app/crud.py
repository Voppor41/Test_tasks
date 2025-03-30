from sqlalchemy.orm import Session, sessionmaker
from .models import TronRequest

def create_tron_requests(db: Session, address: str):
    db_request = TronRequest(adress=address)
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request

def get_tron_requests(db:Session, skip: int = 0, limit: int = 0):
    return db.query(TronRequest).order_by(TronRequest.timestamp.desc()).offset(skip).limit(limit).all()
