# 03 — Enrutamiento e incertidumbre

## Combinar todo: el Router

`Router.route(texto, recibido)` junta las dos mitades:

1. Clasifica (tipo, departamento, confianzas, términos explicativos).
2. Aplica las reglas (prioridad + razones, fecha límite + días hábiles).
3. Ensambla una `RoutingDecision` con todo.

El resultado tiene: tipo, departamento, ambas confianzas, prioridad y sus razones,
fecha de recepción y fecha límite, los días hábiles del SLA, los términos
explicativos, y una bandera `uncertain`.

## La incertidumbre: baja confianza → revisión humana

Un clasificador a veces duda: un mensaje raro, una mezcla de asuntos, o un
fraseo muy distinto de lo visto. Enrutar con una corazonada débil puede mandar la
solicitud al departamento equivocado y gastar parte del plazo legal antes de que
alguien note el error.

Por eso usamos la **confianza** del tipo. Si está por debajo del umbral
(`PQ_MIN_CONFIDENCE`, por defecto 0,45), se marca `uncertain = True` y la solicitud
va a **revisión humana (manual triage)** en lugar de enrutarse a ciegas.

### Pero sigue siendo útil cuando duda

Aun marcada como incierta, la decisión trae el departamento estimado, la prioridad
y la fecha límite. Así, la revisión humana arranca desde un **borrador útil**, no
desde cero.

Y recuerda (guía 02): la **urgencia actúa igual**, aunque el tipo sea incierto. En
la demo, el mensaje de la fuga de agua queda con tipo incierto (fraseo fuera de
plantilla), pero igual se enruta a infraestructura con prioridad **alta**. Eso es
degradación elegante: lo que se sabe con seguridad se usa; lo dudoso se deriva.

## Un recorrido de la demo

- "Me quejo del trato grosero de un agente" → queja → atención al cliente, media,
  15 días hábiles. Enrutada con confianza.
- "Solicito información sobre el horario del portal" → petición → general, baja.
- "Hay una fuga peligrosa de agua, es urgente" → tipo **incierto** (fuera de
  plantilla) → revisión humana, pero infraestructura + **alta** por urgencia.
- "Sugiero mejorar el agendamiento" → sugerencia → atención al cliente, baja, 30
  días hábiles.
- "Exijo corregir un cargo incorrecto en mi factura" → reclamo → facturación,
  media, 15 días hábiles.

## Para fijar la idea

- El Router combina clasificación + reglas en una `RoutingDecision` explicable.
- Baja confianza de tipo → `uncertain` → revisión humana, no enrutado a ciegas.
- Aun incierta, la decisión aporta departamento, prioridad y plazo: un borrador
  útil para el humano.
