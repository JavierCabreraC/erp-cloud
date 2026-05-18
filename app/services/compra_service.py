from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.compra import Compra
from app.models.inventario import Inventario
from app.schemas.compra import CompraCreate

def get_all(db: Session):
    return db.query(Compra).all()

def get_by_id(db: Session, id: int):
    compra = db.query(Compra).filter(Compra.id == id).first()
    if not compra:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    return compra

def get_by_producto(db: Session, producto_id: int):
    return db.query(Compra).filter(Compra.producto_id == producto_id).all()

def create(db: Session, data: CompraCreate):
    compra = Compra(**data.model_dump())
    db.add(compra)
    db.commit()  # trigger dispara aquí → actualiza inventario.stock_actual
    db.refresh(compra)
    return compra

def delete(db: Session, id: int):
    compra = get_by_id(db, id)
    inv = db.query(Inventario).filter(Inventario.producto_id == compra.producto_id).first()
    if inv:
        inv.stock_actual -= compra.cantidad
    db.delete(compra)
    db.commit()
