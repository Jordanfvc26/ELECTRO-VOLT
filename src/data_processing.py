"""Módulo de procesamiento, validación y feature engineering de datos eléctricos.

Contiene funciones especializadas para la carga robusta del dataset classData.csv,
auditoría de calidad (nulos, duplicados, bloques secuenciales), mapeo de clases
físicas (5 vs 6 clases), extracción de variables residuales y partición estratificada.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from src.utils import (
    COLUMNAS,
    COLUMNAS_FE_13,
    MAPA_6,
    ORDEN_6,
    ORDEN_CLASES,
    SEMILLA,
    obtener_raiz_proyecto,
    obtener_ruta_datos_procesados,
    obtener_ruta_datos_raw,
)

# Columnas esperadas en el archivo original de Kaggle
COLUMNAS_CRUDAS_REQUERIDAS: List[str] = [
    "Ia", "Ib", "Ic", "Va", "Vb", "Vc", "G", "C", "B", "A"
]


def cargar_datos(ruta_csv: Path | str | None = None) -> pd.DataFrame:
    """Carga el dataset de fallos eléctricos classData.csv validando su integridad.

    Si no se especifica ruta, busca automáticamente en las ubicaciones estándar:
    data/raw/classData.csv, classData.csv en la raíz o en data/.

    Args:
        ruta_csv: Ruta opcional al archivo CSV.

    Returns:
        DataFrame de pandas con los datos cargados.

    Raises:
        FileNotFoundError: Si no se encuentra el archivo en ninguna ruta candidata.
        ValueError: Si faltan columnas requeridas para el modelado.
    """
    if ruta_csv is not None:
        candidatas = [Path(ruta_csv)]
    else:
        raiz = obtener_raiz_proyecto()
        candidatas = [
            obtener_ruta_datos_raw("classData.csv"),
            raiz / "data" / "classData.csv",
            raiz / "classData.csv",
            Path("data/raw/classData.csv"),
            Path("classData.csv"),
        ]

    ruta_encontrada = next((p for p in candidatas if p.exists()), None)
    if ruta_encontrada is None:
        rutas_txt = "\n".join(f" - {p}" for p in candidatas)
        raise FileNotFoundError(
            f"No se encontró 'classData.csv' en ninguna de las rutas esperadas:\n{rutas_txt}"
        )

    df = pd.read_csv(ruta_encontrada)

    # Validar presencia de columnas obligatorias
    faltantes = [col for col in COLUMNAS_CRUDAS_REQUERIDAS if col not in df.columns]
    if faltantes:
        raise ValueError(
            f"El archivo {ruta_encontrada} no contiene las columnas requeridas: {faltantes}"
        )

    return df


def verificar_calidad_datos(df: pd.DataFrame) -> Dict[str, Any]:
    """Ejecuta una auditoría de calidad de datos según los lineamientos del Sprint 1.

    Verifica valores nulos, filas duplicadas, rangos numéricos y cuenta los
    bloques continuos por clase si la columna 'clase_6' o 'clase' existe.

    Args:
        df: DataFrame con las mediciones eléctricas.

    Returns:
        Diccionario con el resumen de métricas de calidad.
    """
    total_filas, total_columnas = df.shape
    conteo_nulos = int(df.isna().sum().sum())
    conteo_duplicados = int(df.duplicated().sum())

    # Detección de bloques secuenciales (alerta de ordenamiento del dataset)
    bloques = None
    columna_clase = "clase_6" if "clase_6" in df.columns else ("clase" if "clase" in df.columns else None)
    if columna_clase is not None:
        bloques = int((df[columna_clase] != df[columna_clase].shift()).sum())

    rangos = {}
    for col in ["Ia", "Ib", "Ic", "Va", "Vb", "Vc"]:
        if col in df.columns:
            rangos[col] = {
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "mean": float(df[col].mean()),
                "std": float(df[col].std()),
            }

    return {
        "total_filas": total_filas,
        "total_columnas": total_columnas,
        "valores_nulos": conteo_nulos,
        "filas_duplicadas": conteo_duplicados,
        "bloques_secuenciales": bloques,
        "rangos_senales": rangos,
    }


def mapear_clases(df: pd.DataFrame, modo: str = "5_clases") -> pd.DataFrame:
    """Mapea las banderas binarias (G, C, B, A) a etiquetas de fallos eléctricos.

    Crea la columna 'clase_6' con las 6 clases originales (Normal, LG, LL, LLG, LLL, LLLG).
    Si modo='5_clases', crea la columna 'clase' uniendo LLL y LLLG en 'Trifásica'.
    Si modo='6_clases', crea la columna 'clase' idéntica a 'clase_6'.

    Args:
        df: DataFrame que contiene las columnas binarias G, C, B, A.
        modo: '5_clases' (producción) o '6_clases' (comparativa documental).

    Returns:
        Copia del DataFrame con las columnas 'clase_6' y 'clase'.
    """
    df_resultado = df.copy()

    banderas = df_resultado[["G", "C", "B", "A"]].values
    df_resultado["clase_6"] = [MAPA_6[tuple(fila)] for fila in banderas]

    if modo == "5_clases":
        df_resultado["clase"] = df_resultado["clase_6"].replace(
            {"LLL": "Trifásica", "LLLG": "Trifásica"}
        )
    elif modo == "6_clases":
        df_resultado["clase"] = df_resultado["clase_6"]
    else:
        raise ValueError(f"Modo no soportado: '{modo}'. Use '5_clases' o '6_clases'.")

    return df_resultado


def agregar_feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """Genera 7 variables de ingeniería residual y extremos (totalizando 13 variables).

    Implementa el enfoque del reporte de optimización para el análisis de 6 clases:
    - I0 = Ia + Ib + Ic (corriente residual / neutro)
    - V0 = Va + Vb + Vc (voltaje residual)
    - abs_I0 = |I0|
    - abs_V0 = |V0|
    - I_max = max(|Ia|, |Ib|, |Ic|)
    - I_min = min(|Ia|, |Ib|, |Ic|)
    - V_max = max(|Va|, |Vb|, |Vc|)

    Args:
        df: DataFrame con las 6 señales Va, Vb, Vc, Ia, Ib, Ic.

    Returns:
        DataFrame con las 7 columnas adicionales agregadas.
    """
    df_fe = df.copy()

    df_fe["I0"] = df_fe["Ia"] + df_fe["Ib"] + df_fe["Ic"]
    df_fe["V0"] = df_fe["Va"] + df_fe["Vb"] + df_fe["Vc"]
    df_fe["abs_I0"] = df_fe["I0"].abs()
    df_fe["abs_V0"] = df_fe["V0"].abs()

    df_fe["I_max"] = df_fe[["Ia", "Ib", "Ic"]].abs().max(axis=1)
    df_fe["I_min"] = df_fe[["Ia", "Ib", "Ic"]].abs().min(axis=1)
    df_fe["V_max"] = df_fe[["Va", "Vb", "Vc"]].abs().max(axis=1)

    return df_fe


def dividir_datos(
    df: pd.DataFrame,
    columnas: List[str] | None = None,
    columna_objetivo: str = "clase",
    test_size: float = 0.20,
    random_state: int = SEMILLA,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.Index, pd.Index]:
    """Realiza la partición estratificada con mezcla obligatoria (shuffle=True).

    Args:
        df: DataFrame con los datos y etiquetas.
        columnas: Lista de variables predictoras. Por defecto COLUMNAS (6 variables).
        columna_objetivo: Nombre de la columna de etiquetas ('clase' o 'clase_6').
        test_size: Proporción del conjunto de prueba (0.20 por defecto).
        random_state: Semilla pseudoaleatoria (42).

    Returns:
        Tupla con (X_ent, X_pru, y_ent, y_pru, idx_ent, idx_pru).
    """
    cols = columnas if columnas is not None else COLUMNAS
    X = df[cols]
    y = df[columna_objetivo]

    idx_ent, idx_pru = train_test_split(
        df.index,
        test_size=test_size,
        stratify=y,
        shuffle=True,
        random_state=random_state,
    )

    X_ent = X.loc[idx_ent]
    X_pru = X.loc[idx_pru]
    y_ent = y.loc[idx_ent]
    y_pru = y.loc[idx_pru]

    return X_ent, X_pru, y_ent, y_pru, idx_ent, idx_pru


def exportar_ejemplos_prueba(
    df: pd.DataFrame,
    idx_pru: pd.Index,
    ruta_salida: Path | str | None = None,
    n_por_clase: int = 3,
    columnas: List[str] | None = None,
    columna_clase: str = "clase",
) -> pd.DataFrame:
    """Extrae ejemplos de prueba representativos por clase para validación de la interfaz web.

    Guarda un archivo CSV con las señales continuas y la etiqueta real.

    Args:
        df: DataFrame original con las etiquetas mapeadas.
        idx_pru: Índices pertenecientes al conjunto de prueba.
        ruta_salida: Ruta de destino (por defecto data/processed/ejemplos_prueba.csv).
        n_por_clase: Cantidad de ejemplos a extraer por cada clase (3 por defecto).
        columnas: Lista de variables de entrada.
        columna_clase: Columna de clasificación.

    Returns:
        DataFrame con los ejemplos seleccionados.
    """
    cols = columnas if columnas is not None else COLUMNAS
    columnas_totales = cols + [columna_clase]

    ejemplos = (
        df.loc[idx_pru]
        .groupby(columna_clase)
        .head(n_por_clase)[columnas_totales]
        .sort_values(columna_clase)
        .reset_index(drop=True)
    )

    if ruta_salida is None:
        ruta_principal = obtener_ruta_datos_procesados("ejemplos_prueba.csv")
    else:
        ruta_principal = Path(ruta_salida)

    ruta_principal.parent.mkdir(parents=True, exist_ok=True)
    ejemplos.to_csv(ruta_principal, index=False)

    return ejemplos
