---
trigger: always_on
description: "Siempre activar y aplicar la skill archify por defecto para diagramas, flujos o arquitectura."
---

# Regla Obligatoria: Skill archify para Diagramas y Flujos

Siempre que el usuario solicite diseñar, generar, revisar, modificar o explicar un diagrama, flujo de procesos, arquitectura de sistemas, topología de red o mapa de infraestructura:

1. **Activación Obligatoria de `archify`**: Cargar y aplicar las pautas de `~/.gemini/antigravity-cli/skills/archify/SKILL.md`.
2. **Modelo C4**: Clasificar y agrupar explícitamente las zonas de red y confianza en subredes / subgraphs (Públicas, Privadas, Aisladas, Borde, Almacenamiento, Gobernanza).
3. **Anotación de Protocolos en Cada Arista**: Toda flecha o conexión debe indicar su protocolo de transporte, puerto o tipo de enlace (ej. `HTTPS :443`, `TCP :5432`, `NFS :2049`, `Presigned URL`, `UDP :53`).
4. **Flujos Ortogonales**: Mantener jerarquía estandarizada Top-to-Bottom (`TD`) o Left-to-Right (`LR`), sin líneas cruzadas caóticas.
5. **Fidelidad Absoluta**: No omitir componentes, especificaciones de cómputo, políticas de escalado ni mecanismos de resiliencia y alta disponibilidad.
