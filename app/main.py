from fastapi import FastAPI
from app.routers import clientes, productos, inventario, compras, ventas

app = FastAPI(title="ERP Minisúper")

# Inclusión de routers para la aplicación completa (útil para desarrollo local o monolito)
app.include_router(clientes.router)
app.include_router(productos.router)
app.include_router(inventario.router)
app.include_router(compras.router)
app.include_router(ventas.router)

@app.get("/")
def health_check():
    return {"status": "ok", "service": "ERP Cloud"}
