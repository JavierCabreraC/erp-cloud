"""
Script de seed — poblar BD con datos mock para pruebas.
Ejecutar: uv run python scripts/seed.py
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine

# ─────────────────────────────────────────
# DATOS MOCK
# ─────────────────────────────────────────

clientes = [
    ("Ana",     "García",    "ana.garcia@email.com",    "70012345", "Av. Montes 123"),
    ("Carlos",  "Mendoza",   "carlos.m@email.com",      "71198765", "Calle 6 de Agosto 45"),
    ("Luisa",   "Torrez",    "luisa.t@email.com",       "76543210", "Av. Arce 890"),
    ("Roberto", "Quispe",    "roberto.q@email.com",     "72234567", "Zona Sur, Calle 10"),
    ("María",   "Condori",   "maria.c@email.com",       "79876543", "El Alto, Av. 6"),
]

productos = [
    # (nombre, descripcion, precio_unitario, unidad_medida, categoria)
    ("Arroz Fino 1kg",      "Arroz grano largo",         12.50,  "kg",     "Abarrotes"),
    ("Aceite Fino 1L",      "Aceite vegetal refinado",   18.00,  "litro",  "Abarrotes"),
    ("Azúcar Blanca 1kg",   "Azúcar refinada",           10.00,  "kg",     "Abarrotes"),
    ("Harina de Trigo 1kg", "Harina 000",                 8.50,  "kg",     "Abarrotes"),
    ("Leche PIL 1L",        "Leche entera pasteurizada", 11.00,  "litro",  "Lácteos"),
    ("Queso Taquiña 250g",  "Queso fresco",              22.00,  "unidad", "Lácteos"),
    ("Pan Marraqueta",      "Pan blanco de panadería",    0.50,  "unidad", "Panadería"),
    ("Coca Cola 2L",        "Refresco cola",             15.00,  "unidad", "Bebidas"),
    ("Agua Vital 600ml",    "Agua purificada",            5.00,  "unidad", "Bebidas"),
    ("Jabón Bolivar",       "Jabón de lavar ropa",        7.00,  "unidad", "Limpieza"),
]

# inventario: stock_actual, stock_minimo, stock_maximo (mismo orden que productos)
inventario_inicial = [
    (100, 20, 500),
    ( 80, 10, 300),
    (150, 30, 600),
    ( 60, 15, 200),
    ( 90, 20, 400),
    ( 40, 10, 150),
    (200, 50, 800),
    ( 50, 10, 200),
    (120, 30, 500),
    ( 70, 15, 300),
]

compras = [
    # (producto_id, proveedor, cantidad, precio_compra, fecha_compra)
    (1, "Distribuidora Norte",  200, 10.00, "2025-01-10"),
    (2, "Aceites del Sur",      100, 14.00, "2025-01-11"),
    (3, "Ingenio Sucrobol",     300,  7.50, "2025-01-12"),
    (5, "PIL Andina",           150,  8.00, "2025-01-13"),
    (8, "Coca-Cola Bolivia",    100, 11.00, "2025-01-14"),
]

# ventas: (cliente_id, fecha_venta, [(producto_id, cantidad, precio_unitario)])
ventas = [
    (1, "2025-01-15", [(1, 2, 12.50), (5, 3, 11.00), (7, 4, 0.50)]),
    (2, "2025-01-15", [(2, 1, 18.00), (8, 2, 15.00)]),
    (3, "2025-01-16", [(3, 5, 10.00), (6, 1, 22.00)]),
    (4, "2025-01-16", [(9, 3,  5.00), (10,2,  7.00)]),
    (1, "2025-01-17", [(1, 1, 12.50), (4, 2,  8.50), (7, 6, 0.50)]),
]

# ─────────────────────────────────────────
# FUNCIONES DE INSERT
# ─────────────────────────────────────────

def seed_clientes(conn):
    print("→ Insertando clientes...")
    for nombre, apellido, email, telefono, direccion in clientes:
        conn.execute(text("""
            INSERT INTO clientes (nombre, apellido, email, telefono, direccion)
            VALUES (:nombre, :apellido, :email, :telefono, :direccion)
            ON CONFLICT (email) DO NOTHING
        """), dict(nombre=nombre, apellido=apellido, email=email,
                   telefono=telefono, direccion=direccion))
    print(f"   {len(clientes)} clientes insertados.")

def seed_productos_e_inventario(conn):
    print("→ Insertando productos e inventario...")
    for i, (nombre, desc, precio, unidad, cat) in enumerate(productos):
        result = conn.execute(text("""
            INSERT INTO productos (nombre, descripcion, precio_unitario, unidad_medida, categoria)
            VALUES (:nombre, :desc, :precio, :unidad, :cat)
            RETURNING id
        """), dict(nombre=nombre, desc=desc, precio=precio, unidad=unidad, cat=cat))

        producto_id = result.fetchone()[0]
        stock_actual, stock_min, stock_max = inventario_inicial[i]

        conn.execute(text("""
            INSERT INTO inventario (producto_id, stock_actual, stock_minimo, stock_maximo)
            VALUES (:pid, :actual, :minimo, :maximo)
            ON CONFLICT (producto_id) DO NOTHING
        """), dict(pid=producto_id, actual=stock_actual,
                   minimo=stock_min, maximo=stock_max))

    print(f"   {len(productos)} productos + inventarios insertados.")

def seed_compras(conn):
    print("→ Insertando compras...")
    for producto_id, proveedor, cantidad, precio, fecha in compras:
        conn.execute(text("""
            INSERT INTO compras (producto_id, proveedor, cantidad, precio_compra, fecha_compra)
            VALUES (:pid, :prov, :cant, :precio, :fecha)
        """), dict(pid=producto_id, prov=proveedor, cant=cantidad,
                   precio=precio, fecha=fecha))
    print(f"   {len(compras)} compras insertadas.")

def seed_ventas(conn):
    print("→ Insertando ventas...")
    for cliente_id, fecha, detalles in ventas:
        total = sum(cant * precio for _, cant, precio in detalles)

        result = conn.execute(text("""
            INSERT INTO ventas (cliente_id, total, fecha_venta)
            VALUES (:cid, :total, :fecha)
            RETURNING id
        """), dict(cid=cliente_id, total=total, fecha=fecha))

        venta_id = result.fetchone()[0]

        for producto_id, cantidad, precio_unit in detalles:
            conn.execute(text("""
                INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario)
                VALUES (:vid, :pid, :cant, :precio)
            """), dict(vid=venta_id, pid=producto_id,
                       cant=cantidad, precio=precio_unit))

    print(f"   {len(ventas)} ventas con detalle insertadas.")

# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────

def main():
    print("\n🌱 Iniciando seed de la base de datos...\n")
    with engine.begin() as conn:  # begin() hace commit automático al salir
        seed_clientes(conn)
        seed_productos_e_inventario(conn)
        seed_compras(conn)
        seed_ventas(conn)
    print("\n✅ Seed completado exitosamente.\n")

if __name__ == "__main__":
    main()