# Parámetros de Entrada - AWS Pricing Calculator
**Región de referencia:** `US East (N. Virginia)` (`us-east-1`)  

---

### 1. Amazon EC2
* **Choose a location type:** `Region`
* **Choose a Region:** `US East (N. Virginia)`
* **Tenancy:** `Shared Instances`
* **Operating system:** `Linux`
* **Workloads:** `Constant usage`
* **Number of instances:** `1`
* **Instance type:** `t3.small`
* **Payment option:** `On-Demand`
* **Expected utilization (Usage):** `100 %` (o `730 Hours/Month`)
* **EBS / Monitoring / Data Transfer / Additional costs:** *Vacío / Desmarcado*
* **Precio final mensual:** **`$15.18 USD`**

---

### 2. Amazon Elastic Block Store (EBS)
* **Choose a Region:** `US East (N. Virginia)`
* **Number of volumes:** `1`
* **Average duration of volume:** `730 hours per month`
* **Storage for each EC2 instance:** `General Purpose SSD (gp3)`
* **Storage amount per volume:** `30 GB`
* **Snapshot Frequency:** `No snapshot storage`
* **IOPS / Throughput / Fast Snapshot / APIs:** *Vacío*
* **Precio final mensual:** **`$2.40 USD`**

---

### 3. Amazon RDS for PostgreSQL
* **Choose a Region:** `US East (N. Virginia)`
* **Nodes:** `1`
* **Deployment Option:** `Single-AZ`
* **DB Engine:** `PostgreSQL`
* **Instance type:** `db.t3.micro`
* **Utilization:** `730 Hours/Month` (o `100 %`)
* **Pricing Model:** `OnDemand`
* **Would you be creating an RDS Proxy...?:** `No`
* **Storage volume:** `General Purpose SSD (gp3)`
* **Storage amount:** `20 GB`
* **Would you be enabling Database Insights...?:** `No`
* **RDS Extended Support:** `No`
* **Additional backup storage / Snapshot Export:** *Vacío (0 GB)*
* **Precio final mensual:** **`$15.44 USD`**

---

### 4. Amazon Simple Storage Service (S3)
* **Choose a Region:** `US East (N. Virginia)`
* **Select S3 storage classes:** Activar únicamente `S3 Standard`
* **S3 Standard storage:** `15 GB per month`
* **How will data be moved into S3 Standard?:** `The specified amount of data is already stored in S3 Standard`
* **PUT, COPY, POST, LIST requests:** `1000`
* **GET, SELECT, and all other requests:** `10000`
* **S3 Select / Data Transfer:** *Vacío*
* **Precio final mensual:** **`$0.35 USD`**

---

### 5. AWS Systems Manager
* **Choose a Region:** `US East (N. Virginia)`
* **Standard parameters:** `10` (o vacío)
* **Advanced parameters:** *Vacío*
* **On-Premises Instance Management / Otros:** *Vacío (0)*
* **Precio final mensual:** **`$0.00 USD`**

---

### 6. Amazon CloudWatch
* **Choose a Region:** `US East (N. Virginia)`
* **Metrics / APIs / Database Insights:** *Vacío*
* **Logs > Standard Logs: Data Ingested:** `2 GB`
* **Logs > Log Storage/Archival:** `Yes to Store Logs: Assuming 1 month retention`
* **Alarms > Standard resolution alarms:** `2`
* **Dashboards:** `1` (o vacío)
* **Precio final mensual:** **`$1.21 USD`**

---

### 7. Amazon Route 53
* **Hosted Zones:** `1`
* **Additional Records / Standard queries / Otros:** *Vacío*
* **DNS Failover Health Checks / Resolver / Firewall:** *Vacío*
* **Precio final mensual:** **`$0.50 USD`**

---

### 8. Data Transfer
* **Inbound Data Transfer / Intra-Region:** *Vacío*
* **Outbound Data Transfer > Data transfer to:** `Internet`
* **Outbound Data Transfer > Enter Amount:** `11`
* **Outbound Data Transfer > Data amount:** `GB per month`
* **Precio final mensual:** **`$0.99 USD`**

---

## Presupuesto Final Consolidado

| # | Servicio AWS | Configuración Clave Ingresada | Precio Final Mensual |
| :-: | :--- | :--- | :---: |
| 1 | **Amazon EC2** | `t3.small` On-Demand (730 h, Linux) | $15.18 USD |
| 2 | **Amazon EBS** | 30 GB `gp3` (SSD Uso General) | $2.40 USD |
| 3 | **Amazon RDS for PostgreSQL** | `db.t3.micro` Single-AZ + 20 GB `gp3` | $15.44 USD |
| 4 | **Amazon S3** | 15 GB S3 Standard + 11k requests | $0.35 USD |
| 5 | **AWS Systems Manager** | SSM Session Manager estándar | $0.00 USD |
| 6 | **Amazon CloudWatch** | 2 Alarmas + 2 GB Logs | $1.21 USD |
| 7 | **Amazon Route 53** | 1 Hosted Zone pública | $0.50 USD |
| 8 | **Data Transfer** | 11 GB Outbound a Internet | $0.99 USD |
| | **PRESUPUESTO FINAL MENSUAL** | | **$36.07 USD** |

