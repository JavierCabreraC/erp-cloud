from pydantic import BaseModel, ConfigDict
from datetime import date

class CompraCreate(BaseModel):
    producto_id: int
    proveedor: str
    cantidad: float
    precio_compra: float
    fecha_compra: date

class CompraRead(CompraCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)
