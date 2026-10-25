# Análisis exploratorio de datos y preprocesamiento: ELECTROVOLT

**Proyecto integrador de maestría en Inteligencia Artificial**  
**Universidad de Especialidades Espíritu Santo (UEES) — 2026**  
**Autores:** Jordan Fabian Vera Coello y Jorge Rafael Estrella Frere  

---

## 1. Descripción detallada del dataset

El conjunto de datos utilizado en este proyecto corresponde al repositorio público *Electrical Fault Detection and Classification*, elaborado mediante simulaciones en el entorno MATLAB y Simulink sobre un sistema de transmisión de energía eléctrica trifásico operando a una frecuencia nominal de 60 Hz.

### Estructura y dimensiones
* **Archivo base:** `data/raw/classData.csv`.
* **Volumen total:** 7,861 observaciones y 10 columnas numéricas continuas y discretas.
* **Integridad:** 0 valores nulos en todas las columnas y 0 registros duplicados.

### Variables predictoras de entrada
Se compone de seis magnitudes físicas continuas medidas en las barras del sistema:
* $V_a, V_b, V_c$: Voltajes de fase instantáneos expresados en valores por unidad (p.u.).
* $I_a, I_b, I_c$: Corrientes de fase instantáneas expresadas en Amperios (A).

### Variables objetivo originales
Cuatro banderas binarias que describen el estado de la red:
* $G$: Indicador de presencia de falla a tierra (1 si existe contacto a tierra, 0 en caso contrario).
* $C$: Indicador de falla que involucra a la fase C (1 activo, 0 inactivo).
* $B$: Indicador de falla que involucra a la fase B (1 activo, 0 inactivo).
* $A$: Indicador de falla que involucra a la fase A (1 activo, 0 inactivo).

---

## 2. Estadísticas descriptivas

Las estadísticas descriptivas de las seis magnitudes analógicas de fase se presentan a continuación, calculadas sobre la totalidad de las 7,861 muestras del dataset:

| Métrica estadística | $V_a$ (p.u.) | $V_b$ (p.u.) | $V_c$ (p.u.) | $I_a$ (A) | $I_b$ (A) | $I_c$ (A) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Recuento (count)** | 7,861 | 7,861 | 7,861 | 7,861 | 7,861 | 7,861 |
| **Media (mean)** | -0.0077 | 0.0012 | 0.0065 | 13.7212 | -44.8453 | 34.3924 |
| **Desviación estándar (std)** | 0.2892 | 0.3134 | 0.3079 | 464.7417 | 439.2692 | 371.1074 |
| **Mínimo (min)** | -0.6207 | -0.6080 | -0.6127 | -883.5423 | -900.5270 | -883.3578 |
| **Primer cuartil (25%)** | -0.1303 | -0.1595 | -0.2160 | -119.8025 | -271.8459 | -61.0342 |
| **Mediana (50%)** | -0.0053 | 0.0016 | 0.0093 | 2.0428 | 5.5133 | -4.3267 |
| **Tercer cuartil (75%)** | 0.1116 | 0.1535 | 0.2400 | 227.2464 | 91.1943 | 49.1151 |
| **Máximo (max)** | 0.5953 | 0.6279 | 0.6002 | 885.7386 | 889.8689 | 901.2743 |

### Análisis de rangos y simetría
* **Señales de voltaje:** Los valores oscilan entre aproximadamente -0.62 p.u. y +0.63 p.u., con medias cercanas a cero, lo cual refleja la naturaleza oscilatoria sinusoidal de la red eléctrica. Las reducciones drásticas de voltaje están directamente asociadas a la proximidad eléctrica de cortocircuitos.
* **Señales de corriente:** En condiciones de régimen permanente normal, las corrientes se mantienen en magnitudes inferiores a 100 A. Durante eventos de falla franca, las corrientes alcanzan picos simétricos superiores a 880 A tanto en semiciclos positivos como negativos.

---

## 3. Visualizaciones del análisis exploratorio

A continuación se detallan las seis visualizaciones generadas para comprender la distribución física y el comportamiento de las señales:

### Gráfico 1: Distribución de las seis clases originales
* **Archivo:** ![distribucion_6_clases.png](/results/figures/distribucion_6_clases.png)
* **Descripción:** Muestra la cantidad de registros en cada una de las seis combinaciones originales de Kaggle: Normal (2,365 muestras), LLG (1,134 muestras), LLLG (1,133 muestras), LG (1,129 muestras), LLL (1,096 muestras) y LL (1,004 muestras).
* **Hallazgo:** Existe una proporción mayoritaria de muestras en estado normal (30.1%) y cantidades homogéneas cercanas a 1,100 registros en cada una de las cinco clases de perturbación.

### Gráfico 2: Distribución de las cinco clases de producción
* **Archivo:** ![distribucion_5_clases.png](/results/figures/distribucion_5_clases.png)
* **Descripción:** Ilustra la distribución resultante tras la unificación técnica de fallas trifásicas en una sola categoría: Normal (2,365 muestras), Trifásica (2,229 muestras), LLG (1,134 muestras), LG (1,129 muestras) y LL (1,004 muestras).
* **Hallazgo:** Las clases presentan un equilibrio operativo sólido, donde las fallas simétricas severas y el estado normal representan los dos grupos con mayor volumen de datos.

### Gráfico 3: Matriz de correlación de Pearson
* **Archivo:** ![matriz_correlacion.png](/results/figures/matriz_correlacion.png)
* **Descripción:** Mapa de calor que cuantifica la correlación lineal bivariada entre los seis canales de adquisición analógica.
* **Hallazgo:** Se evidencian correlaciones negativas moderadas entre voltajes de fase (Va contra Vb en -0.48 y Vb contra Vc en -0.57), correspondientes al desfase angular teórico de 120 grados en sistemas trifásicos equilibrados.

### Gráfico 4: Dispersión de corrientes de fase según la falla
* **Archivo:** ![boxplots_corrientes_clase.png](/results/figures/boxplots_corrientes_clase.png)
* **Descripción:** Diagrama de cajas que compara los rangos de corriente en las fases A, B y C para cada una de las cinco condiciones operativas.
* **Hallazgo:** Permite visualizar con claridad cómo en la falla LG la fase A experimenta amplitudes extremas mientras las fases B y C permanecen en niveles nominales bajos. En fallas LL y LLG las fases B y C reflejan sobrecorrientes conjuntas, y en fallas trifásicas las tres fases presentan dispersiones elevadas simultáneas.

### Gráfico 5: Matriz de confusión del modelo supervisado
* **Archivo:** ![matriz_confusion.png](/results/figures/matriz_confusion.png)
* **Descripción:** Evaluación del clasificador Random Forest sobre el conjunto de prueba independiente de 1,573 registros.
* **Hallazgo:** Diagonal dominante casi perfecta con 1,572 clasificaciones correctas y únicamente una muestra confundida entre LL y LLG, confirmando la separabilidad de las clases en el espacio de características.

### Gráfico 6: Importancia global y mapa de calor de explicabilidad con SHAP
* **Archivo:** ![shap_heatmap_clases.png](/results/figures/shap_heatmap_clases.png)
* **Descripción:** Representación del impacto de cada señal trifásica en la función de decisión del modelo por tipo de perturbación.
* **Hallazgo:** Las corrientes de fase dominan la predicción de fallas específicas (Ia en falla monofásica LG, Ib e Ic en fallas bifásicas LL), mientras que los voltajes aportan la justificación de estabilidad en el estado normal.

---

## 4. Identificación de patrones, correlaciones y valores extremos

### Patrones de comportamiento físico
* **Régimen normal:** Amplitudes de corriente reducidas y tensiones trifásicas simétricas con desfasaje angular balanceado.
* **Falla monofásica a tierra (LG):** Incremento súbito de la corriente en la fase en contacto con tierra (fase A en este dataset), acompañado de una caída de tensión en dicha fase por efecto de la impedancia de falla.
* **Falla entre fases (LL):** Elevación simétrica de corriente entre las dos fases en cortocircuito (fases B y C), circulando en sentidos opuestos y sin elevación de corriente de retorno por tierra.
* **Falla de doble fase a tierra (LLG):** Sobrecorrientes en dos fases con presencia simultánea de corriente de desbalance retornando hacia la tierra.
* **Falla trifásica simétrica:** Afectación simultánea de los tres conductores con sobrecorrientes elevadas y voltajes colapsados hacia cero en el punto de contacto.

### Matriz de correlación entre señales
Los coeficientes de Pearson calculados sobre las variables continuas son:

| Variable | $V_a$ | $V_b$ | $V_c$ | $I_a$ | $I_b$ | $I_c$ |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **$V_a$** | 1.000 | -0.480 | -0.450 | 0.036 | 0.029 | -0.069 |
| **$V_b$** | -0.480 | 1.000 | -0.567 | -0.275 | 0.032 | -0.057 |
| **$V_c$** | -0.450 | -0.567 | 1.000 | 0.246 | -0.060 | 0.123 |
| **$I_a$** | 0.036 | -0.275 | 0.246 | 1.000 | -0.374 | -0.276 |
| **$I_b$** | 0.029 | 0.032 | -0.060 | -0.374 | 1.000 | -0.528 |
| **$I_c$** | -0.069 | -0.057 | 0.123 | -0.276 | -0.528 | 1.000 |

### Análisis de valores extremos (outliers)
En el análisis exploratorio se identifican mediciones de corriente que superan los 800 A, alejadas de la media general situada en torno a 0 A. Sin embargo, en el dominio de la ingeniería eléctrica estos registros **no constituyen valores atípicos espurios ni errores de medición**. Representan el régimen transitorio de cortocircuito que el modelo debe aprender a detectar. Por tal razón, ningún registro extremo fue eliminado ni truncado arbitrariamente.

---

## 5. Decisiones de preprocesamiento justificadas

A partir del análisis exploratorio se adoptaron tres decisiones metodológicas fundamentales:

### Detección y mitigación del ordenamiento en bloques
* **Hallazgo:** El archivo original contiene 7,861 registros agrupados en bloques secuenciales continuos por tipo de falla. Si se aplicara una partición temporal o sin barajado, los conjuntos de entrenamiento y prueba recibirían clases incompletas, provocando fugas de información y métricas irreales.
* **Decisión:** Implementación forzosa del parámetro `shuffle=True` con semilla fija 42 en toda partición estratificada (`StratifiedShuffleSplit` y `StratifiedKFold`), garantizando que cada subconjunto preserve la representatividad estadística de todos los estados.

### Fusión física de clases trifásicas (5 clases de producción)
* **Demostración experimental:** Se aisló el subconjunto de muestras pertenecientes a fallas trifásicas simétricas (LLL) y trifásicas a tierra (LLLG). Al entrenar un clasificador Random Forest utilizando únicamente las seis lecturas de fase ($V_a, V_b, V_c, I_a, I_b, I_c$), la exactitud obtenida fue del 50.8%, equivalente a una predicción aleatoria.
* **Justificación física:** En una falla trifásica simétrica balanceada, la suma fasorial de corrientes es igual a cero ($I_a + I_b + I_c = 0$), lo que implica que no circula corriente por el neutro ni por la conexión a tierra ($I_n = 0\text{ A}$). Por ende, las seis señales de fase no contienen información física para diferenciar si el cortocircuito involucra tierra o no.
* **Decisión:** Unificación de LLL y LLLG bajo la clase `Trifásica`, evitando sobreajuste y ajustando el modelo a la realidad operativa de subestación, donde la orden de disparo de protecciones es idéntica en ambos casos.

### Partición estratificada y escalado de características
* **Partición de datos:** División del 80% para entrenamiento (6,288 muestras) y 20% para evaluación independiente (1,573 muestras), preservando la proporción original de cada categoría.
* **Normalización:** Las señales numéricas se mantienen en su escala física original para el entrenamiento de Random Forest, facilitando la interpretación directa en Amperios y p.u. Para los modelos baseline sensibles a escala (regresión logística y SVM), se integró `StandardScaler` dentro de pipelines desacoplados para evitar fugas entre particiones.

---

## 6. Manejo de datos faltantes y desbalanceados

### Manejo de datos faltantes
La auditoría ejecutada con `verificar_calidad_datos()` arrojó un total de 0 valores nulos en los 7,861 registros. En consecuencia, no fue necesario aplicar técnicas de imputación por media, mediana ni interpolación temporal, preservando la fidelidad de las ondas simuladas.

### Manejo del desbalance de clases
La distribución porcentual de las cinco clases oficiales es la siguiente:
* Normal: 30.09% (2,365 muestras)
* Trifásica: 28.35% (2,229 muestras)
* LLG: 14.43% (1,134 muestras)
* LG: 14.36% (1,129 muestras)
* LL: 12.77% (1,004 muestras)

Para contrarrestar el desbalance moderado entre las clases mayoritarias (Normal y Trifásica) y las fallas bifásicas y monofásicas:
1. **Ponderación de clases:** Se configuró el hiperparámetro `class_weight='balanced'` en los algoritmos de Scikit-Learn. Esta técnica penaliza con mayor severidad los errores cometidos en clases con menor volumen de datos.
2. **Métricas de optimización:** Se seleccionó el puntaje F1 macro y el recall por clase como criterios rectores de decisión en lugar de la exactitud global simple, asegurando que ninguna topología de falla quede desatendida.
3. **Muestreo estratificado:** Tanto la partición inicial como la validación cruzada de 5 pliegues mantuvieron estrictamente las proporciones relativas en cada iteración.
