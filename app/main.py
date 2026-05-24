from fastapi import FastAPI, Depends
from app.dependencies import verify_api_key
from app.routers import clientes, productos, inventario, compras, ventas

app = FastAPI(title="ERP Minisúper")

# Inclusión de routers para la aplicación completa (útil para desarrollo local o monolito)
app.include_router(clientes.router, dependencies=[Depends(verify_api_key)])
app.include_router(productos.router, dependencies=[Depends(verify_api_key)])
app.include_router(inventario.router, dependencies=[Depends(verify_api_key)])
app.include_router(compras.router, dependencies=[Depends(verify_api_key)])
app.include_router(ventas.router, dependencies=[Depends(verify_api_key)])

@app.get("/")
def health_check():
    return {"status": "ok", "service": "ERP Cloud"}
