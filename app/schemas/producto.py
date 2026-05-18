from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class ProductoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio_unitario: float
    unidad_medida: str
    categoria: Optional[str] = None

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio_unitario: Optional[float] = None
    unidad_medida: Optional[str] = None
    categoria: Optional[str] = None

class ProductoRead(ProductoBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
