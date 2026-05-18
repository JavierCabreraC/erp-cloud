from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from app.database import Base

class Compra(Base):
    __tablename__ = "compras"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    proveedor = Column(String, nullable=False)
    cantidad = Column(Numeric(10, 2), nullable=False)
    precio_compra = Column(Numeric(10, 2), nullable=False)
    fecha_compra = Column(Date, nullable=False)
