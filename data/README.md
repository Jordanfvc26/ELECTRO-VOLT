# Datos del Proyecto ELECTROVOLT

Este directorio almacena los conjuntos de datos crudos y procesados para el entrenamiento y evaluación de modelos de detección y clasificación multiclase de fallos eléctricos.

## 1. Estructura de Carpetas

```text
data/
├── raw/
│   └── classData.csv          # Dataset original de Kaggle: Electrical Fault Detection and Classification)
├── processed/
│   └── ejemplos_prueba.csv    # Muestras representativas de prueba para testing y app web
└── README.md                  # Este documento
```

## 2. Descripción de `classData.csv`
- **Fuente:** Dataset *Electrical Fault Detection and Classification* (Kaggle), generado a partir de simulaciones en MATLAB/Simulink de un sistema de transmisión de potencia trifásico.
- **Volumen:** 7,861 registros y 10 columnas.
- **Calidad:** 0 valores nulos y 0 filas duplicadas.
- **Variables predictoras (6 señales continuas):**
  - Voltajes de fase: `Va`, `Vb`, `Vc`
  - Corrientes de fase: `Ia`, `Ib`, `Ic` (en Amperios, A).
- **Columnas binarias objetivo:** `G` (Tierra), `C` (Fase C), `B` (Fase B), `A` (Fase A).
- **Alerta de ordenamiento:** El archivo se encuentra ordenado secuencialmente en bloques de clases, por lo que toda partición o validación cruzada debe ejecutarse con `shuffle=True` y semilla fija (`SEMILLA=42`).

## 3. Clases de Fallas y Mapeo Físico
- **6 Clases Originales:**
  - `(0, 0, 0, 0)` $\rightarrow$ **Normal** (Sin falla, 2,365 muestras)
  - `(1, 0, 0, 1)` $\rightarrow$ **LG** (Fase A a tierra, 1,129 muestras)
  - `(0, 1, 1, 0)` $\rightarrow$ **LL** (Fases B-C, 1,004 muestras)
  - `(1, 0, 1, 1)` $\rightarrow$ **LLG** (Fases A-B a tierra, 1,134 muestras)
  - `(0, 1, 1, 1)` $\rightarrow$ **LLL** (Trifásica simétrica, 1,096 muestras)
  - `(1, 1, 1, 1)` $\rightarrow$ **LLLG** (Trifásica a tierra, 1,133 muestras)
- **5 Clases de Producción (Fusión Física):**
  - Se unifican `LLL` y `LLLG` en la clase **`Trifásica`** (2,229 muestras) debido a la indistinguibilidad física de fase en fallas balanceadas (la corriente a tierra se anula vectorialmente y las señales $Va, Vb, Vc, Ia, Ib, Ic$ son idénticas).
