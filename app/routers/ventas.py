from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db
from app.schemas.venta import VentaCreate, VentaRead, VentaReadConDetalles
from app.services import venta_service

router = APIRouter(prefix="/ventas", tags=["Ventas"])

@router.get("", response_model=List[VentaRead])
def list_ventas(db: Session = Depends(get_db)):
    return venta_service.get_all(db)

# /cliente/{cliente_id} antes de /{id} por claridad
@router.get("/cliente/{cliente_id}", response_model=List[VentaRead])
def get_ventas_por_cliente(cliente_id: int, db: Session = Depends(get_db)):
    return venta_service.get_by_cliente(db, cliente_id)

@router.get("/{id}", response_model=VentaReadConDetalles)
def get_venta(id: int, db: Session = Depends(get_db)):
    return venta_service.get_by_id_con_detalles(db, id)

@router.post("", response_model=VentaReadConDetalles, status_code=201)
def create_venta(data: VentaCreate, db: Session = Depends(get_db)):
    return venta_service.create(db, data)

@router.delete("/{id}", status_code=204)
def delete_venta(id: int, db: Session = Depends(get_db)):
    venta_service.delete(db, id)
