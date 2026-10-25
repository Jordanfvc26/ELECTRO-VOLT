# Planificación del proyecto: ELECTROVOLT

**Proyecto integrador de maestría en Inteligencia Artificial**  
**Universidad de Especialidades Espíritu Santo (UEES) — 2026**  
**Autores:** Jordan Fabian Vera Coello y Jorge Rafael Estrella Frere  

---

## 1. Definición del problema y objetivos

### Definición del problema
En los sistemas de distribución eléctrica, las fallas por cortocircuito entre conductores y los contactos a tierra generan interrupciones no programadas que afectan la continuidad del suministro de energía. Los relés de protección tradicionales basados en sobrecorriente operan desconectando el circuito ante la superación de un límite predeterminado, pero no identifican la topología específica de la falla ni explican qué fases están interactuando.

Como consecuencia, el diagnóstico de la causa raíz depende de inspecciones manuales reactivas por parte de cuadrillas técnicas en campo. Este proceso toma en promedio dos horas por evento, lo que prolonga los cortes de energía, incrementa los índices regulatorios de indisponibilidad y expone los transformadores de subestación a esfuerzos térmicos y electrodinámicos severos.

### Objetivo general
Desarrollar una aplicación web basada en un modelo de aprendizaje automático supervisado e inteligencia artificial explicable para la detección y clasificación de fallos eléctricos a partir de seis señales trifásicas de tensión y corriente, reduciendo el tiempo de diagnóstico de horas a milisegundos y proporcionando al operador una justificación física comprensible antes de ejecutar maniobras en la red.

### Objetivos específicos
* Procesar y estructurar las señales trifásicas de voltaje y corriente mediante análisis exploratorio de datos y partición estratificada, asegurando la consistencia física de las lecturas y mitigando el sobreajuste.
* Entrenar y comparar modelos de aprendizaje automático supervisado en scikit-learn, seleccionando la arquitectura que alcance una exactitud y un puntaje F1 macro superiores al 90%.
* Integrar un módulo de explicabilidad algorítmica mediante valores SHAP que cuantifique el aporte individual de cada fase en la predicción generada.
* Implementar un panel web interactivo para operadores de subestación que admita diagnósticos individuales en tiempo real e inferencias masivas por archivo, manteniendo tiempos de respuesta inferiores a 100 milisegundos.

---

## 2. Justificación de la relevancia del proyecto

La energía eléctrica constituye un servicio esencial e infraestructura crítica para el desarrollo social y productivo. El desarrollo de este proyecto se fundamenta en tres áreas de impacto:

* **Continuidad del suministro y cumplimiento regulatorio:** La reducción en los tiempos de identificación de fallas disminuye directamente los indicadores internacionales SAIDI, correspondiente a la duración promedio de las interrupciones, y SAIFI, correspondiente a la frecuencia media de cortes. Esto evita sanciones económicas impuestas por las entidades de regulación del sector eléctrico.
* **Preservación de activos de alto costo:** El diagnóstico preciso previene maniobras de reconexión a ciegas sobre fallas permanentes activas, protegiendo transformadores de potencia y disyuntores cuyo reemplazo demanda semanas de trabajo e inversiones de cientos de miles de dólares.
* **Seguridad del personal operativo y linieros:** Conocer de antemano la topología del evento y si existe contacto con tierra permite enviar cuadrillas con las herramientas de aislamiento adecuadas, disminuyendo el riesgo de accidentes por contacto accidental o arco eléctrico.
* **Eficiencia económica:** La solución fue concebida bajo una premisa de costo cero en licenciamiento e infraestructura, aprovechando herramientas de código abierto para democratizar el uso de analítica avanzada en empresas distribuidoras.

---

## 3. Alcance del proyecto

### Qué incluye el proyecto
* Ingesta, limpieza y normalización de seis magnitudes físicas trifásicas continuas: voltajes de fase $V_a, V_b, V_c$ y corrientes de fase $I_a, I_b, I_c$.
* Clasificación multiclase en cinco estados operativos de la red: normal, monofásica a tierra (LG), bifásica (LL), doble línea a tierra (LLG) y trifásica.
* Fusión técnica fundamentada de las fallas trifásica simétrica y trifásica a tierra en una sola categoría, debido a la anulación de corriente de neutro en condiciones balanceadas.
* Entrenamiento, optimización y comparación sistemática de tres algoritmos supervisados: regresión logística como modelo base lineal, máquinas de vectores de soporte con kernel de base radial y ensamble por bosques aleatorios.
* Módulo de inteligencia artificial explicable tanto a nivel local como global mediante TreeExplainer de SHAP.
* Interfaz web interactiva construida en Streamlit con navegación entre diagnóstico en tiempo real, procesamiento masivo de datos mediante archivos CSV, panel de auditoría de métricas y páginas informativas.
* Exportación de reportes ejecutivos en formatos PDF, hojas de cálculo Excel y texto separado por comas.
* Pruebas unitarias automatizadas con pytest para garantizar la robustez del código ante entradas fuera de rango.

### Qué NO incluye el proyecto
* Conexión física directa o bidireccional a relés de protección, unidades terminales remotas o redes industriales SCADA en subestaciones reales.
* Procesamiento de información no tabular, tales como registros oscilográficos continuos en formato COMTRADE sin muestrear, imágenes termográficas de transformadores o señales acústicas.
* Implementación de redes neuronales profundas o modelos no supervisados en el servidor de producción, con el propósito de preservar un consumo de memoria liviano y respuesta inmediata en CPU estándar.
* Accionamiento o disparo físico automatizado de interruptores de potencia. La plataforma opera estrictamente como un sistema de soporte consultivo a la decisión del operador humano de turno.

---

## 4. Cronograma de desarrollo: planificado vs. real

El proyecto fue planificado para ejecutarse a lo largo de cinco semanas mediante ciclos iterativos basados en la metodología ágil Scrum:

| Fase o sprint | Período planificado | Entregables planificados | Estado y resultado real |
|---|---|---|---|
| **Sprint 1: Investigación y diseño** | 21/09/2026 al 27/09/2026 | Revisión de estado del arte, selección de dataset, análisis exploratorio inicial y reporte de calidad de datos. | **Completado:** Dataset de Kaggle validado con 7,861 registros limpios, 0% de nulos y arquitectura modular definida en el repositorio. |
| **Sprint 2: Desarrollo core y baselines** | 28/09/2026 al 04/10/2026 | Tubería de preprocesamiento, partición estratificada 80/20, regresión logística baseline y primer modelo Random Forest. | **Completado:** Pipeline funcional establecido en `src/data_processing.py`. El baseline lineal alcanzó 75.4% de exactitud y Random Forest superó el 99%. |
| **Sprint 3: Optimización y explicabilidad** | 05/10/2026 al 11/10/2026 | Ajuste de hiperparámetros, validación cruzada estratificada de 5 pliegues e integración de explicaciones SHAP. | **Completado:** Modelo final Random Forest ajustado con 100 árboles, F1 macro de 99.91% en prueba y generación de gráficos SHAP locales y globales. |
| **Sprint 4: Interfaz web y pruebas** | 12/10/2026 al 18/10/2026 | Desarrollo de interfaz web en Streamlit, oscilograma trifásico, módulo de carga CSV y plan de pruebas unitarias. | **Completado:** Dashboard industrial SCADA concluido con exportación en PDF, Excel y 24 pruebas unitarias aprobadas en pytest. |
| **Sprint 5: Despliegue, documentación final y videos** | 19/10/2026 al 30/10/2026 | Despliegue en servidor en la nube sin costo, documentación técnica en la carpeta docs y manual de usuario. Así como la grabación de video pitch y preguntas. | **Completado:** Despliegue en producción activa mediante Render, repositorio sincronizado en GitHub y redacción de informes técnicos. |

---

## 5. Recursos necesarios

### Datos
* Conjunto de datos público *Electrical Fault Detection and Classification*, generado mediante simulaciones en MATLAB y Simulink sobre un sistema de transmisión a 60 Hz.
* 7,861 instancias tabulares sin registros nulos ni duplicados, compuestas por seis columnas numéricas de entrada y cuatro banderas binarias de salida.
* Conjunto de respaldo disponible con 22,000 registros para contingencias de reemplazo directo.

### Hardware
* **Entorno de desarrollo y ejecución:** Computador personal estándar con procesador de arquitectura x86-64 de 4 núcleos o superior.
* **Memoria RAM:** Mínimo 4 GB de memoria principal.
* **Almacenamiento:** Menos de 1 GB de espacio en disco para el entorno virtual, dependencias y datos del proyecto.
* **Aceleración gráfica:** No se requiere tarjeta gráfica dedicada ni recursos GPU, dado que el modelo de ensamble y las inferencias operan de manera eficiente sobre CPU.

### Software y librerías
* **Lenguaje base:** Python versión 3.10 o 3.12.
* **Procesamiento numérico y tabular:** NumPy y Pandas.
* **Modelado y métricas:** Scikit-Learn y Joblib para serialización comprimida de artefactos.
* **Inteligencia artificial explicable:** SHAP con algoritmo TreeExplainer.
* **Interfaz de usuario:** Streamlit con estilos CSS industriales personalizados.
* **Visualización y generación de reportes:** Matplotlib, Seaborn, Altair, OpenPyXL y ReportLab.
* **Control de calidad y pruebas:** Pytest.
* **Control de versiones y alojamiento:** Git, GitHub y plataforma en la nube Render para despliegue web gratuito.

---

## 6. Riesgos identificados y mitigación

| Riesgo identificado | Nivel de impacto | Probabilidad | Estrategia de mitigación aplicada |
|---|:---:|:---:|---|
| **Desbalance relativo entre clases de fallas** | Medio | Media | Configuración del parámetro `class_weight='balanced'` en el clasificador Random Forest y evaluación prioritaria mediante F1-score macro en lugar de exactitud simple. |
| **Sobreajuste derivado del ordenamiento en bloques del dataset** | Alto | Alta | Implementación de partición estratificada con barajado obligatorio (`shuffle=True`) y validación cruzada estratificada de 5 pliegues para verificar la estabilidad del modelo. |
| **Elevada latencia en el cálculo de explicabilidad con SHAP** | Alto | Media | Elección de Random Forest en lugar de modelos no lineales opacos, permitiendo el uso de `TreeExplainer` de tiempo polinómico y cálculo de explicaciones en menos de 100 milisegundos. |
| **Límite de memoria en la capa gratuita del servidor en la nube** | Medio | Media | Optimización del empaquetado del modelo serializado comprimido en 480 KB, eliminación de dependencias pesadas y separación modular del código en archivos livianos. |
| **Confusión del operador por sobrecarga de información técnica** | Medio | Baja | Diseño visual con jerarquía clara de alertas, código cromático industrial estándar, mensajes operativos concretos y porcentaje de confianza en cada diagnóstico. |
| **Uso inadecuado como certificador de desenergización en campo** | Crítico | Baja | Inclusión explícita de advertencias operativas y términos de uso en la interfaz, reiterando que la plataforma es consultiva y que el personal liniero debe aplicar siempre las cinco reglas de oro de seguridad eléctrica. |
