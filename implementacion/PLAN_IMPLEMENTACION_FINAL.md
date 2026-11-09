# Plan de Implementación Integral: Ecosistema SOFI, Clientes B2B, CI/CD y Entorno de Desarrollo EC2

Hoja de ruta ejecutiva y técnica para completar el despliegue de los servicios productivos (SOFI y Clientes Comerciales B2B), el pipeline de automatización CI/CD y las estaciones de trabajo en Amazon EC2 para practicantes sobre AWS (`us-east-1`).

---

## Ruta Rápida de Ejecución (Quick Path)

1. **Bloque 1 — Aplicaciones (`apps/`):** Construir el simulador full-stack de **SOFI** (Web + API + S3 + RDS + Discord) y los dos portales comerciales B2B (**Reflexo Perú** y **Arte & Ideas**) con persistencia de clientes potenciales en base de datos.
2. **Bloque 2 — Infraestructura como Código (`implementacion/`):** Completar las plantillas CloudFormation de Fase 4 (`04-compute-ecs.yaml`) y Fase 5 (`05-alb-monitoring.yaml`) e integrarlas con las Fases 1, 2 y 3.
3. **Bloque 3 — Pipeline CI/CD (`.github/workflows/`):** Configurar GitHub Actions (`lint → test → build → deploy`) hacia Amazon ECR y Amazon ECS Fargate con notificaciones a Discord.
4. **Bloque 4 — Despliegue y Verificación End-to-End:** Aprovisionar los 5 stacks en AWS, publicar imágenes en ECR y validar el flujo completo en vivo (S3, RDS, Discord, Landings B2B y acceso SSM a EC2 Dev).

---

## 1. Decisiones Arquitectónicas y Aclaraciones Técnicas

| Dominio | Decisión Técnica | Justificación |
| :--- | :--- | :--- |
| **Simulador SOFI** | Aplicación Web + API REST + Bot/Webhook Discord integrada con **Amazon S3** y **Amazon RDS PostgreSQL 16**. | Permite registrar practicantes con fotografía de perfil (almacenada en S3 privado con *Presigned URLs*), persistir datos relacionales en `sofi_db` y notificar/consultar en tiempo real vía Discord. |
| **Webs Clientes B2B** | 2 Landing Pages (**Reflexo Perú** y **Arte & Ideas**) con formulario de contacto/citas y panel de registros. | Desacopladas a nivel de cómputo en tareas ECS Fargate independientes, enrutadas por el ALB (`/reflexo`, `/arteideas` o Host Header). |
| **Base de Datos Clientes** | Esquema lógico aislado (`clientes_b2b`) dentro de la instancia **Amazon RDS PostgreSQL 16** (`db.t3.micro`). | Evita el costo de una segunda instancia RDS manteniendo aislamiento lógico de tablas y erradicando la contención de múltiples motores en un mismo host. |
| **Pipeline CI/CD** | **GitHub Actions** $\rightarrow$ **Amazon ECR** $\rightarrow$ **Amazon ECS Fargate** + Webhook Discord. | Automatiza validación, construcción de imágenes Docker multi-stage con caché `type=gha`, despliegue sin tiempo de inactividad y verificación de `/api/health`. |
| **Horario EC2 Dev** | Encendido programado en horario de prácticas (160 h/mes) + apagado automático vía **EventBridge Scheduler / SSM**. | Optimización FinOps (~$2.70–$3.50 USD/mes) conservando intactos los datos en el volumen EBS `gp3` de 25 GB. |
| **Usuarios y Acceso EC2** | Grupo IAM `grp-compute-developers` + cuentas locales Linux en EC2 + conexión vía **AWS Systems Manager (SSM Session Manager)**. | Seguridad perimetral con **cero puertos de entrada abiertos** (sin puerto 22 SSH expuesto a Internet ni distribución de llaves `.pem`). |
| **Herramientas y Editor EC2** | **Neovim / LazyVim + Tmux**, Git, Node.js 20 LTS, Python 3, Docker CLI, `psql` y AWS CLI v2 preinstalados vía `UserData`. | Neovim/LazyVim + Tmux consume ~25 MiB de RAM por sesión frente a los ~500 MiB de `vscode-server`, garantizando fluidez para múltiples practicantes en instancias `t3.micro` / `t3.small`. |
| **Clonado de Proyectos y GitHub** | Plantillas base compartidas en **Amazon EFS (`/workspace`)** + autenticación individual con **GitHub CLI (`gh auth login`)** o llave SSH por usuario. | Permite iniciar prácticas al instante copiando desde `/workspace` sin exponer credenciales globales, y exige identidad individual de cada practicante al hacer `git push` a la organización. |

---

## 2. Detalle de los Bloques de Implementación

### Bloque 1: Aplicaciones Funcionales (`apps/`)

#### 1.1 Simulador de Plataforma SOFI (`apps/sofi-app/`)
* **Módulo Web y Backend (`/`, `/api/*`):**
  - Formulario de registro de practicantes: Nombre completo, carrera/sede SENATI, especialidad, turno y carga de fotografía de perfil.
  - **Almacenamiento S3:** Subida de imágenes al bucket privado `SofiStorageBucket` bajo el prefijo `lms-media/` utilizando el rol de tarea `EcsTaskRole` (sin credenciales estáticas en código) y lectura segura mediante **Presigned URLs**.
  - **Persistencia RDS:** Almacenamiento y listado en tiempo real desde la tabla `practicantes` en PostgreSQL (`sofi_db`).
  - **Integración Discord:** Envío automático de notificación enriquecida (*Embed*) al canal de Discord al registrar un practicante o asistencia, acompañado de comandos de consulta desde el bot hacia RDS.
  - **Health Check:** Endpoint `GET /api/health` que valida el estado del servicio y la conectividad con RDS.

#### 1.2 Portales Comerciales B2B (`apps/clientes-b2b/`)
* **Landing 1 — Reflexo Perú (`/reflexo`):**
  - Portal institucional de salud integrativa y reflexoterapia con formulario de solicitud de citas y registro de pacientes/clientes.
* **Landing 2 — Arte & Ideas (`/arteideas`):**
  - Portal comercial de estudio fotográfico y producción audiovisual con formulario de cotización de sesiones y eventos.
* **Persistencia en Base de Datos (`/api/clientes/leads`):**
  - Almacenamiento de las solicitudes de ambos portales en el esquema `clientes_b2b` (tabla `leads_comerciales`) en RDS PostgreSQL, diferenciando el origen (`REFLEXO_PERU` o `ARTE_IDEAS`) y exponiendo una vista de verificación para la demostración.

---

### Bloque 2: Infraestructura como Código (`implementacion/`)

| Fase | Archivo CloudFormation | Estado | Recursos Principales |
| :--- | :--- | :---: | :--- |
| **Fase 1** | `implementacion/01-networking/01-networking-vpc.yaml` | Completado | VPC `10.0.0.0/16`, 7 subredes Multi-AZ, IGW, Route Tables, S3 Gateway Endpoint, `DBSubnetGroup`. |
| **Fase 2** | `implementacion/02-security/02-security-iam.yaml` | Completado | 5 Grupos IAM PoLP, Usuarios de equipo, Roles (`EC2DevWorkstationRole`, `EcsTaskExecutionRole`, `EcsTaskRole`), Security Groups encadenados y NACLs. |
| **Fase 3** | `implementacion/03-database-storage/03-database-storage.yaml` | Completado | Secretos en Secrets Manager, RDS PostgreSQL 16 (`gp3`), Bucket S3 con Lifecycle a Standard-IA y Glacier, Amazon EFS Multi-AZ con Access Point `/workspace`. |
| **Fase 4** | `implementacion/04-compute-ecs/04-compute-ecs.yaml` | Por crear | Repositorios ECR, Clúster ECS con Container Insights, Task Definitions Fargate (`sofi-app` y `clientes-b2b`), Estación EC2 Dev con `UserData` (usuarios Linux, montaje EFS `/workspace`, Neovim/LazyVim, Tmux, Git, Docker CLI) y programación de apagado automático. |
| **Fase 5** | `implementacion/05-alb-monitoring/05-alb-monitoring.yaml` | Por crear | Application Load Balancer (ALB) público Multi-AZ, Target Groups, Listener Rules por ruta/host, Servicios ECS con Application Auto Scaling (2 a 6 tareas) y alarmas en CloudWatch + SNS. |

---

### Bloque 3: Automatización CI/CD (`.github/workflows/ci-cd-aws.yml`)

1. **Etapa `lint-and-test`:** Verificación de sintaxis, dependencias y pruebas unitarias/salud de `apps/sofi-app` y `apps/clientes-b2b`.
2. **Etapa `build-and-push-ecr`:** Autenticación en AWS, construcción de imágenes Docker optimizadas con caché de capas en GitHub Actions y publicación en **Amazon ECR** etiquetadas con el SHA del commit y versión semántica.
3. **Etapa `deploy-ecs`:** Actualización declarativa de los servicios en **Amazon ECS Fargate**, espera de estabilización del servicio (`aws ecs wait services-stable`), comprobación de `GET /api/health` a través del ALB y notificación del resultado al canal de Discord.

---

### Bloque 4: Flujo Operativo de Practicantes en EC2 Dev

1. **Encendido y Horario:** La instancia EC2 de desarrollo opera dentro de la ventana horaria definida y se apaga automáticamente fuera de turno para control de costos.
2. **Conexión Cero-SSH:** El practicante inicia sesión con su usuario IAM y abre su terminal mediante **AWS Systems Manager Session Manager** (vía consola web o AWS CLI sobre HTTPS `:443`).
3. **Entorno de Trabajo:** Cambia a su usuario local de Linux, inicia una sesión persistente con `tmux` y edita código con **Neovim / LazyVim**.
4. **Proyectos y Control de Versiones:**
   - Copia plantillas base directamente desde el montaje compartido **Amazon EFS** en `/workspace`.
   - Autentica su cuenta personal de GitHub mediante `gh auth login` (o llave SSH propia en `~/.ssh/`) para clonar repositorios privados de la organización y enviar Pull Requests bajo su propia autoría.

---

## Lista de Verificación para la Presentación (Checklist)

- [ ] **Stack 01, 02 y 03 desplegados** en `us-east-1` (VPC, IAM, Security Groups, RDS PostgreSQL 16, S3 y EFS activos).
- [ ] **Imágenes Docker publicadas en Amazon ECR** para `sofi-app` y `clientes-b2b`.
- [ ] **Stack 04 y 05 desplegados** (ECS Fargate corriendo detrás del ALB Multi-AZ + EC2 Dev activa por SSM).
- [ ] **Prueba en vivo SOFI:** Registro de practicante con foto subida a S3, fila creada en RDS y alerta recibida en Discord.
- [ ] **Prueba en vivo Clientes B2B:** Envío de formulario en las landings de *Reflexo Perú* y *Arte & Ideas* persistiendo en RDS PostgreSQL.
- [ ] **Prueba en vivo EC2 Dev:** Conexión por SSM Session Manager sin puerto 22, verificación de `/workspace` en EFS y apertura de Neovim/LazyVim.
- [ ] **Prueba de CI/CD:** Ejecución del pipeline en GitHub Actions actualizando los contenedores en ECS Fargate automáticamente.
