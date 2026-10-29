"""Módulo de utilidades generales, carga en memoria y caché para la interfaz Streamlit."""

from __future__ import annotations

import base64
import logging
from pathlib import Path
import sys
from typing import Any, Dict, Optional, Tuple

import pandas as pd
import shap
import streamlit as st

raiz = Path(__file__).resolve().parents[1]
if str(raiz) not in sys.path:
    sys.path.insert(0, str(raiz))

from src.config import obtener_logger
from src.model import cargar_paquete_modelo
from src.utils import cargar_json, obtener_ruta_datos_procesados, obtener_ruta_resultados

logger = obtener_logger(__name__)


def render_html(html_str: str) -> None:
    """Renderiza contenido HTML garantizando cero indentación en cada línea para evitar code blocks en Markdown.

    Args:
        html_str: Cadena con el contenido HTML a renderizar.
    """
    lines = [line.strip() for line in html_str.strip().splitlines() if line.strip()]
    cleaned_html = "\n".join(lines)
    st.markdown(cleaned_html, unsafe_allow_html=True)


@st.cache_resource(show_spinner=False)
def cargar_recursos_modelo() -> Tuple[Dict[str, Any], Any]:
    """Carga el paquete del modelo y precalienta el explicador TreeExplainer una sola vez.

    Returns:
        Tupla con (paquete_modelo_dict, explicador_shap).

    Raises:
        RuntimeError: Si ocurre un fallo en la carga del modelo o inicialización de SHAP.
    """
    logger.info("Iniciando carga de recursos del modelo para la interfaz web...")
    try:
        paquete = cargar_paquete_modelo()
        modelo = paquete["modelo"]
        if hasattr(modelo, "named_steps"):
            estimador = modelo.named_steps.get("randomforestclassifier", modelo)
        else:
            estimador = modelo
        explicador = shap.TreeExplainer(estimador)
        logger.info("Recursos del modelo y explicador SHAP cargados exitosamente.")
        return paquete, explicador
    except Exception as err:
        logger.error(f"Fallo crítico al cargar recursos del modelo: {err}")
        raise RuntimeError(f"No fue posible cargar el modelo de Machine Learning: {err}") from err


@st.cache_data(show_spinner=False)
def cargar_ejemplos_prueba() -> pd.DataFrame | None:
    """Carga las muestras representativas preprocesadas para pruebas de 1 clic.

    Returns:
        DataFrame con los ejemplos o None si el archivo no existe.
    """
    ruta = obtener_ruta_datos_procesados("ejemplos_prueba.csv")
    if ruta.exists():
        try:
            df = pd.read_csv(ruta)
            logger.debug(f"Ejemplos de prueba cargados: {len(df)} registros.")
            return df
        except Exception as err:
            logger.warning(f"Error al leer ejemplos de prueba en {ruta}: {err}")
            return None
    logger.warning(f"Archivo de ejemplos de prueba no encontrado en: {ruta}")
    return None


@st.cache_data(show_spinner=False)
def cargar_metricas_sistema() -> dict | None:
    """Carga el reporte de métricas y cumplimiento de metas SMART.

    Returns:
        Diccionario con las métricas del sistema o None si no se encuentra.
    """
    ruta = obtener_ruta_resultados("metrics") / "metricas.json"
    if ruta.exists():
        try:
            return cargar_json(ruta)
        except Exception as err:
            logger.warning(f"Error al cargar métricas del sistema desde {ruta}: {err}")
            return None
    return None


@st.cache_data(show_spinner=False)
def obtener_logo_base64() -> str:
    """Carga y cachea el logotipo oficial en base64 para renderizado universal.

    Returns:
        Cadena en base64 del logotipo PNG o cadena vacía si no existe.
    """
    ruta_logo = raiz / "src" / "images" / "electrovolt-logotipo.png"
    if ruta_logo.exists():
        try:
            return base64.b64encode(ruta_logo.read_bytes()).decode("utf-8")
        except Exception as err:
            logger.warning(f"No se pudo codificar el logotipo en base64: {err}")
            return ""
    return ""


@st.cache_data(show_spinner=False)
def obtener_isotipo_base64() -> str:
    """Carga y cachea el isotipo oficial en base64 para favicon y metadatos.

    Returns:
        Cadena en base64 del isotipo PNG o cadena vacía si no existe.
    """
    ruta_iso = raiz / "src" / "images" / "electrovolt-isotipo.png"
    if ruta_iso.exists():
        try:
            return base64.b64encode(ruta_iso.read_bytes()).decode("utf-8")
        except Exception as err:
            logger.warning(f"No se pudo codificar el isotipo en base64: {err}")
            return ""
    return ""
