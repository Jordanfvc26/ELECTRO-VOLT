"""Módulo de utilidades generales, carga en memoria y caché"""

from __future__ import annotations

import base64
from pathlib import Path
import sys

import pandas as pd
import shap
import streamlit as st

raiz = Path(__file__).resolve().parents[1]
if str(raiz) not in sys.path:
    sys.path.insert(0, str(raiz))

from src.model import cargar_paquete_modelo
from src.utils import cargar_json, obtener_ruta_datos_procesados, obtener_ruta_resultados


def render_html(html_str: str) -> None:
    """Renderiza contenido HTML garantizando cero indentación en cada línea para evitar code blocks en Markdown."""
    lines = [line.strip() for line in html_str.strip().splitlines() if line.strip()]
    cleaned_html = "\n".join(lines)
    st.markdown(cleaned_html, unsafe_allow_html=True)


@st.cache_resource(show_spinner=False)
def cargar_recursos_modelo():
    """Carga el paquete del modelo y precalienta el explicador TreeExplainer una sola vez."""
    paquete = cargar_paquete_modelo()
    modelo = paquete["modelo"]
    if hasattr(modelo, "named_steps"):
        estimador = modelo.named_steps.get("randomforestclassifier", modelo)
    else:
        estimador = modelo
    explicador = shap.TreeExplainer(estimador)
    return paquete, explicador


@st.cache_data(show_spinner=False)
def cargar_ejemplos_prueba() -> pd.DataFrame | None:
    """Carga las muestras representativas preprocesadas para pruebas de 1 clic."""
    ruta = obtener_ruta_datos_procesados("ejemplos_prueba.csv")
    if ruta.exists():
        return pd.read_csv(ruta)
    return None


@st.cache_data(show_spinner=False)
def cargar_metricas_sistema() -> dict | None:
    """Carga el reporte de métricas y cumplimiento de metas SMART."""
    ruta = obtener_ruta_resultados("metrics") / "metricas.json"
    if ruta.exists():
        return cargar_json(ruta)
    return None


@st.cache_data(show_spinner=False)
def obtener_logo_base64() -> str:
    """Carga y cachea el logotipo oficial en base64 para renderizado universal."""
    ruta_logo = raiz / "src" / "images" / "electrovolt-logotipo.png"
    if ruta_logo.exists():
        return base64.b64encode(ruta_logo.read_bytes()).decode("utf-8")
    return ""


@st.cache_data(show_spinner=False)
def obtener_isotipo_base64() -> str:
    """Carga y cachea el isotipo oficial en base64 para favicon y metadatos."""
    ruta_iso = raiz / "src" / "images" / "electrovolt-isotipo.png"
    if ruta_iso.exists():
        return base64.b64encode(ruta_iso.read_bytes()).decode("utf-8")
    return ""

