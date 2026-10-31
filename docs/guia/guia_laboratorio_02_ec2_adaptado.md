# Módulo 3: Laboratorio 2 — Creación de Instancias Amazon EC2 (Adaptado a Proyecto APM-SOFI)

## 1. Mapeo de Arquitectura y Recursos

| Componente | Parámetro en Laboratorio Original | Equivalente en Proyecto APM-SOFI |
| :--- | :--- | :--- |
| **VPC** | `Lab VPC` | `apm-sofi-prod-vpc` |
| **Subred Pública** | `Public Subnet` | `apm-sofi-prod-public-subnet-a` |
| **Servidor Bastión** | `Bastion Server` | `apm-sofi-prod-bastion-server` |
| **Security Group Bastión** | `Bastion security group` | `apm-sofi-prod-sg-bastion` (SSH TCP :22) |
| **IAM Instance Profile** | `Bastion-Role` | `apm-sofi-prod-profile-bastion` |
| **Par de Claves (Key Pair)** | `vockey` | `bastion.pem` (Clave RSA propia) |
| **Servidor Web** | `Web Server` | `apm-sofi-prod-web-server` |
| **Security Group Web** | `WebSecurityGroup` | `apm-sofi-prod-public-test-sg` (HTTP TCP :80) |

---

## 2. Tarea 1: Configuración del Servidor Bastión (Consola AWS)

Para referencia de la configuración aplicada en la consola de EC2:

1. **Nombre:** `apm-sofi-prod-bastion-server`
2. **AMI:** `Amazon Linux 2023 (AMI)` (64-bit x86)
3. **Tipo de instancia:** `t3.micro` (o `t2.micro`)
4. **Key pair:** `bastion`
5. **Configuración de red:**
   - **VPC:** `apm-sofi-prod-vpc`
   - **Subred:** `apm-sofi-prod-public-subnet-a`
   - **Auto-assign Public IP:** Habilitada (Enable)
   - **Security Group:** `apm-sofi-prod-sg-bastion` (Regla Inbound: SSH, TCP 22, 0.0.0.0/0)
6. **Detalles avanzados:**
   - **IAM instance profile:** `apm-sofi-prod-profile-bastion` (contiene políticas para EC2, SSM y SSM Parameter Store).

---

## 3. Tarea 2: Conexión SSH al Servidor Bastión (Terminal Local Fedora)

Desde la terminal local:

```bash
cd ~/Descargas
chmod 400 bastion.pem
ssh -i bastion.pem ec2-user@44.201.6.40
```

---

## 4. Tarea 3: Despliegue de Servidor Web mediante AWS CLI

Una vez iniciada la sesión SSH en el servidor bastión, ejecute los siguientes comandos en orden:

### Paso 3.1: Obtención de Token IMDSv2, Región y AMI de Amazon Linux 2023

```bash
# 1. Obtener token seguro de metadatos (IMDSv2)
TOKEN=$(curl -s --request PUT "http://169.254.169.254/latest/api/token" --header "X-aws-ec2-metadata-token-ttl-seconds: 21600")

# 2. Extraer la region actual
AZ=$(curl -s --request GET "http://169.254.169.254/latest/meta-data/placement/availability-zone" --header "X-aws-ec2-metadata-token: $TOKEN")
export AWS_DEFAULT_REGION=${AZ::-1}

# 3. Obtener el ID de la AMI mas reciente de Amazon Linux 2023 desde Parameter Store
AMI=$(aws ssm get-parameters \
  --names /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 \
  --query 'Parameters[0].[Value]' \
  --output text)

echo "AMI obtenida: $AMI"
```

### Paso 3.2: Consultar la Subred Pública y el Security Group del Proyecto

```bash
# 1. Recuperar el Subnet ID de la Subred Publica A
SUBNET=$(aws ec2 describe-subnets \
  --filters "Name=tag:Name,Values=apm-sofi-prod-public-subnet-a" \
  --query "Subnets[0].SubnetId" \
  --output text)

echo "Subnet ID: $SUBNET"

# 2. Recuperar el Security Group que permite trafico HTTP (puerto 80)
SG=$(aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=apm-sofi-prod-public-test-sg" \
  --query "SecurityGroups[0].GroupId" \
  --output text)

echo "Security Group ID: $SG"
```

### Paso 3.3: Descargar UserData y Lanzar la Instancia Web

```bash
# 1. Descargar el script de inicializacion UserData
wget https://aws-tc-largeobjects.s3.amazonaws.com/ILT-TF-200-ACSOPS-1/lab-2-ec2-linux/UserData.txt

# 2. Iniciar la instancia con etiquetas de gobierno APM-SOFI
INSTANCE=$(aws ec2 run-instances \
  --image-id $AMI \
  --subnet-id $SUBNET \
  --security-group-ids $SG \
  --user-data file:///home/ec2-user/UserData.txt \
  --instance-type t2.micro \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=apm-sofi-prod-web-server},{Key=Project,Value=APM-SOFI},{Key=Environment,Value=Production}]' \
  --query 'Instances[0].InstanceId' \
  --output text)

echo "Instancia Web creada con ID: $INSTANCE"
```

### Paso 3.4: Verificar Estado y Probar Conexión Web

```bash
# 1. Consultar estado de ejecucion (repetir hasta que retorne 'running')
aws ec2 describe-instances \
  --instance-ids $INSTANCE \
  --query 'Reservations[0].Instances[0].State.Name' \
  --output text

# 2. Obtener la direccion DNS publica o IP publica
aws ec2 describe-instances \
  --instance-ids $INSTANCE \
  --query 'Reservations[0].Instances[0].PublicDnsName' \
  --output text

aws ec2 describe-instances \
  --instance-ids $INSTANCE \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text
```

Abra la dirección obtenida en su navegador web (`http://<PUBLIC_DNS_O_IP>`) para verificar la página de bienvenida.

---

## 5. Resolución de Desafíos Opcionales

### Desafío 1: Conexión a Servidor Mal Configurado
* **Diagnóstico:** El Security Group de la instancia no tiene una regla Inbound autorizando el puerto `22` (SSH).
* **Solución:** En la consola de EC2 > Security Groups, seleccionar el grupo de seguridad de la instancia y agregar una regla de entrada tipo `SSH (TCP 22)` para `0.0.0.0/0` o la IP local.

### Desafío 2: Solución de Servidor Web no disponible
* **Diagnóstico:** El servicio web Apache (`httpd`) no inició automáticamente durante el arranque o fue bloqueado por firewall local.
* **Solución:** Conectarse vía SSH a la instancia y ejecutar:
  ```bash
  sudo systemctl enable --now httpd
  sudo systemctl status httpd
  ```
  Verificar además que el Security Group permita tráfico entrante en el puerto `80` (HTTP).
