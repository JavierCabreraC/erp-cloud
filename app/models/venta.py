from sqlalchemy import Column, Integer, Numeric, Date, ForeignKey, Computed
from sqlalchemy.orm import relationship
from app.database import Base

class Venta(Base):
    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)
    total = Column(Numeric(10, 2), nullable=False)
    fecha_venta = Column(Date, nullable=False)
    detalles = relationship("DetalleVenta", back_populates="venta")


class DetalleVenta(Base):
    __tablename__ = "detalle_ventas"

    id = Column(Integer, primary_key=True, index=True)
    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Numeric(10, 2), nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    # columna generada en PostgreSQL: GENERATED ALWAYS AS (cantidad * precio_unitario) STORED
    subtotal = Column(Numeric(10, 2), Computed("cantidad * precio_unitario", persisted=True))
    venta = relationship("Venta", back_populates="detalles")
