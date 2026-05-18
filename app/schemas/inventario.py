from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class InventarioCreate(BaseModel):
    producto_id: int
    stock_actual: float = 0
    stock_minimo: float = 0
    stock_maximo: Optional[float] = None

class InventarioUpdate(BaseModel):
    stock_actual: Optional[float] = None
    stock_minimo: Optional[float] = None
    stock_maximo: Optional[float] = None

class InventarioRead(BaseModel):
    id: int
    producto_id: int
    stock_actual: float
    stock_minimo: float
    stock_maximo: Optional[float] = None
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
