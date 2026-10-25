# ELECTROVOLT — Detección y Clasificación Multiclase de Fallos Eléctricos con Machine Learning e IA Explicable (XAI)

[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Streamlit App](https://img.shields.io/badge/Frontend-Streamlit%201.30%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn%201.3%2B-F7931E?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![XAI Engine](https://img.shields.io/badge/XAI-SHAP%200.42%2B-002A69)](https://shap.readthedocs.io/)
[![Unit Tests](https://img.shields.io/badge/Tests-24%2F24%20Passing-brightgreen?logo=pytest)](tests/)
[![Architecture](https://img.shields.io/badge/Infraestructura-%240%20USD%20(Open%20Source)-blue)](#)
[![Status](https://img.shields.io/badge/Estado-Producci%C3%B3n%20%2F%20Validado-success)](#)

**ELECTRO-VOLT** es una plataforma web industrial de soporte a la decisión operativa en subestaciones y redes eléctricas de distribución. A partir de 6 lecturas trifásicas de voltaje y corriente ($V_a, V_b, V_c, I_a, I_b, I_c$), implementa un modelo de Machine Learning supervisado (**Random Forest**) optimizado que clasifica instantáneamente la topología de la red en 5 estados físicos con **99.94% de exactitud**. El sistema integra Inteligencia Artificial Explicable (**SHAP**) para entregar a los operadores una justificación física auditable en milisegundos, transformando inspecciones manuales reactivas de ~2 horas en diagnósticos inmediatos con una inversión de infraestructura de **$0 USD**.

---

## Tabla de Contenidos
1. [Descripción del Problema](#1-descripción-del-problema)
2. [Dataset y Mapeo Físico](#2-dataset-y-mapeo-físico)
3. [Metodología y Arquitectura](#3-metodología-y-arquitectura)
4. [Resultados y Comparativa de Modelos](#4-resultados-y-comparativa-de-modelos)
5. [Instalación y Uso Local](#5-instalación-y-uso-local)
6. [Interfaz de Usuario (Dashboard SCADA)](#6-interfaz-de-usuario-dashboard-scada)
7. [Estructura del Proyecto](#7-estructura-del-proyecto)
8. [Consideraciones Éticas y Limitaciones](#8-consideraciones-éticas-y-limitaciones)
9. [Autores y Contribuciones](#9-autores-y-contribuciones)
10. [Licencia](#10-licencia)
11. [Agradecimientos y Referencias](#11-agradecimientos-y-referencias)
12. [Videos y Enlaces Multimedia](#12-videos-y-enlaces-multimedia)

---

## 1. Descripción del Problema

### ¿Qué problema resuelve el proyecto?
En las redes eléctricas de potencia y distribución, los cortocircuitos entre fases y las fallas a tierra representan eventos críticos que provocan interrupciones no programadas del servicio, severo estrés electrodinámico y térmico en transformadores de subestación, y elevados riesgos para la seguridad del personal y la ciudadanía. 

Tradicionalmente, los relés de protección electromecánicos o numéricos de sobrecorriente (funciones IEEE 50/51/51N) despejan el circuito ante la superación de un umbral fijo; sin embargo, **no clasifican la topología exacta del fallo ni explican qué conductores están interactuando**. Por ello, el diagnóstico de la causa raíz depende de inspecciones manuales reactivas en campo que toman en promedio **2 horas**, dilatando los tiempos de restitución del suministro eléctrico.

### ¿Por qué es importante?
* **Calidad y continuidad del servicio (SAIDI / SAIFI):** Reduce de manera directa la duración equivalente de las interrupciones por cliente (SAIDI) y la frecuencia promedio (SAIFI), mitigando severas penalizaciones regulatorias emitidas por los entes de control.
* **Protección de activos críticos:** Minimiza las reconexiones a ciegas sobre fallas activas, previniendo la degradación y destrucción prematura de transformadores de potencia cuyos reemplazos superan los cientos de miles de dólares.
* **Seguridad operativa y linieros:** Brinda certeza previa sobre la fase energizada o involucrada en tierra antes del despliegue de las cuadrillas de mantenimiento.

### ¿Quiénes son los usuarios objetivo?
* **Usuarios Primarios (Directos):** Operadores de consola en subestaciones eléctricas, técnicos de mantenimiento predictivo/correctivo en líneas de distribución e ingenieros de protecciones y estudios de red.
* **Usuarios Secundarios (Institucionales):** Empresas distribuidoras de energía, el Operador Nacional de Electricidad e industrias con subestaciones dedicadas.

---

## 2. Dataset y Mapeo Físico

### Descripción y Fuente de los Datos
Para garantizar rigor, reproducibilidad y viabilidad a costo cero, el proyecto adoptó el dataset científico tabular:
* **Dataset Principal:** *Electrical Fault Detection and Classification* (Kaggle), generado a partir de simulaciones en MATLAB/Simulink de una red de transmisión trifásica a 60 Hz.
* **Fuente Oficial:** [Kaggle Dataset Link](https://www.kaggle.com/datasets/esathyaprakash/electrical-fault-detection-and-classification?select=detect_dataset.csv)
* **Licencia:** Dominio Público, libre para reutilización académica y/o tecnológica.
* **Dataset de Respaldo (Plan B):** *Hybrid Electrical Fault Detection Dataset (Real + Synthetic)* de Mendeley Data (22,000 registros), totalmente compatible con las 6 variables trifásicas.

### Características principales del conjunto de datos
* **Volumen:** 7,861 registros (archivo [`data/raw/classData.csv`] con 10 columnas numéricas.
* **Calidad de Datos:** **0 valores nulos** (100% de completitud) y **0 filas duplicadas**.
* **Variables Predictoras de Entrada (6 señales continuas):**
  * Voltajes de fase: $V_a, V_b, V_c$ (en valores por unidad, p.u.).
  * Corrientes de fase: $I_a, I_b, I_c$ (en Amperios, A).
* **Variables Objetivo:** 4 banderas binarias $[G, C, B, A]$ que identifican la presencia de falla a tierra ($G$) y las fases involucradas ($C, B, A$).

### Mapeo y Fusión Física a 5 Clases
En el dataset original de Kaggle se codifican 6 combinaciones:
1. `(0, 0, 0, 0)` $\rightarrow$ **Normal** (Sin perturbación, 2,365 muestras).
2. `(1, 0, 0, 1)` $\rightarrow$ **LG** (Fase A a tierra, 1,129 muestras).
3. `(0, 1, 1, 0)` $\rightarrow$ **LL** (Fases B-C entre sí, 1,004 muestras).
4. `(1, 0, 1, 1)` $\rightarrow$ **LLG** (Fases A-B y tierra, 1,134 muestras).
5. `(0, 1, 1, 1)` $\rightarrow$ **LLL** (Trifásica simétrica, 1,096 muestras).
6. `(1, 1, 1, 1)` $\rightarrow$ **LLLG** (Trifásica a tierra, 1,133 muestras).

> [NOTA]
> **Ajuste físico de dominio (fusión de clases):**  
> En una falla trifásica simétrica balanceada, la suma fasorial de las tres corrientes es nula ($\vec{I}_a + \vec{I}_b + \vec{I}_c = 0$), lo que significa que **por la conexión a tierra no circula corriente neutra ($I_n = 0\text{ A}$)**. Por tanto, las señales de fase ($V_a, V_b, V_c, I_a, I_b, I_c$) son idénticas e indistinguibles entre `LLL` y `LLLG`. Para evitar confusiones artificiales en los árboles de decisión, se consolidaron en una única clase física de producción: **`Trifásica`** (2,229 muestras).

---

## 3. Metodología y Arquitectura

```
                        FLUJO MODULAR DE ELECTRO-VOLT
 [ classData.csv ] 
        │
        ▼
 [ Ingesta & Limpieza ] ──► Verificación de nulos (0%) y rangos de tensión/corriente
        │
        ▼
 [ Mapeo Físico (5 Clases) ] ──► Normal, LG, LL, LLG, Trifásica
        │
        ▼
 [ Partición Estratificada ] ──► 80% Entrenamiento (6,288) / 20% Prueba (1,573) con shuffle=True
        │
        ▼
 [ Benchmarking Supervisado ]
   ├─ Baseline 1: Clasificador Aleatorio (~16.7%)
   ├─ Baseline 2: Regresión Logística + StandardScaler (F1: 74.8%)
   ├─ Candidato: SVM Kernel RBF + StandardScaler (F1: 98.7%)
   └─ Seleccionado: Random Forest (100 árboles, balanced) (F1: 99.91%)
        │
        ▼
 [ Validación Cruzada ] ──► StratifiedKFold (k=5) con F1-Macro = 0.9991 ± 0.0011
        │
        ▼
 [ IA Explicable (XAI) ] ──► TreeExplainer de SHAP (Explicación local y global)
        │
        ▼
 [ Empaquetado & Producción ] ──► models/best_model.pkl + Dashboard SCADA en Streamlit
```

### Preprocesamiento aplicado
1. **Verificación de Integridad:** Comprobación estricta de no nulidad y no duplicidad en `src/data_processing.py`.
2. **Estratificación y Barajado:** El dataset original contiene bloques secuenciales ordenados por clase. Se aplica `StratifiedShuffleSplit` (80% Train, 20% Test) con barajado forzoso (`shuffle=True, random_state=42`) para evitar fugas de información (*data leakage*).
3. **Escalado Controlado:** Se utiliza `StandardScaler` únicamente dentro de los `Pipelines` de scikit-learn para los modelos basados en distancia/hiperplanos (Regresión Logística y SVM), garantizando que las estadísticas de normalización provengan exclusivamente del conjunto de entrenamiento.

### Modelo Seleccionado y Justificación
Se seleccionó **Random Forest Classifier** (`n_estimators=100`, `class_weight='balanced'`, `random_state=42`):
* **No Linealidad y Robustez:** Modela con precisión la interacción multicanal entre fases acopladas electromagnéticamente.
* **Baja Latencia de Inferencia:** Permite evaluar predicciones individuales en **16.83 ms en CPU estándar**, cumpliendo holgadamente el criterio de aceptación SMART (< 100 ms).
* **Interpretabilidad Nativa con SHAP:** Compatible con algoritmos optimizados `TreeExplainer` de complejidad polinómica, a diferencia de los aproximadores KernelSHAP que colapsan en tiempo real.
* **Eficiencia Energética y Costo:** No requiere GPUs para entrenamiento (tiempo total de ajuste: **0.89 segundos**) ni para inferencia en servidores Cloud gratuitos.

---

## 4. Resultados y Comparativa de Modelos

### Evaluación Comparativa vs. Baselines
La evaluación sobre el conjunto de prueba independiente (*hold-out test set*, 1,573 muestras) demostró la superioridad del ensamble:

| Modelo Supervisado | Tipo de Modelo | Accuracy (Test) | F1-Score Macro | Gap (Train - Test) | Latencia CPU | Estado |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **Clasificador Aleatorio** | Baseline Teórico | 16.70% | 0.1667 | 0.0000 | < 1 ms | Descartado |
| **Regresión Logística** | Baseline Lineal | 75.40% | 0.7482 | +0.0084 | ~12 ms | Descartado |
| **SVM (Kernel RBF)** | Modelo No Lineal | 98.79% | 0.9871 | +0.0051 | ~45 ms | Candidato |
| **Random Forest (100 árboles)** | **Ensamble Oficial** | **99.94%** | **0.9991** | **+0.0006** | **16.83 ms** | **Seleccionado** |

> **Cumplimiento de la Brecha de Generalización:**  
> La brecha entre entrenamiento y prueba del modelo Random Forest fue de tan solo **0.06% ($Gap = 0.0006 < 0.05$)**, lo que descarta cualquier síntoma de sobreajuste (*overfitting*) y certifica una óptima capacidad de generalización.

### Métricas Detalladas por Clase (Random Forest en Test)
De las 1,573 muestras evaluadas en el conjunto de prueba, el modelo obtuvo **1,572 aciertos** y solo 1 confusión mínima entre LL y LLG:

| Clase de Red | Muestras (Soporte) | Precision | Recall (Sensibilidad) | F1-Score |
|---|:---:|:---:|:---:|:---:|
| **Normal** | 473 | 1.0000 | 1.0000 | 1.0000 |
| **LG (Fase a Tierra)** | 226 | 1.0000 | 1.0000 | 1.0000 |
| **LL (Fase a Fase)** | 201 | 0.9950 | 1.0000 | 0.9975 |
| **LLG (Doble Fase a Tierra)**| 227 | 1.0000 | 0.9956 | 0.9978 |
| **Trifásica (Simétrica/Tierra)**| 446 | 1.0000 | 1.0000 | 1.0000 |
| **Promedio Macro / Global** | **1,573** | **0.9990** | **0.9991** | **0.9991** |

### Validación Cruzada Estratificada (k=5)
* **F1-Score Macro Promedio:** **0.9991** (99.91%).
* **Desviación Estándar ($\sigma$):** **0.0011** (consistencia extrema en todos los pliegues).
* **Intervalo de Confianza al 95%:** $[0.9980, 1.0000]$.

### Verificación de Cumplimiento de Metas SMART

| Criterio de Aceptación SMART | Umbral Mínimo Requerido | Resultado Medido Real | Estado |
|---|:---:|:---:|:---:|
| **Accuracy en Test** | $\ge 0.90$ (90%) | **0.9994 (99.94%)** | Cumple con creces |
| **F1-Score Macro** | $\ge 0.90$ (90%) | **0.9991 (99.91%)** | Cumple con creces |
| **Recall Mínimo por Clase** | $\ge 0.85$ (85%) | **0.9956 (99.56% en LLG)** | Cumple con creces |
| **Latencia por Inferencia** | $< 100\text{ ms}$ | **16.83 ms en CPU** | Cumple con creces |
| **Throughput de Procesamiento**| $\ge 500\text{ muestras/s}$ | **70,138 muestras/s** | Cumple con creces |
| **Tiempo de Entrenamiento** | $< 300\text{ s}$ (5 min) | **0.89 segundos** | Cumple con creces |

### Evidencia Gráfica del Desempeño
Los gráficos generados por el pipeline en `results/figures/` respaldan la auditoría visual:
* `matriz_confusion.png`: Diagonal dominante casi perfecta (1 sola muestra confundida).
* `f1_comparativa_modelos.png`: Superación categórica del baseline lineal frente al umbral SMART (0.90).
* `shap_importancia_global.png` y `shap_heatmap_clases.png`: Corroboración de que las corrientes de fase ($I_a, I_b, I_c$) y caídas de tensión ($V_a, V_b, V_c$) gobiernan físicamente la decisión del modelo según las leyes de Kirchhoff.

---

## 5. Instalación y Uso Local

### Requisitos del Sistema
* **Sistema Operativo:** Windows 10/11, Ubuntu 20.04+ o macOS.
* **Python:** Versión 3.10 o 3.12 (64-bit recomendada).
* **Memoria RAM:** Mínimo 2 GB (recomendado 4 GB).
* **GPU:** No requerida (ejecución optimizada en CPU).

### Instrucciones Paso a Paso

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/Jordanfvc26/ELECTRO-VOLT.git
   cd ELECTRO-VOLT
   ```

2. **Crear y activar un entorno virtual aislado:**
   * En Windows (PowerShell):
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   * En Linux / macOS:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Instalar dependencias oficiales:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Ejecutar el conjunto de pruebas automatizadas (Testing):**
   ```bash
   pytest tests/
   ```
   *(Verificará las 24 pruebas unitarias de procesamiento de datos, inferencia del modelo y componentes web)*.

5. **Re-entrenar el modelo y generar reportes:**
   ```bash
   python src/train.py
   ```

6. **Iniciar el Dashboard Web Interactivo (Streamlit):**
   ```bash
   streamlit run app/app.py
   ```
   La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`.

### Ejemplo Rápido de Inferencia en Código Python

```python
import joblib
import pandas as pd

# Cargar el paquete serializado oficial
paquete = joblib.load("models/best_model.pkl")
modelo = paquete["modelo"]
columnas = paquete["columnas"]

# Simulación de un evento de falla bifásica (LL entre B y C)
lectura_sensor = pd.DataFrame([{
    "Va": 0.40,  "Vb": -0.13, "Vc": -0.27,
    "Ia": -151.29, "Ib": 850.45, "Ic": -840.12
}])[columnas]

prediccion = modelo.predict(lectura_sensor)[0]
probabilidades = modelo.predict_proba(lectura_sensor)[0]
confianza = max(probabilidades) * 100

print(f"Diagnóstico: {prediccion}")
print(f"Confianza: {confianza:.2f}%")
print(f"Recomendación: {paquete['mensajes_operador'][prediccion]}")
```

---

## 6. Interfaz de Usuario (Dashboard SCADA)

La plataforma cuenta con una interfaz web industrial desarrollada con Streamlit y estilizada con CSS puro personalizado, adoptando la paleta institucional `#002a69`, tipografía técnica Inter / JetBrains Mono y diseño libre del branding estándar de Streamlit:

### Módulos Principales de la Aplicación:
1. **Diagnóstico en Tiempo Real:**
   * Entrada interactiva de magnitudes trifásicas mediante sliders e inputs numéricos.
   * Oscilograma dinámico trifásico sincronizado a 60 Hz.
   * Diagnóstico multiclase instantáneo, porcentaje de confianza y advertencia de seguridad.
   * Gráfico de fuerza explicativo SHAP local que resalta qué fase originó la sobrecorriente.
2. **Procesamiento Masivo por Lote:**
   * Zona de carga tipo *Drag & Drop* para archivos CSV con oscilogramas o registros masivos.
   * Diagnóstico en lote procesando más de 70,000 muestras por segundo.
   * Tablas de resultados con insignias cromáticas de severidad.
   * Exportación de reportes ejecutivos en formatos **PDF corporativo**, **Excel (.xlsx)** y **CSV**.
3. **Auditoría Oficial y Metas SMART:**
   * Panel de métricas operacionales auditables (Accuracy, F1, Recall, Latencia).
   * Matriz de confusión interactiva y comparativa frente a baselines.
   * Galería de explicabilidad global SHAP y mapa de calor de señales por falla.
4. **Páginas Institucionales y de Navegación Segura:**
   * *¿Qué es ElectroVOLT?* (`/que-es-electrovolt`): Marco conceptual y topologías de falla.
   * *Política de Privacidad* (`/politica-privacidad-electrovolt`): Manejo local de datos y cero telemetría externa.
   * *Términos y Condiciones* (`/terminos-condiciones-electrovolt`): Alcance consultivo académico y deslinde de responsabilidad.

### Enlace a la Aplicación Desplegada en la Nube
* **Demo en Vivo alojada en Render:** [https://electro-volt.onrender.com/](https://electro-volt.onrender.com/)

---

## 7. Estructura del Proyecto

El repositorio sigue una arquitectura de software limpia y modular para analítica de datos e ingeniería de Machine Learning:

```text
ELECTRO-VOLT/
├── app/                     # Código fuente de la aplicación web (Dashboard)
│   ├── app.py               # Enrutador principal de nivel superior (Streamlit)
│   ├── requirements.txt     # Dependencias de producción ligera
│   ├── styles.py            # Sistema de diseño CSS industrial SCADA (#002a69)
│   ├── seo.py               # Inyección de metadatos SEO, OpenGraph y JSON-LD
│   ├── utils.py             # Funciones auxiliares de sesión y caché
│   ├── exports.py           # Generación de reportes ejecutivos (PDF, Excel, CSV)
│   ├── components/          # Componentes visuales reutilizables
│   │   ├── header.py        # Barra superior con logotipo y estado de conexión
│   │   ├── navbar.py        # Barra de navegación por módulos operativos
│   │   └── footer.py        # Pie de página institucional y enlaces de contacto
│   └── views/               # Módulos de vistas desacoplados
│       ├── tiempo_real.py   # Diagnóstico interactivo de 6 señales y SHAP
│       ├── procesamiento_lote.py # Inferencia masiva CSV y descargas
│       ├── auditoria_smart.py    # Auditoría de KPIs y matrices de confusión
│       ├── que_es.py        # Vista institucional del proyecto
│       ├── privacidad.py    # Política de privacidad de datos
│       ├── terminos.py      # Términos de uso y consideraciones académicas
│       └── not_found.py     # Vista de error 404 personalizada
├── data/                    # Gestión de conjuntos de datos
│   ├── raw/                 # Dataset original de Kaggle (classData.csv)
│   ├── processed/           # Muestras representativas para testing y lotes
│   └── README.md            # Documentación técnica de los datos
├── docs/                    # Documentación formal del proyecto integrador
│   ├── planificacion.md     # Planificación inicial y alcance SMART
│   ├── analisis_datos.md    # Reporte de análisis exploratorio (EDA)
│   ├── arquitectura.md      # Especificación técnica del pipeline
│   ├── optimizacion.md      # Proceso de ajuste y benchmarking
│   ├── consideraciones_eticas.md # Análisis ético, gobernanza y stakeholders
│   └── manual_usuario.md    # Guía operativa para operadores de subestación
├── models/                  # Artefactos serializados de modelos
│   ├── best_model.pkl       # Paquete oficial final (Random Forest, 5 clases)
│   ├── modelo_fallos_rf.joblib # Réplica en formato Joblib
│   ├── model_v1.pkl         # Modelo baseline previo (6 clases)
│   └── README.md            # Especificación del contrato de datos de inferencia
├── notebooks/               # Cuadernos Jupyter para experimentación
│   ├── 01_exploracion.ipynb
│   ├── 02_preprocesamiento.ipynb
│   ├── 03_modelado.ipynb
│   ├── 04_optimizacion.ipynb
│   └── 05_evaluacion.ipynb
├── results/                 # Resultados experimentales y reportes
│   ├── figures/             # Gráficos generados (Matriz confusión, SHAP, ROC)
│   └── metrics/             # Archivo consolidado metricas.json
├── src/                     # Núcleo modular de código fuente Python
│   ├── __init__.py
│   ├── data_processing.py   # Ingesta, limpieza y partición estratificada
│   ├── model.py             # Definición de estimadores y contratos de inferencia
│   ├── train.py             # Script de entrenamiento, CV y exportación
│   ├── evaluate.py          # Cálculo de métricas, SHAP y graficación
│   ├── utils.py             # Constantes físicas, mensajes y rutas relativas
│   └── images/              # Activos visuales (logotipos e isotipos oficiales)
├── tests/                   # Pruebas unitarias automatizadas (pytest)
│   ├── test_data_processing.py # Pruebas de datos y estratificación
│   ├── test_model.py           # Pruebas de inferencia, métricas y latencia
│   └── test_app.py             # Pruebas de componentes de la aplicación web
├── requirements.txt         # Dependencias completas del entorno de desarrollo
├── robots.txt               # Configuración de rastreo para motores de búsqueda
├── sitemap.xml              # Mapa del sitio web para indexación SEO
└── README.md                # Este documento principal
```

---

## 8. Consideraciones Éticas y Limitaciones

El proyecto implementa un estricto marco de gobernanza algorítmica documentado en detalle en `docs/consideraciones_eticas.md`:

1. **Frontera Operativa y Rol Consultivo (*Human-in-the-loop*):**  
   ElectroVOLT es una herramienta de **soporte a la decisión**, no un sistema de control autónomo. Está expresamente prohibido conectar el software a mecanismos de disparo físico o accionamiento directo de disyuntores sin validación humana. La responsabilidad de maniobra recae exclusivamente en el operador de subestación.
2. **Mitigación del Sesgo de Complacencia:**  
   Para evitar que el personal acepte pasivamente las predicciones ("automatización ciega"), la interfaz despliega simultáneamente la probabilidad de confianza, las advertencias de seguridad física y el desglose de contribución de cada fase mediante SHAP.
3. **Limitaciones Conocidas del Modelo:**  
   * Los datos provienen de simulaciones matemáticas en MATLAB/Simulink bajo condiciones nominales a 60 Hz.
   * El modelo no ha sido expuesto a distorsiones armónicas severas de orden superior, descargas atmosféricas directas o fallos de calibración de transformadores de medida (TP/TC) en campo.
   * Antes de cualquier adopción comercial o en redes de distribución en vivo, se requiere una fase de calibración piloto con eventos reales de oscilografía digital (archivos COMTRADE).
4. **Advertencia Crítica de Seguridad para Cuadrillas:**  
   Bajo ninguna circunstancia las cuadrillas de linieros deben utilizar la predicción de estado "Normal" como garantía de ausencia de tensión para intervenir un circuito. El trabajo en campo exige cumplir rigurosamente las cinco reglas de oro de la seguridad eléctrica (corte efectivo, bloqueo, verificación de ausencia de tensión, puesta a tierra y señalización).

---

## 9. Autores y Contribuciones

Proyecto Integrador desarrollado para la **Maestría en Inteligencia Artificial** de la **Universidad de Especialidades Espíritu Santo (UEES)**, Samborondón, Ecuador (2026).

* **Ing. Jordan Fabian Vera Coello:**  
  *Product Owner, ML Engineer & Full-Stack Developer*  
  Arquitectura del software, diseño modular en `src/`, integración de IA Explicable con SHAP, diseño del sistema SCADA en Streamlit, pruebas unitarias y despliegue en la nube.  
  [![LinkedIn](https://img.shields.io/badge/LinkedIn-jordanfvc26-0077B5?logo=linkedin)](https://www.linkedin.com/in/jordanfvc26) | [![GitHub](https://img.shields.io/badge/GitHub-Jordanfvc26-181717?logo=github)](https://github.com/Jordanfvc26)

* **Ing. Jorge Rafael Estrella Frere:**  
  *Tech Lead, Data Scientist & Experto de Dominio Eléctrico*  
  +22 años de experiencia en sistemas eléctricos de potencia y subestaciones. Análisis exploratorio (EDA), validación física de señales trifásicas, formulación de la fusión a 5 clases y evaluación de impacto operacional.  
  [![LinkedIn](https://img.shields.io/badge/LinkedIn-jorgeestrella-0077B5?logo=linkedin)](https://www.linkedin.com/in/jorgeestrella) | [![GitHub](https://img.shields.io/badge/GitHub-JorgeEstrella-181717?logo=github)](https://github.com/jrestrella-ai)

* **Docente y Evaluadora Principal:**  
  **Ph.D. Gladys Villegas Rugel** — Docente del Proyecto Integrador en Inteligencia Artificial, Facultad de Postgrados, UEES.

---

## 10. Licencia

Este proyecto se distribuye bajo la licencia **MIT License**. Consulte el archivo [LICENSE](LICENSE) para obtener más información. Se autoriza el uso, modificación y distribución para fines académicos, de investigación y desarrollo tecnológico, sin costo de licenciamiento ($0 USD).

---

## 11. Agradecimientos y Referencias

Los autores expresan su sincero agradecimiento a la **Ph.D. Gladys Villegas Rugel** por su guía metodológica y rigor académico durante el desarrollo de la maestría, así como a la **Universidad de Especialidades Espíritu Santo (UEES)** por promover la investigación aplicada en inteligencia artificial para infraestructuras críticas.

### Referencias Bibliográficas Principales
1. **Bin Akter, S., et al. (2024).** *Ensemble learning based transmission line fault classification using PMU data with explainable AI (XAI)*. PLOS ONE, [doi:10.1371/journal.pone.0295144](https://doi.org/10.1371/journal.pone.0295144).
2. **Hsu, C.-C., et al. (2025).** *Explainable AI guided unsupervised fault diagnostics for high-voltage circuit breakers*. Reliability Engineering & System Safety, [doi:10.1016/j.ress.2025.111199](https://doi.org/10.1016/j.ress.2025.111199).
3. **Ogar, V. N., Hussain, S., & Gamage, K. (2022).** *Transmission Line Fault Classification of Multi-Dataset Using CatBoost Classifier*. Signals, [doi:10.3390/signals3030027](https://doi.org/10.3390/signals3030027).
4. **Moparthi, J. R., et al. (2024).** *Enhancing transmission line protection with adaptive ANN-based relay for high resistance fault diagnosis*. Electrical Engineering, [doi:10.1007/s00202-024-02369-w](https://doi.org/10.1007/s00202-024-02369-w).
5. **Turanlı, O., & Yakut, Y. B. (2024).** *Classification of Faults in Power System Transmission Lines Using Deep Learning Methods*. Applied Sciences, [doi:10.3390/app14209590](https://doi.org/10.3390/app14209590).
6. **Lundberg, S. M., & Lee, S.-I. (2017).** *A Unified Approach to Interpreting Model Predictions*. Advances in Neural Information Processing Systems (NeurIPS 2017).

---

## 12. Videos y Enlaces Multimedia

* **Video pitch ejecutivo del proyecto:**  
  

* **Video de respuestas a preguntas de defensa:**  
  

* **Repositorio oficial en GitHub:**  
  [![GitHub](https://img.shields.io/badge/GitHub-Jordanfvc26-181717?logo=github)](https://github.com/Jordanfvc26/ELECTRO-VOLT)

* **Aplicación web desplegada en producción:**  
  [![Render](https://img.shields.io/badge/Render-ELECTRO--VOLT-181717?logo=render&logoColor=white)](https://electro-volt.onrender.com/)