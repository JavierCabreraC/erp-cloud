from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db
from app.models.producto import Producto
from app.models.inventario import Inventario
from app.schemas.producto import ProductoCreate, ProductoRead

router = APIRouter(prefix="/productos", tags=["Productos"])

@router.get("", response_model=List[ProductoRead])
def list_productos(db: Session = Depends(get_db)):
    return db.query(Producto).all()

@router.get("/{id}", response_model=ProductoRead)
def get_producto(id: int, db: Session = Depends(get_db)):
    p = db.query(Producto).filter(Producto.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return p

@router.post("", response_model=ProductoRead, status_code=201)
def create_producto(data: ProductoCreate, db: Session = Depends(get_db)):
    producto = Producto(**data.model_dump())
    db.add(producto)
    db.flush()
    inv = Inventario(producto_id=producto.id, stock_actual=0, stock_minimo=0, stock_maximo=0)
    db.add(inv)
    db.commit()
    db.refresh(producto)
    return producto

@router.put("/{id}", response_model=ProductoRead)
def update_producto(id: int, data: ProductoCreate, db: Session = Depends(get_db)):
    p = db.query(Producto).filter(Producto.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    for key, value in data.model_dump().items():
        setattr(p, key, value)
    db.commit()
    db.refresh(p)
    return p

@router.delete("/{id}", status_code=204)
def delete_producto(id: int, db: Session = Depends(get_db)):
    p = db.query(Producto).filter(Producto.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(p)
    db.commit()
