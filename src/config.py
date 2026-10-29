"""Módulo de configuración centralizada y gestión de logging para ELECTROVOLT.

Carga parámetros desde config.yaml y variables de entorno (.env), garantizando
que ningún hiperparámetro o ruta esté hardcodeado en el código fuente.
Provee utilidades de logging estructurado con formato estándar para auditoría.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ==============================================================================
# CONFIGURACIÓN POR DEFECTO (FALLBACK ROBUSTO)
# ==============================================================================
CONFIGURACION_POR_DEFECTO: Dict[str, Any] = {
    "proyecto": {
        "nombre": "ELECTROVOLT",
        "version": "1.0.0",
        "autores": [
            "Jordan Fabian Vera Coello",
            "Jorge Rafael Estrella Frere",
        ],
        "descripcion": "Detección y Clasificación Multiclase de Fallos Eléctricos con Machine Learning e IA Explicable",
        "entorno": "production",
    },
    "semilla": 42,
    "datos": {
        "ruta_raw": "data/raw/classData.csv",
        "ruta_procesados": "data/processed/ejemplos_prueba.csv",
        "test_size": 0.20,
        "shuffle": True,
        "columnas_requeridas_crudas": [
            "Ia", "Ib", "Ic", "Va", "Vb", "Vc", "G", "C", "B", "A"
        ],
        "columnas_modelo": ["Va", "Vb", "Vc", "Ia", "Ib", "Ic"],
        "columnas_fe_13": [
            "Va", "Vb", "Vc", "Ia", "Ib", "Ic",
            "I0", "V0", "abs_I0", "abs_V0",
            "I_max", "I_min", "V_max",
        ],
    },
    "modelos": {
        "random_forest": {
            "n_estimators": 100,
            "class_weight": "balanced",
            "random_state": 42,
            "n_jobs": -1,
        },
        "regresion_logistica": {
            "max_iter": 2000,
            "class_weight": "balanced",
            "random_state": 42,
        },
        "svm_rbf": {
            "kernel": "rbf",
            "C": 10.0,
            "gamma": "scale",
            "class_weight": "balanced",
            "probability": True,
            "random_state": 42,
        },
        "validacion_cruzada": {
            "n_splits": 5,
            "shuffle": True,
            "scoring": "f1_macro",
        },
        "serializacion": {
            "nombre_best_model": "best_model.pkl",
            "nombre_joblib": "modelo_fallos_rf.joblib",
            "nombre_v1": "model_v1.pkl",
            "compresion": 3,
        },
    },
    "operacion": {
        "rango_voltaje_pu": {
            "min": -0.65,
            "max": 0.65,
        },
        "rango_corriente_amperios": {
            "min": -900.0,
            "max": 900.0,
        },
        "umbral_confianza_minima": 0.80,
        "umbral_retorno_tierra_amperios": 20.0,
        "tiempo_maximo_inferencia_ms": 100.0,
    },
    "metas_smart": {
        "accuracy_minimo": 0.90,
        "f1_macro_minimo": 0.90,
        "recall_minimo_por_clase": 0.85,
        "latencia_maxima_ms": 100.0,
        "throughput_minimo_muestras_seg": 500.0,
        "tiempo_entrenamiento_maximo_seg": 300.0,
    },
    "logging": {
        "nivel": "INFO",
        "formato": "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        "formato_fecha": "%Y-%m-%d %H:%M:%S",
    },
}

_CONFIG_CACHE: Optional[Dict[str, Any]] = None


def obtener_raiz_proyecto() -> Path:
    """Retorna la ruta absoluta del directorio raíz del repositorio ELECTROVOLT.

    Utiliza resolución basada en __file__ para garantizar portabilidad en
    cualquier sistema operativo sin rutas absolutas fijas.

    Returns:
        Path del directorio raíz del proyecto.
    """
    return Path(__file__).resolve().parents[1]


def cargar_configuracion(
    ruta_config: Optional[Path | str] = None,
    recargar: bool = False,
) -> Dict[str, Any]:
    """Carga y valida el archivo de configuración YAML del proyecto.

    Aplica fusión con la configuración por defecto y sobreescrituras por
    variables de entorno (ELECTROVOLT_SEMILLA, ELECTROVOLT_LOG_LEVEL, etc.).

    Args:
        ruta_config: Ruta opcional al archivo de configuración. Si es None,
            se busca en la variable de entorno ELECTROVOLT_CONFIG_PATH o
            en la raíz del proyecto como config.yaml.
        recargar: Booleano que fuerza la recarga ignorando la caché.

    Returns:
        Diccionario anidado con la configuración activa.
    """
    global _CONFIG_CACHE

    if _CONFIG_CACHE is not None and not recargar and ruta_config is None:
        return _CONFIG_CACHE

    raiz = obtener_raiz_proyecto()
    if ruta_config is not None:
        candidata = Path(ruta_config)
    else:
        env_path = os.getenv("ELECTROVOLT_CONFIG_PATH")
        if env_path:
            candidata = Path(env_path)
            if not candidata.is_absolute():
                candidata = raiz / candidata
        else:
            candidata = raiz / "config.yaml"

    config_cargada: Dict[str, Any] = {}
    if candidata.exists() and yaml is not None:
        try:
            with open(candidata, "r", encoding="utf-8") as f:
                contenido = yaml.safe_load(f)
                if isinstance(contenido, dict):
                    config_cargada = contenido
        except Exception as e:
            logging.getLogger("src.config").warning(
                f"No se pudo parsear el archivo YAML en {candidata}: {e}. "
                "Se utilizará la configuración por defecto."
            )

    # Fusión profunda con valores por defecto
    config_final = _fusionar_diccionarios(CONFIGURACION_POR_DEFECTO, config_cargada)

    # Sobreescrituras desde variables de entorno
    env_seed = os.getenv("ELECTROVOLT_SEMILLA")
    if env_seed is not None:
        try:
            config_final["semilla"] = int(env_seed)
        except ValueError:
            pass

    env_log_level = os.getenv("ELECTROVOLT_LOG_LEVEL")
    if env_log_level is not None:
        config_final.setdefault("logging", {})["nivel"] = env_log_level.upper()

    env_umbral_conf = os.getenv("ELECTROVOLT_UMBRAL_CONFIANZA")
    if env_umbral_conf is not None:
        try:
            config_final.setdefault("operacion", {})["umbral_confianza_minima"] = float(env_umbral_conf)
        except ValueError:
            pass

    env_umbral_tierra = os.getenv("ELECTROVOLT_UMBRAL_TIERRA")
    if env_umbral_tierra is not None:
        try:
            config_final.setdefault("operacion", {})["umbral_retorno_tierra_amperios"] = float(env_umbral_tierra)
        except ValueError:
            pass

    _CONFIG_CACHE = config_final
    return config_final


def _fusionar_diccionarios(base: Dict[str, Any], sobreescritura: Dict[str, Any]) -> Dict[str, Any]:
    """Combina recursivamente dos diccionarios preservando subclaves no declaradas."""
    resultado = dict(base)
    for k, v in sobreescritura.items():
        if k in resultado and isinstance(resultado[k], dict) and isinstance(v, dict):
            resultado[k] = _fusionar_diccionarios(resultado[k], v)
        else:
            resultado[k] = v
    return resultado


def obtener_logger(nombre: str) -> logging.Logger:
    """Configura y retorna un logger estándar unificado para el módulo solicitante.

    Aplica el formato y nivel especificados en config.yaml o variables de entorno.
    Evita la duplicación de handlers si se invoca múltiples veces.

    Args:
        nombre: Identificador del módulo (típicamente __name__).

    Returns:
        Instancia de logging.Logger configurada.
    """
    config = cargar_configuracion()
    log_cfg = config.get("logging", CONFIGURACION_POR_DEFECTO["logging"])
    nivel_texto = str(log_cfg.get("nivel", "INFO")).upper()
    formato = log_cfg.get("formato", "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s")
    formato_fecha = log_cfg.get("formato_fecha", "%Y-%m-%d %H:%M:%S")

    nivel_numerico = getattr(logging, nivel_texto, logging.INFO)

    logger = logging.getLogger(nombre)
    logger.setLevel(nivel_numerico)

    if not logger.handlers:
        consola = logging.StreamHandler()
        consola.setLevel(nivel_numerico)
        formateador = logging.Formatter(fmt=formato, datefmt=formato_fecha)
        consola.setFormatter(formateador)
        logger.addHandler(consola)

    return logger

