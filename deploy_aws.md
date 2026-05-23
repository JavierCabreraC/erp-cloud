# Guía de Despliegue — AWS App Runner (desde código fuente)

Este enfoque conecta App Runner directamente al repositorio de GitHub. No se requiere Docker local, ECR, GitHub Actions, ni usuarios IAM. AWS gestiona el build y el despliegue automáticamente.

---

## Estrategia

| Componente | Solución |
|---|---|
| **Cómputo** | AWS App Runner |
| **CI/CD** | App Runner nativo (detecta push a `main` automáticamente) |
| **Registro de imágenes** | No requerido |
| **Base de datos** | Neon — inyectada como variable de entorno |

---

## Prerequisitos

- Cuenta en [AWS](https://aws.amazon.com) (una cuenta nueva tiene capa gratuita por 12 meses)
- El código subido a un repositorio en GitHub
- La `DATABASE_URL` de Neon disponible (`postgresql://user:password@host/dbname?sslmode=require`)

---

## IAM — ¿Hay que crear usuarios o roles?

**No.** A diferencia del enfoque con GitHub Actions + ECR, este método no requiere crear usuarios IAM ni Access Keys. App Runner crea automáticamente los roles de servicio necesarios durante la configuración en la consola.

Lo único que ocurre en IAM de forma automática:

- `AWSServiceRoleForAppRunner` — rol vinculado al servicio, creado por AWS la primera vez que usás App Runner en tu cuenta. No requiere acción manual.

---

## Paso 1 — Crear el servicio en App Runner

1. Entrá a la consola de AWS y buscá **AWS App Runner**.
2. Hacé clic en **Create service**.
3. En **Source**, seleccioná **Source code repository**.

---

## Paso 2 — Conectar GitHub

1. Hacé clic en **Add new** junto a "GitHub".
2. AWS abre una ventana de autorización de GitHub — iniciá sesión y autorizá el acceso.
3. Seleccioná el repositorio del proyecto y la rama `main`.
4. En **Deployment trigger**, seleccioná **Automatic** — App Runner redesplegará solo en cada push.

> La conexión a GitHub usa OAuth. No se generan credenciales ni secrets en ningún lado.

---

## Paso 3 — Configurar el build

En la sección **Configure build**, completar:

| Campo | Valor |
|---|---|
| **Runtime** | `Python 3` |
| **Build command** | `pip install uv && uv sync --no-dev` |
| **Start command** | `.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8080` |
| **Port** | `8080` |

> `uv sync --no-dev` instala las dependencias del proyecto en `.venv/`. El start command llama a uvicorn directamente desde ese entorno virtual.

---

## Paso 4 — Configurar las variables de entorno

En la sección **Configure service**, expandir **Environment variables** y agregar:

| Clave | Valor |
|---|---|
| `DATABASE_URL` | `postgresql://user:password@host/dbname?sslmode=require` |
| `API_KEY` | `reemplazar-con-un-string-secreto-largo` |

> Reemplazá con los valores reales.
>
> Para generar un API key seguro: `python -c "import secrets; print(secrets.token_hex(32))"`

---

## Paso 5 — Crear el servicio

Hacé clic en **Next** → **Next** → **Create & Deploy**.

App Runner clona el repositorio, ejecuta el build command y levanta el servidor. El proceso tarda entre 3 y 5 minutos la primera vez. El progreso se puede seguir en **App Runner → [nombre del servicio] → Logs**.

---

## Paso 6 — Verificar el despliegue

Una vez que el estado sea **Running**, App Runner asigna una URL pública con el formato:

```
https://xxxx.us-east-1.awsapprunner.com
```

Para verificar que el servicio está activo:

```
GET https://xxxx.us-east-1.awsapprunner.com/
```

Respuesta esperada:
```json
{ "status": "ok", "service": "ERP Cloud" }
```

Documentación interactiva:
```
https://xxxx.us-east-1.awsapprunner.com/docs
```

Todos los módulos disponibles bajo la misma URL base:
```
https://xxxx.us-east-1.awsapprunner.com/clientes
https://xxxx.us-east-1.awsapprunner.com/productos
https://xxxx.us-east-1.awsapprunner.com/inventario
https://xxxx.us-east-1.awsapprunner.com/compras
https://xxxx.us-east-1.awsapprunner.com/ventas
```

---

## ¿Se necesita una API key para llamar a los endpoints?

**Sí.** El servicio requiere el header `X-API-Key` en cada request. Sin él, la API responde `401 Unauthorized`.

En Postman, agregar en la pestaña **Headers** de cada request (o a nivel de Collection para aplicarlo a todos):

| Key | Value |
|---|---|
| `X-API-Key` | `tu-api-key-configurada-en-las-variables-de-entorno` |

El endpoint raíz `GET /` no requiere autenticación — sirve como health check.

---

## Despliegues posteriores

Cualquier `git push` a la rama `main` dispara automáticamente un nuevo build y despliegue. No se requiere ninguna acción manual adicional.

---

## Solución de problemas comunes

**El build falla con error de `uv` o dependencias:**
Verificar que el build command sea exactamente `pip install uv && uv sync --no-dev` y que `pyproject.toml` y `uv.lock` estén commiteados en el repositorio.

**El servicio arranca pero responde 500:**
La variable `DATABASE_URL` probablemente tiene un valor incorrecto o falta `sslmode=require`. Verificar en **App Runner → [servicio] → Configuration → Environment variables**.

**El servicio no inicia (status "Create failed"):**
Revisar los logs en **App Runner → [servicio] → Logs → Deployment**. El error más común es un start command incorrecto o un puerto que no coincide con el configurado.

**Ver logs del servicio en producción:**
Ir a **App Runner → [servicio] → Logs → Application**.

---

## Comparación con Google Cloud Run

| Característica | Google Cloud Run | AWS App Runner (esta guía) |
|---|---|---|
| **Pipeline** | Cloud Build (`cloudbuild.yaml`) | App Runner nativo |
| **Usuarios IAM a crear** | Ninguno | Ninguno |
| **Archivos extra en el repo** | `cloudbuild.yaml` (ya existe) | Ninguno |
| **Registro de imágenes** | GCR (automático en el pipeline) | No requerido |
| **Escalado a cero** | Sí | No (mínimo 1 instancia activa — mayor costo base) |
| **API key para endpoints** | Sí (`X-API-Key` header) | Sí (`X-API-Key` header) |
