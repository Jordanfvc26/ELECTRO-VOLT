# Consideraciones éticas, impacto social y gobernanza de ElectroVOLT

**Proyecto integrador de maestría en inteligencia artificial**  
**Universidad de Especialidades Espíritu Santo (UEES) — 2026**

* **Autores:** Jordan Fabian Vera Coello y Jorge Rafael Estrella Frere  
* **Docente:** Ph.D. Gladys Villegas Rugel  
* **Materia:** Proyecto integrador en inteligencia artificial  

---

## 1. Alcance ético y frontera de decisión

ElectroVOLT es una plataforma de analítica predictiva diseñada para asistir en el diagnóstico de fallas eléctricas en subestaciones y redes de distribución, clasificando eventos en cinco estados validados físicamente: normal, monofásica a tierra (LG), bifásica (LL), doble línea a tierra (LLG) y trifásica.

Desde el punto de vista ético y operativo, los límites del sistema están definidos de manera estricta:

* **Soporte consultivo a la decisión humana:** el sistema calcula el tipo de falla, un nivel de confianza y la justificación física de las señales mediante explicaciones de SHAP. Su función es entregar información rápida y comprensible al operador.
* **Prohibición de actuación autónoma:** el software no interactúa con relés de disparo ni ejecuta maniobras sobre interruptores en el campo. La potestad sobre cualquier acción física en la red recae invariablemente en el criterio y autorización del operador humano de turno.

---

## 2. Mapa de partes interesadas (stakeholders)

El impacto de un diagnóstico de fallas eléctricas abarca desde el personal en subestación hasta los servicios esenciales de la comunidad:

| Parte interesada | Rol en relación con el sistema | Beneficios | Riesgos y posibles daños | Nivel de poder y voz |
|---|---|---|---|:---:|
| **Operadores de subestación y consola** | Usuarios directos que reciben la predicción durante una contingencia. | Diagnóstico rápido en milisegundos, visualización del aporte de cada fase y reducción de incertidumbre en eventos críticos. | Sesgo de complacencia (confiar a ciegas en la pantalla), sobrecarga de información o resistencia al uso por desconfianza en la tecnología. | Poder medio, voz alta |
| **Cuadrillas de mantenimiento en campo** | Técnicos y linieros que intervienen físicamente los postes y alimentadores. | Conocimiento previo de la fase involucrada y si hay contacto con tierra, optimizando herramientas y equipos de protección personal. | **Riesgo crítico de electrocución o arco eléctrico** si un falso negativo o una mala clasificación indica erróneamente que una línea no está energizada. | Poder bajo, voz media |
| **Empresas distribuidoras (CNEL EP, EEQ)** | Entidades responsables de la infraestructura, seguridad operativa y calidad del servicio. | Reducción de tiempos de corte, protección de transformadores de subestación y menores penalizaciones económicas. | Responsabilidad legal y civil por errores de operación; retos de seguridad digital si el sistema se conecta a redes de control. | Poder alto, voz alta |
| **Operador nacional de electricidad (CENACE)** | Organismo coordinador de la estabilidad del sistema interconectado nacional. | Alertas tempranas de fallas nodales que evitan desconexiones en cadena a nivel regional. | Decisiones operativas desfavorables si se reportan fallas con información de fase inconsistente. | Poder alto, voz media |
| **Entidades reguladoras (ARCERNNR, Ministerio)** | Supervisión de los índices reglamentarios de continuidad (SAIDI y SAIFI) y tarifas. | Información auditable sobre causas de interrupción y evaluación técnica basada en datos. | Dificultad para fiscalizar sistemas si las empresas usan algoritmos de caja negra sin explicabilidad. | Poder alto, voz baja |
| **Cargas críticas y servicios esenciales** | Hospitales, estaciones de bombeo de agua potable, transporte masivo y centros de datos. | Restablecimiento prioritario del suministro eléctrico, reduciendo el riesgo de cortes prolongados. | **Pérdida de vidas humanas** o interrupción de servicios de salud y agua potable si un mal diagnóstico retrasa la normalización del circuito. | Poder bajo, voz alta |
| **Ciudadanía y usuarios finales** | Familias, comercios e industrias que dependen de la energía eléctrica diaria. | Mayor confiabilidad del suministro y menores daños en electrodomésticos por cortes repetidos. | Riesgo a la seguridad ciudadana si un conductor caído a tierra no es atendido oportunamente por el personal técnico. | Poder bajo, voz baja |

---

## 3. Resultados reales medidos frente a metas proyectadas

Un principio básico de honestidad técnica es separar los objetivos teóricos de los resultados reales medidos sobre los datos:

* **Las metas de diseño** (como lograr exactitud y F1 mayores al 90%, o sensibilidad sobre el 85%) son criterios de aceptación iniciales, no evidencia empírica.
* **El ahorro del 20% al 30% en costos y la reducción del 80% en tiempo de diagnóstico** son hipótesis de impacto operacional formuladas para una etapa de prueba piloto en campo. El algoritmo reduce el tiempo de análisis de datos a 17 milisegundos, pero la restauración completa del servicio siempre dependerá del traslado y maniobras de las cuadrillas.
* **El sistema no "garantiza" rendimiento en campo:** ha sido entrenado y validado sobre datos simulados en MATLAB/Simulink, por lo que su comportamiento en subestaciones reales debe comprobarse antes de cualquier despliegue formal.

### Métricas reales obtenidas en el conjunto de prueba (1,573 muestras)

| Estado evaluado | Muestras de prueba | Precisión | Sensibilidad (recall) | F1-score |
|---|:---:|:---:|:---:|:---:|
| **Normal** | 473 | 1.000 | 1.000 | 1.000 |
| **Línea a tierra (LG)** | 226 | 1.000 | 1.000 | 1.000 |
| **Línea a línea (LL)** | 201 | 0.995 | 1.000 | 0.998 |
| **Doble línea a tierra (LLG)** | 227 | 1.000 | 0.996 | 0.998 |
| **Trifásica** | 446 | 1.000 | 1.000 | 1.000 |
| **Promedio macro** | **1,573** | **0.999** | **0.999** | **0.999** |

* **Exactitud global (accuracy):** 99.94% (1,572 de 1,573 casos clasificados correctamente).
* **Validación cruzada estratificada (5 pliegues):** F1-score promedio de **0.999 ± 0.001**, con un intervalo de confianza al 95% entre **0.998 y 1.000**.
* **Latencia de procesamiento:** 16.8 milisegundos por predicción en procesador convencional.

---

## 4. Riesgos éticos y operativos del sistema

El análisis de riesgos no se limita a listas genéricas de verificación, sino a los problemas propios de un sistema ciberfísico en redes eléctricas:

1. **Ciberseguridad y confidencialidad en nube pública gratuita:** el prototipo se ejecuta sobre servidores públicos compartidos fuera del país. Subir telemetría de subestaciones a este entorno expone datos sobre perfiles de consumo, puntos vulnerables y flujos de potencia de una infraestructura crítica nacional.
2. **Manipulación de señales de entrada y fallas de medición:** si un transformador de corriente o voltaje se descalibra, se satura o sufre una manipulación maliciosa de datos, el clasificador puede recibir valores alterados y catalogar una falla grave como estado normal, postergando la apertura de protecciones.
3. **Brecha entre datos simulados y entorno real (sim-to-real gap):** el modelo aprendió con señales limpias de simulación. En una subestación real existen armónicos, transitorios por maniobras de capacitores, desbalances y ruido de línea que pueden degradar la precisión y elevar la tasa de falsas alarmas.
4. **Falsos negativos en fallas con contacto a tierra:** si una falla monofásica a tierra con alta resistencia de contacto no es clasificada correctamente, las cuadrillas podrían acercarse a una línea viva creyendo que se encuentra desenergizada, con peligro mortal de electrocución.
5. **Indisponibilidad del servicio en la nube:** los servicios gratuitos pueden presentar suspensión por inactividad o lentitud ante cortes de conexión a internet, lo que deja al operador sin la herramienta justamente durante una tormenta eléctrica o emergencia.
6. **Sesgo de automatización y complacencia:** existe el peligro de que operadores con menos experiencia dejen de analizar las señales fasoriales y adopten la recomendación del modelo sin contraste crítico.

---

## 5. Estrategias de mitigación y criterios de verificación

Cada riesgo cuenta con una medida técnica u organizativa, un responsable y una forma objetiva de comprobar su cumplimiento. Cabe recalcar que **un aviso de descargo o exención de responsabilidad en la interfaz no exime a los desarrolladores ni a la empresa de su responsabilidad operativa y técnica**.

| Riesgo | Estrategia de mitigación | Responsable | Mecanismo de verificación medible |
|---|---|---|---|
| **Ciberseguridad en la nube** | Diseñar una arquitectura local (edge) contenerizada en Docker para operar dentro de la red privada de la subestación, sin salida a internet público. | Jordan Vera | Informe de pruebas de ejecución local sin conexión a internet y escaneo de vulnerabilidades sin alertas críticas. |
| **Manipulación y datos anómalos** | Implementar validadores físicos en el código (`validar_rango_senales`) que rechacen entradas fuera de escala física o lecturas con ceros absolutos. | Jordan Vera y Jorge Estrella | Pruebas unitarias automatizadas (`test_validar_rango_senales_ood`) pasando al 100% en el repositorio. |
| **Brecha simulado-real** | Aplicar pruebas de robustez inyectando ruido gaussiano y variaciones de amplitud; preparar una fase de reentrenamiento con oscilografías de campo. | Jorge Estrella | Evaluación de degradación: el F1-score no debe caer por debajo de 0.92 con ruido simulado moderado. |
| **Falsos negativos a tierra** | Priorizar la sensibilidad con pesos balanceados de clase y calcular la corriente neutra ($In = Ia + Ib + Ic$). Si $|In| > 20\text{ A}$, emitir alerta obligatoria de tierra. | Jorge Estrella | Verificación con la prueba `test_umbral_retorno_tierra_observacion_jorge` en pytest; recall a tierra $\ge 0.995$. |
| **Indisponibilidad de servicio** | Mantener los paneles físicos y relés convencionales como primera línea de control. El software actúa como apoyo secundario. | Jordan Vera | Protocolo de contingencia documentado en el manual; tiempo de respuesta manual garantizado sin depender de la aplicación web. |
| **Resistencia al cambio y complacencia** | Desarrollar talleres de capacitación con operadores veteranos, mostrando la justificación de SHAP y definiendo al sistema como copiloto, no sustituto. | Jordan Vera y Jorge Estrella | Encuesta estandarizada de usabilidad (escala SUS) con meta superior a 80 puntos tras las sesiones formativas. |

---

## 6. Marco de responsabilidad y gobernanza

Para evitar vacíos legales, la toma de decisiones y el mantenimiento del sistema se distribuyen de acuerdo con las etapas de desarrollo y operación:

### Matriz de responsabilidades (RACI)

* **R (Responsable de ejecutar):** quien realiza el trabajo técnico o maniobra.
* **A (Aprobador final / Accountable):** quien responde jurídica y administrativamente por el resultado.
* **C (Consultado):** especialista que aporta criterio técnico.
* **I (Informado):** quien debe conocer los resultados o alertas.

| Actor | Desarrollo y modelado | Pruebas y validación | Despliegue en subestación | Operación en tiempo real |
|---|:---:|:---:|:---:|:---:|
| **Equipo de desarrollo (Jordan Vera)** | R / A | R | C | I (soporte evolutivo) |
| **Experto de dominio eléctrico (Jorge Estrella)** | R | R / A | C | I (auditoría técnica) |
| **Gerencia de la empresa distribuidora** | I | C | A | A (responsable legal del servicio) |
| **Jefatura de protecciones y mantenimiento** | C | C | R | R (supervisión de protocolos) |
| **Operador de consola de turno** | I | C | I | R (autoridad única de maniobra) |
| **Cuadrilla técnica de campo** | I | I | I | R (verificación en sitio) |

> **Regla de oro de operación:**  
> Ningún operario puede autorizar maniobras amparándose exclusivamente en el diagnóstico de la aplicación. Toda orden de apertura o cierre requiere la confirmación visual de los relés de protección físicos y el cumplimiento de las cinco reglas de oro de seguridad eléctrica.

### Estado real de los mecanismos de rendición de cuentas

Para reflejar con sinceridad el estado del proyecto, se diferencian las funciones ya programadas de aquellas planificadas para un piloto formal:

* **Documentación del modelo y datos:** implementada en el repositorio mediante fichas técnicas en las carpetas de modelos y datos.
* **Detección de entradas fuera de rango:** implementada y evaluada en las pruebas unitarias del código.
* **Explicabilidad individual (SHAP):** implementada en la aplicación web para cada diagnóstico en pantalla.
* **Auditoría de deriva de datos (data drift):** propuesta para la fase piloto con una frecuencia de revisión **semestral**.
* **Registro de discrepancias entre operador y modelo:** propuesto para registrarse en base de datos local y revisarse con una frecuencia **mensual** entre los ingenieros de protecciones y ciencia de datos.

### Plan de contingencia ante fallas diagnósticas

1. **Suspensión inmediata:** ante cualquier discrepancia evidente entre el modelo y los instrumentos de la subestación, el operador desestima la sugerencia digital y continúa con los procedimientos tradicionales.
2. **Protección del personal:** prohibición de autorizar traslados a campo hasta confirmar la condición de la línea mediante mediciones físicas directas.
3. **Registro forense:** guardado del registro oscilográfico y de las señales de entrada para su análisis posterior.
4. **Revisión y ajuste:** el equipo técnico analiza el evento en un plazo menor a 72 horas para determinar si la causa fue descalibración del sensor o deficiencia del clasificador, incorporando el caso al conjunto de reentrenamiento.

---

## 7. Cumplimiento normativo (compliance)

Se analiza la relación del proyecto con los marcos regulatorios aplicables en Ecuador y las referencias internacionales:

* **Regulaciones ARCERNNR 001/20 y 002/20 (antes ARCONEL):** la Agencia de Regulación y Control de Energía y Recursos Naturales No Renovables fija los umbrales de continuidad del suministro eléctrico (SAIDI y SAIFI). El proyecto se alinea con este objetivo al facilitar la identificación expedita de contingencias, respetando los protocolos vigentes sin intervenir en las protecciones obligatorias de despeje.
* **Ley Orgánica del Servicio Público de Energía Eléctrica (LOSPEE):** exige eficiencia, seguridad y continuidad en la prestación del servicio. El sistema apoya esta meta mediante la digitalización de diagnósticos para cuidar transformadores y alimentadores.
* **Ley Orgánica de Protección de Datos Personales (LOPDP, Ecuador):** las señales eléctricas de fase y corriente son variables físicas de máquinas, por lo que no constituyen datos personales. Sin embargo, los registros de acceso, nombres y turnos de los operadores sí están sujetos a la ley, requiriendo almacenamiento seguro y control de permisos de usuario.
* **Seguridad de la información (EGSI v2 y normas NERC-CIP):** el prototipo actual en la nube de acceso público no cumple los requisitos para operar en redes críticas de distribución. Para un entorno productivo, las normas exigen que el sistema se instale en servidores locales dentro de la red operativa (OT) de la subestación, aislada del tráfico de internet público.
* **Reglamento de inteligencia artificial de la Unión Europea (EU AI Act):** clasifica a los sistemas de analítica empleados en infraestructuras críticas como tecnologías de alto riesgo, requiriendo supervisión humana efectiva, explicabilidad de resultados y gestión periódica de riesgos técnicos, principios que fundamentan el diseño de ElectroVOLT.

---

## 8. Reflexión y compromisos éticos

### Reflexión del equipo

* **El dilema principal:** balancear la urgencia por restablecer el servicio a los clientes frente a la certeza de que una línea caída no ponga en peligro a linieros o peatones. La decisión ética del diseño fue priorizar la vida: ante la menor señal de corriente residual a tierra, el sistema fuerza la advertencia de falla y exige comprobación física.
* **Lección sobre los datos sintéticos:** la simulación en software ofrece métricas de laboratorio casi perfectas que pueden generar una falsa sensación de infalibilidad. La ingeniería responsable exige reconocer que el ruido, los armónicos y las condiciones climáticas reales pondrán a prueba cualquier modelo.
* **Mejoras aplicadas al código:** a partir de este análisis se introdujo el cálculo directo de corriente neutra ($In$), filtros de valores fuera de escala física, coherencia en las alertas del sinóptico visual y el aislamiento completo respecto a protocolos de disparo automático.

### Compromiso ético de los autores

Los autores asumen los siguientes compromisos profesionales de ingeniería:

1. **Prioridad a la seguridad humana:** anteponer la integridad física del personal técnico y de la comunidad a cualquier meta de velocidad diagnóstica o reducción de costos.
2. **Supervisión humana irrenunciable:** mantener la herramienta en un rol estrictamente consultivo, sin facultades para abrir o cerrar circuitos de forma automática.
3. **Transparencia y claridad técnica:** rechazar modelos de caja negra y proveer siempre información de confianza y explicabilidad con SHAP para cada resultado.
4. **Honestidad sobre el alcance:** comunicar con transparencia que las pruebas actuales corresponden a entornos de simulación y que su adopción formal requiere validación piloto con registros reales de campo.
5. **Responsabilidad ante incidentes:** mantener canales abiertos para auditar fallas de clasificación, corregir datos anómalos y colaborar con las áreas de mantenimiento.

---

## 9. Referencias

1. **Agencia de Regulación y Control de Energía y Recursos Naturales No Renovables (ARCERNNR).** (2020). *Regulación Nro. ARCERNNR-001/20: Calidad del servicio de distribución y comercialización de energía eléctrica*. Registro Oficial del Ecuador.
2. **Asamblea Nacional del Ecuador.** (2015). *Ley Orgánica del Servicio Público de Energía Eléctrica (LOSPEE)*. Registro Oficial Suplemento 418.
3. **Asamblea Nacional del Ecuador.** (2021). *Ley Orgánica de Protección de Datos Personales (LOPDP)*. Registro Oficial Suplemento 459.
4. **European Union.** (2024). *Artificial Intelligence Act (Regulation EU 2024/1689)*. Disposiciones sobre sistemas de alto riesgo en infraestructuras críticas (Anexo III).
5. **IEEE Power and Energy Society.** (2014). *IEEE Std C37.114-2014: Guide for Determining Fault Location on AC Transmission and Distribution Lines*. IEEE Standards Association.
6. **IEEE Power and Energy Society.** (2019). *IEEE Std 1159-2019: Recommended Practice for Monitoring Electric Power Quality*. IEEE Standards Association.
7. **North American Electric Reliability Corporation (NERC).** (2021). *Critical Infrastructure Protection (CIP) Reliability Standards*.
8. **Lundberg, S. M., & Lee, S.-I.** (2017). A unified approach to interpreting model predictions. *Advances in Neural Information Processing Systems (NeurIPS)*, 30, 4765–4774.
9. **UNESCO.** (2021). *Recomendación sobre la ética de la inteligencia artificial*. París, Francia.
