import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tron_service.app.database import get_db
from tron_service.app.main import app
from tron_service.app.models import Base
import httpx
from unittest.mock import AsyncMock

TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    Base.metadate.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadate.drop_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.mark.asyncio
async def test_fetch_tron_data_success(mocker):
    mock_fetch = mocker.patch("app.api.endpoints.fetch_tron_data_async", new_callable=AsyncMock)

    # Настроим, чтобы `get` возвращал фейковые данные

    mock_fetch.return_value = ({"balance": 10_000_000}, {"freeNetUsed": 500, "energyUsed": 1000})

    response = client.post("/tron/", json={"address": "TCsRyu2z1zYzZsL5HoZzNfwFQpEuyFzpZ4"})

    assert response.status_code == 200
    data = response.json()
    assert data["address"] == "TCsRyu2z1zYzZsL5HoZzNfwFQpEuyFzpZ4"
    assert data["balance"] == 10  # 10_000_000 / 1_000_000
    assert data["bandwidth"] == 500
    assert data["energy"] == 1000

def test_fetch_tron_data_invalid_address(mocker):
    mock_client = mocker.patch("app.tron_client.client")
    mock_client.get_account.side_effect = Exception("Invalid address")

    response = client.post("/tron/", json={"address": "INVALID"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid address"