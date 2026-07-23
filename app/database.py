from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_settings
from app.logging_config import configure_application_logging

settings = get_settings()
logger = configure_application_logging()

if settings.db_engine.lower().startswith("sqlite"):
    import os

    os.makedirs(os.path.dirname(os.path.abspath(settings.sqlite_db_path)), exist_ok=True)

DATABASE_URL = settings.database_url()
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

logger.info(
    "Database configured engine=%s host=%s port=%s name=%s user=%s",
    settings.db_engine,
    settings.db_hostname,
    settings.db_port,
    settings.db_name,
    settings.db_username,
)

engine = create_engine(DATABASE_URL, connect_args=connect_args)
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
    logger.info("Recreated appointments table after legacy schema mismatch")
