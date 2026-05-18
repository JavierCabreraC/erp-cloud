from fastapi import FastAPI
from app.routers.ventas import router

app = FastAPI(title="ERP - Módulo Ventas")
app.include_router(router)

@app.get("/")
def health():
    return {"status": "ok", "module": "ventas"}
