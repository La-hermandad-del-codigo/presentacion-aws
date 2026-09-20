# Diapositivas Modulares (Reveal.js)

Cada archivo en esta carpeta representa una diapositiva (`<section>...</section>`) independiente:

| Archivo | Diapositiva | Descripción |
| :--- | :--- | :--- |
| `01_portada.html` | Slide 1 | Título, autor (Jhefry Cabanillas), SENATI, APM Inversiones EIRL |
| `02_modelo_negocio.html` | Slide 2 | Modelo B2B y segregación del área TI |
| `03_ecosistema_sofi.html` | Slide 3 | Plataforma interna SOFI (NestJS, Next.js, Discord) |
| `04_telemetria_vps.html` | Slide 4 | Diagnóstico real del VPS (vCPUs, RAM, Swap 0B, Docker) |
| `05_limitaciones_criticas.html` | Slide 5 | Puntos de falla, OOM killer y puertos públicos expuestos |
| `06_aws_caf.html` | Slide 6 | Marco de Adopción de la Nube (6 perspectivas) |
| `07_arquitectura_aws.html` | Slide 7 | Diseño en AWS (VPC, ECS Fargate, RDS Multi-AZ, S3) |
| `08_seguridad_gobierno.html` | Slide 8 | Seguridad IAM, principio de mínimo privilegio y auditoría |
| `09_tco_costos.html` | Slide 9 | Desglose económico, comparación TCO y ROI |
| `10_conclusion_roadmap.html` | Slide 10 | Hoja de ruta (Fases 1 a 4) y conclusiones |

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
