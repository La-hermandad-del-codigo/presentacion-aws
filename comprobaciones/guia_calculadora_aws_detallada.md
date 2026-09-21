# Manual Detallado de Configuración - AWS Pricing Calculator
**Proyecto:** Arquitectura Cloud para la Plataforma SOFI (RPsoft / SENATI)  
**Herramienta Oficial:** [AWS Pricing Calculator (calculator.aws)](https://calculator.aws/)  
**Región de despliegue:** `US East (N. Virginia)` (`us-east-1`)  
**Objetivo del documento:** Guía paso a paso, visual y descriptiva para que cualquier docente, evaluador técnico o desarrollador pueda reproducir con precisión milimétrica la estimación mensual de costos de la arquitectura base en AWS.

---

## Instrucciones Generales Previas

1. Ingresar al portal oficial: **[https://calculator.aws/](https://calculator.aws/)**.
2. Hacer clic en el botón naranja **"Create estimate"** (*Crear estimación*).
3. En la esquina superior derecha o al configurar cada servicio, verificar siempre que la región seleccionada sea **US East (N. Virginia)** / *Este de EE. UU. (Norte de Virginia)* (`us-east-1`), ya que las tarifas varían según la ubicación geográfica de los centros de datos.

---

## 1. Amazon EC2 (Servidor de Cómputo de Aplicaciones)

Este servicio proporciona la máquina virtual sobre la que se ejecutan los contenedores Docker del backend NestJS (`sofi-backend`), la interfaz Next.js (`SOFI-WEB`) y el bot de asistencia de Discord.

### Paso a paso en la calculadora:
1. En el buscador de servicios, escribir **`Amazon EC2`** y hacer clic en **`Configure`**.
2. **Location (Ubicación):**
   * *Choose a location type:* Seleccionar **`Region`**.
   * *Choose a Region:* Seleccionar **`US East (N. Virginia)`**.
3. **EC2 specifications (Especificaciones de cómputo):**
   * *Tenancy (Inquilinato):* Seleccionar **`Shared Instances`** (*Instancias compartidas estándar*).
   * *Operating system:* Seleccionar **`Linux`**.
   * *Workloads (Carga de trabajo):* Marcar el botón de radio **`Constant usage`** (*Uso constante*).
   * *Number of instances:* Ingresar **`1`**.
   * *Búsqueda de instancia:* En la barra de búsqueda escribir `t3.small` y seleccionar la fila correspondiente:
     * **vCPU:** 2
     * **Memoria RAM:** 2 GiB
     * **Rendimiento de red:** Hasta 5 Gbps
4. **Payment options (Modelo de facturación):**
   * Seleccionar la tarjeta de opción **`On-Demand`** (*Bajo demanda*).
   * En *Expected utilization (Usage)*, ingresar **`100`** y confirmar que la unidad sea **`%`** (o ingresar `730` con unidad `Hours/Month`).
5. **Secciones opcionales a omitir (Evitar duplicidad de costos):**
   * *Amazon Elastic Block Store (EBS) - optional:* **Dejar completamente vacío**. No ingresar cantidad de almacenamiento aquí, ya que el disco persistente se cotiza como un servicio independiente para mantener la coherencia fila por fila con la tabla del entregable.
   * *Detailed monitoring - optional:* **Dejar desmarcado** (`Enable monitoring` sin tilde). La monitorización estándar gratuita de 5 minutos es suficiente.
   * *Data transfer - optional:* **Dejar vacío**.
   * *Additional costs - optional:* **Dejar vacío**.

### Desglose del costo mensual:
* **Fórmula:** $730 \text{ horas} \times \$0.0208 \text{ USD/hora}$
* **Subtotal mensual EC2:** **`$15.18 USD`** *(redondeado en entregable a ~$15.20)*
* **Acción:** Hacer clic en **`Save and add service`** para continuar.

---

## 2. Amazon Elastic Block Store - EBS (Almacenamiento Persistente del Servidor)

Provee el volumen de estado sólido (SSD) adjunto a la instancia EC2 donde residen el sistema operativo Linux Ubuntu Server, las imágenes y dependencias de Docker y los volúmenes temporales de ejecución.

### Paso a paso en la calculadora:
1. En el buscador de servicios, escribir **`Amazon Elastic Block Store (EBS)`** y hacer clic en **`Configure`**.
2. **Location (Ubicación):**
   * *Choose a location type:* **`Region`**.
   * *Choose a Region:* **`US East (N. Virginia)`**.
3. **Service Settings (Configuración del disco):**
   * *Number of volumes:* Ingresar **`1`**.
   * *Average duration of volume:* ⚠️ Ingresar **`730`** con unidad **`hours per month`** *(si se deja en blanco el formulario genera un error en rojo)*.
   * *Storage for each EC2 instance (Tipo de volumen):* ⚠️ Cambiar el desplegable de `gp2` a **`General Purpose SSD (gp3)`**. El volumen `gp3` representa la tecnología moderna de AWS a $0.08/GB-mes, frente a $0.10/GB-mes del estándar antiguo `gp2`.
   * *Storage amount per volume:* Ingresar **`30`** y verificar que la unidad sea **`GB`**.
   * *General Purpose SSD (gp3) - IOPS / Throughput:* **Dejar vacíos**. La configuración base incluye 3,000 IOPS y 125 MB/s de rendimiento sin ningún costo adicional.
   * *Snapshot Frequency (Frecuencia de respaldos):* ⚠️ Cambiar a **`No snapshot storage`**. En la calculadora suele aparecer por defecto *2x Daily*; se debe seleccionar *No snapshot storage* para no generar cobros automáticos de snapshots nativos de EBS.
4. **Opciones avanzadas (Omitir):**
   * *EBS Fast Snapshot Restore:* **Dejar vacío**.
   * *EBS direct APIs for Snapshots:* **Dejar vacío**.

### Desglose del costo mensual:
* **Fórmula:** $30 \text{ GB} \times \$0.08 \text{ USD/GB-mes}$
* **Subtotal mensual EBS:** **`$2.40 USD`**
* **Acción:** Hacer clic en **`Save and add service`**.

---

## 3. Amazon RDS for PostgreSQL (Base de Datos Administrada)

Aloja el motor transaccional de PostgreSQL 16 desacoplado de la capa de cómputo, garantizando el aislamiento de fallas y la persistencia de usuarios, marcas de asistencia de practicantes y configuración de SOFI.

### Paso a paso en la calculadora:
1. En el buscador de servicios, escribir **`Amazon RDS for PostgreSQL`** y hacer clic en **`Configure`**.
2. **Location y despliegue inicial:**
   * *Region:* **`US East (N. Virginia)`**.
   * *Nodes (Cantidad de nodos):* Ingresar **`1`**.
   * *Deployment Option (Opción de despliegue):* ⚠️ Seleccionar **`Single-AZ`** *(Instancia de base de datos única)*. No seleccionar *Multi-AZ* para el presupuesto base porque duplicaría el costo de cómputo y disco.
3. **PostgreSQL instance specifications (Cómputo de BD):**
   * *Buscar instancia:* Escribir `db.t3.micro` y seleccionarla:
     * **vCPU:** 2
     * **Memoria RAM:** 1 GiB
   * *Utilization (On-Demand only):* Ingresar **`730`** con unidad **`Hours/Month`** (o `100 %Utilized/Month`).
   * *Pricing Model:* Seleccionar **`OnDemand`**.
   * *(Costo de la instancia de cómputo: $13.14 USD)*
4. **Trampas críticas a desactivar (Opciones Enterprise que inflan la factura):**
   * ⚠️ *Would you be creating an RDS Proxy...?:* Cambiar a **`No`**. *(Si se deja en Yes agrega $21.90 USD/mes innecesarios para esta carga).*
   * ⚠️ *Would you be enabling Database Insights...?:* Cambiar a **`No`**. *(Si se deja en Yes suma $18.25 USD/mes).*
   * ⚠️ *RDS Extended Support:* Cambiar a **`No`**. *(PostgreSQL 16 es una versión moderna y vigente con soporte estándar de AWS; el soporte extendido solo aplica a versiones discontinuadas como PostgreSQL 11 o 12).*
5. **Storage (Almacenamiento del motor):**
   * *Storage volume:* ⚠️ Cambiar a **`General Purpose SSD (gp3)`**.
   * *Storage amount:* Ingresar **`20`** con unidad **`GB`**.
   * *IOPS / Throughput adicionales:* **Dejar vacíos** (3,000 IOPS y 125 MB/s incluidos a $0.00).
   * *(Costo de almacenamiento: 20 GB × $0.115 USD/GB-mes = $2.30 USD. Es más alto que EBS regular porque incluye la gestión y redundancia nativa de RDS).*
6. **Backup Storage y Snapshot Export:**
   * *Additional backup storage:* **Dejar en blanco o ingresar `0 GB`**. AWS incluye almacenamiento de copias de seguridad automáticas sin costo hasta el 100% de la capacidad de la base de datos durante el periodo de retención (20 GB de disco = 20 GB de snapshots a **$0.00 USD**).
   * *Snapshot Export:* **Dejar vacío**.

### Desglose del costo mensual:
* **Cómputo (`db.t3.micro`):** `$13.14 USD`
* **Almacenamiento (20 GB `gp3`):** `$2.30 USD`
* **Copias de seguridad:** `$0.00 USD`
* **Subtotal mensual RDS:** **`$15.44 USD`**
* **Acción:** Hacer clic en **`Save and add service`**.

---

## 4. Amazon Simple Storage Service - S3 (Cursos y Respaldos)

Servicio de almacenamiento de objetos altamente escalable y duradero (99.999999999% de durabilidad) para almacenar manuales de inducción, videos didácticos del módulo LMS y copias de seguridad de la base de datos, evitando saturar el almacenamiento local del servidor.

### Paso a paso en la calculadora:
1. En el buscador de servicios, escribir **`Amazon Simple Storage Service (S3)`** y hacer clic en **`Configure`**.
2. **Location (Ubicación):**
   * *Region:* **`US East (N. Virginia)`**.
3. **Select S3 Storage classes (Selección de características):**
   * ⚠️ **Activar únicamente el interruptor:** **`S3 Standard`**.
   * Desactivar o dejar sin tilde todas las demás opciones (*S3 Intelligent-Tiering, Glacier, Data Transfer, Object Lambda, etc.*).
4. **S3 Standard feature (Parámetros de S3 Estándar):**
   * *S3 Standard storage:* Ingresar **`15`** y verificar que la unidad sea **`GB per month`**.
   * *How will data be moved into S3 Standard?:* Dejar la opción seleccionada por defecto: **`The specified amount of data is already stored in S3 Standard`** (*La cantidad de datos especificada ya está almacenada en S3 Standard*).
   * *PUT, COPY, POST, LIST requests:* Ingresar **`1000`** solicitudes al mes.
   * *GET, SELECT, and all other requests:* Ingresar **`10000`** solicitudes al mes.
   * *Data returned / scanned by S3 Select:* **Dejar vacíos**.

### Desglose del costo mensual:
* **Almacenamiento (15 GB × $0.023):** `$0.345 USD`
* **Peticiones PUT/POST (1,000 × $0.000005):** `$0.005 USD`
* **Peticiones GET (10,000 × $0.0000004):** `$0.004 USD`
* **Subtotal mensual S3:** **`$0.35 USD`** *(redondeo matemático oficial de $0.354)*
* **Acción:** Hacer clic en **`Save and add service`**.

---

## 5. AWS Systems Manager - SSM (Administración Remota Segura)

Reemplaza el acceso administrativo mediante SSH tradicional por túneles cifrados y autenticados con credenciales IAM mediante **SSM Session Manager**, permitiendo cerrar por completo el puerto 22 a Internet y mitigar ataques de fuerza bruta.

### Paso a paso en la calculadora:
1. En el buscador de servicios, escribir **`AWS Systems Manager`** y hacer clic en **`Configure`**.
2. **Location (Ubicación):**
   * *Region:* **`US East (N. Virginia)`**.
3. **Parámetros del servicio:**
   * *On-Premises Instance Management:* **Dejar en `0`** o vacío. Solo aplica para servidores físicos fuera de AWS.
   * *Parameter Store > Standard parameters:* Ingresar **`10`** o dejar vacío. Los primeros 10,000 parámetros estándar para almacenar variables de entorno y credenciales son 100% gratuitos.
   * *Parameter Store > Advanced parameters:* **Dejar vacío**. Los parámetros avanzados tienen un costo de $0.05 c/u y no se requieren para esta solución.
   * *Automation / Incident Manager / AppConfig:* **Dejar vacíos**.

### Desglose del costo mensual:
* **Licencia de gestión de instancias EC2:** `$0.00 USD` (Servicio nativo incluido sin costo).
* **Subtotal mensual Systems Manager:** **`$0.00 USD`**
* **Acción:** Hacer clic en **`Save and add service`**.

---

## 6. Amazon CloudWatch (Monitoreo, Métricas y Alarmas)

Monitorea la disponibilidad del backend y del bot de asistencia, capturando logs de ejecución de Docker e informando de manera proactiva ante caídas o saturación de la máquina.

### Paso a paso en la calculadora:
1. En el buscador de servicios, escribir **`Amazon CloudWatch`** y hacer clic en **`Configure`**.
2. **Location (Ubicación):**
   * *Region:* **`US East (N. Virginia)`**.
3. **Métricas, APIs y Database Insights (Omitir cobros innecesarios):**
   * *Metrics:* **Dejar vacío**. Las métricas base de CPU, memoria y disco cada 5 minutos son gratuitas.
   * *APIs:* **Dejar vacío**. El nivel gratuito cubre hasta 1 millón de peticiones API.
   * *Database Insights for Aurora/RDS:* **Dejar vacío**.
4. **Logs (Telemetría de contenedores Docker):**
   * Desplegar la sección **`► Logs`**.
   * *Standard Logs: Data Ingested:* Ingresar **`2`** con unidad **`GB`**. *(Costo: 2 GB × $0.50/GB = $1.00 USD).*
   * *Log Storage/Archival:* Dejar seleccionada la opción predeterminada: **`Yes to Store Logs: Assuming 1 month retention`**. *(Al asumir compresión al 15%, AWS cobra solo **$0.01 USD**).*
   * *Infrequent Access / Logs to S3 / Insights Queries:* **Dejar vacíos**.
5. **Dashboards and Alarms (Alarmas y Paneles):**
   * Desplegar la sección **`► Dashboards and Alarms`**.
   * *Number of Dashboards:* Ingresar **`1`** o dejar vacío *(AWS incluye 3 dashboards con hasta 50 métricas gratis al mes = $0.00 USD)*.
   * *Number of Standard Resolution Alarm Metrics:* Ingresar **`2`**. Corresponden a las 2 alarmas del entregable: caída de la máquina (`StatusCheckFailed`) y alerta de CPU > 85% a $0.10 c/u = **`$0.20 USD`**.
   * *High Resolution / Composite alarms:* **Dejar vacíos**.

### Desglose del costo mensual:
* **Ingesta de logs (2 GB):** `$1.00 USD`
* **Almacenamiento de logs comprimido (1 mes):** `$0.01 USD`
* **Alarmas estándar (2 unidades):** `$0.20 USD`
* **Subtotal mensual CloudWatch:** **`$1.21 USD`** *(redondeado en el entregable original a ~$1.50 como margen operativo)*
* **Acción:** Hacer clic en **`Save and add service`**.

---

## 7. Amazon Route 53 (DNS y Gestión de Dominios)

Servicio de DNS administrado y de alta disponibilidad para enrutar los subdominios institucionales de la plataforma (`admin.sofi.rpsoft.com` y `api.sofi.rpsoft.com`) hacia los recursos en AWS.

### Paso a paso en la calculadora:
1. En el buscador de servicios, escribir **`Amazon Route 53`** y hacer clic en **`Configure`**.
2. **Hosted Zones (Zonas hospedadas):**
   * *Hosted Zones:* Ingresar **`1`**. *(AWS factura una tarifa fija de **$0.50 USD/mes** por cada una de las primeras 25 zonas hospedadas públicas).*
   * *Additional Records in Hosted Zones:* **Dejar vacío**. Cada zona hospedada incluye hasta 10,000 registros gratuitos.
3. **Consultas y funciones adicionales (Omitir):**
   * *Traffic Flow:* **Dejar vacío**.
   * *Standard queries:* **Dejar vacío o ingresar `0`**. Las consultas de tráfico interno institucional son despreciables y el millón de consultas cuesta apenas $0.40 USD.
   * *Latency / Geo DNS / IP queries:* **Dejar vacíos**.
   * *DNS Failover Health Checks:* **Dejar vacíos**.
   * *Route 53 Resolver / DNS Firewall:* **Dejar vacíos**.

### Desglose del costo mensual:
* **Tarifa mensual de la zona hospedada pública:** **`$0.50 USD`**
* **Subtotal mensual Route 53:** **`$0.50 USD`**
* **Acción:** Hacer clic en **`Save and add service`**.

---

## 8. Data Transfer (Transferencia de Datos Saliente a Internet)

Ancho de banda saliente desde los servidores de AWS hacia Internet (computadoras de los practicantes remotos y administradores de SOFI al consultar la aplicación web o APIs).

### Paso a paso en la calculadora:
1. En el buscador de servicios, escribir **`Data Transfer`** y hacer clic en **`Configure`**.
2. **Inbound e Intra-Region:**
   * *Inbound Data Transfer (Tráfico entrante):* **Dejar vacío**. Todo el tráfico que ingresa a AWS desde Internet es 100% gratuito.
   * *Intra-Region Data Transfer:* **Dejar vacío**. El tráfico interno entre subredes de la misma AZ en la VPC no genera costos.
3. **Outbound Data Transfer (Tráfico saliente a Internet):**
   * *Data transfer to:* Seleccionar **`Internet`** en el menú desplegable.
   * *Enter Amount:* Ingresar **`11`** (o `10`).
   * ⚠️ *Data amount (Unidad):* **Cambiar el desplegable a `GB per month`**. *(Por defecto viene en `TB per month`; si se deja en TB el cálculo se dispararía erróneamente a varios cientos de dólares).*

### Desglose del costo mensual:
* **Fórmula:** $11 \text{ GB} \times \$0.09 \text{ USD/GB}$
* **Subtotal mensual Transferencia:** **`$0.99 USD`** *(redondeado en el entregable a ~$1.00)*
* **Acción:** Hacer clic en **`Save and view summary`**.

---

## 9. Presupuesto Final Consolidado

Una vez cargados los 8 componentes, al ingresar a la vista de resumen de la estimación (*My Estimate*), la calculadora oficial de AWS refleja exactamente el siguiente cuadro de inversión mensual:

| # | Servicio AWS | Recurso / Configuración Específica Ingresada | Propósito Técnico en la Arquitectura SOFI | Costo Real Calculadora | Costo en Entregable |
| :-: | :--- | :--- | :--- | :---: | :---: |
| 1 | **Amazon EC2** | Instancia `t3.small` (2 vCPU, 2 GiB RAM), Linux, On-Demand (730 h) | Cómputo desacoplado de `sofi-backend`, `SOFI-WEB` y bot Discord | **$15.18 USD** | ~$15.20 USD |
| 2 | **Amazon EBS** | Volumen raíz de 30 GB `gp3` (3,000 IOPS y 125 MB/s base incluidos) | Almacenamiento SSD persistente del SO Ubuntu y contenedores Docker | **$2.40 USD** | $2.40 USD |
| 3 | **Amazon RDS for PostgreSQL** | Instancia `db.t3.micro` Single-AZ + 20 GB disco `gp3` (Snapshots incluidos) | Base de datos relacional administrada y aislada para asistencias y usuarios | **$15.44 USD** | $15.44 USD |
| 4 | **Amazon S3** | 15 GB S3 Standard + 1,000 peticiones PUT + 10,000 peticiones GET | Almacenamiento multimedia para cursos LMS y copias de seguridad externas | **$0.35 USD** | $0.35 USD |
| 5 | **AWS Systems Manager** | SSM Session Manager estándar (10 parámetros estándar en Parameter Store) | Gestión remota y auditoría sin requerir puertos SSH (22) expuestos | **$0.00 USD** | $0.00 USD |
| 6 | **Amazon CloudWatch** | 2 Alarmas de salud/CPU + 2 GB Logs con retención a 1 mes + 1 Dashboard | Monitoreo continuo de disponibilidad y alertas ante caídas del bot | **$1.21 USD** | ~$1.50 USD |
| 7 | **Amazon Route 53** | 1 Hosted Zone pública (consultas estándar dentro de cuota) | Resolución de DNS para subdominios institucionales (`sofi.rpsoft.com`) | **$0.50 USD** | ~$0.50 USD |
| 8 | **Data Transfer** | 11 GB de tráfico de salida hacia Internet (Outbound DTO) | Respuestas web y de API hacia practicantes y supervisores remotos | **$0.99 USD** | ~$1.00 USD |
| | **PRESUPUESTO MENSUAL TOTAL** | | **Inversión mensual base consolidada y reproducible en AWS** | **`$36.07 USD`** | **`~$36.37 USD`** |

> **Nota técnica para la defensa académica:** La diferencia marginal de 30 centavos entre el total de la calculadora ($36.07 USD) y el entregable ($36.37 USD) se debe exclusivamente al redondeo conservador aplicado como margen de seguridad en CloudWatch ($1.50 vs $1.21) y EC2 ($15.20 vs $15.18).
