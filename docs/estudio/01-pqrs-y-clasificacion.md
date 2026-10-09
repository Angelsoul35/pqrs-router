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

### Evaluación sin fuga (over/underfitting)

Con datos sintéticos de plantillas, un split aleatorio daría ~1.0 de exactitud y
sería **mentira**: train y test compartirían las frases y mediríamos memoria. Por
eso `evaluation.py` hace un **split por frases disjuntas** (aperturas de tipo,
temas de departamento y cláusulas de contexto se parten; la prueba usa solo las
partes retiradas). Resultado sin fuga:

```
type accuracy      : 0.965  (5 tipos; azar ~0.20)   gap 0.035 -> no sobreajusta
department accuracy: 0.892  (6 áreas; azar ~0.17)   gap 0.108
```

Generaliza porque la señal de cada etiqueta está repartida en **vocabulario
recurrente** (invoice/charge, connection/signal, outage/leak...) que los n-gramas
de carácter reconocen aunque el fraseo exacto esté retirado. No hay underfitting
(muy por encima del azar) ni overfitting patológico (la brecha es pequeña). Además
usamos word + char n-grams (`FeatureUnion`) para capturar esas raíces.

### Validación con datos reales (quejas de la CFPB)

La evaluación por frases disjuntas mide la generalización a *fraseos* nuevos de
solicitudes sintéticas. La otra prueba es dato **real**: el mismo pipeline
(word + char TF-IDF + regresión logística) se entrena sobre un corpus real de
quejas de consumidores de la CFPB de EE. UU. (`fathyshalab/complaints`), enrutando
cada queja a su **producto financiero** — el análogo real de enrutar a un
departamento. Con `python -m pqrs_router.real_benchmark` sobre 3000 quejas
balanceadas en 10 clases:

```
CV accuracy    : 0.689 +/- 0.021   (azar 0.100 -> ~7x)
train / test   : 0.894 / 0.679     (gap 0.215, con C=0.3)
shuffled labels: 0.111             (colapsa al azar: la señal es real)

ruta de regularización (la exactitud de test es estable; la brecha es de train):
  C=0.2  train 0.868  test 0.676
  C=2.0  train 0.992  test 0.685
```

**La lección clave sobre over/underfitting está aquí.** El modelo lineal sobre
TF-IDF disperso **memoriza** el train (su exactitud sube a ~1.0 con C alto), así que
la brecha train/test crece con C. Pero la exactitud de **test apenas se mueve**
(~0.68) en toda la ruta: la brecha es memorización del train, no generalización
desperdiciada. Por eso usamos un `C=0.3` más regularizado (brecha sana 0.215) sin
perder test. El techo real (~0.68) no es overfitting: son categorías de la CFPB que
**se solapan de verdad** (p. ej. *Credit reporting* vs *Credit reporting, credit
repair services…*), que ni una persona separaría siempre bien. El control de
etiquetas barajadas (0.111 ≈ azar) confirma que lo aprendido es señal real.

## La explicabilidad, paso a paso

Para el tipo predicho: se toman los coeficientes de esa clase, se multiplican por
el vector TF-IDF del mensaje, y se reportan los términos de mayor contribución
positiva. Son las palabras que empujaron la clasificación.

## Para fijar la idea

- PQRS = petición, queja, reclamo, sugerencia (+ denuncia); cada tipo con su plazo.
- Dos modelos lineales (tipo y departamento) sobre un TF-IDF compartido.
- Lineales porque son rápidos, deterministas y explicables: lo adecuado para
  intake de alto volumen y auditable.
