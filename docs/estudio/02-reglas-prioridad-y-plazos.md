# 02 — Reglas: prioridad y plazos

El clasificador decide **qué** es la solicitud. Las reglas deciden **con qué
urgencia** se atiende y **para cuándo**. Estas dos cosas tienen peso legal y de
política, así que **no** se aprenden: son deterministas, en `rules.py` y
`taxonomy.py`.

## La prioridad

Cada tipo tiene una prioridad base:

- Denuncia (report) → **alta** por defecto (posible irregularidad).
- Queja y reclamo → **media**.
- Petición y sugerencia → **baja**.

Luego, cualquier solicitud se eleva a **alta** si su texto contiene términos de
**urgencia**: seguridad, salud, "urgent", "emergency", cortes de agua o luz,
fugas, fraude, o personas vulnerables (menor, discapacitado, anciano). Esos
términos están en `URGENCY_TERMS`.

La función `assess_priority` devuelve la prioridad y las **razones** (la base del
tipo y, si aplica, qué términos de urgencia la elevaron). Todo queda explicado.

Un detalle importante: la urgencia actúa **independientemente** del tipo y de la
confianza del clasificador. Así, una solicitud urgente nunca se desprioriza solo
porque su tipo quedó incierto.

## Los plazos (SLA) en días hábiles

Cada tipo tiene una ventana legal de respuesta, en `SLA_BUSINESS_DAYS`
(valores ilustrativos; en producción se fijan desde la ley que aplique):

- Petición, queja, reclamo → 15 días hábiles.
- Sugerencia → 30 días hábiles.
- Denuncia → 10 días hábiles.

### ¿Por qué días hábiles y no naturales?

Porque los plazos legales casi siempre se cuentan en **días hábiles**, no
naturales. Un plazo que caiga en sábado, o que ignore los fines de semana, está
**mal** y puede incumplir la ley.

`add_business_days(fecha, n)` suma `n` días hábiles saltando sábados y domingos.
`sla_due(recibido, tipo)` devuelve la fecha límite y el número de días.

### Ejemplo

Recibido el lunes 2026-01-05, una petición (15 días hábiles) vence el lunes
2026-01-26 (tres semanas después, saltando los fines de semana). Una sugerencia
(30 días hábiles) vence el 2026-02-16.

### Una extensión natural

El cálculo salta fines de semana pero **no** festivos, que varían por país y año.
`add_business_days` es el único sitio donde añadir un calendario de festivos, y
está aislado a propósito para que esa mejora no toque nada más.

## Para fijar la idea

- Prioridad y plazos son **política/ley**, así que son reglas deterministas, no
  aprendidas.
- Prioridad = base por tipo, elevada a alta por términos de urgencia; con razones.
- Plazos en **días hábiles** por tipo; el cálculo salta fines de semana (los
  festivos son una extensión en un único punto).
