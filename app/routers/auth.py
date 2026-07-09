from fastapi import APIRouter
from app.auth import create_access_token
from app.logging_config import LOGGER_NAME
import logging

router = APIRouter(prefix="/auth", tags=["Auth"])
logger = logging.getLogger(LOGGER_NAME)


@router.post("/token", summary="Get a dev JWT token (Sprint 0)")
def get_token(business_id: int = 1):
    """Returns a signed JWT for testing authenticated endpoints."""
    logger.info("Development token requested for business_id=%s", business_id)
    token = create_access_token({"sub": str(business_id), "business_id": business_id})
    return {"access_token": token, "token_type": "bearer"}
