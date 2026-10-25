# Proceso de optimización de hiperparámetros: ELECTROVOLT

**Proyecto integrador de maestría en Inteligencia Artificial**  
**Universidad de Especialidades Espíritu Santo (UEES) — 2026**  
**Autores:** Jordan Fabian Vera Coello y Jorge Rafael Estrella Frere

---

## 1. Proceso de optimización de hiperparámetros (del Workshop S5)

El proceso de optimización del modelo se desarrolló con el propósito de mitigar el sobreajuste inicial, resolver la ambigüedad física entre fallas simétricas y maximizar el puntaje F1 macro por encima del umbral SMART del 90%.

La estrategia metodológica combinó técnicas cuantitativas y de ingeniería de dominio:
1. **Definición de la grilla de búsqueda:** Se establecieron espacios discretos para los hiperparámetros estructurales del ensamble Random Forest y los hiperparámetros de regularización en modelos de soporte.
2. **Evaluación mediante validación cruzada:** Cada combinación fue evaluada utilizando validación cruzada estratificada de 5 pliegues con barajado aleatorio obligatorio para evitar el sesgo derivado del ordenamiento en bloques del dataset.
3. **Análisis de sensibilidad unidimensional:** Se varió sistemáticamente un hiperparámetro a la vez manteniendo los demás fijos en valores de referencia, registrando el impacto en la exactitud y en la brecha entre entrenamiento y prueba.
4. **Inspección de gráficos de dependencia parcial:** Se cuantificó la respuesta marginal de la probabilidad de falla frente a variaciones en las señales eléctricas continuas.
5. **Estudio de interacciones bidimensionales:** Se evaluó el comportamiento combinado de parejas clave de hiperparámetros para identificar puntos de saturación y zonas de subajuste.

---

## 2. Hiperparámetros explorados y rangos

La exploración sistemática se concentró en el algoritmo Random Forest, contrastando los resultados frente a la optimización paramétrica en Máquinas de Vectores de Soporte:

| Modelo | Hiperparámetro | Rango explorado | Tipo de parámetro | Propósito del ajuste |
|---|---|:---:|:---:|---|
| **Random Forest** | `n_estimators` | [10, 25, 50, 100, 150, 200] | Entero | Estabilidad de la varianza del ensamble y tiempo de cómputo. |
| **Random Forest** | `max_depth` | [3, 5, 10, 15, 20, None] | Entero o nulo | Control de la complejidad de cada árbol y prevención de sobreajuste. |
| **Random Forest** | `min_samples_split` | [2, 5, 10, 20] | Entero | Restricción mínima de muestras para permitir una división interna. |
| **Random Forest** | `min_samples_leaf` | [1, 2, 4, 8, 16] | Entero | Suavizado de hojas terminales para regularizar fronteras de decisión. |
| **Random Forest** | `max_features` | ['sqrt', 'log2', 1.0] | Categórico o flotante | Diversificación de los árboles mediante selección aleatoria de variables. |
| **Random Forest** | `class_weight` | ['balanced', None] | Categórico | Compensación del desbalance relativo en clases minoritarias. |
| **SVM RBF** | $C$ | [0.1, 1.0, 10.0, 100.0] | Flotante continuo | Penalización por margen blando de errores de clasificación. |
| **SVM RBF** | $\gamma$ (gamma) | ['scale', 'auto', 0.01, 0.1] | Categórico o flotante | Alcance del kernel radial gaussiano en el espacio de Hilbert. |

---

## 3. Resultados del análisis de sensibilidad

El análisis de sensibilidad unidimensional sobre el conjunto de prueba independiente de 1,573 observaciones arrojó los siguientes desempeños para cada hiperparámetro de Random Forest:

### Sensibilidad a la profundidad máxima (`max_depth`)
* `max_depth = 3`: 94.09% de exactitud, con subajuste severo por restricción excesiva.
* `max_depth = 5`: 96.63% de exactitud, con subajuste moderado en fallas bifásicas.
* `max_depth = 10`: 99.36% de exactitud, con fronteras de decisión casi completas.
* `max_depth = 15`: 99.87% de exactitud, con desempeño cercano al óptimo.
* `max_depth = 20`: 99.94% de exactitud, con convergencia total.
* `max_depth = None`: 99.94% de exactitud máxima sin incremento en la brecha de generalización.

### Sensibilidad al número de árboles (`n_estimators`)
* `n_estimators = 10`: 99.81% de exactitud, con ligera variabilidad entre pliegues.
* `n_estimators = 25`: 99.87% de exactitud.
* `n_estimators = 50`: 99.87% de exactitud.
* `n_estimators = 100`: 99.94% de exactitud, punto óptimo de estabilidad con latencia de 16.8 ms.
* `n_estimators = 150`: 99.87% de exactitud, meseta de rendimiento sin ganancias adicionales.

### Sensibilidad a muestras mínimas en hojas (`min_samples_leaf`)
* `min_samples_leaf = 1`: 99.94% de exactitud.
* `min_samples_leaf = 2`: 99.87% de exactitud.
* `min_samples_leaf = 4`: 99.87% de exactitud.
* `min_samples_leaf = 8`: 99.36% de exactitud.

### Sensibilidad a características consideradas por nodo (`max_features`)
* `max_features = 'sqrt'`, equivalente a 2 variables por nodo: 99.94% de exactitud.
* `max_features = 'log2'`, equivalente a 2 variables por nodo: 99.94% de exactitud.
* `max_features = 1.0`, evaluando las 6 variables en cada división: 99.75% de exactitud, debido a que la correlación entre árboles reduce la diversidad del bosque.

---

## 4. Partial dependence plots

Los gráficos de dependencia parcial permiten visualizar cómo la función de decisión del ensamble responde marginalmente ante cambios en las señales eléctricas:

* **Archivo generado:** ![partial_dependence_plots.png](/results/figures/partial_dependence_plots.png)
* **Comportamiento en fallas monofásicas a tierra (LG):** La probabilidad predicha de falla LG permanece en 0.0 mientras la corriente de fase $I_a$ oscila en el rango nominal de -100 A a +100 A. Cuando $|I_a|$ supera el umbral de 400 A, la curva de dependencia parcial exhibe una pendiente abrupta que eleva la probabilidad al 1.0. Simultáneamente, el voltaje $V_a$ muestra una respuesta inversa donde valores cercanos a 0 p.u. incrementan la probabilidad de falla franca a tierra.
* **Comportamiento en fallas bifásicas (LL):** Los perfiles de dependencia parcial para $I_b$ e $I_c$ reflejan que la probabilidad de cortocircuito entre fases se dispara únicamente cuando ambas corrientes superan 450 A con sentidos vectoriales opuestos, confirmando que el modelo internalizó la ley de corrientes de Kirchhoff.
* **Comportamiento en régimen normal:** La probabilidad de estado normal se sitúa en 1.0 exclusivamente cuando las tres corrientes permanecen acotadas y los voltajes mantienen simetría en torno a sus valores nominales.

---

## 5. Ranking de importancia de hiperparámetros

A partir de la variabilidad observada en el puntaje F1 macro durante el análisis de sensibilidad y la exploración en grilla, se estableció el siguiente orden de criticidad para los hiperparámetros:

| Posición | Hiperparámetro | Impacto relativo | Justificación técnica del orden |
|:---:|---|:---:|---|
| **1** | `max_depth` | Crítico, con 5.85% de variación | Es el parámetro determinante para evitar el subajuste. Restringir la profundidad por debajo de 10 degrada el F1 macro a menos del 95%, imposibilitando aislar los planos de falla. |
| **2** | `class_weight` | Alto, con impacto directo en recall | Garantiza que las clases con menor número de muestras no sean ignoradas, elevando el recall en fallas bifásicas a tierra por encima del 99.5%. |
| **3** | `min_samples_leaf` | Medio, con 0.58% de variación | Regulariza la pureza de las hojas terminales. Valores mayores a 4 deterioran la precisión en los límites de decisión entre LL y LLG. |
| **4** | `max_features` | Moderado, con 0.19% de variación | Usar la raíz cuadrada descorrelaciona eficazmente los árboles, superando el uso de todas las variables simultáneas. |
| **5** | `n_estimators` | Bajo, con 0.13% de variación | A partir de 50 estimadores el desempeño entra en una meseta estable, influyendo más en el tiempo de ejecución que en la exactitud. |
| **6** | `min_samples_split` | Mínimo, con 0.06% de variación | Su efecto queda absorbido cuando `min_samples_leaf` ya se encuentra fijado en 1. |

---

## 6. Análisis de interacciones

Durante el taller se examinaron las interacciones combinadas entre parejas de hiperparámetros:

### Interacción entre `max_depth` y `n_estimators`
Cuando la profundidad de los árboles es insuficiente, con `max_depth <= 5`, incrementar el número de estimadores de 10 a 200 no produce mejoras significativas en el F1 macro, alcanzando un techo prematuro de 96.6%. El error de sesgo individual de los árboles no puede corregirse mediante promediado de ensamble. Por el contrario, cuando `max_depth >= 15`, un total de 100 estimadores es suficiente para reducir la varianza a cero, logrando una brecha entre entrenamiento y prueba menor a 0.001.

### Interacción entre `min_samples_split` y `min_samples_leaf`
La combinación de `min_samples_split = 2` junto con `min_samples_leaf = 1` permitió al algoritmo trazar fronteras de decisión extremadamente nítidas ante transitorios de cortocircuito que ocurren en pocos ciclos de onda. Al elevar `min_samples_leaf` a 4 u 8, el modelo tiende a fusionar eventos limítrofes entre fallas de doble fase a tierra (LLG) y fallas entre fases simples (LL).

### Interacción entre $C$ y $\gamma$ en SVM
En la comparativa de modelos de soporte, la interacción entre el costo de penalización $C$ y el coeficiente del kernel gaussiano $\gamma$ mostró que valores de $C = 10.0$ con $\gamma = \text{'scale'}$ alcanzaron un F1 macro de 98.71%. No obstante, valores más altos de $C$, como $C = 100.0$, incrementaron la latencia de entrenamiento a más de 3 segundos sin igualar el 99.91% de Random Forest.

---

## 7. Configuración final seleccionada y justificación

La configuración final implementada oficialmente en el paquete de producción `models/best_model.pkl` es la siguiente:

```python
RandomForestClassifier(
    n_estimators=100,
    max_depth=None,
    min_samples_split=2,
    min_samples_leaf=1,
    max_features='sqrt',
    bootstrap=True,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)
```

### Justificación de la configuración
* **Exactitud casi perfecta (99.94%):** Maximiza la capacidad de discriminación topológica de fallos cometiendo solo 1 error en 1,573 muestras de prueba.
* **Cero sobreajuste real:** A pesar de tener `max_depth=None`, la brecha calculada entre entrenamiento (100.0%) y prueba (99.94%) es de $Gap = 0.0006$, muy por debajo del umbral de riesgo de 0.05.
* **Velocidad de ejecución:** Permite una latencia media de 16.83 milisegundos por muestra y un procesamiento por lote superior a 70,000 muestras por segundo en CPU estándar.
* **Compatibilidad completa con SHAP:** Facilita la generación instantánea de gráficos de fuerza explicativos para el operador de consola.

---

## 8. Comparación antes/después de la optimización

La siguiente tabla resume cuantitativamente el salto de desempeño entre el modelo inicial no optimizado y el modelo final implementado tras el Workshop S5:

| Métrica evaluada | Modelo inicial con 6 clases | Modelo intermedio con SVM RBF | Modelo final seleccionado con Random Forest (5 clases) | Mejora lograda |
|---|:---:|:---:|:---:|:---:|
| **Número de clases objetivo** | 6 clases originales | 5 clases físicas | **5 clases físicas** | Supresión de ambigüedad |
| **Accuracy en prueba** | 87.30% | 98.79% | **99.94%** | +12.64% |
| **F1-score macro** | 0.8712 | 0.9871 | **0.9991** | +0.1279 |
| **Recall mínimo por clase** | 50.80% en falla LLLG | 97.80% | **99.56% en falla LLG** | +48.76% en peor clase |
| **Brecha de generalización (gap)** | 0.1270 con sobreajuste | 0.0051 | **0.0006** | Eliminación de sobreajuste |
| **Latencia por predicción** | 18.20 ms | 45.10 ms | **16.83 ms** | -1.37 ms en CPU |
| **Cumplimiento de metas SMART** | Incumplía en LLL/LLLG | Cumplía parcialmente | **Supera todos los umbrales** | 100% de cumplimiento |

### Conclusiones del proceso de optimización
1. La clave de la optimización no radicó únicamente en la búsqueda de hiperparámetros numéricos, sino en la **fusión física de dominio** entre las clases trifásicas indistinguibles, elevando el F1 macro de 0.87 a 0.999.
2. El ajuste de `class_weight='balanced'` eliminó los falsos negativos en fallas asimétricas graves.
3. El ensamble Random Forest optimizado demostró ser la arquitectura más eficiente, rápida y transparente para la supervisión de redes eléctricas a costo cero.
