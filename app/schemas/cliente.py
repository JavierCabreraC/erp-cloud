from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class ClienteBase(BaseModel):
    nombre: str
    apellido: str
    email: str
    telefono: Optional[str] = None
    direccion: Optional[str] = None

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None

class ClienteRead(ClienteBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
