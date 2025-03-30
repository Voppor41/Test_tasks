import pytest
from fastapi.testclient import TestClient
from tron_service.app.main import app
from tron_service.app.database import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tron_service.app.models import Base


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

def test_fetch_tron_data_success(mocker):
    mock_client = mocker.patch("app.tron_client.client")
    mock_client.get_account.return_value = {"balance": 10_000_000}  # 10 TRX
    mock_client.get_account_resource.return_value = {"freeNetUsed": 500, "energyUsed": 1000}

    response = client.post("/tron/", json={"address": "TXYZ123456789"})

    assert response.status_code == 200
    data = response.json()
    assert data["address"] == "TXYZ123456789"
    assert data["balance"] == 10  # 10_000_000 / 1_000_000
    assert data["bandwidth"] == 500
    assert data["energy"] == 1000

def test_fetch_tron_data_invalid_address(mocker):
    mock_client = mocker.patch("app.tron_client.client")
    mock_client.get_account.side_effect = Exception("Invalid address")

    response = client.post("/tron/", json={"address": "INVALID"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid address"