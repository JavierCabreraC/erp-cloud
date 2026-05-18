# Guía de Despliegue — Google Cloud Run

Este proyecto despliega un **único servicio monolítico** en Cloud Run con todos los módulos incluidos, conectado a la base de datos PostgreSQL en Neon. El proceso es automático vía Cloud Build cada vez que se hace push a la rama principal en GitHub.

---

## Prerequisitos

- Cuenta en [Google Cloud Platform](https://console.cloud.google.com) con un proyecto creado
- El código subido a un repositorio en GitHub
- La `DATABASE_URL` de Neon disponible (formato: `postgresql://user:password@host/dbname?sslmode=require`)
- [Google Cloud CLI](https://cloud.google.com/sdk/docs/install) instalado (opcional, para los pasos por terminal)

---

## Paso 1 — Habilitar las APIs de GCP

En la consola de GCP: **APIs & Services → Enable APIs and Services**, buscar y habilitar:

- Cloud Build API
- Cloud Run API
- Container Registry API

O desde Cloud Shell / terminal con `gcloud` autenticado:

```bash
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  containerregistry.googleapis.com
```

---

## Paso 2 — Dar permisos a Cloud Build

Cloud Build necesita permisos para desplegar en Cloud Run.

1. Ir a **IAM & Admin → IAM**
2. Buscar la cuenta de servicio de Cloud Build:
   ```
   [PROJECT_NUMBER]@cloudbuild.gserviceaccount.com
   ```
3. Agregarle los siguientes roles:
   - **Cloud Run Admin**
   - **Service Account User**

> El `PROJECT_NUMBER` se encuentra en **Home → Project info** de la consola de GCP.

---

## Paso 3 — Conectar el repositorio de GitHub

1. Ir a **Cloud Build → Triggers**
2. Hacer clic en **Connect Repository**
3. Seleccionar **GitHub** como proveedor
4. Autenticar con GitHub y seleccionar el repositorio del proyecto
5. Confirmar la conexión

---

## Paso 4 — Crear el Trigger de Cloud Build

1. En **Cloud Build → Triggers**, hacer clic en **Create Trigger**
2. Completar la configuración:

   | Campo | Valor |
   |---|---|
   | Nombre | `erp-cloud-deploy` (o el que prefieras) |
   | Región | `us-central1` |
   | Evento | Push to a branch |
   | Rama | `^main$` |
   | Tipo de configuración | Cloud Build configuration file (yaml) |
   | Ubicación del archivo | `cloudbuild.yaml` |

3. En la sección **Substitution variables**, agregar:

   | Variable | Valor |
   |---|---|
   | `_DATABASE_URL` | `postgresql://user:password@host/dbname?sslmode=require` |

   > Reemplazar con el string de conexión real de Neon. Esta variable no se guarda en el repositorio.

4. Hacer clic en **Save**

---

## Paso 5 — Ejecutar el primer despliegue

Hacer push a la rama principal desde el repositorio local:

```bash
git push origin main
```

Cloud Build detecta el push automáticamente y ejecuta el pipeline definido en `cloudbuild.yaml`:

1. Construye la imagen Docker
2. La sube a Google Container Registry (`gcr.io/$PROJECT_ID/erp-cloud`)
3. Despliega el servicio `erp-cloud` en Cloud Run

Para ver el progreso en tiempo real: **Cloud Build → History**.

---

## Paso 6 — Verificar el servicio desplegado

Una vez completado el build, ir a **Cloud Run**. Debe aparecer el servicio `erp-cloud` con una URL del formato:

```
https://erp-cloud-xxxxxxxxxx-uc.a.run.app
```

Para verificar que el servicio está activo, acceder a la URL raíz (`GET /`). Debe responder:

```json
{ "status": "ok", "service": "ERP Cloud" }
```

Todos los módulos están disponibles bajo la misma URL base:

```
https://erp-cloud-xxxxxxxxxx-uc.a.run.app/clientes
https://erp-cloud-xxxxxxxxxx-uc.a.run.app/productos
https://erp-cloud-xxxxxxxxxx-uc.a.run.app/inventario
https://erp-cloud-xxxxxxxxxx-uc.a.run.app/compras
https://erp-cloud-xxxxxxxxxx-uc.a.run.app/ventas
```

La documentación interactiva está disponible en:

```
https://erp-cloud-xxxxxxxxxx-uc.a.run.app/docs
```

---

## Paso 7 — Configurar Postman para producción

Crear un environment en Postman llamado **Cloud** con la variable:

| Variable | Valor |
|---|---|
| `BASE_URL` | `https://erp-cloud-xxxxxxxxxx-uc.a.run.app` |

Usar `{{BASE_URL}}/clientes`, `{{BASE_URL}}/ventas`, etc. en cada request — idéntico al entorno local, solo cambia el valor de `BASE_URL`.

---

## Despliegues posteriores

Cualquier push a `main` dispara automáticamente el pipeline completo: build → push → deploy. No se requiere ninguna acción manual adicional.

---

## Solución de problemas comunes

**El build falla en el paso de deploy:**
Verificar que la cuenta de servicio de Cloud Build tiene los roles **Cloud Run Admin** y **Service Account User** (Paso 2).

**El servicio responde con error 500:**
La variable `_DATABASE_URL` en el trigger probablemente tiene un valor incorrecto o el servidor Neon no permite conexiones desde las IPs de Cloud Run. Verificar el string de conexión y que Neon tenga habilitadas conexiones externas.

**`gcloud` no reconoce el proyecto:**
```bash
gcloud config set project [PROJECT_ID]
```

**Ver los logs del servicio en producción:**
```bash
gcloud run services logs read erp-cloud --region=us-central1
```
O desde la consola: **Cloud Run → erp-cloud → Logs**.



# Test
Deploy!