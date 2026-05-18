from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.cliente import Cliente
from app.schemas.cliente import ClienteCreate, ClienteUpdate

def get_all(db: Session):
    return db.query(Cliente).all()

def get_by_id(db: Session, id: int):
    cliente = db.query(Cliente).filter(Cliente.id == id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

def create(db: Session, data: ClienteCreate):
    cliente = Cliente(**data.model_dump())
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente

def update(db: Session, id: int, data: ClienteCreate):
    cliente = get_by_id(db, id)
    for key, value in data.model_dump().items():
        setattr(cliente, key, value)
    db.commit()
    db.refresh(cliente)
    return cliente

def partial_update(db: Session, id: int, data: ClienteUpdate):
    cliente = get_by_id(db, id)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(cliente, key, value)
    db.commit()
    db.refresh(cliente)
    return cliente

def delete(db: Session, id: int):
    cliente = get_by_id(db, id)
    db.delete(cliente)
    db.commit()
