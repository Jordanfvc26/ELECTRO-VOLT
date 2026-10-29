"""Módulo de utilidades y constantes globales para el proyecto ELECTROVOLT.

Provee configuraciones de reproducibilidad, definiciones de clases eléctricas,
mensajes operativos estandarizados y utilidades de gestión de rutas y archivos,
sincronizados directamente con la configuración centralizada (config.yaml).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from src.config import cargar_configuracion, obtener_logger, obtener_raiz_proyecto

# Instancia de logger para utilidades
logger = obtener_logger(__name__)

# Carga inicial de configuración centralizada
_config = cargar_configuracion()

# ==============================================================================
# CONSTANTES GLOBALES Y REPRODUCIBILIDAD (CONFIGURABLES)
# ==============================================================================
SEMILLA: int = int(_config.get("semilla", 42))

# Columnas canónicas de entrada para el modelo en producción (6 variables)
COLUMNAS: List[str] = list(
    _config.get("datos", {}).get("columnas_modelo", ["Va", "Vb", "Vc", "Ia", "Ib", "Ic"])
)

# Columnas extendidas para feature engineering experimental (13 variables)
COLUMNAS_FE_13: List[str] = list(
    _config.get("datos", {}).get("columnas_fe_13", [
        "Va", "Vb", "Vc", "Ia", "Ib", "Ic",
        "I0", "V0", "abs_I0", "abs_V0",
        "I_max", "I_min", "V_max"
    ])
)

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
    "Normal": "Operación normal. Parámetros del sistema dentro de los márgenes nominales.",
    "LG": "Falla de línea a tierra detectada. Se recomienda inspección visual y prueba de aislamiento en la fase afectada.",
    "LL": "Falla entre fases detectada sin contacto a tierra. Verificar aislamiento entre conductores involucrados.",
    "LLG": "Falla de doble línea a tierra. Riesgo elevado de corriente de cortocircuito; desenergizar tramo según protocolo.",
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
# RANGOS FÍSICOS DE ENTRENAMIENTO Y VALIDACIÓN OOD (OUT-OF-DISTRIBUTION)
# ==============================================================================
_cfg_op = _config.get("operacion", {})
_cfg_volt = _cfg_op.get("rango_voltaje_pu", {"min": -0.65, "max": 0.65})
_cfg_corr = _cfg_op.get("rango_corriente_amperios", {"min": -900.0, "max": 900.0})

RANGO_VOLTAJE: Tuple[float, float] = (float(_cfg_volt.get("min", -0.65)), float(_cfg_volt.get("max", 0.65)))
RANGO_CORRIENTE: Tuple[float, float] = (float(_cfg_corr.get("min", -900.0)), float(_cfg_corr.get("max", 900.0)))
UMBRAL_CONFIANZA_MINIMA: float = float(_cfg_op.get("umbral_confianza_minima", 0.80))
UMBRAL_RETORNO_TIERRA_A: float = float(_cfg_op.get("umbral_retorno_tierra_amperios", 20.0))


def validar_rango_senales(
    Va: float,
    Vb: float,
    Vc: float,
    Ia: float,
    Ib: float,
    Ic: float,
) -> Tuple[bool, List[str]]:
    """Valida si las 6 señales de telemetría se encuentran dentro del rango físico de entrenamiento.

    El modelo de Machine Learning fue entrenado exclusivamente en estos rangos:
    - Tensiones de fase: [-0.65, 0.65] p.u.
    - Corrientes de fase: [-900.0, 900.0] A

    Args:
        Va: Tensión Fase A (en p.u.).
        Vb: Tensión Fase B (en p.u.).
        Vc: Tensión Fase C (en p.u.).
        Ia: Corriente Fase A (en Amperios).
        Ib: Corriente Fase B (en Amperios).
        Ic: Corriente Fase C (en Amperios).

    Returns:
        Tupla (es_valido, lista_anomalias). Si es_valido es False, lista_anomalias contiene
        el detalle de las variables que violan el dominio de entrenamiento.

    Raises:
        TypeError: Si alguno de los valores no es convertible a float.
    """
    anomalias: List[str] = []
    voltajes = [("Va", Va), ("Vb", Vb), ("Vc", Vc)]
    corrientes = [("Ia", Ia), ("Ib", Ib), ("Ic", Ic)]

    for nombre, val in voltajes:
        if val is None:
            anomalias.append(f"{nombre} es nulo (None)")
            continue
        try:
            val_f = float(val)
        except (ValueError, TypeError) as err:
            raise TypeError(f"El valor de {nombre} debe ser numérico. Recibido: {val}") from err

        if not (RANGO_VOLTAJE[0] <= val_f <= RANGO_VOLTAJE[1]):
            anomalias.append(
                f"{nombre} = {val_f:.4f} p.u. (rango de entrenamiento: [{RANGO_VOLTAJE[0]}, {RANGO_VOLTAJE[1]}])"
            )

    for nombre, val in corrientes:
        if val is None:
            anomalias.append(f"{nombre} es nulo (None)")
            continue
        try:
            val_f = float(val)
        except (ValueError, TypeError) as err:
            raise TypeError(f"El valor de {nombre} debe ser numérico. Recibido: {val}") from err

        if not (RANGO_CORRIENTE[0] <= val_f <= RANGO_CORRIENTE[1]):
            anomalias.append(
                f"{nombre} = {val_f:.2f} A (rango de entrenamiento: [{RANGO_CORRIENTE[0]}, {RANGO_CORRIENTE[1]}])"
            )

    if anomalias:
        logger.debug(f"Anomalías fuera de rango detectadas: {anomalias}")

    return (len(anomalias) == 0, anomalias)


def determinar_estados_fases(
    diag_clase: str,
    corriente_n: float = 0.0,
    fases_afectadas: List[str] | None = None,
) -> Tuple[bool, bool, bool, bool]:
    """Determina el estado operativo (falla o nominal) de las fases A, B, C y Neutro/Tierra.

    Garantiza sincronización total entre la predicción del modelo y las tarjetas sinópticas:
    - 'Normal': Todo el sistema en verde (falla_a=falla_b=falla_c=falla_g=False).
    - Si se especifica 'fases_afectadas', activa con precisión las fases identificadas.
    - Si 'fases_afectadas' es None, mantiene el mapeo canónico por defecto para retrocompatibilidad:
      - 'LG': Fase A y Tierra activas.
      - 'LL': Fases B y C activas, tierra aislada.
      - 'LLG': Fases A, B y Tierra activas.
      - 'Trifásica': Fases A, B y C activas. Tierra activa solo si |In| > 20 A.

    Args:
        diag_clase: Diagnóstico predicho por el modelo ('Normal', 'LG', 'LL', 'LLG', 'Trifásica').
        corriente_n: Corriente residual calculada (Ia + Ib + Ic) en Amperios.
        fases_afectadas: Lista opcional con las fases involucradas (ej. ['A'], ['B', 'C']).

    Returns:
        Tupla (falla_a, falla_b, falla_c, falla_g) con valores booleanos.
    """
    if not isinstance(diag_clase, str):
        diag_clase = str(diag_clase)

    if diag_clase == "Normal":
        return (False, False, False, False)

    if fases_afectadas is not None:
        falla_a = "A" in fases_afectadas
        falla_b = "B" in fases_afectadas
        falla_c = "C" in fases_afectadas
        if diag_clase in ("LG", "LLG"):
            falla_g = True
        elif diag_clase == "Trifásica":
            falla_g = abs(corriente_n) > UMBRAL_RETORNO_TIERRA_A
        else:  # LL u otros
            falla_g = False
        return (falla_a, falla_b, falla_c, falla_g)

    # Mapeo canónico por defecto
    if diag_clase == "LG":
        return (True, False, False, True)
    elif diag_clase == "LL":
        return (False, True, True, False)
    elif diag_clase == "LLG":
        return (True, True, False, True)
    elif diag_clase == "Trifásica":
        retorno_tierra = abs(corriente_n) > UMBRAL_RETORNO_TIERRA_A
        return (True, True, True, retorno_tierra)
    else:
        retorno_tierra = abs(corriente_n) > UMBRAL_RETORNO_TIERRA_A
        return (False, False, False, retorno_tierra)


# ==============================================================================
# GESTIÓN DE RUTAS RELATIVAS DEL PROYECTO
# ==============================================================================
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

    Raises:
        TypeError: Si los datos no son serializables a JSON.
        IOError: Si ocurre un error al escribir el archivo en disco.
    """
    ruta = Path(ruta_archivo)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
        logger.debug(f"Archivo JSON guardado exitosamente en: {ruta}")
    except TypeError as e:
        logger.error(f"Error de serialización JSON en {ruta}: {e}")
        raise
    except IOError as e:
        logger.error(f"Error de E/S al escribir {ruta}: {e}")
        raise
    return ruta


def cargar_json(ruta_archivo: Path | str) -> Dict[str, Any]:
    """Carga y parsea un archivo JSON asegurando codificación UTF-8.

    Args:
        ruta_archivo: Ruta al archivo JSON.

    Returns:
        Diccionario con los datos parseados.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError: Si el contenido del archivo no es un JSON válido.
    """
    ruta = Path(ruta_archivo)
    if not ruta.exists():
        logger.error(f"Archivo no encontrado al cargar JSON: {ruta}")
        raise FileNotFoundError(f"No se encontró el archivo JSON en: {ruta}")
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Error al decodificar JSON en {ruta}: {e}")
        raise ValueError(f"El archivo {ruta} contiene JSON inválido: {e}") from e
