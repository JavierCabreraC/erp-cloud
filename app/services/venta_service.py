from sqlalchemy.orm import Session, selectinload
from fastapi import HTTPException
from app.models.venta import Venta, DetalleVenta
from app.models.inventario import Inventario
from app.schemas.venta import VentaCreate

def get_all(db: Session):
    return db.query(Venta).all()

def get_by_id(db: Session, id: int):
    venta = db.query(Venta).filter(Venta.id == id).first()
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return venta

def get_by_id_con_detalles(db: Session, id: int):
    venta = (
        db.query(Venta)
        .options(selectinload(Venta.detalles))
        .filter(Venta.id == id)
        .first()
    )
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return venta

def get_by_cliente(db: Session, cliente_id: int):
    return db.query(Venta).filter(Venta.cliente_id == cliente_id).all()

def create(db: Session, data: VentaCreate):
    total = sum(d.cantidad * d.precio_unitario for d in data.detalles)
    venta = Venta(cliente_id=data.cliente_id, fecha_venta=data.fecha_venta, total=round(total, 2))
    db.add(venta)
    db.flush()

    for d in data.detalles:
        detalle = DetalleVenta(
            venta_id=venta.id,
            producto_id=d.producto_id,
            cantidad=d.cantidad,
            precio_unitario=d.precio_unitario,
            # subtotal es GENERATED ALWAYS en PostgreSQL, no se inserta
        )
        db.add(detalle)

    db.commit()  # trigger dispara por cada DetalleVenta → descuenta stock
    return get_by_id_con_detalles(db, venta.id)

def delete(db: Session, id: int):
    venta = get_by_id(db, id)
    detalles = db.query(DetalleVenta).filter(DetalleVenta.venta_id == id).all()
    for d in detalles:
        inv = db.query(Inventario).filter(Inventario.producto_id == d.producto_id).first()
        if inv:
            inv.stock_actual += d.cantidad
        db.delete(d)
    db.delete(venta)
    db.commit()
