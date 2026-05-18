from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db
from app.schemas.inventario import InventarioCreate, InventarioRead, InventarioUpdate
from app.services import inventario_service

router = APIRouter(prefix="/inventario", tags=["Inventario"])

@router.get("", response_model=List[InventarioRead])
def list_inventario(db: Session = Depends(get_db)):
    return inventario_service.get_all(db)

# /alertas debe ir ANTES de /{producto_id} para evitar que "alertas" sea parseado como int
@router.get("/alertas", response_model=List[InventarioRead])
def get_alertas(db: Session = Depends(get_db)):
    return inventario_service.get_alertas(db)

@router.get("/{producto_id}", response_model=InventarioRead)
def get_inventario(producto_id: int, db: Session = Depends(get_db)):
    return inventario_service.get_by_producto(db, producto_id)

@router.post("", response_model=InventarioRead, status_code=201)
def create_inventario(data: InventarioCreate, db: Session = Depends(get_db)):
    return inventario_service.create(db, data)

@router.patch("/{producto_id}", response_model=InventarioRead)
def update_inventario(producto_id: int, data: InventarioUpdate, db: Session = Depends(get_db)):
    return inventario_service.update(db, producto_id, data)
