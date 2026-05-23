# Guía de Despliegue — AWS Elastic Beanstalk (Docker)

Este enfoque utiliza **AWS Elastic Beanstalk** para orquestar la infraestructura (EC2, Load Balancer, Auto Scaling) de forma automática. Usaremos la plataforma de **Docker** de Beanstalk, aprovechando el `Dockerfile` que ya existe en el repositorio.

---

## Estrategia

| Componente | Solución |
|---|---|
| **Cómputo** | Amazon EC2 (gestionado por Elastic Beanstalk) |
| **Plataforma** | Docker (Amazon Linux 2023) |
| **CI/CD** | AWS CodePipeline (conectado a GitHub) |
| **Base de datos** | Neon — inyectada como variable de entorno |

---

## Prerequisitos

- Cuenta en [AWS](https://aws.amazon.com).
- El código subido a un repositorio en GitHub.
- La `DATABASE_URL` de Neon disponible.

---

## IAM — Configuración de Seguridad (Recomendado)

En lugar de usar el usuario root, crearemos un usuario IAM con los permisos necesarios:

1.  Crea un usuario (ej. `erp-admin`) con **Acceso a la Consola**.
2.  Adjunta las siguientes políticas administradas:
    -   `AdministratorAccess-AWSElasticBeanstalk`
    -   `AWSCodeStarFullAccess` (para la conexión con GitHub)
    -   `IAMFullAccess` (solo para la primera vez, ya que Beanstalk necesita crear roles de servicio).

---

## Paso 1 — Crear la aplicación en Elastic Beanstalk

1.  Entrá a la consola de AWS y buscá **Elastic Beanstalk**.
2.  Hacé clic en **Create application**.
3.  Nombre de la aplicación: `erp-cloud`.

---

## Paso 2 — Configurar el entorno

1.  **Tier:** Web server environment.
2.  **Environment name:** `erp-cloud-env`.
3.  **Platform:** Seleccioná **Docker**.
4.  **Platform branch:** Docker running on 64bit Amazon Linux 2023.
5.  **Application code:** Seleccioná **Existing certificate** o simplemente "Sample application" para la configuración inicial (luego lo conectaremos a GitHub).

---

## Paso 3 — Configurar variables y recursos

Hacé clic en **Configure more options** o avanzá por los pasos del asistente:

1.  **Instancias:** Seleccioná `t3.micro` para mantenerte en la capa gratuita (Free Tier).
2.  **Actualizaciones y despliegues:** Asegurate de que el puerto sea `8080` (el que usa nuestro `Dockerfile`).
3.  **Variables de entorno (Software):** Agregá las siguientes:

| Nombre | Valor |
|---|---|
| `DATABASE_URL` | `postgresql://user:password@host/dbname?sslmode=require` |
| `API_KEY` | `tu-api-key-secreta` |
| `PORT` | `8080` |

---

## Paso 4 — Conectar GitHub (CI/CD)

Beanstalk no tiene un botón de "Conectar a GitHub" tan directo como App Runner, por lo que usaremos el asistente de **CodePipeline**:

1.  Buscá **CodePipeline** en la consola de AWS.
2.  Creá una nueva tubería (Pipeline).
3.  **Source:** Seleccioná **GitHub (Version 2)** y conectá tu cuenta y repositorio.
4.  **Build:** Podés saltar este paso (Skip build stage) ya que Beanstalk construirá la imagen Docker por nosotros.
5.  **Deploy:** Seleccioná **AWS Elastic Beanstalk**, tu aplicación `erp-cloud` y tu entorno `erp-cloud-env`.

---

## Paso 5 — Verificar el despliegue

Una vez que el pipeline termine y Beanstalk muestre el estado **Health: OK**, te dará una URL similar a:

```
http://erp-cloud-env.eba-xxxx.us-east-1.elasticbeanstalk.com
```

Para verificar:
```
GET http://erp-cloud-env.eba-xxxx.us-east-1.elasticbeanstalk.com/
```

> **Nota:** Por defecto Beanstalk usa HTTP. Para HTTPS deberás configurar un certificado en AWS Certificate Manager (ACM) y adjuntarlo al Load Balancer creado por Beanstalk.

---

## Comparación: Elastic Beanstalk vs App Runner

| Característica | App Runner | Elastic Beanstalk |
|---|---|---|
| **Abstracción** | Muy alta (No ves servidores) | Media (Ves las EC2 y el Balanceador) |
| **Control** | Limitado | Total (SSH, Configuración de red) |
| **Costo** | Basado en recursos | Basado en recursos (EC2) |
| **Dificultad** | Muy fácil | Moderada |

---

## Solución de problemas

- **Error de permisos:** Asegurate de que el `aws-elasticbeanstalk-ec2-role` tenga permisos para leer de S3 y permisos básicos de ejecución.
- **Health degraded:** Revisá los logs en la sección **Logs -> Request Logs** de Beanstalk. Generalmente es por una `DATABASE_URL` mal configurada o porque el contenedor no arrancó en el puerto `8080`.
