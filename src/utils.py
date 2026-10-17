"""Módulo de utilidades y constantes globales para el proyecto ELECTRO-VOLT.

Provee configuraciones de reproducibilidad, definiciones de clases eléctricas,
mensajes operativos estandarizados y utilidades de gestión de rutas y archivos.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

# ==============================================================================
# CONSTANTES GLOBALES Y REPRODUCIBILIDAD
# ==============================================================================
SEMILLA: int = 42

# Columnas canónicas de entrada para el modelo en producción (6 variables)
COLUMNAS: List[str] = ["Va", "Vb", "Vc", "Ia", "Ib", "Ic"]

# Columnas extendidas para feature engineering experimental (13 variables)
COLUMNAS_FE_13: List[str] = [
    "Va", "Vb", "Vc", "Ia", "Ib", "Ic",
    "I0", "V0", "abs_I0", "abs_V0",
    "I_max", "I_min", "V_max"
]

# Mapeo de banderas binarias (G, C, B, A) a las 6 clases originales de Kaggle
MAPA_6: Dict[Tuple[int, int, int, int], str] = {
    (0, 0, 0, 0): "Normal",
    (1, 0, 0, 1): "LG",    # Línea a tierra (Fase A)
    (0, 1, 1, 0): "LL",    # Línea a línea (Fases B-C)
    (1, 0, 1, 1): "LLG",   # Doble línea a tierra (Fases A-B a tierra)
    (0, 1, 1, 1): "LLL",   # Trifásica simétrica
    (1, 1, 1, 1): "LLLG",  # Trifásica a tierra
}

# Orden canónico de las 6 clases originales
ORDEN_6: List[str] = ["Normal", "LG", "LL", "LLG", "LLL", "LLLG"]

# Orden canónico del sistema ajustado a 5 clases (Producción)
ORDEN_CLASES: List[str] = ["Normal", "LG", "LL", "LLG", "Trifásica"]

# Mensajes normalizados de recomendación y acción técnica para el operador
MENSAJES_OPERADOR: Dict[str, str] = {
    "Normal": "Operación normal. No se detecta falla.",
    "LG": "Falla de línea a tierra.",
    "LL": "Falla de línea a línea.",
    "LLG": "Falla de doble línea a tierra.",
    "Trifásica": (
        "Falla trifásica. Con las señales de fase no se distingue si involucra tierra "
        "(LLL o LLLG); verificar con la medición de neutro/tierra."
    ),
}

# Justificación física del ajuste de clases para soporte técnico y auditoría
NOTA_CLASES: str = (
    "LLL y LLLG se unieron en una sola clase 'Trifásica' porque en una falla trifásica "
    "balanceada la conexión a tierra no lleva corriente y las señales de fase son las mismas."
)


# ==============================================================================
# GESTIÓN DE RUTAS RELATIVAS DEL PROYECTO
# ==============================================================================
def obtener_raiz_proyecto() -> Path:
    """Retorna la ruta absoluta del directorio raíz del repositorio ELECTRO-VOLT."""
    return Path(__file__).resolve().parents[1]


def obtener_ruta_datos_raw(nombre_archivo: str = "classData.csv") -> Path:
    """Retorna la ruta al archivo de datos original dentro de data/raw/."""
    return obtener_raiz_proyecto() / "data" / "raw" / nombre_archivo


def obtener_ruta_datos_procesados(nombre_archivo: str = "ejemplos_prueba.csv") -> Path:
    """Retorna la ruta al archivo dentro de data/processed/."""
    return obtener_raiz_proyecto() / "data" / "processed" / nombre_archivo


def obtener_ruta_modelo(nombre_archivo: str = "best_model.pkl") -> Path:
    """Retorna la ruta de guardado o lectura dentro de models/."""
    return obtener_raiz_proyecto() / "models" / nombre_archivo


def obtener_ruta_resultados(subdirectorio: str = "figures") -> Path:
    """Retorna la ruta del subdirectorio de resultados (figures, metrics o reports)."""
    ruta = obtener_raiz_proyecto() / "results" / subdirectorio
    ruta.mkdir(parents=True, exist_ok=True)
    return ruta


# ==============================================================================
# SERIALIZACIÓN Y PERSISTENCIA DE METADATOS (JSON)
# ==============================================================================
def guardar_json(datos: Dict[str, Any], ruta_archivo: Path | str) -> Path:
    """Guarda un diccionario en formato JSON con indentación y soporte UTF-8.

    Args:
        datos: Diccionario de datos a serializar.
        ruta_archivo: Ruta de destino (Path o string).

    Returns:
        Path del archivo guardado.
    """
    ruta = Path(ruta_archivo)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)
    return ruta


def cargar_json(ruta_archivo: Path | str) -> Dict[str, Any]:
    """Carga y parsea un archivo JSON asegurando codificación UTF-8.

    Args:
        ruta_archivo: Ruta al archivo JSON.

    Returns:
        Diccionario con los datos parseados.
    """
    ruta = Path(ruta_archivo)
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el archivo JSON en: {ruta}")
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)
