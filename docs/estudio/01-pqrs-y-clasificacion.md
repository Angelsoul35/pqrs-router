# 01 — PQRS y la clasificación

## Qué es PQRS

PQRS es el modelo estándar de atención al ciudadano en gran parte de
Latinoamérica:

- **P**etición: una solicitud de información o de una actuación.
- **Q**ueja: insatisfacción con la conducta o el servicio.
- **R**eclamo: exigir que se corrija una falla concreta.
- **S**ugerencia: una propuesta de mejora.
- (+ **Denuncia**: reporte de una posible irregularidad.)

Cada tipo tiene un **plazo legal** de respuesta. Una entidad pública recibe muchos
mensajes sin estructurar y está obligada a responder cada uno a tiempo. Equivocar
el enrutamiento o pasarse del plazo tiene consecuencias reales.

## El problema de clasificación

De un mensaje en texto libre hay que deducir dos cosas:

- el **tipo** PQRS (una de 5 clases);
- el **departamento** que debe atenderlo (facturación, técnico, legal, atención al
  cliente, infraestructura, general).

Son dos preguntas de lenguaje, así que se aprenden de datos.

## Los modelos

Dos regresiones logísticas comparten un mismo **vectorizador TF-IDF**:

- un modelo predice el **tipo** (5 clases);
- otro predice el **departamento** (6 clases).

TF-IDF convierte el texto en números dando más peso a las palabras distintivas.
La regresión logística es un clasificador lineal: una suma ponderada de esas
palabras.

### ¿Por qué modelos lineales?

Tres razones, importantes en la ventanilla de una entidad pública:

- **Rápidos y baratos:** clasifican en microsegundos y no cuestan por solicitud.
  A volúmenes de intake, esto importa.
- **Deterministas:** el mismo mensaje se enruta siempre igual → reproducible y
  testeable.
- **Explicables:** la decisión es una suma ponderada de palabras, así que los
  términos que más contribuyen **son** la explicación, sin maquinaria extra.

Cada predicción trae una **confianza** (probabilidad), que luego usamos para
decidir si la decisión es fiable o va a revisión (guía 03).

### Calidad

En datos de validación (que el modelo no vio), la exactitud de tipo y de
departamento es muy alta, porque el lenguaje de estas solicitudes es distintivo.

## La explicabilidad, paso a paso

Para el tipo predicho: se toman los coeficientes de esa clase, se multiplican por
el vector TF-IDF del mensaje, y se reportan los términos de mayor contribución
positiva. Son las palabras que empujaron la clasificación.

## Para fijar la idea

- PQRS = petición, queja, reclamo, sugerencia (+ denuncia); cada tipo con su plazo.
- Dos modelos lineales (tipo y departamento) sobre un TF-IDF compartido.
- Lineales porque son rápidos, deterministas y explicables: lo adecuado para
  intake de alto volumen y auditable.
