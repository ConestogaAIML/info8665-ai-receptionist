from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.auth import verify_token
from app.database import get_db
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientListResponse, ClientResponse, ClientUpdate

router = APIRouter(prefix="/api/clients", tags=["Clients"])


@router.get("/", response_model=ClientListResponse, summary="List all clients")
def list_clients(
    search: str | None = Query(default=None, description="Search by name or email"),
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    q = db.query(Client)
    if search:
        like = f"%{search}%"
        q = q.filter(
            Client.first_name.ilike(like)
            | Client.last_name.ilike(like)
            | Client.email.ilike(like)
        )
    items = q.order_by(Client.created_at.desc()).all()
    return ClientListResponse(count=len(items), results=items)


@router.post("/", response_model=ClientResponse, status_code=201, summary="Create a client")
def create_client(
    payload: ClientCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    if db.query(Client).filter(Client.email == str(payload.email)).first():
        raise HTTPException(status_code=409, detail="A client with this email already exists")
    client = Client(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=str(payload.email),
        phone=payload.phone,
        notes=payload.notes,
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.get("/{client_id}/", response_model=ClientResponse, summary="Get a client")
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.put("/{client_id}/", response_model=ClientResponse, summary="Update a client")
def update_client(
    client_id: int,
    payload: ClientUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    if str(payload.email) != client.email:
        if db.query(Client).filter(Client.email == str(payload.email)).first():
            raise HTTPException(status_code=409, detail="A client with this email already exists")
    client.first_name = payload.first_name
    client.last_name = payload.last_name
    client.email = str(payload.email)
    client.phone = payload.phone
    client.notes = payload.notes
    db.commit()
    db.refresh(client)
    return client


@router.delete("/{client_id}/", status_code=204, summary="Delete a client")
def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    db.delete(client)
    db.commit()
