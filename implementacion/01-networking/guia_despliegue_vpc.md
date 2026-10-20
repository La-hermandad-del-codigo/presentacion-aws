# Guía de Despliegue: Amazon VPC Multi-AZ (Fase 3)

Esta guía detalla los pasos exactos para implementar la infraestructura de red en **Amazon Web Services (AWS)** utilizando la plantilla de Infraestructura como Código (IaC) `01-networking-vpc.yaml`.

---

## 1. Resumen de la Topología a Desplegar

* **Región:** `us-east-1` (N. Virginia).
* **Bloque CIDR de la VPC:** `10.0.0.0/16`.
* **Distribución de Subredes:**

| Nombre de Subred | Bloque CIDR | Zona (AZ) | Tipo / Capa | Destino en Tabla de Ruteo |
| :--- | :---: | :---: | :---: | :--- |
| `apm-sofi-prod-public-subnet-a` | `10.0.1.0/24` | `us-east-1a` | Pública | `0.0.0.0/0` ➔ Internet Gateway (`igw`) |
| `apm-sofi-prod-public-subnet-b` | `10.0.2.0/24` | `us-east-1b` | Pública | `0.0.0.0/0` ➔ Internet Gateway (`igw`) |
| `apm-sofi-prod-private-app-subnet-a` | `10.0.10.0/24` | `us-east-1a` | Privada Cómputo | Solo local (`10.0.0.0/16`) / Salida NAT |
| `apm-sofi-prod-private-app-subnet-b` | `10.0.20.0/24` | `us-east-1b` | Privada Cómputo | Solo local (`10.0.0.0/16`) / Salida NAT |
| `apm-sofi-prod-private-dev-subnet-a` | `10.0.30.0/24` | `us-east-1a` | Privada Gestión/Dev | Solo local (`10.0.0.0/16`) / VPC Endpoints |
| `apm-sofi-prod-isolated-db-subnet-a` | `10.0.100.0/24` | `us-east-1a` | Aislada de Datos | **Solo local (Cero salida a Internet)** |
| `apm-sofi-prod-isolated-db-subnet-b` | `10.0.101.0/24` | `us-east-1b` | Aislada de Datos | **Solo local (Cero salida a Internet)** |

---

## 2. Método 1: Despliegue desde la Consola Web de AWS (Recomendado)

Este es el método más rápido y visual para tu compañero.

### Paso 1: Ubicación en AWS
1. Iniciar sesión en la [Consola de AWS](https://console.aws.amazon.com/).
2. Asegurarse de tener seleccionada la región **US East (N. Virginia) `us-east-1`** en la esquina superior derecha.

### Paso 2: Crear el Stack en CloudFormation
1. En la barra de búsqueda superior, escribir **CloudFormation** y seleccionar el servicio.
2. Hacer clic en el botón naranja **Create stack** ➔ **With new resources (standard)**.
3. En la sección **Prerequisite - Prepare template**, dejar seleccionada la opción **Template is ready**.
4. En **Specify template**:
   * Seleccionar **Upload a template file**.
   * Hacer clic en **Choose file** y subir el archivo [`01-networking-vpc.yaml`](./01-networking-vpc.yaml).
5. Hacer clic en **Next**.

### Paso 3: Especificar Parámetros
1. **Stack name:** Ingresar `apm-sofi-networking`.
2. Los parámetros de red (`VpcCIDR`, `Subnet CIDRs`) ya vienen preconfigurados con los valores del diseño; dejar los valores por defecto a menos que se requiera personalización.
3. Hacer clic en **Next**.

### Paso 4: Configurar Opciones y Enviar
1. En **Configure stack options**, dejar todo por defecto y hacer clic en **Next**.
2. Revisar el resumen final en **Review** y hacer clic en **Submit**.

### Paso 5: Esperar el aprovisionamiento
* CloudFormation creará la VPC, las 7 subredes, el Internet Gateway, las 3 tablas de ruteo y el grupo de subredes RDS en aproximadamente **60 segundos**.
* El estado debe cambiar a **`CREATE_COMPLETE`**.

---

## 3. Método 2: Despliegue mediante AWS CLI (Terminal)

Si tu compañero prefiere usar la consola de comandos con sus credenciales configuradas (`aws configure`):

```bash
aws cloudformation create-stack \
  --stack-name apm-sofi-networking \
  --template-body file://01-networking-vpc.yaml \
  --region us-east-1
```

Para monitorear el progreso hasta que finalice:

```bash
aws cloudformation wait stack-create-complete \
  --stack-name apm-sofi-networking \
  --region us-east-1
```

---

## 4. Evidencias para Presentar al Profesor

Una vez desplegada la red, ingresar a la consola para recopilar las siguientes evidencias:

1. **Portal Web de Validación de Conectividad y Aislamiento:**
   * Ir a la pestaña **Outputs** del stack en CloudFormation y copiar el enlace de **`PublicTestPortalUrl`** (ej. `http://54.x.x.x`).
   * Abrirlo en el navegador: se verá el panel de diagnóstico demostrando que la **Subred Pública** y el **Internet Gateway** están en línea.
   * Hacer clic en el botón **"Ejecutar Sonda Interna"**: la web pública enviará una petición interna Este-Oeste a la instancia de la **Subred Privada** (`10.0.10.X:8080`), demostrando comunicación local sin salir a Internet.
   * Hacer clic en el enlace de prueba negativa hacia la IP privada: el navegador quedará en `ERR_CONNECTION_TIMED_OUT`, evidenciando el aislamiento perimetral.

2. **Mapa de Recursos de la VPC (VPC Resource Map):**
   * Ir a **VPC** ➔ **Your VPCs** ➔ Seleccionar `apm-sofi-prod-vpc`.
   * En la parte inferior, pestaña **Resource map**: se verá visualmente cómo cada una de las 7 subredes está conectada a su tabla de ruteo correspondiente y al Internet Gateway. Esta es la evidencia visual nativa más valorada por los evaluadores de AWS.

3. **Tablas de Ruteo Segregadas:**
   * Ir a **Route tables**:
     * Mostrar que `apm-sofi-prod-public-rt` tiene una ruta `0.0.0.0/0` apuntando a `igw-...`.
     * Mostrar que `apm-sofi-prod-isolated-db-rt` **NO** tiene ruta `0.0.0.0/0` (garantía de aislamiento total de la base de datos).

4. **Grupo de Subredes de RDS (DB Subnet Group):**
   * Ir a **RDS** ➔ **Subnet groups**:
     * Mostrar el grupo `apm-sofi-prod-db-subnet-group` abarcando las dos zonas (`us-east-1a` y `us-east-1b`) para cumplir el requisito de alta disponibilidad Multi-AZ.

---

## 5. Limpieza / Eliminación de Recursos (Clean-up)

Para no dejar recursos en la cuenta cuando termine la evaluación o si se requiere recrear el stack:

1. Ir a **CloudFormation** ➔ Seleccionar el stack `apm-sofi-networking`.
2. Hacer clic en **Delete** ➔ Confirmar con **Delete**.
3. AWS eliminará todos los componentes de red asociados automáticamente sin dejar recursos huérfanos.
