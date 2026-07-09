import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import create_access_token
from app.database import Base, get_db
from app.main import app

TEST_SQLITE_URL = "sqlite:///:memory:"

# StaticPool forces all connections to reuse one underlying connection,
# so the in-memory DB created by reset_db is visible to TestClient sessions.
test_engine = create_engine(
    TEST_SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(autouse=True)
def reset_db():
    """Create all tables before each test and drop them after."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db(reset_db):
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(reset_db):
    """FastAPI TestClient with the in-memory DB injected."""
    def override_get_db():
        session = TestSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers():
    """Valid JWT bearer headers for authenticated requests."""
    token = create_access_token({"sub": "1", "business_id": 1})
    return {"Authorization": f"Bearer {token}"}
