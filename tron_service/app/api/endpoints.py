from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..schemas import TronRequestCreate, TronRequestResponse
from ..crud import create_tron_requests, get_tron_requests
from ..database import get_db
from app.tron_client import client # Убедись, что у тебя есть этот клиент
print(client)

router = APIRouter()

@router.post("/tron/", response_model=TronRequestResponse)
def fetch_tron_data(request: TronRequestCreate, db: Session = Depends(get_db)):
    try:
        account = client.get_account(request.address)
        balance = account.get("balance", 0) / 1_000_000
        bandwidth = client.get_account_resource(request.address)["freeNetUsed"]
        energy = client.get_account_resource(request.address)["energyUsed"]

        db_entry = create_tron_requests(db, request.address)
        return {
            "id": db_entry.id,
            "address": request.address,
            "balance": balance,
            "bandwidth": bandwidth,
            "energy": energy,
            "timestamp": db_entry.timestamp
        }
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid address")

@router.get("/tron/history/", response_model=list[TronRequestResponse])
def get_history(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_tron_requests(db, skip, limit)