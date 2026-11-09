# Arquitectura y Especificación Detallada por Fases: Ecosistema SOFI y Portales B2B

Documento técnico descriptivo que consolida la arquitectura implementada en las 5 plantillas de CloudFormation (`implementacion/`), detallando la topología de red, políticas de seguridad, persistencia relacional aislada, cómputo en contenedores Fargate, estación de desarrollo y balanceo de carga HTTPS.

---

## Matriz Resumen de Fases y Componentes

| Fase | Archivo CloudFormation | Dominio Arquitectónico | Componentes Clave |
| :--- | :--- | :--- | :--- |
| **Fase 1** | `01-networking-vpc.yaml` | Redes y Alta Disponibilidad | VPC `10.0.0.0/16`, 7 subredes Multi-AZ, Internet Gateway, S3 Gateway Endpoint. |
| **Fase 2** | `02-security-iam.yaml` | Seguridad e Identidad (PoLP) | Roles IAM (`EC2Dev`, `EcsTaskExecution`, `EcsTask`), Security Groups en capas, NACLs. |
| **Fase 3** | `03-database-storage.yaml` | Persistencia y Storage | 3 RDS PostgreSQL 16 (`db.t3.micro`), 3 Secretos en Secrets Manager, S3 Glacier, EFS `/workspace`. |
| **Fase 4** | `04-compute-ecs.yaml` | Cómputo ECS y EC2 Dev | 7 Repositorios ECR, Clúster ECS, Task Definitions Fargate, EC2 Dev (Zero-SSH, SSM, Neovim/Tmux). |
| **Fase 5** | `05-alb-monitoring.yaml` | Balanceo, DNS y Monitoreo | Certificado ACM Wildcard, ALB público, Enrutamiento por Host Header, Route 53, Auto Scaling, SNS. |

---

## 1. Fase 1 — Red y Topología Base (`01-networking-vpc.yaml`)

### 1.1 VPC y Bloques CIDR
* **VPC:** Bloque `10.0.0.0/16` desplegado en la región `us-east-1`.
* **Soporte DNS:** Habilitados `EnableDnsSupport` y `EnableDnsHostnames` para la resolución interna de servicios y endpoints.

### 1.2 Segmentación Multi-AZ (7 Subredes)
* **Subredes Públicas (Capa Perimetral / ALB):**
  * `PublicSubnetA`: `10.0.1.0/24` (AZ `us-east-1a`).
  * `PublicSubnetB`: `10.0.2.0/24` (AZ `us-east-1b`).
  * Ruteo directo al `InternetGateway`.
* **Subredes Privadas de Aplicación (Capa de Cómputo Fargate & EFS):**
  * `PrivateAppSubnetA`: `10.0.11.0/24` (AZ `us-east-1a`).
  * `PrivateAppSubnetB`: `10.0.12.0/24` (AZ `us-east-1b`).
  * Sin asignación de IP pública (`MapPublicIpOnLaunch: false`).
* **Subred Privada de Desarrollo (Estación EC2 Practicantes):**
  * `PrivateDevSubnetA`: `10.0.21.0/24` (AZ `us-east-1a`).
  * Aislamiento de workstations sin exposición perimetral.
* **Subredes Aisladas de Base de Datos (Persistencia RDS):**
  * `IsolatedDbSubnetA`: `10.0.31.0/24` (AZ `us-east-1a`).
  * `IsolatedDbSubnetB`: `10.0.32.0/24` (AZ `us-east-1b`).
  * Asociadas al recurso `DBSubnetGroup` sin tabla de ruteo hacia Internet Gateway (aislamiento criptográfico y de red).

### 1.3 VPC Endpoints
* **S3 Gateway Endpoint:** Asociado a todas las tablas de enrutamiento privadas para tráfico directo hacia Amazon S3 sin costos de transferencia por NAT Gateway.

---

## 2. Fase 2 — Seguridad y Control de Acceso (`02-security-iam.yaml`)

### 2.1 Roles IAM (Principio de Menor Privilegio - PoLP)
* **`EC2DevWorkstationRole` / Instance Profile:**
  * Política administrada `AmazonSSMManagedInstanceCore` para acceso 100% interactivo mediante **AWS Systems Manager Session Manager** (sin abrir puerto 22 SSH ni compartir archivos `.pem`).
  * Permisos granulares de montaje EFS (`elasticfilesystem:ClientMount`, `elasticfilesystem:ClientWrite`).
  * Permiso de lectura/escritura en el bucket de SOFI en S3.
* **`EcsTaskExecutionRole`:**
  * Rol del plano de control de ECS para descarga de imágenes de ECR, escritura de logs en CloudWatch (`/ecs/...`) y resolución segura de credenciales en AWS Secrets Manager.
* **`EcsTaskRole`:**
  * Rol del contenedor en tiempo de ejecución. Permite a la API NestJS generar **Presigned URLs** y leer/escribir objetos bajo el prefijo `lms-media/` en S3 sin necesidad de credenciales estáticas (`AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`) en el código.

### 2.2 Security Groups Encadenados (Defensa en Profundidad)
* **`AlbSecurityGroup`:** Permite tráfico entrante HTTP (`:80`) y HTTPS (`:443`) desde `0.0.0.0/0`.
* **`FargateSecurityGroup`:** Acepta tráfico en el puerto `3000` **únicamente** si proviene del `AlbSecurityGroup`.
* **`RdsSecurityGroup`:** Permite tráfico PostgreSQL (`:5432`) **exclusivamente** desde `FargateSecurityGroup` y `DevSecurityGroupId`.
* **`DevSecurityGroupId`:** Cero puertos de entrada autorizados desde Internet. Toda la comunicación es saliente hacia los endpoints de SSM y repositorios.
* **`EfsSecurityGroupId`:** Acepta tráfico NFS (`:2049`) únicamente desde las subredes de aplicación y desarrollo.

---

## 3. Fase 3 — Persistencia Relacional y Almacenamiento (`03-database-storage.yaml`)

### 3.1 Tres Instancias Amazon RDS PostgreSQL 16 Dedicadas
Alineadas con la arquitectura aprobada de 3 bases de datos independientes sobre hardware `db.t3.micro`:
1. **`PostgresDBInstanceSofi`:** Base de datos `sofi_db`, usuario maestro `sofi_admin`.
2. **`PostgresDBInstanceReflexo`:** Base de datos `reflexo_db`, usuario maestro `reflexo_admin`.
3. **`PostgresDBInstanceArteIdeas`:** Base de datos `arteideas_db`, usuario maestro `arteideas_admin`.
* **Configuración del Motor:**
  * Versión: PostgreSQL 16.3.
  * Disco SSD `gp3` con 20 GB asignados inicialmente y *Storage Autoscaling* hasta 100 GB.
  * `DBParameterGroup` con parámetro `rds.force_ssl = 1` forzando conexiones cifradas TLS/SSL en tránsito.
  * `DeletionProtection: false` para agilizar la destrucción controlada de recursos tras la presentación.

### 3.2 Gestión de Secretos en AWS Secrets Manager
* **Secretos Independientes:**
  * `apm-sofi-prod/rds/sofi/credentials`
  * `apm-sofi-prod/rds/reflexo/credentials`
  * `apm-sofi-prod/rds/arteideas/credentials`
* Generación criptográfica aleatoria de contraseñas de 16 caracteres excluyendo símbolos conflictivos (`/@" \`).

### 3.3 Amazon S3 y Jerarquía de Storage con Glacier
* **Bucket S3 Privado (`apm-sofi-storage-*`):**
  * Bloqueo público total (`BlockPublicAcls`, `BlockPublicPolicy`, `IgnorePublicAcls`, `RestrictPublicBuckets`).
  * Encriptación Server-Side obligatoria con algoritmo AES-256 (`aws:kms` o `AES256`).
  * Bucket Policy que deniega explícitamente cualquier petición no cifrada (`aws:SecureTransport: 'false'`).
  * **Ciclo de Vida (Lifecycle Rules):**
    * Prefijo `lms-media/`: Transición a **S3 Standard-IA** a los 60 días.
    * Prefijo `backups/`: Transición a **S3 Glacier Flexible Retrieval** a los 90 días y expiración automática definitiva a los 365 días.

### 3.4 Amazon EFS para Estaciones de Trabajo
* **Sistema de Archivos Elástico (`SharedFileSystem`):**
  * Cifrado en reposo con KMS.
  * Puntos de montaje (Mount Targets) en `PrivateAppSubnetA` y `PrivateAppSubnetB`.
  * **Access Point (`/workspace`):** Configurado con POSIX UID `1000` y GID `1000` con permisos `0755` para que los practicantes compartan plantillas de código sin conflicto de permisos.
  * Transición automática a almacenamiento *Infrequent Access (IA)* tras 30 días de inactividad.

---

## 4. Fase 4 — Cómputo ECS Fargate y EC2 Dev Workstation (`04-compute-ecs.yaml`)

### 4.1 Repositorios Amazon ECR
Siete repositorios privados con escaneo de seguridad en push (`ScanOnPush: true`) y política de retención para conservar únicamente las últimas 5 imágenes:
1. `apm-sofi-prod-sofi-frontend`
2. `apm-sofi-prod-sofi-backend`
3. `apm-sofi-prod-sofi-discord-bot`
4. `apm-sofi-prod-reflexo-frontend`
5. `apm-sofi-prod-reflexo-backend`
6. `apm-sofi-prod-arteideas-frontend`
7. `apm-sofi-prod-arteideas-backend`

### 4.2 Clúster Amazon ECS y Definiciones de Tareas
* **Clúster ECS:** `apm-sofi-prod-cluster` con Container Insights habilitado y soporte para Fargate y Fargate Spot.
* **Patrón de Tareas Multi-Contenedor (Red `awsvpc`):**
  * **SOFI Platform (`sofi-task`):** Contenedor Frontend (:3000) + Contenedor Backend (:8080) + Contenedor Bot Discord.
  * **Reflexo Perú (`reflexo-task`):** Contenedor Frontend (:3000) + Contenedor Backend (:8080).
  * **Arte & Ideas (`arteideas-task`):** Contenedor Frontend (:3000) + Contenedor Backend (:8080).
  * **Ventaja Arquitectónica:** Al ejecutarse dentro del mismo pod Fargate, Next.js se comunica internamente con NestJS a través de `http://localhost:8080` sin latencia adicional ni necesidad de Service Discovery privado.
  * **Inyección de Secretos:** Las contraseñas de PostgreSQL se leen dinámicamente desde Secrets Manager hacia la variable `DB_PASSWORD` en cada contenedor.

### 4.3 Estación de Trabajo Amazon EC2 Dev Workstation
* **Instancia:** `t3.micro` ejecutando Amazon Linux 2023 con volumen EBS `gp3` de 25 GB cifrado.
* **Conexión Zero-SSH:** Sin puerto 22 abierto. Conexión interactiva mediante **AWS Systems Manager Session Manager** (consola web o terminal con `aws ssm start-session`).
* **Aprovisionamiento Automatizado (`UserData`):**
  1. Actualización de paquetes base e inicio de `amazon-ssm-agent`.
  2. Instalación de Docker Engine y Docker CLI (habilitado y arrancado).
  3. Instalación de Node.js 20 LTS, npm, Python 3 y pip.
  4. Instalación de Neovim v0.10+ y preconfiguración de **LazyVim** en el home del practicante.
  5. Creación del usuario Linux `jhefry` con permisos en el grupo `docker` y `sudo`.
  6. Montaje automático persistente de Amazon EFS en `/workspace` usando TLS y el Access Point.
  7. **FinOps Preventivo:** Cron de apagado automático programado a las 23:00 UTC (18:00 hora de Lima) de lunes a viernes en `/etc/cron.d/auto-shutdown-ec2`.

---

## 5. Fase 5 — Balanceo ALB, Dominios y Monitoreo (`05-alb-monitoring.yaml`)

### 5.1 Certificado SSL/TLS en AWS Certificate Manager (ACM)
* Certificado Wildcard para `cabanillas.net.pe` y `*.cabanillas.net.pe`.
* Validación automática mediante registros DNS en la Hosted Zone de Route 53 sin intervención manual.

### 5.2 Application Load Balancer Público Multi-AZ
* Desplegado en las subredes públicas A y B.
* **Listener HTTP (:80):** Redirección permanente (código 301) hacia HTTPS (:443).
* **Listener HTTPS (:443):** Política de cifrado moderno `ELBSecurityPolicy-TLS13-1-2-2021-06`.
* **Enrutamiento por Host Header:**
  * `sofi.cabanillas.net.pe` $\rightarrow$ `TargetGroupSofi` (puerto 3000).
  * `reflexo.cabanillas.net.pe` $\rightarrow$ `TargetGroupReflexo` (puerto 3000).
  * `arteideas.cabanillas.net.pe` $\rightarrow$ `TargetGroupArteIdeas` (puerto 3000).
* **Target Groups:** Tipo `ip` con comprobaciones de estado periódicas en `/api/health`.

### 5.3 Resolución de Nombres en Route 53
Registros de alias tipo `A` que delegan el tráfico del dominio y los 3 subdominios al ALB:
* `cabanillas.net.pe` $\rightarrow$ Alias ALB
* `sofi.cabanillas.net.pe` $\rightarrow$ Alias ALB
* `reflexo.cabanillas.net.pe` $\rightarrow$ Alias ALB
* `arteideas.cabanillas.net.pe` $\rightarrow$ Alias ALB

### 5.4 Servicios ECS Fargate y Auto Scaling
* Tres servicios Fargate (`sofi-service`, `reflexo-service`, `arteideas-service`) desplegados en subredes privadas con `AssignPublicIp: DISABLED`.
* Política de autoescalado reactivo con **Application Auto Scaling** basada en la utilización media de CPU (>70%), escalando entre 1 y 4 tareas.

### 5.5 Monitoreo Proactivo y Notificaciones SNS
* Tópico SNS `apm-sofi-prod-devops-alerts` suscrito al correo `jhefrycabanillas@gmail.com`.
* **Alarma 1 (`HTTPCode_Target_5XX_Count`):** Se dispara si el ALB supera 10 errores 5XX en un periodo de 5 minutos.
* **Alarma 2 (`UnHealthyHostCount`):** Se dispara de inmediato si el Target Group detecta tareas Fargate que no responden satisfactoriamente al endpoint `/api/health`.
