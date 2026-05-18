from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import List, Optional

class DetalleVentaCreate(BaseModel):
    producto_id: int
    cantidad: float
    precio_unitario: float

class DetalleVentaRead(DetalleVentaCreate):
    id: int
    venta_id: int
    subtotal: float
    model_config = ConfigDict(from_attributes=True)

class VentaCreate(BaseModel):
    cliente_id: int
    fecha_venta: date
    detalles: List[DetalleVentaCreate]

class VentaRead(BaseModel):
    id: int
    cliente_id: Optional[int] = None  # null si el cliente fue eliminado (ON DELETE SET NULL)
    total: float
    fecha_venta: date
    model_config = ConfigDict(from_attributes=True)

class VentaReadConDetalles(VentaRead):
    detalles: List[DetalleVentaRead] = []
