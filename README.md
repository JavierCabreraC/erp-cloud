# ERP Minisúper — Documentación del Proyecto

> Sistema backend de gestión para una tienda pequeña, construido con **FastAPI + PostgreSQL (Neon)**, desplegado en **Google Cloud Run**.

---

## Propósito General

Este sistema implementa un ERP (Enterprise Resource Planning) de alcance pequeño-mediano orientado a la gestión operativa de un minisúper. Cubre cuatro módulos principales:

- **Clientes** — registro y administración de compradores
- **Productos** — catálogo de artículos del negocio
- **Compras** — entradas de mercadería desde proveedores (actualiza stock automáticamente vía trigger)
- **Ventas** — salidas de mercadería hacia clientes (descuenta stock automáticamente vía trigger)
- **Inventario** — seguimiento en tiempo real del stock por producto

El proyecto es 100% backend. No incluye interfaz gráfica. Todas las pruebas e interacciones se realizan mediante **Postman**.

---

## Stack Tecnológico

| Capa | Tecnología |
|---|---|
| Framework | FastAPI 0.136.1+ |
| Lenguaje | Python 3.12 |
| Package manager | UV |
| ORM | SQLAlchemy 2.0 |
| Base de datos | PostgreSQL hosteado en Neon |
| Despliegue | Google Cloud Run |
| CI/CD | Google Cloud Build (desde GitHub) |
| Pruebas | Postman |

---

## Estructura del Repositorio

```
erp-cloud/
│
├── .venv/                          # Entorno virtual — NO subir a git
├── .env                            # Variables locales — NO subir a git
├── .example.env                    # Template de variables — SÍ subir
├── .gitignore
├── .python-version                 # Contiene "3.12"
├── pyproject.toml                  # Dependencias gestionadas por UV
├── uv.lock                         # Lockfile — SÍ subir a git
├── Dockerfile                      # Imagen para Cloud Run
├── cloudbuild.yaml                 # Pipeline CI/CD en Google Cloud
│
├── scripts/
│   ├── __init__.py
│   └── seed.py                     # Poblar BD con datos mock
│
└── app/
    ├── __init__.py
    ├── main.py                     # Monolito local: instancia FastAPI con todos los routers
    │
    ├── entrypoints/                # Un FastAPI por módulo — usados para despliegue independiente en Cloud Run
    │   ├── clientes.py
    │   ├── productos.py
    │   ├── inventario.py
    │   ├── compras.py
    │   └── ventas.py
    ├── database.py                 # Engine SQLAlchemy + SessionLocal
    ├── dependencies.py             # Inyección de dependencias (get_db, etc.)
    │
    ├── models/                     # Modelos ORM — mapean las tablas de PostgreSQL
    │   ├── __init__.py
    │   ├── cliente.py
    │   ├── producto.py
    │   ├── inventario.py
    │   ├── compra.py
    │   └── venta.py                # Incluye Venta y DetalleVenta
    │
    ├── schemas/                    # Schemas Pydantic — validación de request/response
    │   ├── __init__.py
    │   ├── cliente.py
    │   ├── producto.py
    │   ├── inventario.py
    │   ├── compra.py
    │   └── venta.py
    │
    ├── routers/                    # Endpoints agrupados por módulo
    │   ├── __init__.py
    │   ├── clientes.py
    │   ├── productos.py
    │   ├── inventario.py
    │   ├── compras.py
    │   └── ventas.py
    │
    └── services/                   # Lógica de negocio desacoplada de los routers
        ├── __init__.py
        ├── cliente_service.py
        ├── inventario_service.py
        ├── compra_service.py
        └── venta_service.py
```

---

## Base de Datos — Tablas

| Tabla | Descripción |
|---|---|
| `clientes` | Datos de los compradores |
| `productos` | Catálogo de artículos con precio y categoría |
| `inventario` | Stock actual/mínimo/máximo por producto (1 fila por producto) |
| `compras` | Registro de entradas de mercadería por proveedor |
| `ventas` | Cabecera de cada transacción de venta |
| `detalle_ventas` | Líneas de producto dentro de una venta |

> Los triggers de PostgreSQL actualizan el stock en `inventario` automáticamente al insertar en `compras` o `detalle_ventas`.

---

## Endpoints

### Clientes — `/clientes`

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/clientes` | Listar todos los clientes |
| `GET` | `/clientes/{id}` | Obtener cliente por ID |
| `POST` | `/clientes` | Crear nuevo cliente |
| `PUT` | `/clientes/{id}` | Actualizar cliente completo |
| `PATCH` | `/clientes/{id}` | Actualizar campos parciales |
| `DELETE` | `/clientes/{id}` | Eliminar cliente |

### Productos — `/productos`

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/productos` | Listar todos los productos |
| `GET` | `/productos/{id}` | Obtener producto por ID |
| `POST` | `/productos` | Crear producto (también inicializa su inventario) |
| `PUT` | `/productos/{id}` | Actualizar producto |
| `DELETE` | `/productos/{id}` | Eliminar producto |

### Compras — `/compras`

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/compras` | Listar todas las compras |
| `GET` | `/compras/{id}` | Detalle de una compra |
| `GET` | `/compras/producto/{producto_id}` | Historial de compras de un producto |
| `POST` | `/compras` | Registrar compra — actualiza stock vía trigger |
| `DELETE` | `/compras/{id}` | Anular compra |

### Ventas — `/ventas`

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/ventas` | Listar todas las ventas |
| `GET` | `/ventas/{id}` | Detalle de venta con sus líneas |
| `GET` | `/ventas/cliente/{cliente_id}` | Historial de ventas de un cliente |
| `POST` | `/ventas` | Crear venta completa con detalle — descuenta stock |
| `DELETE` | `/ventas/{id}` | Anular venta |

### Inventario — `/inventario`

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/inventario` | Ver stock de todos los productos |
| `GET` | `/inventario/{producto_id}` | Stock de un producto específico |
| `GET` | `/inventario/alertas` | Productos con stock por debajo del mínimo |
| `POST` | `/inventario` | Inicializar inventario manualmente |
| `PATCH` | `/inventario/{producto_id}` | Ajuste manual de stock |

---

## Flujo de Despliegue en Google Cloud

```
Desarrollo local
      │
      │  git push origin main
      ▼
GitHub (repositorio remoto)
      │
      │  Cloud Build detecta el push (via trigger configurado)
      ▼
Cloud Build ejecuta cloudbuild.yaml
      │
      ├─ Paso 1: docker build -t gcr.io/$PROJECT_ID/erp-cloud .
      ├─ Paso 2: docker push gcr.io/$PROJECT_ID/erp-cloud
      └─ Paso 3: gcloud run deploy erp-cloud --image ...
      │
      ▼
Google Cloud Run
      │
      └─ URL pública HTTPS generada automáticamente:
         https://erp-cloud-xxxxxxxxxx-uc.a.run.app
```

### Archivos clave para el despliegue

**`Dockerfile`**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install uv && uv sync --no-dev
COPY ./app ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**`cloudbuild.yaml`**
```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/erp-cloud', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/erp-cloud']
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    args:
      - gcloud
      - run
      - deploy
      - erp-cloud
      - '--image=gcr.io/$PROJECT_ID/erp-cloud'
      - '--region=us-central1'
      - '--platform=managed'
      - '--allow-unauthenticated'
```

### Variables de entorno en Cloud Run

```bash
gcloud run services update erp-cloud \
  --region=us-central1 \
  --set-env-vars DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
```

---

## Pruebas con Postman

### Configuración inicial

1. Crear un **Workspace** nuevo en Postman llamado `ERP Minisúper`
2. Crear una **Collection** con carpetas por módulo: `Clientes`, `Productos`, `Compras`, `Ventas`, `Inventario`
3. Crear dos **Environments**:

| Variable | Env: Local | Env: Cloud |
|---|---|---|
| `BASE_URL` | `http://localhost:8000` | `https://erp-cloud-xxxx-uc.a.run.app` |

4. En cada request usar `{{BASE_URL}}/clientes`, `{{BASE_URL}}/ventas`, etc.
5. Cambiar de environment con un solo clic para alternar entre local y producción.

### Orden recomendado para pruebas

```
1. POST /productos          → crear productos base
2. GET  /inventario         → verificar inicialización de stock
3. POST /clientes           → registrar clientes
4. POST /compras            → registrar entradas de mercadería
5. GET  /inventario         → verificar que el stock subió
6. POST /ventas             → registrar ventas con detalle
7. GET  /inventario         → verificar que el stock bajó
8. GET  /inventario/alertas → ver productos en nivel mínimo
9. GET  /ventas/cliente/{id}→ historial de un cliente
```

> **Tip:** Postman tiene una pestaña **"Docs"** dentro de cada Collection. Podés documentar el body esperado de cada endpoint ahí para facilitar el trabajo en equipo.

---

## Comandos de referencia rápida

```bash
# Instalar dependencias
uv add fastapi uvicorn[standard] sqlalchemy psycopg2-binary pydantic pydantic-settings python-dotenv

# Correr en local
uv run uvicorn app.main:app --reload --port 8000

# Poblar BD con datos mock
uv run python scripts/seed.py

# Ver documentación automática generada por FastAPI
# Abrir en navegador: http://localhost:8000/docs
```

---

*Proyecto universitario — Tópicos Especiales en Ingeniería de Software — 2026*