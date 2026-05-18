from fastapi import FastAPI
from app.routers.clientes import router

app = FastAPI(title="ERP - Módulo Clientes")
app.include_router(router)

@app.get("/")
def health():
    return {"status": "ok", "module": "clientes"}
