"""Módulo de procesamiento, validación y feature engineering de datos eléctricos.

Contiene funciones especializadas para la carga robusta del dataset classData.csv,
auditoría de calidad (nulos, duplicados, bloques secuenciales), mapeo de clases
físicas (5 vs 6 clases), extracción de variables residuales y partición estratificada.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from src.config import obtener_logger
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

logger = obtener_logger(__name__)

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
        TypeError: Si ruta_csv no es de tipo Path o str.
        FileNotFoundError: Si no se encuentra el archivo en ninguna ruta candidata.
        ValueError: Si faltan columnas requeridas o el archivo está vacío.
    """
    if ruta_csv is not None:
        if not isinstance(ruta_csv, (Path, str)):
            raise TypeError(f"ruta_csv debe ser Path, str o None. Recibido: {type(ruta_csv)}")
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

    ruta_encontrada = next((p for p in candidatas if p.exists() and p.is_file()), None)
    if ruta_encontrada is None:
        rutas_txt = "\n".join(f" - {p}" for p in candidatas)
        logger.error(f"Archivo de datos no localizado en candidatos:\n{rutas_txt}")
        raise FileNotFoundError(
            f"No se encontró 'classData.csv' en ninguna de las rutas esperadas:\n{rutas_txt}"
        )

    logger.info(f"Cargando dataset desde: {ruta_encontrada}")
    try:
        df = pd.read_csv(ruta_encontrada)
    except pd.errors.EmptyDataError as err:
        logger.error(f"El archivo {ruta_encontrada} está vacío.")
        raise ValueError(f"El archivo CSV {ruta_encontrada} se encuentra vacío.") from err
    except Exception as err:
        logger.error(f"Error al leer el archivo CSV {ruta_encontrada}: {err}")
        raise ValueError(f"Error de lectura en {ruta_encontrada}: {err}") from err

    if df.empty:
        raise ValueError(f"El archivo {ruta_encontrada} no contiene registros.")

    # Validar presencia de columnas obligatorias
    faltantes = [col for col in COLUMNAS_CRUDAS_REQUERIDAS if col not in df.columns]
    if faltantes:
        logger.error(f"Columnas faltantes en dataset: {faltantes}")
        raise ValueError(
            f"El archivo {ruta_encontrada} no contiene las columnas requeridas: {faltantes}"
        )

    logger.info(f"Dataset cargado exitosamente: {df.shape[0]} filas, {df.shape[1]} columnas.")
    return df


def verificar_calidad_datos(df: pd.DataFrame) -> Dict[str, Any]:
    """Ejecuta una auditoría de calidad de datos según los lineamientos del Sprint 1.

    Verifica valores nulos, filas duplicadas, rangos numéricos y cuenta los
    bloques continuos por clase si la columna 'clase_6' o 'clase' existe.

    Args:
        df: DataFrame con las mediciones eléctricas.

    Returns:
        Diccionario con el resumen de métricas de calidad.

    Raises:
        TypeError: Si df no es una instancia de pd.DataFrame.
        ValueError: Si df está vacío.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Se esperaba pd.DataFrame, se recibió {type(df)}")
    if df.empty:
        raise ValueError("El DataFrame suministrado está vacío.")

    total_filas, total_columnas = df.shape
    conteo_nulos = int(df.isna().sum().sum())
    conteo_duplicados = int(df.duplicated().sum())

    # Detección de bloques secuenciales (alerta de ordenamiento del dataset)
    bloques = None
    columna_clase = "clase_6" if "clase_6" in df.columns else ("clase" if "clase" in df.columns else None)
    if columna_clase is not None:
        bloques = int((df[columna_clase] != df[columna_clase].shift()).sum())

    rangos: Dict[str, Dict[str, float]] = {}
    for col in ["Ia", "Ib", "Ic", "Va", "Vb", "Vc"]:
        if col in df.columns:
            rangos[col] = {
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "mean": float(df[col].mean()),
                "std": float(df[col].std()),
            }

    logger.info(
        f"Auditoría de calidad: {total_filas} filas, {conteo_nulos} nulos, "
        f"{conteo_duplicados} duplicados, {bloques} bloques de clase."
    )

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

    Raises:
        TypeError: Si df no es pd.DataFrame.
        ValueError: Si faltan columnas de banderas o el modo no es soportado.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Se esperaba pd.DataFrame, se recibió {type(df)}")

    banderas_cols = ["G", "C", "B", "A"]
    faltantes = [c for c in banderas_cols if c not in df.columns]
    if faltantes:
        raise ValueError(f"Faltan las columnas de banderas binarias: {faltantes}")

    df_resultado = df.copy()

    banderas = df_resultado[banderas_cols].values
    try:
        df_resultado["clase_6"] = [MAPA_6[tuple(fila)] for fila in banderas]
    except KeyError as err:
        logger.error(f"Combinación binaria no reconocida en banderas: {err}")
        raise ValueError(f"Tupla de banderas binarias inválida: {err}") from err

    if modo == "5_clases":
        df_resultado["clase"] = df_resultado["clase_6"].replace(
            {"LLL": "Trifásica", "LLLG": "Trifásica"}
        )
    elif modo == "6_clases":
        df_resultado["clase"] = df_resultado["clase_6"]
    else:
        raise ValueError(f"Modo no soportado: '{modo}'. Use '5_clases' o '6_clases'.")

    logger.debug(f"Mapeo de clases completado en modo '{modo}'. Clases únicas: {list(df_resultado['clase'].unique())}")
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

    Raises:
        TypeError: Si df no es pd.DataFrame.
        ValueError: Si faltan señales eléctricas básicas en df.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Se esperaba pd.DataFrame, se recibió {type(df)}")

    senales_requeridas = ["Ia", "Ib", "Ic", "Va", "Vb", "Vc"]
    faltantes = [c for c in senales_requeridas if c not in df.columns]
    if faltantes:
        raise ValueError(f"Faltan señales para feature engineering: {faltantes}")

    df_fe = df.copy()

    df_fe["I0"] = df_fe["Ia"] + df_fe["Ib"] + df_fe["Ic"]
    df_fe["V0"] = df_fe["Va"] + df_fe["Vb"] + df_fe["Vc"]
    df_fe["abs_I0"] = df_fe["I0"].abs()
    df_fe["abs_V0"] = df_fe["V0"].abs()

    df_fe["I_max"] = df_fe[["Ia", "Ib", "Ic"]].abs().max(axis=1)
    df_fe["I_min"] = df_fe[["Ia", "Ib", "Ic"]].abs().min(axis=1)
    df_fe["V_max"] = df_fe[["Va", "Vb", "Vc"]].abs().max(axis=1)

    logger.debug(f"Feature engineering aplicado exitosamente: 7 nuevas variables generadas.")
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

    Raises:
        TypeError: Si df no es pd.DataFrame.
        ValueError: Si test_size no está en (0, 1) o columna_objetivo no existe.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Se esperaba pd.DataFrame, se recibió {type(df)}")

    if not (0.0 < test_size < 1.0):
        raise ValueError(f"test_size debe estar entre 0.0 y 1.0 exclusivo. Recibido: {test_size}")

    if columna_objetivo not in df.columns:
        raise ValueError(f"La columna objetivo '{columna_objetivo}' no existe en el DataFrame.")

    cols = columnas if columnas is not None else COLUMNAS
    faltantes = [c for c in cols if c not in df.columns]
    if faltantes:
        raise ValueError(f"Columnas predictoras ausentes en el DataFrame: {faltantes}")

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

    logger.info(
        f"Partición estratificada completada: Train={len(X_ent)} muestras, "
        f"Test={len(X_pru)} muestras (test_size={test_size}, shuffle=True)."
    )

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

    Raises:
        TypeError: Si df no es pd.DataFrame o idx_pru no es iterable.
        ValueError: Si n_por_clase <= 0 o columnas ausentes.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Se esperaba pd.DataFrame, se recibió {type(df)}")

    if n_por_clase <= 0:
        raise ValueError(f"n_por_clase debe ser mayor a cero. Recibido: {n_por_clase}")

    cols = columnas if columnas is not None else COLUMNAS
    columnas_totales = cols + [columna_clase]

    faltantes = [c for c in columnas_totales if c not in df.columns]
    if faltantes:
        raise ValueError(f"Columnas ausentes para exportación de ejemplos: {faltantes}")

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
    try:
        ejemplos.to_csv(ruta_principal, index=False)
        logger.info(f"Ejemplos de prueba exportados exitosamente ({len(ejemplos)} filas) en: {ruta_principal}")
    except Exception as err:
        logger.error(f"Error al escribir ejemplos de prueba en {ruta_principal}: {err}")
        raise IOError(f"No se pudo guardar {ruta_principal}: {err}") from err

    return ejemplos
