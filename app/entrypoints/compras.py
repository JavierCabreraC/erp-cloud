from fastapi import FastAPI
from app.routers.compras import router

app = FastAPI(title="ERP - Módulo Compras")
app.include_router(router)

@app.get("/")
def health():
    return {"status": "ok", "module": "compras"}
