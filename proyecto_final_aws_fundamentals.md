# SENATI

## PROPUESTA DE PROYECTO: DISEÑO E IMPLEMENTACIÓN DE ARQUITECTURA CLOUD ESCALABLE, TOLERANTE A FALLOS Y DE ALTA DISPONIBILIDAD EN AWS PARA EL ÁREA DE DESARROLLO DE SOFTWARE

---

### Objetivo General del Proyecto

Aplicar las técnicas, servicios y modelos de arquitectura que ofrece la computación en la nube con AWS para evaluar, diseñar y proponer una infraestructura tecnológica escalable, flexible, tolerante a fallos y de alta disponibilidad, asegurando un entorno seguro y optimizado para el desarrollo, pruebas y despliegue de soluciones de software en la empresa de formación práctica del estudiante.

---

### ETAPA 1: Diagnóstico de la Empresa y Fundamentos Cloud

- **Periodo de ejecución:** Entregar en la Semana 6.
- **Contenido curricular relacionado (Semanas 5 y 6):** Introducción a la nube, ventajas, infraestructura global de AWS, CAF (Cloud Adoption Framework), facturación, economía de la nube (TCO, modelos de precios), estrategias de seguridad iniciales (IAM, Modelo de Responsabilidad Compartida) y fundamentos de redes (VPC, Route 53, CloudFront).

#### Estructura del Entregable 1:

1. **Descripción de la Empresa de Formación Práctica:**
   - **Naturaleza de la empresa, sector y modelo de negocio:** (¿Desarrollan software comercial o sistemas internos para otro rubro como comercios, clínicas de salud, etc.?).
   - **Identificación y descripción del área de desarrollo de soluciones de TI:** (productos de software que ofrecen al público o desarrollo de proyectos internos en curso o planificados).

2. **Análisis de la Infraestructura y Tecnología Actual:**
   - **Descripción tecnológica:** Servidores físicos o virtuales locales, herramientas y control de versiones.
   - **Modalidad de trabajo:** Especificar si el trabajo de los colaboradores y practicantes es remoto, presencial o híbrido.
   - **Identificación de limitaciones actuales (Enfoque crítico):** Detallar explícitamente la falta de flexibilidad y escalabilidad ante picos de trabajo, la ausencia de tolerancia a fallos frente a interrupciones físicas, la carencia de alta disponibilidad (riesgo de caída total por depender de un único entorno local), además de evaluar los costos y brechas de seguridad actuales.

3. **Propuesta Conceptual basada en Fundamentos AWS (Cloud Foundations):**
   - **Justificación de Migración / Adopción Cloud:** Aplicación del marco de adopción de la nube (CAF) de AWS para dar solución a las limitaciones diagnosticadas.
   - **Estimación Económica Inicial:** Análisis preliminar de costos (Pricing y TCO) aplicando los fundamentos de precios de AWS para los servicios requeridos.
   - **Modelo de Seguridad y Gobierno Inicial:** Propuesta de control de accesos basada en el Modelo de Responsabilidad Compartida de AWS y políticas iniciales de AWS Identity and Access Management (IAM).
   - **Diagrama de Arquitectura de Red Propuesto (Nivel Conceptual):** Diseño inicial de una Amazon VPC, subredes públicas/privadas y uso de Amazon Route 53 o CloudFront de acuerdo con los requerimientos de la empresa.

---

### ETAPA 2: Implementación de Servicios Core, Almacenamiento y Bases de Datos en la Nube

- **Periodo de ejecución:** Presentación en la Semana 7.
- **Contenido curricular relacionado (Semana 7):** Servicios de computación (Amazon EC2, contenedores, AWS Lambda, Elastic Beanstalk), servicios de almacenamiento (EBS, S3, EFS, S3 Glacier) y servicios de bases de datos administradas (RDS, DynamoDB, Redshift, Aurora).

#### Estructura del Entregable 2:

1. **Diseño de la Capa de Computación y Servidores Cloud:**
   - **Selección y configuración propuesta de instancias Amazon EC2** para los equipos de desarrollo y/o despliegue de aplicaciones, detallando tipos de instancias y opciones de almacenamiento (EBS).
   - **Evaluación de arquitecturas modernas** (contenedores y servicios sin servidor como AWS Lambda o Elastic Beanstalk) aplicadas al software de la empresa.

2. **Estrategia de Almacenamiento y Archivo de Datos:**
   - **Propuesta de uso para Amazon S3** (almacenamiento de objetos, archivos estáticos o respaldos) y **Amazon EFS** para sistemas de archivos compartidos entre equipos de desarrollo.
   - **Políticas de retención y archivado** utilizando Amazon S3 Glacier.

3. **Implementación de Bases de Datos Administradas:**
   - **Selección del motor de base de datos óptimo** para la solución de la empresa (bases de datos relacionales con Amazon RDS / Amazon Aurora o NoSQL con Amazon DynamoDB).
   - **Justificación técnica del motor seleccionado** según las cargas de trabajo del software desarrollado.

---

### ETAPA 3: Arquitecturas Escalables, Operaciones y Automatización

- **Periodo de ejecución:** Semanas 7 y 8 (Entrega del trabajo final en la Semana 8).
- **Contenido curricular relacionado (Semana 8 en adelante - AWS Cloud Operations):** Arquitecturas de alta disponibilidad, Elastic Load Balancing (ELB), Auto Scaling, CloudWatch, AWS Systems Manager, infraestructura como código (CloudFormation) y seguridad avanzada en VPC.

#### Estructura del Entregable Final (Trabajo Terminado):

1. **Arquitectura Dinámica, de Alta Disponibilidad y Tolerante a Fallos:**
   - **Diseño de mecanismos de tolerancia a fallos y alta disponibilidad** mediante la distribución de recursos en múltiples zonas de disponibilidad, integrando Elastic Load Balancing (ELB) y Amazon EC2 Auto Scaling para garantizar la elasticidad y continuidad operativa de las aplicaciones ante picos de tráfico o fallas imprevistas.

2. **Seguridad Avanzada de Red (AWS VPC y Protección en Capas):**
   - **Configuración detallada de la VPC:** Grupos de seguridad (Security Groups), listas de control de acceso (Network ACLs), y uso de hosts bastión para el acceso seguro a los equipos de desarrollo.

3. **Monitoreo, Auditoría y Gestión de Recursos:**
   - **Configuración de Amazon CloudWatch** (métricas, alarmas y logs) para la supervisión constante del estado de la infraestructura y rendimiento de las aplicaciones.
   - **Implementación de estrategias de control de costos y gobernanza** mediante etiquetado de recursos (Tagging) y recomendaciones de AWS Trusted Advisor.

4. **Automatización e Infraestructura como Código (IaC):**
   - **Propuesta de despliegues automatizados y repetibles** mediante plantillas de AWS CloudFormation o herramientas de automatización afines para estandarizar los ambientes de desarrollo, prueba y producción de la empresa.
