# Diapositivas Modulares (Reveal.js)

Cada archivo en esta carpeta representa una diapositiva (`<section>...</section>`) independiente:

| Archivo | Diapositiva | Descripción |
| :--- | :--- | :--- |
| `01_portada.html` | Slide 1 | Título, autor (Jhefry Cabanillas), SENATI, APM Inversiones EIRL |
| `03_ecosistema_sofi.html` | Slide 2 | Ecosistema SOFI (Diagrama de convergencia: Web, Discord, Backend y Usuarios) |
| `04_proyectos_externos.html` | Slide 3 | Desarrollo Externo (Clientes Comerciales y Cargas Aisladas) |
| `05_telemetria_vps.html` | Slide 4 | Diagnóstico real del VPS (vCPUs, RAM, Swap 0B, Docker) |
| `06_limitaciones_criticas.html` | Slide 5 | Puntos de falla, OOM killer y puertos públicos expuestos |
| `07_aws_caf.html` | Slide 6 | Marco de Adopción de la Nube (AWS CAF) |
| `08_tco_costos.html` | Slide 7 | Desglose económico, comparación TCO y ROI |
| `09_seguridad_gobierno.html` | Slide 8 | Seguridad IAM, principio de mínimo privilegio y gobierno |
| `10_arquitectura_aws.html` | Slide 9 | Diseño en AWS (VPC, Subredes, ALB, EC2, RDS, S3) |
| `11_conclusion_roadmap.html` | Slide 10 | Hoja de ruta (Fases 1 a 4) y conclusiones |

## Flujo de Trabajo

1. Modificá cualquier archivo en `slides/`.
2. Para compilar manualmente:
   ```bash
   ./build.py
   ```
3. O dejá corriendo el observador automático en una terminal para que recompile solo en cada guardado:
   ```bash
   ./build.py --watch
   ```
4. O levantá el servidor web local con recarga:
   ```bash
   ./build.py --serve
   ```
