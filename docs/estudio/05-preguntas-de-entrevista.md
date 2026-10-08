# 05 — Preguntas de entrevista

Preguntas típicas sobre este proyecto y cómo responderlas con seguridad.
Practica diciéndolas en voz alta en inglés también.

## Sobre el enfoque

**¿Por qué separas la clasificación (aprendida) de la prioridad y los plazos
(reglas)?**
Porque son juicios distintos. "Qué es la solicitud" es lenguaje y se beneficia de
aprender; "cómo atenderla" es política con peso legal y debe ser determinista y
auditable. Separarlos mantiene los plazos revisables por un humano y el
clasificador reentrenable sin tocar la ley.

**¿Por qué modelos lineales y no un LLM?**
Porque es intake de alto volumen, sensible a latencia y coste, y auditable. Un
modelo lineal clasifica en microsegundos, no cuesta por solicitud, es
determinista y se explica (suma ponderada de palabras). Un LLM añadiría latencia,
coste y opacidad sin ganancia aquí. La interfaz permite cambiarlo si hiciera
falta.

**¿No es raro que un proyecto de IA no use un LLM?**
Al contrario: es criterio de ingeniería. La buena práctica es elegir la
herramienta adecuada al problema. No todos los proyectos necesitan las mismas
tecnologías.

## Sobre la clasificación

**¿Cómo clasificas tipo y departamento?**
Dos regresiones logísticas sobre un TF-IDF compartido (word + char n-gramas): una
para el tipo (5 clases), otra para el departamento (6). En la evaluación con frases
disjuntas —fraseo nunca visto en entrenamiento— da 0,965 de exactitud en tipo
(azar ~0,20) y 0,892 en departamento (azar ~0,17), con brechas train-test de 0,035
y 0,108: generaliza sin memorizar.

**¿Cómo das explicabilidad?**
Multiplico el vector TF-IDF por los coeficientes de la clase predicha y reporto los
términos de mayor contribución. Son las palabras que empujaron la decisión.

## Sobre reglas y plazos

**¿Cómo asignas la prioridad?**
Una base por tipo (denuncia alta, queja/reclamo media, petición/sugerencia baja) y
la elevo a alta si hay términos de urgencia (seguridad, salud, cortes, fugas,
fraude, personas vulnerables). Todo con razones registradas, y la urgencia actúa
aunque el tipo sea incierto.

**¿Por qué los plazos en días hábiles?**
Porque la ley casi siempre cuenta en días hábiles. Un plazo en días naturales
podría caer en fin de semana y ser incorrecto. Sumo días hábiles saltando sábados
y domingos; los festivos son una extensión en un único punto.

## Sobre la incertidumbre

**¿Qué pasa si el clasificador no está seguro?**
Si la confianza del tipo está bajo el umbral, marco `uncertain` y la solicitud va
a revisión humana, pero con departamento, prioridad y plazo ya calculados para que
el humano arranque desde un borrador útil. No enruto a ciegas.

## Sobre el diseño

**¿Qué cubren las pruebas?**
Los clasificadores (con una prueba de exactitud en datos no vistos), las reglas
(aritmética de días hábiles, SLA por tipo, prioridad y urgencia), el router
(incluida la bandera de incertidumbre), la API y la CLI. Cobertura 98 %.

## Pregunta trampa

**Si subes `PQ_MIN_CONFIDENCE` a 0,9, ¿qué pasa?**
Muchas más solicitudes se marcan como inciertas y van a revisión humana: subes la
seguridad (menos enrutamientos automáticos erróneos) a costa de la automatización
(más trabajo manual). Es la palanca donde la entidad fija ese equilibrio. Y como
la urgencia actúa aparte, una solicitud urgente nunca se desprioriza por ese
umbral.
