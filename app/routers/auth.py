from fastapi import APIRouter
from app.auth import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/token", summary="Get a dev JWT token (Sprint 0)")
def get_token(business_id: int = 1):
    """Returns a signed JWT for testing authenticated endpoints."""
    token = create_access_token({"sub": str(business_id), "business_id": business_id})
    return {"access_token": token, "token_type": "bearer"}
