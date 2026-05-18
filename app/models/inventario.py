from sqlalchemy import Column, Integer, Numeric, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Inventario(Base):
    __tablename__ = "inventario"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), unique=True, nullable=False)
    stock_actual = Column(Numeric(10, 2), nullable=False, default=0)
    stock_minimo = Column(Numeric(10, 2), nullable=False, default=0)
    stock_maximo = Column(Numeric(10, 2), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
