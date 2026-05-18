from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db
from app.schemas.compra import CompraCreate, CompraRead
from app.services import compra_service

router = APIRouter(prefix="/compras", tags=["Compras"])

@router.get("", response_model=List[CompraRead])
def list_compras(db: Session = Depends(get_db)):
    return compra_service.get_all(db)

# /producto/{producto_id} antes de /{id} por claridad
@router.get("/producto/{producto_id}", response_model=List[CompraRead])
def get_compras_por_producto(producto_id: int, db: Session = Depends(get_db)):
    return compra_service.get_by_producto(db, producto_id)

@router.get("/{id}", response_model=CompraRead)
def get_compra(id: int, db: Session = Depends(get_db)):
    return compra_service.get_by_id(db, id)

@router.post("", response_model=CompraRead, status_code=201)
def create_compra(data: CompraCreate, db: Session = Depends(get_db)):
    return compra_service.create(db, data)

@router.delete("/{id}", status_code=204)
def delete_compra(id: int, db: Session = Depends(get_db)):
    compra_service.delete(db, id)
