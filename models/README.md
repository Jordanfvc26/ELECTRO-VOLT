# Modelos Entrenados de ELECTRO-VOLT

Este directorio almacena los artefactos serializados de los modelos de Machine Learning entrenados para la clasificación multiclase de fallos eléctricos.

## 1. Contenido del Directorio

```text
models/
├── best_model.pkl          # Paquete oficial del modelo final (Random Forest 100 estimadores)
├── modelo_fallos_rf.joblib # Réplica oficial para compatibilidad directa con scripts legacy
├── model_v1.pkl            # Versión baseline 1.0 del modelo serializado
└── README.md               # Este documento
```

## 2. Contrato de Datos del Modelo Serializado (`joblib.dump(..., compress=3)`)

El archivo empaqueta un diccionario de Python con las siguientes claves requeridas para la inferencia y la interfaz web:

```python
{
    "modelo": rf,               # RandomForestClassifier entrenado (100 árboles)
    "columnas": ["Va", "Vb", "Vc", "Ia", "Ib", "Ic"],  # Orden estricto de entrada
    "clases": ["LG", "LL", "LLG", "Normal", "Trifásica"],
    "mensajes_operador": {
        "Normal": "Operación normal. No se detecta falla.",
        "LG": "Falla de línea a tierra.",
        "LL": "Falla de línea a línea.",
        "LLG": "Falla de doble línea a tierra.",
        "Trifásica": (
            "Falla trifásica. Con las señales de fase no se distingue si involucra tierra "
            "(LLL o LLLG); verificar con la medición de neutro/tierra."
        ),
    },
    "nota_clases": (
        "LLL y LLLG se unieron en una sola clase 'Trifásica' porque en una falla trifásica "
        "balanceada la conexión a tierra no lleva corriente y las señales de fase son las mismas."
    ),
    "descripcion": "Random Forest (100 árboles) con 6 lecturas trifásicas, 5 clases",
}
```

## 3. Desempeño y Métricas SMART del Modelo Final
- **Accuracy en Test:** $0.9994$ ($99.94\%$)
- **F1-Score Macro:** $0.9996$ ($1.000$)
- **Recall Mínimo por Clase:** $0.998$
- **Brecha de Generalización (Gap):** $0.0006$ (Óptimo, sin overfitting)
- **Validación Cruzada StratifiedKFold (k=5):** $0.9988 \pm 0.0011$
- **Latencia de Inferencia:** $\approx 19\text{ ms}$ por predicción individual en CPU
- **Throughput:** $> 30,000\text{ muestras/s}$ en inferencia en lote
