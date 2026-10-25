# Modelos Entrenados de ELECTROVOLT

Este directorio almacena los artefactos serializados de los modelos de Machine Learning entrenados para la clasificación multiclase de fallos eléctricos a partir de las 6 señales continuas de fase (Va, Vb, Vc, Ia, Ib, Ic).

## 1. Contenido del Directorio

```text
models/
├── best_model.pkl          # Paquete oficial del modelo final optimizado (5 clases, Random Forest)
├── modelo_fallos_rf.joblib # Réplica exacta para compatibilidad con código de inferencia
├── model_v1.pkl            # Versión baseline inicial (6 clases originales de Kaggle)
└── README.md               # Este documento de especificación
```

## 2. Comparativa entre Modelos

| Característica | model_v1.pkl (Baseline v1.0) | best_model.pkl (Producción Final) |
|---|---|---|
| Algoritmo | Random Forest (100 árboles) | Random Forest (100 árboles) |
| Clases objetivo | 6 clases: Normal, LG, LL, LLG, LLL, LLLG | 5 clases: Normal, LG, LL, LLG, Trifásica |
| Justificación física | Modelo previo al análisis de indistinguibilidad | Fusión física de LLL y LLLG (anulación de corriente en tierra) |
| Accuracy en Test | ~87.3% (caída por confusión LLL/LLLG) | 99.94% |
| F1-Score Macro | ~0.871 | 0.9996 |
| Latencia inferencia | ~18 ms | ~17 ms |
| Estado de despliegue | Histórico / Comparativo | Activo en Producción (App Web) |

## 3. Contrato de Datos del Paquete Serializado

Los archivos `.pkl` y `.joblib` están serializados con `joblib.dump(..., compress=3)` y encapsulan un diccionario de Python con las siguientes claves requeridas:

```python
{
    "modelo": rf,               # Objeto RandomForestClassifier entrenado
    "columnas": ["Va", "Vb", "Vc", "Ia", "Ib", "Ic"],  # Orden estricto de entrada
    "clases": ["LG", "LL", "LLG", "Normal", "Trifásica"], # Clases del modelo
    "mensajes_operador": {
        "Normal": "Operación normal.",
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

## 4. Modo de Consumo en Código

```python
import joblib
import pandas as pd

paquete = joblib.load("models/best_model.pkl")
modelo = paquete["modelo"]
columnas = paquete["columnas"]

# DataFrame con las 6 señales en orden canónico
lectura = pd.DataFrame([{"Va": 0.40, "Vb": -0.13, "Vc": -0.27, "Ia": -151.29, "Ib": -9.68, "Ic": 85.80}])[columnas]
prediccion = modelo.predict(lectura)[0]
probabilidades = modelo.predict_proba(lectura)[0]
mensaje = paquete["mensajes_operador"][prediccion]
```
