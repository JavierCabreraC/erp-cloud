from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db
from app.schemas.cliente import ClienteCreate, ClienteRead, ClienteUpdate
from app.services import cliente_service

router = APIRouter(prefix="/clientes", tags=["Clientes"])

@router.get("", response_model=List[ClienteRead])
def list_clientes(db: Session = Depends(get_db)):
    return cliente_service.get_all(db)

@router.get("/{id}", response_model=ClienteRead)
def get_cliente(id: int, db: Session = Depends(get_db)):
    return cliente_service.get_by_id(db, id)

@router.post("", response_model=ClienteRead, status_code=201)
def create_cliente(data: ClienteCreate, db: Session = Depends(get_db)):
    return cliente_service.create(db, data)

@router.put("/{id}", response_model=ClienteRead)
def update_cliente(id: int, data: ClienteCreate, db: Session = Depends(get_db)):
    return cliente_service.update(db, id, data)

@router.patch("/{id}", response_model=ClienteRead)
def partial_update_cliente(id: int, data: ClienteUpdate, db: Session = Depends(get_db)):
    return cliente_service.partial_update(db, id, data)

@router.delete("/{id}", status_code=204)
def delete_cliente(id: int, db: Session = Depends(get_db)):
    cliente_service.delete(db, id)
