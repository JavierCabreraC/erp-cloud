from fastapi import FastAPI
from app.routers.productos import router

app = FastAPI(title="ERP - Módulo Productos")
app.include_router(router)

@app.get("/")
def health():
    return {"status": "ok", "module": "productos"}
