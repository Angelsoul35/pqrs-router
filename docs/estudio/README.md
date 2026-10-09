# Guía de estudio — pqrs-router

Esta carpeta es una guía en español para entender pqrs-router a fondo. El código,
los comentarios y la documentación técnica están en inglés (nivel B2) a propósito,
para que el proyecto sea creíble y sirva para practicar. Esta guía explica el "por
qué" de cada decisión en tu idioma, para estudiar con calma.

## Orden sugerido de lectura

1. **[01-pqrs-y-clasificacion.md](01-pqrs-y-clasificacion.md)** — qué es PQRS y
   cómo se clasifican el tipo y el departamento con modelos lineales, la evaluación
   sin fuga y la validación sobre quejas reales de la CFPB.
2. **[02-reglas-prioridad-y-plazos.md](02-reglas-prioridad-y-plazos.md)** — la
   prioridad por urgencia y los plazos legales en días hábiles.
3. **[03-enrutamiento-e-incertidumbre.md](03-enrutamiento-e-incertidumbre.md)** —
   cómo se combina todo y por qué la baja confianza va a revisión humana.
4. **[04-arquitectura-y-diseno.md](04-arquitectura-y-diseno.md)** — cómo encajan
   las piezas y por qué aquí no hace falta un LLM ni blockchain.
5. **[05-preguntas-de-entrevista.md](05-preguntas-de-entrevista.md)** — preguntas
   típicas y cómo responderlas con seguridad.

## Resumen en una frase

pqrs-router lee una solicitud ciudadana en texto libre, clasifica su tipo PQRS
(petición, queja, reclamo, sugerencia, denuncia) y el departamento responsable con
modelos lineales explicables, le asigna una prioridad por reglas de urgencia y
calcula el plazo legal de respuesta en días hábiles — una decisión de
enrutamiento única y explicable, sin LLM ni blockchain porque aquí no hacen falta.
