from sqlalchemy import Column, Integer, String, Numeric, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    unidad_medida = Column(String, nullable=False)
    categoria = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
