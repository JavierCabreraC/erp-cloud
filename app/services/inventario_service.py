from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.inventario import Inventario
from app.schemas.inventario import InventarioCreate, InventarioUpdate

def get_all(db: Session):
    return db.query(Inventario).all()

def get_by_producto(db: Session, producto_id: int):
    inv = db.query(Inventario).filter(Inventario.producto_id == producto_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Inventario no encontrado")
    return inv

def get_alertas(db: Session):
    return db.query(Inventario).filter(Inventario.stock_actual < Inventario.stock_minimo).all()

def create(db: Session, data: InventarioCreate):
    inv = Inventario(**data.model_dump())
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv

def update(db: Session, producto_id: int, data: InventarioUpdate):
    inv = get_by_producto(db, producto_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(inv, key, value)
    db.commit()
    db.refresh(inv)
    return inv
