import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..crud import create_tron_requests, get_tron_requests
from ..database import get_db
from ..schemas import TronRequestCreate, TronRequestResponse
from ..tron_client import client

router = APIRouter()


async def fetch_tron_data_async(address: str):
    async with httpx.AsyncClient() as client:
        account = await client.get(f"https://api.tronlink.org/account/{address}")
        resources = await client.get(f"https://api.tronlink.org/resources/{address}")

    return account.json(), resources.json()

@router.post("/tron/")
async def fetch_tron_data(request: TronRequestCreate, db: Session = Depends(get_db)):
    try:
        account, resources = await fetch_tron_data_async(request.address)

        balance = account.get("balance", 0) / 1_000_000
        bandwidth = resources.get("freeNetUsed", 0)
        energy = resources.get("energyUsed", 0)

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
async def get_history(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_tron_requests(db, skip, limit)