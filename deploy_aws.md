# Guía de Despliegue — AWS Elastic Beanstalk (Docker)

Este enfoque utiliza **AWS Elastic Beanstalk** para publicar la aplicación en internet. Beanstalk automatiza la infraestructura por vos: crea los servidores, el balanceador de carga y el sistema de escalado. Vos solo le das el código y él se encarga del resto.

Al final de esta guía, cada vez que hagas `git push` a tu rama `main`, el sistema desplegará la nueva versión automáticamente.

---

## Estrategia general

| Componente | Solución |
|---|---|
| **Cómputo** | Amazon EC2 (gestionado por Elastic Beanstalk) |
| **Plataforma** | Docker (Amazon Linux 2023) |
| **CI/CD** | AWS CodePipeline (conectado a GitHub) |
| **Base de datos** | Neon — inyectada como variable de entorno |

---

## Prerequisitos

Antes de empezar, asegurate de tener:

- Una cuenta en [AWS](https://aws.amazon.com) (podés usar la capa gratuita).
- El código subido a un repositorio **público o privado** en GitHub.
- La `DATABASE_URL` de Neon disponible (la obtenés desde el dashboard de Neon → tu proyecto → "Connection string").
- Una `API_KEY` generada (ver sección siguiente).

---

## Generar la API_KEY

La `API_KEY` de este proyecto **no es un servicio externo**. Es una contraseña que vos inventás para proteger los endpoints: si un cliente no la incluye en el header `X-API-Key`, la API rechaza la petición con un error 401.

Para generarla, abrí una terminal y ejecutá:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Esto produce un string aleatorio como:
```
a3f8c21d7e904b1a56f2d8e3c0b7a9f4d1e2c3b4a5f6d7e8c9b0a1f2d3e4c5b6
```

**Guardalo en un lugar seguro** (un gestor de contraseñas, por ejemplo). Lo vas a necesitar para configurar el entorno en AWS y para hacer requests desde Postman.

Para usarla localmente, copiá el archivo de ejemplo y completá los valores:

```bash
cp .example.env .env
# Editá .env y reemplazá los valores reales de DATABASE_URL y API_KEY
```

Para probar un endpoint local con la clave:
```bash
curl -H "X-API-Key: tu-clave-aqui" http://localhost:8000/
```

---

## IAM — Configuración de seguridad (recomendado)

En lugar de operar con el usuario root de AWS, creá un usuario IAM con permisos acotados:

1. En la consola de AWS buscá **IAM** y entrá.
2. En el menú lateral hacé clic en **Users** → **Create user**.
3. Nombre de usuario: `erp-admin`. Marcá la opción **"Provide user access to the AWS Management Console"**.
4. En la siguiente pantalla seleccioná **"Attach policies directly"** y agregá estas tres políticas:
   - `AdministratorAccess-AWSElasticBeanstalk`
   - `AWSCodeStarFullAccess`
   - `IAMFullAccess` (solo necesaria la primera vez; Beanstalk necesita crear roles de servicio internos)
5. Finalizá la creación y copiá la URL de la consola y las credenciales generadas.

A partir de aquí iniciá sesión con ese usuario `erp-admin`.

---

## Paso 1 — Crear la aplicación en Elastic Beanstalk

1. En la barra de búsqueda de la consola de AWS escribí **Elastic Beanstalk** y entrá.
2. Hacé clic en **"Create application"**.
3. Completá los primeros campos:
   - **Application name:** `erp-cloud`
4. Hacé clic en **"Create"**.

Esto crea el contenedor lógico de la aplicación. El entorno (los servidores reales) se configura en el siguiente paso.

---

## Paso 2 — Crear el entorno

Dentro de la aplicación `erp-cloud` que acabás de crear:

1. Hacé clic en **"Create new environment"**.
2. Seleccioná **"Web server environment"** y hacé clic en **Select**.
3. Completá los campos:
   - **Environment name:** `erp-cloud-env`
   - **Domain:** podés dejarlo en blanco para que AWS genere uno automáticamente.
4. En la sección **"Platform"**:
   - **Platform type:** `Managed platform`
   - **Platform:** `Docker`
   - **Platform branch:** `Docker running on 64bit Amazon Linux 2023`
   - **Platform version:** la más reciente (recomendado).
5. En **"Application code"** seleccioná **"Sample application"**. Esto es temporal: el código real llegará desde GitHub via CodePipeline en el Paso 4.
6. Hacé clic en **"Next"** para continuar con la configuración avanzada.

---

## Paso 3 — Variables de entorno y configuración de instancia

Este paso ocurre dentro del asistente de creación del entorno, en la sección **"Configure service access"** y **"Configure instance traffic and scaling"**.

### 3a — Tipo de instancia (para mantenerse en la capa gratuita)

En la sección **"Capacity"** o **"Instance type"**:
- Seleccioná `t3.micro` (incluida en el Free Tier de AWS por 12 meses).

### 3b — Puerto de la aplicación

En la sección **"Updates, monitoring, and logging"**:
- Buscá el campo **"Environment properties"** (puede aparecer también en la sección "Software").
- AWS necesita saber en qué puerto escucha tu contenedor. El `Dockerfile` de este proyecto usa el puerto `8080`.

### 3c — Variables de entorno

En la misma sección **"Environment properties"** vas a ver un formulario con columnas **Name** y **Value**. Hacé clic en **"Add environment property"** tres veces y completá así:

| Name | Value |
|---|---|
| `PORT` | `8080` |
| `DATABASE_URL` | `postgresql://user:password@host/dbname?sslmode=require` |
| `API_KEY` | el string que generaste en la sección anterior |

> **¿Cómo llegan estas variables a tu app?** Beanstalk las inyecta como variables de entorno del sistema operativo dentro del contenedor. Tu app las lee con `os.environ["API_KEY"]`, `os.environ["DATABASE_URL"]`, etc., igual que cuando usás el archivo `.env` en local.

> **Si ya creaste el entorno y necesitás editar las variables después:** entrá al entorno → menú lateral **"Configuration"** → sección **"Software"** → **"Edit"** → "Environment properties".

### 3d — Finalizar el entorno

Continuá con **"Next"** en cada pantalla siguiente hasta llegar a **"Review"** y finalmente hacé clic en **"Submit"**. Beanstalk tardará entre 5 y 10 minutos en crear todos los recursos (EC2, Load Balancer, grupos de seguridad). Podés ver el progreso en tiempo real en la pantalla del entorno.

Cuando el estado cambie a **Health: OK** con un ícono verde, el entorno está listo.

---

## Paso 4 — Conectar GitHub con CodePipeline (CI/CD)

Este paso conecta tu repositorio de GitHub con Beanstalk. A partir de aquí, cada `git push` a `main` desplegará automáticamente la nueva versión.

### 4a — Crear el pipeline

1. En la barra de búsqueda de AWS buscá **CodePipeline** y entrá.
2. Hacé clic en **"Create pipeline"**.
3. Completá los campos iniciales:
   - **Pipeline name:** `erp-cloud-pipeline`
   - **Execution mode:** `Superseded` (el default; si un deploy nuevo llega mientras hay uno en curso, cancela el anterior).
   - **Service role:** seleccioná **"New service role"**. AWS genera automáticamente los permisos necesarios para que el pipeline pueda acceder a Beanstalk y GitHub.
4. Hacé clic en **"Next"**.

### 4b — Source stage (de dónde viene el código)

1. **Source provider:** seleccioná **"GitHub (Version 2)"**.
2. **Connection:** hacé clic en **"Connect to GitHub"**. Se abre una ventana emergente:
   - Poné un nombre a la conexión, por ejemplo `mi-github`.
   - Hacé clic en **"Install a new app"**. Esto te redirige a GitHub donde autorizás el acceso de AWS a tu cuenta.
   - Seleccioná el repositorio `erp-cloud` (o "All repositories" si preferís).
   - Volvés a AWS y la conexión aparece como **"Ready"**. Seleccionála.
3. **Repository name:** buscá y seleccioná tu repositorio (`tu-usuario/erp-cloud`).
4. **Default branch:** `main` (la rama que dispara el deploy al hacer push).
5. **Output artifact format:** dejá el default (`CodePipeline default`).
6. Hacé clic en **"Next"**.

### 4c — Build stage (omitir)

1. Hacé clic en **"Skip build stage"**.
2. Confirmá en el diálogo que aparece.

> Beanstalk construye la imagen Docker por sí solo a partir del `Dockerfile` que está en el repositorio. No necesitamos un paso de build separado.

### 4d — Deploy stage (a dónde va el código)

1. **Deploy provider:** seleccioná **"AWS Elastic Beanstalk"**.
2. **Region:** seleccioná la misma región donde creaste el entorno (ej. `us-east-1`).
3. **Application name:** `erp-cloud`
4. **Environment name:** `erp-cloud-env`
5. Hacé clic en **"Next"**.

### 4e — Revisar y crear

1. Revisá el resumen. Deberías ver tres etapas: **Source (GitHub) → Deploy (Elastic Beanstalk)**.
2. Hacé clic en **"Create pipeline"**.

El pipeline se ejecuta inmediatamente con el código actual de `main`. Podés ver el progreso en tiempo real: cada etapa muestra si está en ejecución (`In progress`), completada (`Succeeded`), o si falló (`Failed`). El primer deploy tarda unos 5 minutos.

---

## Paso 5 — Verificar el despliegue

Una vez que el pipeline muestre todas las etapas en verde y Beanstalk muestre **Health: OK**, buscá la URL pública del entorno. La encontrás en la pantalla principal del entorno de Beanstalk, arriba a la derecha, con el formato:

```
http://erp-cloud-env.eba-xxxx.us-east-1.elasticbeanstalk.com
```

Para verificar que la app está corriendo, hacé un request al health check (este endpoint no requiere API key):

```bash
curl http://erp-cloud-env.eba-xxxx.us-east-1.elasticbeanstalk.com/
```

Respuesta esperada:
```json
{"status": "ok", "service": "ERP Cloud"}
```

Para verificar un endpoint protegido con la API key:
```bash
curl -H "X-API-Key: tu-api-key" \
  http://erp-cloud-env.eba-xxxx.us-east-1.elasticbeanstalk.com/productos
```

También podés acceder a la documentación interactiva generada por FastAPI:
```
http://erp-cloud-env.eba-xxxx.us-east-1.elasticbeanstalk.com/docs
```

> **Nota:** Beanstalk usa HTTP por defecto. Para HTTPS necesitarías configurar un certificado en AWS Certificate Manager (ACM) y adjuntarlo al Load Balancer, lo cual está fuera del alcance de esta guía inicial.

---

## Configurar Postman para producción

En Postman, actualizá el environment de producción con la URL de Beanstalk:

| Variable | Valor |
|---|---|
| `BASE_URL` | `http://erp-cloud-env.eba-xxxx.us-east-1.elasticbeanstalk.com` |
| `API_KEY` | el string que generaste |

En cada request que use autenticación, agregá el header:
```
X-API-Key: {{API_KEY}}
```

---

## Solución de problemas frecuentes

**El pipeline falla en la etapa "Deploy"**
- Revisá que el entorno de Beanstalk esté en estado OK antes de que el pipeline corra.
- Verificá que el `Dockerfile` esté en la raíz del repositorio.

**Health degraded (ícono rojo o naranja en Beanstalk)**
- Entrá al entorno → menú lateral **"Logs"** → **"Request last 100 lines"**.
- Las causas más comunes son: `DATABASE_URL` mal copiada, la variable `PORT` no configurada como `8080`, o un error al iniciar la app.

**Error 401 en los endpoints**
- Verificá que estés enviando el header `X-API-Key` con el valor exacto que configuraste en las variables de entorno.
- Si cambiaste la `API_KEY` en Beanstalk, el entorno necesita reiniciarse. Beanstalk lo hace automáticamente al guardar los cambios en "Configuration".

**Error de permisos al crear el entorno**
- Asegurate de que el rol `aws-elasticbeanstalk-ec2-role` tenga permisos para leer de S3. Si no existe, Beanstalk te ofrecerá crearlo automáticamente durante el asistente.

---

## Comparación: Elastic Beanstalk vs App Runner

| Característica | App Runner | Elastic Beanstalk |
|---|---|---|
| **Abstracción** | Muy alta (no ves servidores) | Media (ves las EC2 y el balanceador) |
| **Control** | Limitado | Total (SSH, configuración de red) |
| **Costo** | Basado en uso | Basado en EC2 activas |
| **Dificultad** | Muy fácil | Moderada |
| **Ideal para** | Prototipos rápidos | Proyectos con más control requerido |