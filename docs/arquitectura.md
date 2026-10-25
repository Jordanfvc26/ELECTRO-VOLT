# Arquitectura del sistema y pipeline de datos: ELECTROVOLT

**Proyecto integrador de maestría en Inteligencia Artificial**  
**Universidad de Especialidades Espíritu Santo (UEES) — 2026**  
**Autores:** Jordan Fabian Vera Coello y Jorge Rafael Estrella Frere  

---

## 1. Tipo de modelo seleccionado y justificación

Para el núcleo analítico de ElectroVOLT se seleccionó un algoritmo de ensamble basado en árboles de decisión: **Random Forest Classifier**.

### Justificación de la selección
* **Capacidad de modelado no lineal:** El comportamiento transitorio de una red eléctrica durante cortocircuitos involucra acoplamientos electromagnéticos inductivos y capacitivos entre conductores. Los modelos lineales, como la regresión logística evaluada como baseline, solo alcanzaron un 75.4% de exactitud debido a su incapacidad para trazar fronteras de decisión curvadas en el espacio multidimensional. Random Forest construye hiperplanos ortogonales combinados que capturan estas relaciones con un 99.94% de exactitud.
* **Baja latencia en inferencia sobre CPU:** A diferencia de las redes neuronales convolucionales o arquitecturas profundas recurrentes que demandan cientos de milisegundos y aceleración por GPU, el bosque aleatorio ejecuta la inferencia en 16.83 milisegundos sobre un procesador estándar, lo que viabiliza el monitoreo continuo en subestaciones sin inversión en hardware costoso.
* **Integración nativa con explicabilidad algorítmica:** La arquitectura de árboles permite emplear el algoritmo `TreeExplainer` de SHAP, el cual calcula los valores de Shapley exactos en tiempo polinómico. Modelos opacos de caja negra requerirían métodos de perturbación tipo KernelSHAP, cuyo costo computacional colapsa el tiempo de respuesta interactivo.
* **Huella de memoria liviana y portabilidad:** El modelo serializado comprimido ocupa 480 KB en disco y menos de 15 MB en memoria RAM activa, facilitando su alojamiento en servidores en la nube de capa gratuita sin riesgo de saturación de recursos.

---

## 2. Arquitectura detallada del modelo

El estimador central es una instancia de `RandomForestClassifier` implementada en Scikit-Learn, optimizada para clasificación multiclase balanceada.

### Configuración de hiperparámetros
* **`n_estimators` = 100:** Número de árboles de decisión independientes que conforman el ensamble. Este valor asegura estabilidad estadística en la votación mayoritaria sin incrementar la latencia de respuesta.
* **`criterion` = 'gini':** Función para medir la calidad de las divisiones en cada nodo interno mediante el índice de impureza de Gini.
* **`max_depth` = None:** Permite que los nodos se expandan hasta que todas las hojas sean puras o contengan menos muestras del umbral de división, aprovechando la ausencia de ruido en el dataset de entrenamiento.
* **`min_samples_split` = 2:** Cantidad mínima de observaciones requeridas para dividir un nodo interno.
* **`min_samples_leaf` = 1:** Cantidad mínima de muestras requeridas para formar una hoja terminal.
* **`max_features` = 'sqrt':** En cada nodo se considera un subconjunto aleatorio de $\sqrt{6} \approx 2$ variables predictoras, descorrelacionando los árboles y fortaleciendo la generalización del ensamble.
* **`bootstrap` = True:** Cada árbol se construye a partir de una muestra bootstrap generada con reemplazo del conjunto de entrenamiento.
* **`class_weight` = 'balanced':** Ajusta automáticamente los pesos de las clases de forma inversamente proporcional a sus frecuencias, mitigando el sesgo hacia las clases mayoritarias.
* **`random_state` = 42:** Semilla determinista que garantiza la reproducibilidad exacta del modelo en cualquier entorno.
* **`n_jobs` = -1:** Emplea todos los núcleos disponibles de la CPU durante el entrenamiento y la inferencia masiva.

### Contrato dimensional del modelo
* **Espacio de entrada:** Vector unidimensional de seis variables numéricas continuas:
  $$\mathbf{x} = [V_a, V_b, V_c, I_a, I_b, I_c] \in \mathbb{R}^6$$
* **Espacio de salida discreto:** Asignación a una de las cinco clases operativas:
  $$y \in \{\text{Normal}, \text{LG}, \text{LL}, \text{LLG}, \text{Trifásica}\}$$
* **Distribución de probabilidades:** Vector de cinco probabilidades calibradas por la fracción de árboles que votaron por cada categoría:
  $$\mathbf{p} = [P(\text{Normal}), P(\text{LG}), P(\text{LL}), P(\text{LLG}), P(\text{Trifásica})], \quad \sum_{i=1}^5 P_i = 1.0$$
* **Nivel de confianza operativa:** Probabilidad máxima asignada:
  $$\text{Confianza} = \max(\mathbf{p}) \times 100\%$$

### Componente de explicabilidad acoplado
* **Algoritmo:** `shap.TreeExplainer(model=random_forest)`.
* **Salida de explicabilidad:** Tensor tridimensional de atribución local de dimensiones $(1 \times 6 \times 5)$, donde cada valor representa la contribución aditiva en unidades de log-odds de una señal física sobre la predicción de cada estado posible.

---

## 3. Diagrama de flujo del sistema completo

```
 ┌─────────────────────────────────────────────────────────────┐
 │               FUENTES DE ENTRADA AL SISTEMA                 │
 │  - Panel de telemetría manual (sliders / inputs numéricos)   │
 │  - Ingesta masiva de oscilografía (archivo CSV por lote)    │
 └──────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │           CAPA DE VALIDACIÓN Y CONTRATO DE ENTRADA          │
 │  - Verificación de tipos numéricos flotantes                 │
 │  - Validación de existencia de columnas Va, Vb, Vc, Ia, Ib, Ic│
 │  - Ordenamiento canónico estricto de señales                │
 └──────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │            NÚCLEO PREDICTIVO (best_model.pkl)               │
 │  - Inferencia de clase con Random Forest (100 árboles)      │
 │  - Extracción de probabilidades por clase (predict_proba)   │
 │  - Cronometraje de latencia de ejecución en milisegundos    │
 └──────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │         MOTOR DE INTELIGENCIA ARTIFICIAL EXPLICABLE         │
 │  - Cálculo de valores de Shapley mediante TreeExplainer     │
 │  - Identificación de fases con mayor aporte a la anomalía   │
 │  - Normalización fasorial para visualización comprensible   │
 └──────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │            CAPA DE ENRIQUECIMIENTO OPERACIONAL              │
 │  - Asignación de mensaje técnico de MENSAJES_OPERADOR       │
 │  - Mapeo cromático de severidad (verde, ámbar, rojo)        │
 │  - Verificación de umbral de confianza mínima               │
 └──────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │       CAPA DE PRESENTACIÓN Y SALIDA (DASHBOARD SCADA)       │
 │  - Diagnóstico en tiempo real y oscilograma trifásico 60 Hz │
 │  - Gráfico de fuerza explicativo local (SHAP force plot)    │
 │  - Tablas interactivas con resumen estadístico de lotes     │
 │  - Módulo de descargas: reportes en PDF, Excel y CSV        │
 └─────────────────────────────────────────────────────────────┘
```

---

## 4. Pipeline de datos: desde la entrada hasta la salida

El flujo de información dentro del código sigue una secuencia modular y determinista:

### Paso 1: Ingesta y validación
Las lecturas ingresan a través del formulario interactivo o mediante la carga de un archivo CSV en el componente de subida de Streamlit. La función `validar_columnas()` comprueba que el vector contenga las seis magnitudes físicas requeridas sin valores nulos ni tipos incompatibles.

### Paso 2: Conformación del vector canónico
Los valores son organizados en un DataFrame de Pandas respetando el orden estricto definido en `src.utils.COLUMNAS`:
```python
columnas = ["Va", "Vb", "Vc", "Ia", "Ib", "Ic"]
X_input = df[columnas]
```
Esta rigurosidad evita desalineaciones posicionales entre las fases durante el paso por los árboles de decisión.

### Paso 3: Inferencia supervisada
El paquete serializado en `models/best_model.pkl` es cargado en memoria mediante la función con caché `@st.cache_resource` para evitar recargas en cada interacción. Se ejecutan los métodos:
```python
prediccion = modelo.predict(X_input)
probabilidades = modelo.predict_proba(X_input)
```

### Paso 4: Extracción de explicabilidad local con SHAP
Cuando el usuario solicita el análisis explicativo, la función `obtener_explicacion_shap()` calcula los valores de Shapley para la muestra activa respecto a la clase predicha:
```python
explicador = shap.TreeExplainer(modelo)
valores_shap = explicador.shap_values(X_input)
```
Esto permite saber con precisión qué variable (por ejemplo, una sobrecorriente de 850 A en la fase B) fue la determinante para emitir la alarma.

### Paso 5: Generación de alertas y recomendaciones operativas
El diagnóstico resultante se cruza con el diccionario `MENSAJES_OPERADOR`. Si la falla clasificada es `Trifásica`, el sistema informa automáticamente que las señales de fase no distinguen si existe contacto a tierra, instruyendo al operador a revisar la corriente residual de neutro.

### Paso 6: Renderizado y exportación
* Si la inferencia fue individual, se actualiza el velocímetro de confianza, el oscilograma dinámico a 60 Hz y el desglose de fases en el panel SCADA.
* Si la inferencia fue por lote, se agrega la columna de diagnóstico y nivel de certeza a la tabla tabular, habilitando los botones de descarga con los módulos de `app.exports` para generar documentos en PDF corporativo mediante ReportLab, hojas de cálculo en Excel con OpenPyXL o archivos planos CSV.

---

## 5. Tecnologías y librerías utilizadas

Todas las herramientas empleadas corresponden a tecnologías abiertas y estándares de la industria, garantizando una arquitectura reproducible a costo cero:

| Herramienta o librería | Versión requerida | Rol específico en la arquitectura |
|---|:---:|---|
| **Python** | 3.10 o 3.12 | Entorno de desarrollo base y ejecución del pipeline backend. |
| **Scikit-Learn** | $\ge$ 1.3.0 | Algoritmos de aprendizaje automático supervisado, validación cruzada estratificada y métricas de desempeño. |
| **SHAP** | $\ge$ 0.42.0 | Motor de interpretabilidad algorítmica y cálculo de valores de Shapley mediante `TreeExplainer`. |
| **Pandas** | $\ge$ 2.0.0 | Manipulación estructurada de matrices tabulares, agrupaciones y lectura de datasets CSV. |
| **NumPy** | $\ge$ 1.24.0 | Operaciones matemáticas vectorizadas sobre las ondas de tensión y corriente. |
| **Streamlit** | $\ge$ 1.30.0 | Plataforma web interactiva para el despliegue del panel SCADA industrial y enrutamiento SPA multipágina. |
| **Joblib** | $\ge$ 1.3.0 | Serialización binaria eficiente y compresión del artefacto del modelo entrenado. |
| **Altair** | $\ge$ 5.0.0 | Generación de oscilogramas trifásicos dinámicos interactivos a 60 Hz. |
| **Matplotlib** | $\ge$ 3.7.0 | Renderizado de figuras científicas estáticas para matrices de confusión y curvas comparativas. |
| **Seaborn** | $\ge$ 0.12.0 | Estilización de mapas de calor para correlaciones de variables y residuos. |
| **ReportLab** | $\ge$ 4.0.0 | Generador programático de reportes ejecutivos de auditoría en formato PDF descargable. |
| **OpenPyXL** | $\ge$ 3.1.0 | Exportación estructurada de resultados de inferencia por lote en libros de cálculo Microsoft Excel. |
| **Pytest** | $\ge$ 8.0.0 | Suite de pruebas unitarias automatizadas para validación continua del código. |
| **Render** | Nube (Cloud) | Plataforma de alojamiento web gratuita para el despliegue continuo de la aplicación en producción. |
