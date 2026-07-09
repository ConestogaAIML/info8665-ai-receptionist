import os
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# In Docker the /data volume is mounted; locally falls back to ./data/
_db_path = os.environ.get("SQLITE_DB_PATH", "./data/receptionist.db")
os.makedirs(os.path.dirname(os.path.abspath(_db_path)), exist_ok=True)

SQLITE_URL = f"sqlite:///{_db_path}"

engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_schema() -> None:
    """Recreate legacy tables that no longer match the ORM models."""
    inspector = inspect(engine)
    if "appointments" not in inspector.get_table_names():
        Base.metadata.create_all(bind=engine)
        return

    column_names = {column["name"] for column in inspector.get_columns("appointments")}
    if "client_id" in column_names and "service_id" in column_names:
        Base.metadata.create_all(bind=engine)
        return

    with engine.begin() as conn:
        conn.execute(text("DROP TABLE appointments"))

    Base.metadata.create_all(bind=engine)
