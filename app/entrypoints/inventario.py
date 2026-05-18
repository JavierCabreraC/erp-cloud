from fastapi import FastAPI
from app.routers.inventario import router

app = FastAPI(title="ERP - Módulo Inventario")
app.include_router(router)

@app.get("/")
def health():
    return {"status": "ok", "module": "inventario"}
