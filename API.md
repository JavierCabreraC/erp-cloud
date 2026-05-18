# API Reference — ERP Minisúper

Base URL local: `http://localhost:8000`  
Base URL producción: `https://erp-cloud-xxxx-uc.a.run.app`  
Documentación interactiva: `{BASE_URL}/docs`

---

## Tabla de contenidos

- [Clientes](#clientes)
- [Productos](#productos)
- [Compras](#compras)
- [Ventas](#ventas)
- [Inventario](#inventario)

---

## Clientes

### `GET /clientes`
Lista todos los clientes registrados.

**Response `200`**
```json
[
  {
    "id": 1,
    "nombre": "Ana",
    "apellido": "García",
    "email": "ana@email.com",
    "telefono": "70012345",
    "direccion": "Av. Montes 123",
    "created_at": "2026-05-17T10:00:00"
  }
]
```

---

### `GET /clientes/{id}`
Obtiene un cliente por su ID.

**Path param:** `id` (integer)

**Response `200`**
```json
{
  "id": 1,
  "nombre": "Ana",
  "apellido": "García",
  "email": "ana@email.com",
  "telefono": "70012345",
  "direccion": "Av. Montes 123",
  "created_at": "2026-05-17T10:00:00"
}
```

**Response `404`**
```json
{ "detail": "Cliente no encontrado" }
```

---

### `POST /clientes`
Crea un nuevo cliente.

**Request body**
| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `nombre` | string | Sí | Nombre del cliente |
| `apellido` | string | Sí | Apellido del cliente |
| `email` | string | Sí | Email único |
| `telefono` | string | No | Número de teléfono |
| `direccion` | string | No | Dirección postal |

```json
{
  "nombre": "Ana",
  "apellido": "García",
  "email": "ana@email.com",
  "telefono": "70012345",
  "direccion": "Av. Montes 123"
}
```

**Response `201`** — mismo esquema que `GET /clientes/{id}`

---

### `PUT /clientes/{id}`
Reemplaza todos los campos de un cliente (requiere todos los campos).

**Path param:** `id` (integer)

**Request body** — mismos campos que `POST /clientes` (todos requeridos excepto los opcionales)

**Response `200`** — mismo esquema que `GET /clientes/{id}`

**Response `404`**
```json
{ "detail": "Cliente no encontrado" }
```

---

### `PATCH /clientes/{id}`
Actualiza uno o más campos de un cliente. Solo se envían los campos a modificar.

**Path param:** `id` (integer)

**Request body** — todos los campos son opcionales
| Campo | Tipo | Descripción |
|---|---|---|
| `nombre` | string | — |
| `apellido` | string | — |
| `email` | string | — |
| `telefono` | string | — |
| `direccion` | string | — |

```json
{
  "telefono": "71100000",
  "direccion": "Calle Nueva 456"
}
```

**Response `200`** — mismo esquema que `GET /clientes/{id}`

**Response `404`**
```json
{ "detail": "Cliente no encontrado" }
```

---

### `DELETE /clientes/{id}`
Elimina un cliente. Las ventas asociadas mantienen `cliente_id = null`.

**Path param:** `id` (integer)

**Response `204`** — sin body

**Response `404`**
```json
{ "detail": "Cliente no encontrado" }
```

---

## Productos

### `GET /productos`
Lista todos los productos del catálogo.

**Response `200`**
```json
[
  {
    "id": 1,
    "nombre": "Arroz Fino 1kg",
    "descripcion": "Grano largo",
    "precio_unitario": 12.50,
    "unidad_medida": "kg",
    "categoria": "Abarrotes",
    "created_at": "2026-05-17T10:00:00"
  }
]
```

---

### `GET /productos/{id}`
Obtiene un producto por su ID.

**Path param:** `id` (integer)

**Response `200`**
```json
{
  "id": 1,
  "nombre": "Arroz Fino 1kg",
  "descripcion": "Grano largo",
  "precio_unitario": 12.50,
  "unidad_medida": "kg",
  "categoria": "Abarrotes",
  "created_at": "2026-05-17T10:00:00"
}
```

**Response `404`**
```json
{ "detail": "Producto no encontrado" }
```

---

### `POST /productos`
Crea un nuevo producto y automáticamente inicializa su fila en inventario con `stock_actual = 0`.

**Request body**
| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `nombre` | string | Sí | Nombre del producto |
| `descripcion` | string | No | Descripción libre |
| `precio_unitario` | float | Sí | Precio de venta (≥ 0) |
| `unidad_medida` | string | Sí | Ej: `"kg"`, `"litro"`, `"unidad"` |
| `categoria` | string | No | Categoría del producto |

```json
{
  "nombre": "Arroz Fino 1kg",
  "descripcion": "Grano largo",
  "precio_unitario": 12.50,
  "unidad_medida": "kg",
  "categoria": "Abarrotes"
}
```

**Response `201`** — mismo esquema que `GET /productos/{id}`

> Al crear el producto se inicializa automáticamente una fila en `/inventario` con `stock_actual = 0`, `stock_minimo = 0`, `stock_maximo = 0`.

---

### `PUT /productos/{id}`
Reemplaza todos los campos de un producto.

**Path param:** `id` (integer)

**Request body** — mismos campos que `POST /productos`

**Response `200`** — mismo esquema que `GET /productos/{id}`

**Response `404`**
```json
{ "detail": "Producto no encontrado" }
```

---

### `DELETE /productos/{id}`
Elimina un producto. Falla si tiene compras o detalle de ventas asociados (restricción FK `ON DELETE RESTRICT`).

**Path param:** `id` (integer)

**Response `204`** — sin body

**Response `404`**
```json
{ "detail": "Producto no encontrado" }
```

---

## Compras

Las compras representan entradas de mercadería. Al insertar una compra, un trigger de PostgreSQL incrementa automáticamente `inventario.stock_actual` del producto correspondiente.

### `GET /compras`
Lista todas las compras registradas.

**Response `200`**
```json
[
  {
    "id": 1,
    "producto_id": 1,
    "proveedor": "Distribuidora Norte",
    "cantidad": 100.0,
    "precio_compra": 10.00,
    "fecha_compra": "2026-05-17"
  }
]
```

---

### `GET /compras/{id}`
Obtiene una compra por su ID.

**Path param:** `id` (integer)

**Response `200`**
```json
{
  "id": 1,
  "producto_id": 1,
  "proveedor": "Distribuidora Norte",
  "cantidad": 100.0,
  "precio_compra": 10.00,
  "fecha_compra": "2026-05-17"
}
```

**Response `404`**
```json
{ "detail": "Compra no encontrada" }
```

---

### `GET /compras/producto/{producto_id}`
Lista el historial de compras de un producto específico.

**Path param:** `producto_id` (integer)

**Response `200`** — lista con el mismo esquema que `GET /compras/{id}`

---

### `POST /compras`
Registra una entrada de mercadería. El trigger `trg_stock_compra` incrementa el stock del producto automáticamente.

**Request body**
| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `producto_id` | integer | Sí | ID del producto que ingresa |
| `proveedor` | string | Sí | Nombre del proveedor |
| `cantidad` | float | Sí | Cantidad que ingresa (> 0) |
| `precio_compra` | float | Sí | Precio pagado por unidad (≥ 0) |
| `fecha_compra` | string (date) | Sí | Formato `YYYY-MM-DD` |

```json
{
  "producto_id": 1,
  "proveedor": "Distribuidora Norte",
  "cantidad": 100,
  "precio_compra": 10.00,
  "fecha_compra": "2026-05-17"
}
```

**Response `201`**
```json
{
  "id": 1,
  "producto_id": 1,
  "proveedor": "Distribuidora Norte",
  "cantidad": 100.0,
  "precio_compra": 10.00,
  "fecha_compra": "2026-05-17"
}
```

---

### `DELETE /compras/{id}`
Anula una compra. El servicio revierte el stock manualmente restando la cantidad de `inventario`.

**Path param:** `id` (integer)

**Response `204`** — sin body

**Response `404`**
```json
{ "detail": "Compra no encontrada" }
```

---

## Ventas

Las ventas tienen dos niveles: la cabecera (`ventas`) y las líneas de detalle (`detalle_ventas`). Al insertar los detalles, el trigger `trg_stock_venta` descuenta el stock. La venta completa se crea en un único `POST`.

### `GET /ventas`
Lista todas las ventas (sin detalles de línea).

**Response `200`**
```json
[
  {
    "id": 1,
    "cliente_id": 1,
    "total": 68.50,
    "fecha_venta": "2026-05-17"
  }
]
```

> `cliente_id` puede ser `null` si el cliente fue eliminado (la venta se conserva con `cliente_id = null`).

---

### `GET /ventas/{id}`
Obtiene una venta con todas sus líneas de detalle.

**Path param:** `id` (integer)

**Response `200`**
```json
{
  "id": 1,
  "cliente_id": 1,
  "total": 68.50,
  "fecha_venta": "2026-05-17",
  "detalles": [
    {
      "id": 1,
      "venta_id": 1,
      "producto_id": 1,
      "cantidad": 5.0,
      "precio_unitario": 12.50,
      "subtotal": 62.50
    },
    {
      "id": 2,
      "venta_id": 1,
      "producto_id": 8,
      "cantidad": 1.0,
      "precio_unitario": 6.00,
      "subtotal": 6.00
    }
  ]
}
```

**Response `404`**
```json
{ "detail": "Venta no encontrada" }
```

---

### `GET /ventas/cliente/{cliente_id}`
Lista el historial de ventas de un cliente (sin detalles de línea).

**Path param:** `cliente_id` (integer)

**Response `200`** — lista con el mismo esquema que `GET /ventas` (sin `detalles`)

---

### `POST /ventas`
Crea una venta completa con todas sus líneas en una sola petición. El trigger descuenta el stock por cada línea. El campo `total` se calcula automáticamente sumando `cantidad × precio_unitario` de todos los detalles.

**Request body**
| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `cliente_id` | integer | Sí | ID del cliente comprador |
| `fecha_venta` | string (date) | Sí | Formato `YYYY-MM-DD` |
| `detalles` | array | Sí | Al menos un elemento |

**Cada elemento de `detalles`**
| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `producto_id` | integer | Sí | ID del producto vendido |
| `cantidad` | float | Sí | Unidades vendidas (> 0) |
| `precio_unitario` | float | Sí | Precio de venta por unidad |

```json
{
  "cliente_id": 1,
  "fecha_venta": "2026-05-17",
  "detalles": [
    {
      "producto_id": 1,
      "cantidad": 5,
      "precio_unitario": 12.50
    },
    {
      "producto_id": 8,
      "cantidad": 1,
      "precio_unitario": 6.00
    }
  ]
}
```

**Response `201`** — mismo esquema que `GET /ventas/{id}` (con `detalles` incluidos)

> Si el stock de algún producto es insuficiente, el trigger lanza una excepción de PostgreSQL y la transacción completa se revierte. Ningún producto queda con stock modificado.

---

### `DELETE /ventas/{id}`
Anula una venta. El servicio revierte el stock manualmente sumando la cantidad de cada línea de vuelta a `inventario`.

**Path param:** `id` (integer)

**Response `204`** — sin body

**Response `404`**
```json
{ "detail": "Venta no encontrada" }
```

---

## Inventario

Una fila por producto. Se inicializa automáticamente al crear un producto vía `POST /productos`. El stock se actualiza vía triggers al registrar compras o ventas.

### `GET /inventario`
Lista el stock de todos los productos.

**Response `200`**
```json
[
  {
    "id": 1,
    "producto_id": 1,
    "stock_actual": 95.0,
    "stock_minimo": 20.0,
    "stock_maximo": 500.0,
    "updated_at": "2026-05-17T12:30:00"
  }
]
```

---

### `GET /inventario/alertas`
Retorna los productos cuyo `stock_actual` está por debajo de `stock_minimo`.

**Response `200`** — lista con el mismo esquema que `GET /inventario/{producto_id}`

---

### `GET /inventario/{producto_id}`
Obtiene el stock de un producto específico.

**Path param:** `producto_id` (integer)

**Response `200`**
```json
{
  "id": 1,
  "producto_id": 1,
  "stock_actual": 95.0,
  "stock_minimo": 20.0,
  "stock_maximo": 500.0,
  "updated_at": "2026-05-17T12:30:00"
}
```

**Response `404`**
```json
{ "detail": "Inventario no encontrado" }
```

---

### `POST /inventario`
Inicializa manualmente una fila de inventario. Normalmente no es necesario porque `POST /productos` lo hace de forma automática.

**Request body**
| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `producto_id` | integer | Sí | ID del producto |
| `stock_actual` | float | No | Default `0` |
| `stock_minimo` | float | No | Default `0` |
| `stock_maximo` | float | No | Default `null` |

```json
{
  "producto_id": 1,
  "stock_actual": 100,
  "stock_minimo": 20,
  "stock_maximo": 500
}
```

**Response `201`** — mismo esquema que `GET /inventario/{producto_id}`

---

### `PATCH /inventario/{producto_id}`
Ajusta manualmente los valores de stock o los umbrales mínimo/máximo. Solo se envían los campos a modificar.

**Path param:** `producto_id` (integer)

**Request body** — todos los campos son opcionales
| Campo | Tipo | Descripción |
|---|---|---|
| `stock_actual` | float | Ajuste directo del stock (corrección manual) |
| `stock_minimo` | float | Umbral para alertas |
| `stock_maximo` | float | Límite máximo de almacenamiento |

```json
{
  "stock_minimo": 20,
  "stock_maximo": 500
}
```

**Response `200`** — mismo esquema que `GET /inventario/{producto_id}`

**Response `404`**
```json
{ "detail": "Inventario no encontrado" }
```
