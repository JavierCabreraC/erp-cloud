# Endpoints POST y PUT — Payloads

Listado de endpoints `POST` y `PUT` del proyecto y los payloads que aceptan.

**POST /clientes**
- Payload (ClienteCreate):

```json
{
  "nombre": "string",
  "apellido": "string",
  "email": "string",
  "telefono": "string | null",
  "direccion": "string | null"
}
```

**PUT /clientes/{id}**
- Payload (ClienteCreate — mismo que arriba):

```json
{
  "nombre": "string",
  "apellido": "string",
  "email": "string",
  "telefono": "string | null",
  "direccion": "string | null"
}
```

**POST /productos**
- Payload (ProductoCreate):

```json
{
  "nombre": "string",
  "descripcion": "string | null",
  "precio_unitario": 0.0,
  "unidad_medida": "string",
  "categoria": "string | null"
}
```

**PUT /productos/{id}**
- Payload (ProductoCreate — mismo que arriba):

```json
{
  "nombre": "string",
  "descripcion": "string | null",
  "precio_unitario": 0.0,
  "unidad_medida": "string",
  "categoria": "string | null"
}
```

**POST /inventario**
- Payload (InventarioCreate):

```json
{
  "producto_id": 1,
  "stock_actual": 0,
  "stock_minimo": 0,
  "stock_maximo": null
}
```

**POST /compras**
- Payload (CompraCreate):

```json
{
  "producto_id": 1,
  "proveedor": "string",
  "cantidad": 0.0,
  "precio_compra": 0.0,
  "fecha_compra": "YYYY-MM-DD"
}
```

**POST /ventas**
- Payload (VentaCreate):

```json
{
  "cliente_id": 1,
  "fecha_venta": "YYYY-MM-DD",
  "detalles": [
    {
      "producto_id": 1,
      "cantidad": 0.0,
      "precio_unitario": 0.0
    }
  ]
}
```

---
Notas:
- Los schemas fuente están en `app/schemas/` (ej. `cliente.py`, `producto.py`, `inventario.py`, `compra.py`, `venta.py`).
- Se listan sólo métodos `POST` y `PUT` (el endpoint `PATCH /inventario/{producto_id}` existe pero no se incluyó porque es `PATCH`).
