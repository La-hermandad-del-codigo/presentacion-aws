# Arquitectura y Especificación Detallada por Fases: Ecosistema SOFI y Portales B2B

Documento técnico descriptivo que consolida la arquitectura final implementada en las **6 plantillas de CloudFormation** (`implementacion/`), detallando la topología de red con NAT Gateway, políticas de seguridad IAM + ABAC, persistencia relacional en 3 instancias RDS, cómputo serverless en ECS Fargate, balanceo de carga HTTPS y la plantilla reutilizable de aprovisionamiento efímero por practicante sobre procesadores AWS Graviton (`t4g.small` ARM64).

---

## Matriz Resumen de Fases y Componentes

| Fase | Archivo CloudFormation | Dominio Arquitectónico | Componentes Clave |
| :--- | :--- | :--- | :--- |
| **Fase 1** | `01-networking-vpc.yaml` | Redes y Alta Disponibilidad | VPC `10.0.0.0/16`, 7 subredes Multi-AZ, Internet Gateway, NAT Gateway Single-AZ, S3 Gateway Endpoint. |
| **Fase 2** | `02-security-iam.yaml` | Seguridad e Identidad (PoLP) | Grupos IAM (incluyendo `grp-platform-admins`), Usuarios del equipo, Roles (`EC2Dev`, `EcsTaskExecution`, `EcsTask`), Security Groups y NACLs. |
| **Fase 3** | `03-database-storage.yaml` | Persistencia y Storage | 3 RDS PostgreSQL 16 (`db.t3.micro`), 3 Secretos en Secrets Manager, S3 Glacier, EFS `/workspace`. |
| **Fase 4** | `04-compute-ecs.yaml` | Cómputo Serverless ECS Fargate | 7 Repositorios ECR, Clúster ECS con Container Insights, CloudWatch Logs y 3 Task Definitions Multi-Contenedor. |
| **Fase 5** | `05-alb-monitoring.yaml` | Balanceo, DNS y Monitoreo | Certificado ACM Wildcard, ALB público, Enrutamiento por Host Header, Route 53, Auto Scaling, CloudWatch + SNS. |
| **Fase 6** | `06-onboarding-practicante.yaml` | Sandbox por Practicante (Reutilizable) | Usuario IAM con ABAC (`Owner=${aws:username}`), EC2 Graviton `t4g.small` ARM64 (LazyVim, Lazygit, Lazysql, `gh`), y 2 subdominios HTTPS (`<nombre>-web` y `<nombre>-api`). |

---

## 1. Fase 1 — Red y Topología Base (`01-networking-vpc.yaml`)

### 1.1 VPC y Bloques CIDR
* **VPC:** Bloque `10.0.0.0/16` desplegado en la región `us-east-1`.
* **Soporte DNS:** Habilitados `EnableDnsSupport` y `EnableDnsHostnames` para la resolución interna de servicios y endpoints.

### 1.2 Segmentación Multi-AZ (7 Subredes)
* **Subredes Públicas (Capa Perimetral / ALB & NAT Gateway):**
  * `PublicSubnetA`: `10.0.1.0/24` (AZ `us-east-1a`).
  * `PublicSubnetB`: `10.0.2.0/24` (AZ `us-east-1b`).
  * Ruteo directo al `InternetGateway`.
* **Subredes Privadas de Aplicación (Capa de Cómputo Fargate & EFS):**
  * `PrivateAppSubnetA`: `10.0.10.0/24` (AZ `us-east-1a`).
  * `PrivateAppSubnetB`: `10.0.20.0/24` (AZ `us-east-1b`).
  * Sin asignación de IP pública (`MapPublicIpOnLaunch: false`).
* **Subred Privada de Desarrollo (Estaciones EC2 de Practicantes):**
  * `PrivateDevSubnetA`: `10.0.30.0/24` (AZ `us-east-1a`).
  * Aislamiento de workstations sin exposición perimetral ni IP pública.
* **Subredes Aisladas de Base de Datos (Persistencia RDS):**
  * `IsolatedDbSubnetA`: `10.0.100.0/24` (AZ `us-east-1a`).
  * `IsolatedDbSubnetB`: `10.0.101.0/24` (AZ `us-east-1b`).
  * Asociadas al recurso `DBSubnetGroup` sin tabla de ruteo hacia Internet Gateway ni NAT Gateway (aislamiento criptográfico y de red).

### 1.3 NAT Gateway (FinOps) y VPC Endpoints
* **NAT Gateway Single-AZ (`PublicSubnetA`):** Provee salida controlada a Internet (`0.0.0.0/0`) en `PrivateRouteTable` para que las tareas Fargate (`AssignPublicIp: DISABLED`) descarguen imágenes de ECR, lean secretos, conecten el bot de Discord, y para que las instancias EC2 de practicantes se registren en SSM Session Manager e instalen herramientas desde GitHub.
* **S3 Gateway Endpoint:** Asociado a `PrivateRouteTable` para tráfico directo hacia Amazon S3 sin pasar por el NAT Gateway ni generar cargos de transferencia.

---

## 2. Fase 2 — Seguridad y Control de Acceso (`02-security-iam.yaml`)

### 2.1 Grupos y Usuarios IAM Base del Equipo
* **Cuentas Administradoras (`grp-platform-admins` con `AdministratorAccess`):**
  * **`jhefry`:** Pertenece a `grp-iam-governance` y `grp-platform-admins` con permisos completos de administrador.
  * **`gustavo-tuesta-admin`:** Segunda cuenta dedicada de administración general para Gustavo Tuesta.
* **Cuentas Operativas por Dominio (Menor Privilegio - PoLP):**
  * **`gustavo-tuesta`:** `grp-networking-security` (VPC, Subredes, Security Groups y NACLs).
  * **`sandro-chavez`:** `grp-database-storage` (RDS, S3 y EFS).
  * **`edward-montero`:** `grp-compute-developers` (ECS, ECR y Cómputo).
  * **`carlos-gago`:** `grp-cloudops-prod` (ALB, Route 53, ACM y CloudWatch).
  * **`jherson-apaza`:** `grp-iam-governance` + `grp-compute-developers`.

### 2.2 Roles IAM de Servicios
* **`EC2DevWorkstationRole` / Instance Profile (`apm-sofi-prod-profile-ec2-dev`):**
  * Política administrada `AmazonSSMManagedInstanceCore` para acceso interactivo mediante **AWS Systems Manager Session Manager** (cero puertos SSH abiertos).
  * Permisos de montaje EFS (`elasticfilesystem:ClientMount`, `elasticfilesystem:ClientWrite`) y lectura en S3.
* **`EcsTaskExecutionRole`:**
  * Rol del plano de control de ECS para descarga de imágenes de ECR, escritura de logs en CloudWatch (`/ecs/...`) y lectura de credenciales en AWS Secrets Manager.
* **`EcsTaskRole`:**
  * Rol del contenedor en tiempo de ejecución. Permite a la API NestJS generar **Presigned URLs** y leer/escribir objetos bajo el prefijo `lms-media/` en S3 sin credenciales estáticas en código.

### 2.3 Security Groups Encadenados (Defensa en Profundidad)
* **`AlbSecurityGroup`:** Permite tráfico entrante HTTP (`:80`) y HTTPS (`:443`) desde `0.0.0.0/0`, y salida hacia los puertos `3000` y `8080` dentro de la VPC.
* **`FargateSecurityGroup`:** Acepta tráfico en los puertos `3000` y `8080` **únicamente** desde `AlbSecurityGroup`.
* **`DevWorkstationSecurityGroup` (`DevSecurityGroupId`):**
  * Cero puertos SSH (`:22`) abiertos.
  * Acepta tráfico en los puertos `3000` (Frontend preview) y `8080` (Backend preview) **exclusivamente** desde el `AlbSecurityGroup`.
  * Permite salida hacia HTTPS (`:443`), HTTP (`:80`), SSH hacia GitHub (`:22`), NFS EFS (`:2049`) y PostgreSQL (`:5432`).
* **`RdsSecurityGroup`:** Permite tráfico PostgreSQL (`:5432`) **exclusivamente** desde `FargateSecurityGroup` y `DevWorkstationSecurityGroup`.
* **`EfsSecurityGroupId`:** Acepta tráfico NFS (`:2049`) únicamente desde `FargateSecurityGroup` y `DevWorkstationSecurityGroup`.

---

## 3. Fase 3 — Persistencia Relacional y Almacenamiento (`03-database-storage.yaml`)

### 3.1 Tres Instancias Amazon RDS PostgreSQL 16 Dedicadas
Tres bases de datos independientes sobre instancias `db.t3.micro`:
1. **`PostgresDBInstanceSofi`:** Base de datos `sofi_db`, usuario maestro `sofi_admin`.
2. **`PostgresDBInstanceReflexo`:** Base de datos `reflexo_db`, usuario maestro `reflexo_admin`.
3. **`PostgresDBInstanceArteIdeas`:** Base de datos `arteideas_db`, usuario maestro `arteideas_admin`.
* **Configuración del Motor:**
  * Versión: PostgreSQL `"16"` (selecciona automáticamente la versión menor activa en `us-east-1`).
  * Disco SSD `gp3` con 20 GB iniciales y *Storage Autoscaling* hasta 100 GB.
  * `DBParameterGroup` con parámetro `rds.force_ssl = 1` forzando conexiones cifradas TLS/SSL en tránsito.
  * `DeletionProtection: false` por defecto para facilitar la limpieza de recursos tras la presentación.

### 3.2 Gestión de Secretos en AWS Secrets Manager
* **Secretos Independientes:**
  * `apm-sofi-prod/rds/sofi/credentials`
  * `apm-sofi-prod/rds/reflexo/credentials`
  * `apm-sofi-prod/rds/arteideas/credentials`
* Generación criptográfica aleatoria de contraseñas de 16 caracteres.

### 3.3 Amazon S3 y Jerarquía de Storage con Glacier
* **Bucket S3 Privado (`apm-sofi-storage-*`):**
  * Bloqueo público total, cifrado AES-256 y Bucket Policy que deniega conexiones sin TLS (`aws:SecureTransport: 'false'`).
  * **Lifecycle Rules:** Prefijo `lms-media/` migra a **S3 Standard-IA** a los 60 días; prefijo `backups/` migra a **S3 Glacier Flexible Retrieval** a los 90 días y expira a los 365 días.

### 3.4 Amazon EFS para Estaciones de Trabajo
* **Sistema de Archivos Elástico (`SharedFileSystem`):**
  * Cifrado en reposo, Mount Targets en `PrivateAppSubnetA` y `PrivateAppSubnetB`, y **Access Point (`/workspace`)** con POSIX UID/GID `1000`.

---

## 4. Fase 4 — Cómputo Serverless ECS Fargate y ECR (`04-compute-ecs.yaml`)

### 4.1 Repositorios Amazon ECR
Siete repositorios privados con escaneo de vulnerabilidades (`ScanOnPush: true`) y retención de las últimas 5 imágenes:
1. `apm-sofi-prod-sofi-frontend`
2. `apm-sofi-prod-sofi-backend`
3. `apm-sofi-prod-sofi-discord-bot`
4. `apm-sofi-prod-reflexo-frontend`
5. `apm-sofi-prod-reflexo-backend`
6. `apm-sofi-prod-arteideas-frontend`
7. `apm-sofi-prod-arteideas-backend`

### 4.2 Clúster Amazon ECS y Definiciones de Tareas Fargate (100% Serverless)
* **Clúster ECS:** `apm-sofi-prod-cluster` con Container Insights habilitado y soporte para Fargate y Fargate Spot.
* **Patrón de Tareas Multi-Contenedor (Red `awsvpc`):**
  * **SOFI Platform (`sofi-task`):** Frontend (:3000) + Backend (:8080) + Bot Discord (con soporte para `DISCORD_WEBHOOK_URL` y `DISCORD_BOT_TOKEN`).
  * **Reflexo Perú (`reflexo-task`):** Frontend (:3000) + Backend (:8080).
  * **Arte & Ideas (`arteideas-task`):** Frontend (:3000) + Backend (:8080).
  * **Comunicación Localhost:** Al compartir el mismo namespace de red `awsvpc` dentro de cada tarea, Next.js enruta `/api/*` hacia `http://localhost:8080` sin latencia externa.
  * **Inyección de Secretos:** `DB_PASSWORD` se inyecta dinámicamente desde Secrets Manager en el arranque del contenedor.

---

## 5. Fase 5 — Balanceo ALB, Dominios y Monitoreo (`05-alb-monitoring.yaml`)

### 5.1 Certificado SSL/TLS en AWS Certificate Manager (ACM)
* Certificado Wildcard para `cabanillas.net.pe` y `*.cabanillas.net.pe` validado por DNS en Route 53.

### 5.2 Application Load Balancer Público Multi-AZ
* **Listener HTTP (:80):** Redirección permanente (HTTP 301) hacia HTTPS (:443).
* **Listener HTTPS (:443):** Política `ELBSecurityPolicy-TLS13-1-2-2021-06` (exportado como `${EnvironmentName}-HttpsListenerArn` para inyectar reglas de practicantes desde la Fase 6).
* **Enrutamiento Productivo por Host Header:**
  * `sofi.cabanillas.net.pe` $\rightarrow$ `TargetGroupSofi` (:3000).
  * `reflexo.cabanillas.net.pe` $\rightarrow$ `TargetGroupReflexo` (:3000).
  * `arteideas.cabanillas.net.pe` $\rightarrow$ `TargetGroupArteIdeas` (:3000).

### 5.3 Registros Route 53, Servicios ECS y Monitoreo
* Registros Alias `A` para `cabanillas.net.pe`, `sofi.`, `reflexo.` y `arteideas.`.
* Tres servicios ECS Fargate con `DependsOn` explícito hacia el Listener HTTPS, Auto Scaling por CPU (>70%) y alarmas CloudWatch (`5XX` y `UnHealthyHostCount`) conectadas a SNS (`jhefrycabanillas@gmail.com`).

---

## 6. Fase 6 — Plantilla Reutilizable de Onboarding de Practicante (`06-onboarding-practicante.yaml`)

Plantilla autónoma (ejecutable desde **Amazon S3 URL** o como Producto en **AWS Service Catalog**) que recibe el nombre del practicante (`PracticanteUsername`, ej. `pedro`) y aprovisiona su entorno aislado de punta a punta:

### 6.1 Usuario IAM con Aislamiento ABAC (`Owner = ${aws:username}`)
* Crea el usuario IAM `<practicante>` con contraseña inicial para la consola de AWS.
* Adjunta una política **ABAC (Attribute-Based Access Control)** que exige la condición `ssm:resourceTag/Owner = "${aws:username}"` y `ec2:ResourceTag/Owner = "${aws:username}"`.
* **Garantía de Seguridad:** El practicante solo puede abrir sesión SSM, encender, apagar o reiniciar la instancia EC2 que tenga su propio nombre en el Tag `Owner`. Cualquier intento sobre instancias de otros compañeros devuelve `AccessDenied`.

### 6.2 Estación de Trabajo EC2 AWS Graviton (`t4g.small` ARM64)
* **Hardware:** Instancia `t4g.small` (2 vCPU, **2 GiB RAM**, procesador AWS Graviton2 `arm64`, apta para la capa gratuita) con disco `gp3` de 25 GB cifrado en `PrivateDevSubnetA`.
* **Acceso Directo por SSM:** Al conectarse por Session Manager desde el navegador, cambia automáticamente al usuario local `/home/<practicante>`.
* **Stack de Herramientas Preinstalado (`UserData` ARM64):**
  * **Editor e IDE en Terminal:** **Neovim v0.10.4 (`arm64`)** con **LazyVim** preconfigurado (`ripgrep`, `fd`, `fzf`, `gcc`, `make`).
  * **Multiplexor:** **Tmux** para dividir paneles y mantener servidores activos.
  * **Git y GitHub:** **Git** preconfigurado con `user.name "<practicante>"` y `user.email "<practicante>@senati.pe"`, **Lazygit (`arm64`)** y **GitHub CLI (`gh`)** para iniciar sesión con `gh auth login`.
  * **Bases de Datos en Terminal:** **`lazysql` (`arm64`)** (interfaz visual TUI estilo `lazygit` para explorar tablas y correr queries), **`pgcli`** (autocompletado inteligente) y **`psql`** (cliente oficial PostgreSQL 16).
  * **Runtimes:** **Docker Engine**, **Node.js 20 LTS** (`npm`) y **Python 3** (`pip`).
  * **Almacenamiento y FinOps:** Montaje automático de Amazon EFS en `/workspace/<practicante>` y cron de apagado preventivo a las 18:00 hora Perú (23:00 UTC) de lunes a viernes.

### 6.3 Dos Subdominios HTTPS Dedicados para Pruebas en Vivo
Registra la instancia EC2 en 2 Target Groups (`:3000` y `:8080`), inyecta las reglas en el Listener HTTPS del ALB y crea los registros Alias `A` en Route 53 bajo el certificado comodín `*.cabanillas.net.pe`:
* **Vista Previa Frontend (Puerto 3000):** `https://<practicante>-web.cabanillas.net.pe`
* **Vista Previa Backend / API (Puerto 8080):** `https://<practicante>-api.cabanillas.net.pe`
* Cuando el practicante termina su ciclo de prácticas, eliminar su stack en CloudFormation destruye limpiamente su usuario IAM, su instancia EC2, sus Target Groups y sus 2 subdominios.
