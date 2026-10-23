"""Dashboard Web Industrial para Diagnóstico y Clasificación de Fallos Eléctricos.

ELECTRO-VOLT: Plataforma interactiva de soporte a la decisión operativa en subestaciones eléctricas.
Implementado con Streamlit, visualizaciones interactivas con Altair y explicabilidad local con SHAP.
Cumple estrictamente con la regla de rendimiento: carga única en memoria con @st.cache_resource.
"""

from __future__ import annotations

import base64
import io
import sys
import textwrap
import time
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import shap
import streamlit as st

# Configurar ruta raíz para importación modular de src
raiz = Path(__file__).resolve().parents[1]
if str(raiz) not in sys.path:
    sys.path.insert(0, str(raiz))

from src.evaluate import normalizar_shap
from src.model import cargar_paquete_modelo, mapear_shap_a_canales_fisicos, predecir_falla
from src.utils import (
    COLUMNAS,
    NOTA_CLASES,
    ORDEN_CLASES,
    RANGO_CORRIENTE,
    RANGO_VOLTAJE,
    UMBRAL_CONFIANZA_MINIMA,
    UMBRAL_RETORNO_TIERRA_A,
    cargar_json,
    determinar_estados_fases,
    obtener_ruta_datos_procesados,
    obtener_ruta_resultados,
    validar_rango_senales,
)

# ==============================================================================
# CONFIGURACIÓN DE PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="ElectroVOLT",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==============================================================================
# ESTILOS PERSONALIZADOS (OCULTAR BRANDING DE STREAMLIT Y COMMUNITY CLOUD)
# ==============================================================================
st.markdown(
    """
    <style>
    /* 1. Ocultar badges flotantes de Streamlit Community Cloud (overlay inferior derecho) */
    div[class*="viewerBadge"],
    div[class*="ProfileContainer"],
    div[class*="profileContainer"],
    div[class*="manageApp"],
    div[class*="ManageApp"],
    [data-testid="manage-app-button"],
    [data-testid="stStatusWidget"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* 2. Ocultar únicamente el pie de página predeterminado de Streamlit ("Made with Streamlit")
          SIN afectar el footer corporativo de ElectroVOLT */
    footer:not(.custom-footer-strip) {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
    }

    /* 3. Asegurar visibilidad total del footer corporativo de la aplicación */
    .custom-footer-strip {
        display: block !important;
        visibility: visible !important;
    }

    /* 4. Ocultar botón 'Deploy' de la barra superior */
    .stDeployButton,
    .stAppDeployButton {
        display: none !important;
        visibility: hidden !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# CARGA DE RECURSOS EN MEMORIA (REGLA DE ORO: CERO REENTRENAMIENTO)
# ==============================================================================
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


paquete, explicador = cargar_recursos_modelo()
df_ejemplos = cargar_ejemplos_prueba()
metricas_dict = cargar_metricas_sistema()
logo_base64 = obtener_logo_base64()


# ==============================================================================
# ESTILOS CSS FIDELIDAD EXACTA A IMAGE 3.MARKDOWN / MOCKUP
# ==============================================================================
def aplicar_estilos_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

        /* Base & Background */
        html, body, .stApp {
            font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
            background-color: #f8fafc !important;
            color: #334155 !important;
        }

        .font-mono-numbers {
            font-family: 'JetBrains Mono', monospace !important;
            font-feature-settings: 'tnum' on, 'zero' on;
        }

        /* Streamlit Default Headers / Chrome Reset & Margen Superior Cero */
        header[data-testid="stHeader"],
        [data-testid="stHeader"],
        .stDeployButton,
        [data-testid="stDeployButton"],
        #MainMenu,
        [data-testid="stMainMenu"],
        [data-testid="stToolbar"],
        div[data-testid="stDecoration"] {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            min-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        /* Colapsar el contenedor invisible del script de estilos */
        div[data-testid="stElementContainer"]:has(style) {
            display: none !important;
            height: 0 !important;
            min-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        /* Reset total del viewport para que el header toque el borde superior absoluto (0px) */
        html, body, .stApp,
        div[data-testid="stAppViewContainer"],
        section[data-testid="stMain"],
        div[data-testid="stMainBlockContainer"],
        div.block-container,
        .stMainBlockContainer {
            padding-top: 0 !important;
            margin-top: 0 !important;
            overflow-x: hidden !important;
        }

        div[data-testid="stMainBlockContainer"] > div[data-testid="stVerticalBlock"] {
            gap: 1.25rem !important;
        }

        /* Espaciado normal, equilibrado y profesional */
        h1, h2, h3, h4 {
            margin-top: 1.25rem !important;
            margin-bottom: 0.75rem !important;
            font-weight: 700 !important;
            color: #0f172a !important;
        }

        h5, [data-testid="stMarkdownContainer"] h5 {
            margin-top: 1.15rem !important;
            margin-bottom: 0.75rem !important;
            font-size: 0.95rem !important;
            font-weight: 700 !important;
            color: #0f172a !important;
            letter-spacing: -0.01em !important;
        }

        .step-heading-row {
            display: flex;
            align-items: center;
            gap: 0.65rem;
            margin-top: 0.5rem !important;
            margin-bottom: 0.45rem !important;
        }

        div[data-testid="stVegaLiteChart"] {
            margin-top: 0.25rem !important;
            margin-bottom: 0.4rem !important;
        }

        .factor-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1.15rem 1.35rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
            margin-top: 0 !important;
            margin-bottom: 1rem !important;
        }

        hr {
            margin: 1.75rem 0 1.25rem 0 !important;
            border: none !important;
            border-top: 1px solid #e2e8f0 !important;
        }

        /* Contenedor principal de Streamlit ocupa el 100% para que Header y Footer sean Full Width */
        .stMainBlockContainer, div.block-container {
            max-width: 100% !important;
            width: 100% !important;
            margin: 0 !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
            padding-top: 76px !important;
            padding-bottom: 0 !important;
            box-sizing: border-box !important;
        }

        /* Contenedores de ancho completo para Header y Footer */
        div[data-testid="stElementContainer"]:has(.top-navbar-strip),
        div[data-testid="stElementContainer"]:has(.custom-footer-strip) {
            max-width: 100% !important;
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        /* Contenido Operativo en 10 Columnas (~1240px en Desktop, centrado, adaptativo a móvil con padding) */
        div[data-testid="stMainBlockContainer"] > div[data-testid="stVerticalBlock"] > div:not(:has(.top-navbar-strip)):not(:has(.custom-footer-strip)) {
            max-width: 1240px !important;
            width: calc(100% - 2.5rem) !important;
            margin-left: auto !important;
            margin-right: auto !important;
            box-sizing: border-box !important;
        }

        /* Top Header Sticky Bar - 100% Full Width Pegado al Techo */
        .top-navbar-strip {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            width: 100% !important;
            height: 58px !important;
            padding: 0 2rem !important;
            box-sizing: border-box !important;
            background: #ffffff !important;
            border-bottom: 1px solid #e2e8f0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: space-between !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
            z-index: 99999 !important;
        }
        .header-brand-box {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        .header-avatar-circle {
            width: 34px;
            height: 34px;
            border-radius: 9999px;
            background: #f1f5f9;
            border: 1px solid #cbd5e1;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75rem;
            font-weight: 700;
            color: #334155;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        }

        /* Título de Sección de Módulos */
        .module-section-title {
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #64748b;
            margin-bottom: 0.65rem;
        }

        /* Grilla de 3 Módulos */
        .module-switcher-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
            margin-bottom: 1rem;
        }
        @media (max-width: 992px) {
            .module-switcher-grid {
                grid-template-columns: 1fr;
            }
        }
        .module-card-v3 {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1rem 1.15rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
            text-decoration: none !important;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-height: 128px;
            transition: all 0.2s ease;
        }
        .module-card-v3:hover {
            background: rgba(248, 250, 252, 0.85);
            border-color: #cbd5e1;
            transform: translateY(-1px);
        }
        .module-card-v3-active {
            border: 2px solid #002a69 !important;
            background: #ffffff !important;
            box-shadow: 0 4px 14px rgba(25, 51, 120, 0.16) !important;
        }
        .module-icon-v3 {
            padding: 0.35rem;
            border-radius: 6px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: #f1f5f9;
            color: #64748b;
            border: 1px solid #e2e8f0;
        }
        .module-icon-v3-active {
            background: #eef2fb !important;
            color: #002a69 !important;
            border: 1px solid #c5d2f3 !important;
        }
        .module-title-v3 {
            font-size: 0.88rem;
            font-weight: 600;
            color: #1e293b;
        }
        .module-title-v3-active {
            font-size: 0.88rem;
            font-weight: 700;
            color: #0f172a;
        }
        .module-desc-v3 {
            font-size: 0.76rem;
            color: #475569;
            line-height: 1.4;
            padding-left: 2rem;
            margin: 0.25rem 0 0 0;
        }
        .module-foot-v3 {
            margin-top: 0.75rem;
            padding-left: 2rem;
            display: flex;
            align-items: center;
            font-size: 0.72rem;
            font-weight: 600;
            color: #002a69;
            opacity: 0.85;
            transition: all 0.2s ease;
        }
        .module-foot-v3-active {
            margin-top: 0.75rem;
            padding-left: 2rem;
            display: flex;
            align-items: center;
            font-size: 0.72rem;
            font-weight: 700;
            color: #002a69;
        }

        /* Overlay interactivo 100% transparente sobre las tarjetas de módulo */
        div[data-testid="stColumn"]:has([class*="st-key-btn_card_nav_"]) {
            position: relative !important;
        }
        div[class*="st-key-btn_card_nav_"] {
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
            width: 100% !important;
            height: 100% !important;
            z-index: 25 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        div[class*="st-key-btn_card_nav_"] div[data-testid="stButton"],
        div[class*="st-key-btn_card_nav_"] button {
            width: 100% !important;
            height: 100% !important;
            min-height: 100% !important;
            opacity: 0 !important;
            cursor: pointer !important;
            border: none !important;
            background: transparent !important;
            padding: 0 !important;
            margin: 0 !important;
            box-shadow: none !important;
        }
        div[data-testid="stColumn"]:has(div[class*="st-key-btn_card_nav_"]:hover) .module-card-v3 {
            border-color: #2c4ea3 !important;
            box-shadow: 0 4px 12px rgba(25, 51, 120, 0.16) !important;
            transform: translateY(-2px) !important;
        }
        div[data-testid="stColumn"]:has(div[class*="st-key-btn_card_nav_"]:hover) .module-foot-v3 {
            color: #002a69 !important;
            opacity: 1 !important;
        }
        div[data-testid="stColumn"]:has(div[class*="st-key-btn_card_nav_"]:hover) .module-foot-v3 svg {
            transform: translateX(4px) !important;
        }

        /* Espaciado limpio y proporcionado de la fila de selección de módulos */
        div[data-testid="stHorizontalBlock"]:has([class*="st-key-btn_card_nav_"]) {
            margin-bottom: 0.75rem !important;
        }

        /* Ocultar elementos contenedores de anclas invisibles para que no generen cajas ni bordes */
        div[data-testid="stElementContainer"]:has(.telemetry-main-card),
        div[data-testid="stElementContainer"]:has(.xai-chart-card),
        div[data-testid="stElementContainer"]:has(.batch-upload-card) {
            display: none !important;
            height: 0 !important;
            min-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            border: none !important;
        }

        /* Fila de Contenedores de Gráficos XAI (Paso 4) más pegada al título */
        div[data-testid="stHorizontalBlock"]:has(.xai-chart-card) {
            margin-top: -0.5rem !important;
            margin-bottom: 0.65rem !important;
        }

        /* Tarjetas de Gráficos XAI (Paso 4): Fondo blanco, bordes redondeados y sombra suave */
        div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"] > div:has(.xai-chart-card) {
            background-color: #ffffff !important;
            background: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 14px !important;
            padding: 1.15rem 1.25rem 0.65rem 1.25rem !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03) !important;
        }
        .xai-chart-title {
            font-size: 0.95rem !important;
            font-weight: 700 !important;
            color: #0f172a !important;
            letter-spacing: -0.01em !important;
            margin: 0 0 0.45rem 0 !important;
            padding: 0 !important;
        }

        /* Contenedor Exterior Blanco de Telemetría (Sección 1) */
        div[data-testid="stMainBlockContainer"] > div[data-testid="stVerticalBlock"] > div:has(.telemetry-main-card) {
            background-color: #ffffff !important;
            background: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 16px !important;
            padding: 1.25rem 1.5rem !important;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04) !important;
            margin-top: 0 !important;
            margin-bottom: 0.5rem !important;
        }

        /* Contenedor Exterior Blanco de Carga de Lote (Página 2) */
        div[data-testid="stMainBlockContainer"] > div[data-testid="stVerticalBlock"] > div:has(.batch-upload-card) {
            background-color: #ffffff !important;
            background: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 14px !important;
            padding: 1.4rem 1.6rem 1.35rem 1.6rem !important;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04) !important;
            margin-top: 0 !important;
            margin-bottom: 0.75rem !important;
        }

        /* Estilización del File Uploader de Streamlit */
        div[data-testid="stFileUploader"] {
            margin-top: 0.25rem !important;
        }
        div[data-testid="stFileUploader"] label {
            font-size: 0.8rem !important;
            font-weight: 600 !important;
            color: #334155 !important;
            margin-bottom: 0.35rem !important;
        }
        section[data-testid="stFileUploaderDropzone"] {
            background-color: #f8fafc !important;
            border: 1.5px dashed #cbd5e1 !important;
            border-radius: 10px !important;
            padding: 1.15rem 1.5rem !important;
            transition: all 0.2s ease !important;
        }
        section[data-testid="stFileUploaderDropzone"]:hover {
            border-color: #002a69 !important;
            background-color: #f1f5f9 !important;
        }

        /* Tarjetas de Métricas KPI Industriales (Procesamiento por Lote) */
        .kpi-card-v2 {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1.15rem 1.25rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-height: 128px;
            box-sizing: border-box;
            transition: all 0.2s ease;
        }
        .kpi-card-v2:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.07);
            border-color: #cbd5e1;
        }
        .kpi-top-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 0.65rem;
        }
        .kpi-label {
            font-size: 0.72rem;
            font-weight: 700;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .kpi-icon-badge {
            width: 32px;
            height: 32px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }
        .kpi-value-row {
            display: flex;
            align-items: baseline;
            gap: 0.35rem;
            margin-bottom: 0.2rem;
        }
        .kpi-value {
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.55rem;
            font-weight: 800;
            color: #0f172a;
            line-height: 1.1;
            letter-spacing: -0.02em;
        }
        .kpi-unit {
            font-size: 0.78rem;
            font-weight: 600;
            color: #64748b;
        }
        .kpi-footer-text {
            font-size: 0.72rem;
            color: #94a3b8;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 0.3rem;
            margin-top: 0.15rem;
        }

        /* Encabezado del Paso 1: Título alineado con el número 1 y subtítulo sin mucho espaciado */
        .telemetry-header-block {
            display: flex;
            flex-direction: column;
            margin: 0 !important;
            padding: 0 !important;
        }
        .telemetry-title-row {
            display: flex;
            align-items: center;
            gap: 0.65rem;
            margin: 0 !important;
            padding: 0 !important;
        }
        .step-pill-badge {
            width: 24px;
            height: 24px;
            min-width: 24px;
            border-radius: 9999px;
            background: #e9eefb;
            color: #002a69;
            border: 1px solid #c5d2f3;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75rem;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
            line-height: 1;
            margin: 0 !important;
            flex-shrink: 0;
        }
        .telemetry-title-text {
            font-size: 1.05rem !important;
            font-weight: 700 !important;
            color: #0f172a !important;
            line-height: 1.25 !important;
            letter-spacing: -0.01em !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        .telemetry-subtitle-text {
            font-size: 0.76rem !important;
            color: #64748b !important;
            line-height: 1.35 !important;
            margin: 0.25rem 0 0 2.15rem !important;
            padding: 0 !important;
        }

        /* Tarjetas Individuales por Fase: Contenedor único, limpio y perfectamente proporcionado */
        div[data-testid="stColumn"] div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #ffffff !important;
            background: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 12px !important;
            padding: 1.15rem 1.15rem 1.25rem 1.15rem !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03) !important;
            margin: 0 !important;
        }

        .phase-header-flex {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid #e2e8f0;
            margin-bottom: 0.6rem;
        }
        .phase-dot-title {
            display: flex;
            align-items: center;
            gap: 0.45rem;
        }
        .phase-dot {
            width: 9px;
            height: 9px;
            border-radius: 9999px;
        }
        .phase-label-a {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            color: #b45309;
        }
        .phase-label-b {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            color: #002a69;
        }
        .phase-label-c {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            color: #558750;
        }
        .tp-tc-badge-a {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.68rem;
            color: #475569;
            background: rgba(254, 243, 199, 0.8);
            border: 1px solid rgba(253, 230, 138, 0.8);
            padding: 0.15rem 0.45rem;
            border-radius: 4px;
        }
        .tp-tc-badge-b {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.68rem;
            color: #002a69;
            background: rgba(25, 51, 120, 0.08);
            border: 1px solid rgba(25, 51, 120, 0.22);
            padding: 0.15rem 0.45rem;
            border-radius: 4px;
        }
        .tp-tc-badge-c {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.68rem;
            color: #558750;
            background: rgba(85, 135, 80, 0.1);
            border: 1px solid rgba(85, 135, 80, 0.28);
            padding: 0.15rem 0.45rem;
            border-radius: 4px;
        }

        /* Estilo y Contraste de Inputs Numéricos de Streamlit */
        div[data-testid="stNumberInput"] label {
            font-size: 0.76rem !important;
            font-weight: 500 !important;
            color: #334155 !important;
            margin-bottom: 0.2rem !important;
        }
        div[data-testid="stNumberInputContainer"],
        div[data-baseweb="base-input"],
        div[data-baseweb="input"] {
            background-color: #f1f5f9 !important;
            border: 1.5px solid #cbd5e1 !important;
            border-radius: 8px !important;
            box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.04) !important;
            transition: all 0.2s ease !important;
        }
        div[data-testid="stNumberInputContainer"]:focus-within,
        div[data-baseweb="input"]:focus-within {
            background-color: #ffffff !important;
            border-color: #002a69 !important;
            box-shadow: 0 0 0 2px rgba(25, 51, 120, 0.2) !important;
        }
        div[data-testid="stNumberInputContainer"] input,
        div[data-baseweb="input"] input {
            color: #0f172a !important;
            background-color: transparent !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 0.88rem !important;
            font-weight: 600 !important;
            padding: 0.45rem 0.75rem !important;
        }

        /* Focus por fase específico */
        div[data-testid="stColumn"]:nth-of-type(1) div[data-testid="stNumberInputContainer"]:focus-within,
        div[data-testid="stColumn"]:nth-of-type(1) div[data-baseweb="input"]:focus-within {
            border-color: #d97706 !important;
            box-shadow: 0 0 0 2px rgba(217, 119, 6, 0.2) !important;
        }
        div[data-testid="stColumn"]:nth-of-type(2) div[data-testid="stNumberInputContainer"]:focus-within,
        div[data-testid="stColumn"]:nth-of-type(2) div[data-baseweb="input"]:focus-within {
            border-color: #002a69 !important;
            box-shadow: 0 0 0 2px rgba(25, 51, 120, 0.2) !important;
        }
        div[data-testid="stColumn"]:nth-of-type(3) div[data-testid="stNumberInputContainer"]:focus-within,
        div[data-testid="stColumn"]:nth-of-type(3) div[data-baseweb="input"]:focus-within {
            border-color: #558750 !important;
            box-shadow: 0 0 0 2px rgba(85, 135, 80, 0.2) !important;
        }

        /* Micro-Steppers en Inputs (- y +) */
        div[data-testid="stNumberInputStepDown"],
        div[data-testid="stNumberInputStepUp"] {
            background-color: #e2e8f0 !important;
            color: #334155 !important;
            border: none !important;
            border-radius: 4px !important;
            margin: 2px !important;
            width: 22px !important;
            height: 22px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        div[data-testid="stNumberInputStepDown"]:hover,
        div[data-testid="stNumberInputStepUp"]:hover {
            background-color: #cbd5e1 !important;
            color: #0f172a !important;
        }

        /* Visualizador de Forma de Onda Mini */
        .waveform-preview-box {
            margin-top: 0.85rem !important;
            margin-bottom: 0.75rem !important;
            padding-top: 0.55rem !important;
            border-top: 1px solid #e2e8f0 !important;
        }
        .waveform-meta-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 0.68rem;
            color: #64748b;
            margin-bottom: 0.35rem;
        }
        .waveform-svg-box-a {
            height: 38px;
            width: 100%;
            background: rgba(254, 243, 199, 0.4);
            border-radius: 6px;
            border: 1px solid rgba(253, 230, 138, 0.7);
            display: flex;
            align-items: center;
            padding: 0 4px;
            margin-bottom: 0.25rem !important;
        }
        .waveform-svg-box-b {
            height: 38px;
            width: 100%;
            background: rgba(25, 51, 120, 0.06);
            border-radius: 6px;
            border: 1px solid rgba(25, 51, 120, 0.22);
            display: flex;
            align-items: center;
            padding: 0 4px;
            margin-bottom: 0.25rem !important;
        }
        .waveform-svg-box-c {
            height: 38px;
            width: 100%;
            background: rgba(85, 135, 80, 0.08);
            border-radius: 6px;
            border: 1px solid rgba(85, 135, 80, 0.25);
            display: flex;
            align-items: center;
            padding: 0 4px;
            margin-bottom: 0.25rem !important;
        }

        /* Botones de Streamlit */
        div[data-testid="stButton"] button {
            border-radius: 8px !important;
            font-family: 'Inter', system-ui, sans-serif !important;
            font-size: 0.85rem !important;
            font-weight: 600 !important;
            padding: 0.45rem 1.15rem !important;
            transition: all 0.2s ease !important;
            min-height: 38px !important;
        }
        button[data-testid="stBaseButton-secondary"] {
            background-color: #ffffff !important;
            border: 1px solid #cbd5e1 !important;
            color: #334155 !important;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04) !important;
        }
        button[data-testid="stBaseButton-secondary"]:hover {
            background-color: #f8fafc !important;
            border-color: #94a3b8 !important;
            color: #0f172a !important;
        }
        button[data-testid="stBaseButton-primary"] {
            background-color: #002a69 !important;
            border: 1px solid #002a69 !important;
            color: #ffffff !important;
            box-shadow: 0 2px 6px rgba(25, 51, 120, 0.3) !important;
        }
        button[data-testid="stBaseButton-primary"]:hover {
            background-color: #122456 !important;
            border-color: #122456 !important;
            box-shadow: 0 4px 12px rgba(25, 51, 120, 0.4) !important;
        }

        /* Footer */
        .footer-strip {
            border-top: 1px solid #e2e8f0;
            background: #ffffff;
            padding: 0.9rem 1.5rem;
            margin: 2.5rem -2rem -2rem -2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 0.72rem;
            color: #64748b;
        }

        /* Contenedor y columnas de Paso 3 para forzar altura idéntica */
        div[data-testid="stHorizontalBlock"]:has(.hud-card),
        div[data-testid="stHorizontalBlock"]:has(.dispatch-card) {
            align-items: stretch !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.hud-card) > div[data-testid="stColumn"],
        div[data-testid="stHorizontalBlock"]:has(.dispatch-card) > div[data-testid="stColumn"] {
            display: flex !important;
            flex-direction: column !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.hud-card) div[data-testid="stVerticalBlock"],
        div[data-testid="stHorizontalBlock"]:has(.dispatch-card) div[data-testid="stVerticalBlock"] {
            display: flex !important;
            flex-direction: column !important;
            flex: 1 1 100% !important;
            height: 100% !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.hud-card) div[data-testid="element-container"],
        div[data-testid="stHorizontalBlock"]:has(.dispatch-card) div[data-testid="element-container"] {
            display: flex !important;
            flex-direction: column !important;
            flex: 1 1 100% !important;
            height: 100% !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.hud-card) div.stMarkdown,
        div[data-testid="stHorizontalBlock"]:has(.dispatch-card) div.stMarkdown {
            display: flex !important;
            flex-direction: column !important;
            flex: 1 1 100% !important;
            height: 100% !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.hud-card) div[data-testid="stMarkdownContainer"],
        div[data-testid="stHorizontalBlock"]:has(.dispatch-card) div[data-testid="stMarkdownContainer"] {
            display: flex !important;
            flex-direction: column !important;
            flex: 1 1 100% !important;
            height: 100% !important;
        }

        /* Tarjetas de Resultados (Paso 3 y 4) */
        .hud-card {
            border-radius: 12px;
            padding: 1.4rem 1.6rem;
            height: 100% !important;
            min-height: 255px !important;
            box-sizing: border-box !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: space-between !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.06);
            flex: 1 1 100% !important;
        }
        .hud-card-normal {
            background: linear-gradient(135deg, #065f46 0%, #047857 100%);
            color: #ffffff !important;
            border: 1px solid #059669;
        }
        .hud-card-alert {
            background: linear-gradient(135deg, #92400e 0%, #b45309 100%);
            color: #ffffff !important;
            border: 1px solid #d97706;
        }
        .hud-card-danger {
            background: linear-gradient(135deg, #991b1b 0%, #dc2626 100%);
            color: #ffffff !important;
            border: 1px solid #b91c1c;
        }
        .hud-badge {
            display: inline-block;
            font-size: 0.72rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            background: rgba(255, 255, 255, 0.22) !important;
            border: 1px solid rgba(255, 255, 255, 0.45) !important;
            color: #ffffff !important;
            padding: 0.25rem 0.8rem;
            border-radius: 9999px !important;
            margin-bottom: 0.45rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
        }
        .hud-title {
            font-size: 1.75rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            margin: 0.2rem 0;
            color: #ffffff !important;
            line-height: 1.15;
        }
        .hud-desc {
            font-size: 0.88rem;
            opacity: 0.95;
            margin-bottom: 0.8rem;
            line-height: 1.35;
        }
        .hud-pills-row {
            display: flex;
            gap: 0.55rem;
            flex-wrap: wrap;
            align-items: center;
        }
        .hud-pill {
            background: #ffffff !important;
            color: #0f172a !important;
            border: 1px solid rgba(255, 255, 255, 0.9) !important;
            border-radius: 9999px !important;
            padding: 0.35rem 0.85rem !important;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.78rem !important;
            font-weight: 700 !important;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.16) !important;
            display: inline-flex !important;
            align-items: center !important;
            letter-spacing: -0.01em !important;
            transition: all 0.2s ease !important;
        }
        .hud-pill:hover {
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.22) !important;
            transform: translateY(-1px);
        }
        .hud-pill-tag {
            color: #475569 !important;
            font-weight: 600 !important;
            font-size: 0.72rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.02em !important;
            margin-right: 0.35rem !important;
        }
        .hud-pill-val {
            color: #0f172a !important;
            font-weight: 800 !important;
        }

        .dispatch-card {
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-left: 5px solid #002a69;
            border-radius: 12px;
            padding: 1.4rem 1.6rem;
            height: 100% !important;
            min-height: 255px !important;
            box-sizing: border-box !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: space-between !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
            flex: 1 1 100% !important;
        }
        .dispatch-header {
            font-size: 0.82rem;
            font-weight: 700;
            color: #002a69;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.6rem;
        }
        .dispatch-step {
            font-size: 0.88rem;
            color: #1e293b;
            margin-bottom: 0.45rem;
            line-height: 1.45;
        }

        /* Sinóptico */
        .synoptic-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 0.8rem;
            margin-bottom: 1.2rem;
        }
        .synoptic-cell {
            border-radius: 10px;
            padding: 0.8rem;
            text-align: center;
            border: 1px solid #cbd5e1;
            background: #ffffff;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
        }
        .synoptic-cell-fault {
            background: #fef2f2;
            border: 1px solid #ef4444;
            box-shadow: 0 0 10px rgba(239, 68, 68, 0.12);
        }
        .synoptic-cell-nominal {
            background: #f0fdf4;
            border: 1px solid #10b981;
        }
        .synoptic-title {
            font-size: 0.8rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        .synoptic-status {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            font-weight: 700;
            margin-top: 0.2rem;
        }

        /* Footer Corporativo Full Width - Ocupa el 100% real de la pantalla de extremo a extremo */
        .custom-footer-strip {
            width: 100% !important;
            box-sizing: border-box !important;
            background-color: #0E1233 !important;
            color: #e2e8f0 !important;
            padding: 3.5rem 2rem 1.75rem 2rem !important;
            border-top: 1px solid #13265c !important;
            margin-top: 3.5rem !important;
        }
        .footer-inner {
            max-width: 1240px !important;
            width: 100% !important;
            margin: 0 auto !important;
        }
        .footer-grid {
            display: grid !important;
            grid-template-columns: 1.2fr 1fr 1fr 1.3fr !important;
            gap: 2.5rem !important;
            margin-bottom: 2.5rem !important;
        }
        .footer-logo-card {
            background: #ffffff;
            padding: 6px 12px;
            border-radius: 8px;
            display: inline-flex;
            align-items: center;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
        }
        .footer-heading {
            font-size: 0.92rem !important;
            font-weight: 700 !important;
            color: #ffffff !important;
            letter-spacing: 0.08em !important;
            text-transform: uppercase !important;
            margin-bottom: 1.25rem !important;
        }
        .footer-text-item {
            color: #cbd5e1 !important;
            font-size: 0.88rem !important;
            font-weight: 400 !important;
            line-height: 2 !important;
            text-decoration: none !important;
            display: block !important;
            cursor: pointer !important;
            transition: color 0.15s ease !important;
        }
        .footer-text-item:hover {
            color: #ffffff !important;
            text-decoration: none !important;
        }
        .footer-contact-item {
            display: flex !important;
            align-items: center !important;
            gap: 0.85rem !important;
            margin-bottom: 0.85rem !important;
        }
        .footer-contact-icon {
            width: 34px !important;
            height: 34px !important;
            border-radius: 8px !important;
            background: rgba(255, 255, 255, 0.14) !important;
            border: 1px solid rgba(255, 255, 255, 0.28) !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            color: #ffffff !important;
            flex-shrink: 0 !important;
        }
        .footer-contact-text {
            color: #ffffff !important;
            font-size: 0.88rem !important;
            font-weight: 400 !important;
        }
        .footer-copyright {
            border-top: 1px solid rgba(255, 255, 255, 0.15) !important;
            padding-top: 1.5rem !important;
            text-align: center !important;
            font-size: 0.82rem !important;
            color: #cbd5e1 !important;
        }

        /* Adaptabilidad Móvil */
        @media (max-width: 992px) {
            .synoptic-grid {
                grid-template-columns: repeat(2, 1fr) !important;
            }
            .footer-grid {
                grid-template-columns: repeat(2, 1fr) !important;
                gap: 2rem !important;
            }
        }
        @media (max-width: 768px) {
            .synoptic-grid {
                grid-template-columns: 1fr !important;
            }
            .top-navbar-strip {
                padding: 0.6rem 1rem !important;
            }
            div[data-testid="stMainBlockContainer"] > div[data-testid="stVerticalBlock"] > div:not(:has(.top-navbar-strip)):not(:has(.custom-footer-strip)) {
                width: calc(100% - 1.5rem) !important;
                margin-left: auto !important;
                margin-right: auto !important;
            }
        }
        @media (max-width: 550px) {
            .footer-grid {
                grid-template-columns: 1fr !important;
                gap: 1.75rem !important;
            }
            .custom-footer-strip {
                padding: 2.5rem 1rem 1.5rem 1rem !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_html(html_str: str) -> None:
    """Renderiza contenido HTML garantizando cero indentación en cada línea para evitar code blocks en Markdown."""
    lines = [line.strip() for line in html_str.strip().splitlines() if line.strip()]
    cleaned_html = "\n".join(lines)
    st.markdown(cleaned_html, unsafe_allow_html=True)


def render_header():
    """Renderiza el TopHeader sticky blanco que ocupa el 100% del ancho con el logotipo oficial."""
    logo_b64 = obtener_logo_base64()
    if logo_b64:
        logo_html = f'<img src="data:image/png;base64,{logo_b64}" alt="ElectroVOLT" style="height: 38px; width: auto; object-fit: contain; display: block;" />'
    else:
        logo_html = '<span style="font-weight: 800; font-size: 1.2rem; color: #002a69;">Electro<span style="color: #f59e0b;">VOLT</span></span>'

    render_html(
        f"""
        <div class="top-navbar-strip">
            <div style="display: flex; align-items: center;">
                {logo_html}
            </div>
            <div class="header-avatar-circle">
                OP
            </div>
        </div>
        """
    )


def cb_cambiar_modulo(m: str):
    """Callback global para cambio instantáneo de módulo en session_state y URL."""
    st.session_state.modulo_activo = m
    st.session_state._url_modulo_guardada = m
    st.query_params["modulo"] = m


def render_navbar(modulo_activo: str):
    """Renderiza las 3 tarjetas de selección de módulo como componentes SPA interactivos con cambio instantáneo."""
    render_html('<div class="module-section-title">SELECCIÓN DE MÓDULO OPERATIVO</div>')

    col1, col2, col3 = st.columns(3, gap="medium")

    es_activa_1 = modulo_activo == "diagnostic-real-time"
    es_activa_2 = modulo_activo == "diagnostic-from-file"
    es_activa_3 = modulo_activo == "info-audit-model"

    with col1:
        card1_class = "module-card-v3 module-card-v3-active" if es_activa_1 else "module-card-v3"
        icon1_class = "module-icon-v3 module-icon-v3-active" if es_activa_1 else "module-icon-v3"
        title1_class = "module-title-v3-active" if es_activa_1 else "module-title-v3"
        foot1_class = "module-foot-v3-active" if es_activa_1 else "module-foot-v3"
        foot1_text = "En ejecución continua" if es_activa_1 else "Abrir módulo en tiempo real"

        render_html(
            f"""
            <div class="{card1_class}" style="cursor: pointer;">
                <div>
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.35rem;">
                        <span class="{icon1_class}">
                            <svg style="width: 16px; height: 16px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                            </svg>
                        </span>
                        <span class="{title1_class}">1. Diagnóstico en Tiempo Real</span>
                    </div>
                    <p class="module-desc-v3">
                        Inyección de señales trifásicas, oscilograma a 60 Hz, clasificación y explicabilidad SHAP.
                    </p>
                </div>
                <div class="{foot1_class}">
                    <span>{foot1_text}</span>
                    <svg style="width: 14px; height: 14px; margin-left: 4px;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                </div>
            </div>
            """
        )
        st.button(
            " ",
            key="btn_card_nav_1",
            on_click=cb_cambiar_modulo,
            args=("diagnostic-real-time",),
        )

    with col2:
        card2_class = "module-card-v3 module-card-v3-active" if es_activa_2 else "module-card-v3"
        icon2_class = "module-icon-v3 module-icon-v3-active" if es_activa_2 else "module-icon-v3"
        title2_class = "module-title-v3-active" if es_activa_2 else "module-title-v3"
        foot2_class = "module-foot-v3-active" if es_activa_2 else "module-foot-v3"
        foot2_text = "En ejecución continua" if es_activa_2 else "Abrir procesador batch"

        render_html(
            f"""
            <div class="{card2_class}" style="cursor: pointer;">
                <div>
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.35rem;">
                        <span class="{icon2_class}">
                            <svg style="width: 16px; height: 16px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2 1 3 3 3h10c2 0 3-1 3-3V7c0-2-1-3-3-3H7C5 4 4 5 4 7zm0 5h16M9 4v16"></path>
                            </svg>
                        </span>
                        <span class="{title2_class}">2. Procesamiento Masivo por Lote</span>
                    </div>
                    <p class="module-desc-v3">
                        Carga tu archivo CSV y obtén resultados instantáneos.
                    </p>
                </div>
                <div class="{foot2_class}">
                    <span>{foot2_text}</span>
                    <svg style="width: 14px; height: 14px; margin-left: 4px;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                </div>
            </div>
            """
        )
        st.button(
            " ",
            key="btn_card_nav_2",
            on_click=cb_cambiar_modulo,
            args=("diagnostic-from-file",),
        )

    with col3:
        card3_class = "module-card-v3 module-card-v3-active" if es_activa_3 else "module-card-v3"
        icon3_class = "module-icon-v3 module-icon-v3-active" if es_activa_3 else "module-icon-v3"
        title3_class = "module-title-v3-active" if es_activa_3 else "module-title-v3"
        foot3_class = "module-foot-v3-active" if es_activa_3 else "module-foot-v3"
        foot3_text = "En ejecución continua" if es_activa_3 else "Ver reporte de auditoría"

        render_html(
            f"""
            <div class="{card3_class}" style="cursor: pointer;">
                <div>
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.35rem;">
                        <span class="{icon3_class}">
                            <svg style="width: 16px; height: 16px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                            </svg>
                        </span>
                        <span class="{title3_class}">3. Auditoría y Metas SMART</span>
                    </div>
                    <p class="module-desc-v3">
                        Cumplimiento de KPIs, estadísticas y gráficos de validación.
                    </p>
                </div>
                <div class="{foot3_class}">
                    <span>{foot3_text}</span>
                    <svg style="width: 14px; height: 14px; margin-left: 4px;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                </div>
            </div>
            """
        )
        st.button(
            " ",
            key="btn_card_nav_3",
            on_click=cb_cambiar_modulo,
            args=("info-audit-model",),
        )


def render_footer():
    """Renderiza el footer corporativo de ancho completo adaptado a móvil y con diseño idéntico a referencia."""
    logo_b64 = obtener_logo_base64()
    if logo_b64:
        logo_html = f'<img src="data:image/png;base64,{logo_b64}" alt="ElectroVOLT" style="height: 32px; width: auto; object-fit: contain; display: block;" />'
    else:
        logo_html = '<span style="font-weight: 800; font-size: 1.1rem; color: #002a69;">Electro<span style="color: #f59e0b;">VOLT</span></span>'

    render_html(
        f"""
        <footer class="custom-footer-strip">
            <div class="footer-inner">
                <div class="footer-grid">
                    <!-- COLUMNA 1: LOGOTIPO -->
                    <div style="display: flex; flex-direction: column; align-items: flex-start;">
                        <div class="footer-logo-card">
                            {logo_html}
                        </div>
                    </div>

                    <!-- COLUMNA 2: NAVEGACIÓN -->
                    <div>
                        <div class="footer-heading">NAVEGACIÓN</div>
                        <div style="display: flex; flex-direction: column; gap: 0.35rem;">
                            <a href="?modulo=diagnostic-real-time" target="_self" class="footer-text-item">Tiempo real</a>
                            <a href="?modulo=diagnostic-from-file" target="_self" class="footer-text-item">Desde archivo</a>
                            <a href="?modulo=info-audit-model" target="_self" class="footer-text-item">Metas SMART</a>
                        </div>
                    </div>

                    <!-- COLUMNA 3: INFORMACIÓN -->
                    <div>
                        <div class="footer-heading">INFORMACIÓN</div>
                        <div style="display: flex; flex-direction: column; gap: 0.35rem;">
                            <span class="footer-text-item" style="cursor: default;">¿Qué es ElectroVOLT?</span>
                            <span class="footer-text-item" style="cursor: default;">Política de Privacidad</span>
                            <span class="footer-text-item" style="cursor: default;">Términos y Condiciones</span>
                        </div>
                    </div>

                    <!-- COLUMNA 4: CONTACTO -->
                    <div>
                        <div class="footer-heading">CONTACTO</div>
                        <div style="display: flex; flex-direction: column; gap: 0.85rem;">
                            <div class="footer-contact-item">
                                <div class="footer-contact-icon">
                                    <svg style="width: 15px; height: 15px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                                    </svg>
                                </div>
                                <span class="footer-contact-text">jordan.verac@uees.edu.ec</span>
                            </div>
                            <div class="footer-contact-item">
                                <div class="footer-contact-icon">
                                    <svg style="width: 15px; height: 15px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                                    </svg>
                                </div>
                                <span class="footer-contact-text">jorge.estrella@uees.edu.ec</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="footer-copyright">
                    © 2026 EelectroVOLT. Todos los derechos reservados
                </div>
            </div>
        </footer>
        """
    )


# ==============================================================================
# PÁGINA 1: DIAGNÓSTICO EN TIEMPO REAL (/diagnostic-real-time)
# ==============================================================================
def pagina_diagnostico_tiempo_real():
    # Inicialización de estado de sesión para widgets con valores por defecto del mockup
    if "widget_va" not in st.session_state:
        st.session_state.widget_va = -0.3741
        st.session_state.widget_vb = 0.4550
        st.session_state.widget_vc = -0.0810
        st.session_state.widget_ia = 315.85
        st.session_state.widget_ib = 63.27
        st.session_state.widget_ic = -45.92
    if "verificado" not in st.session_state:
        st.session_state.verificado = False
    if "mostrar_aviso_incompletos" not in st.session_state:
        st.session_state.mostrar_aviso_incompletos = False

    # Callbacks de botones para evitar StreamlitWidgetAlreadyInstantiatedError
    def cb_valores_prueba():
        if df_ejemplos is not None and len(df_ejemplos) > 0:
            muestra = df_ejemplos.sample(n=1).iloc[0]
            st.session_state.widget_va = float(muestra["Va"])
            st.session_state.widget_vb = float(muestra["Vb"])
            st.session_state.widget_vc = float(muestra["Vc"])
            st.session_state.widget_ia = float(muestra["Ia"])
            st.session_state.widget_ib = float(muestra["Ib"])
            st.session_state.widget_ic = float(muestra["Ic"])
        else:
            st.session_state.widget_va = -0.3741
            st.session_state.widget_vb = 0.4550
            st.session_state.widget_vc = -0.0810
            st.session_state.widget_ia = 315.85
            st.session_state.widget_ib = 63.27
            st.session_state.widget_ic = -45.92
        st.session_state.mostrar_aviso_incompletos = False
        st.session_state.mostrar_aviso_fuera_rango = False
        st.session_state.detalles_fuera_rango = []
        st.session_state.verificado = False

    def cb_limpiar_campos():
        st.session_state.widget_va = None
        st.session_state.widget_vb = None
        st.session_state.widget_vc = None
        st.session_state.widget_ia = None
        st.session_state.widget_ib = None
        st.session_state.widget_ic = None
        st.session_state.mostrar_aviso_incompletos = False
        st.session_state.mostrar_aviso_fuera_rango = False
        st.session_state.detalles_fuera_rango = []
        st.session_state.verificado = False

    def cb_verificar_diagnostico():
        valores = [
            st.session_state.get("widget_va"),
            st.session_state.get("widget_vb"),
            st.session_state.get("widget_vc"),
            st.session_state.get("widget_ia"),
            st.session_state.get("widget_ib"),
            st.session_state.get("widget_ic"),
        ]
        if any(v is None for v in valores):
            st.session_state.mostrar_aviso_incompletos = True
            st.session_state.mostrar_aviso_fuera_rango = False
            st.session_state.detalles_fuera_rango = []
            st.session_state.verificado = False
            return

        st.session_state.mostrar_aviso_incompletos = False

        # Validación física del rango de entrenamiento (Observación 1 de Jorge)
        es_valido, anomalias = validar_rango_senales(
            Va=float(valores[0]),
            Vb=float(valores[1]),
            Vc=float(valores[2]),
            Ia=float(valores[3]),
            Ib=float(valores[4]),
            Ic=float(valores[5]),
        )
        if not es_valido:
            st.session_state.mostrar_aviso_fuera_rango = True
            st.session_state.detalles_fuera_rango = anomalias
            st.session_state.verificado = False
        else:
            st.session_state.mostrar_aviso_fuera_rango = False
            st.session_state.detalles_fuera_rango = []
            st.session_state.verificado = True

    # --------------------------------------------------------------------------
    # CONTENEDOR BLANCO DE TELEMETRÍA (SECCIÓN 1)
    # --------------------------------------------------------------------------
    with st.container():
        render_html('<div class="telemetry-main-card"></div>')
        col_t_title, col_t_btn = st.columns([3.8, 1.2], vertical_alignment="center")

        with col_t_title:
            render_html(
                """
                <div class="telemetry-header-block">
                    <div class="telemetry-title-row">
                        <span class="step-pill-badge">1</span>
                        <span class="telemetry-title-text">Ingrese sus valores de Telemetría</span>
                    </div>
                    <div class="telemetry-subtitle-text">
                        Ajuste las lecturas de los transformadores de medida (<strong style="color: #334155; font-weight: 500;">TP: Tensión en p.u.</strong>, <strong style="color: #334155; font-weight: 500;">TC: Corriente en Amperios</strong>).
                    </div>
                </div>
                """
            )

        with col_t_btn:
            st.button("Valores de prueba", key="btn_valores_prueba", on_click=cb_valores_prueba, use_container_width=True)

        render_html("<div style='border-bottom: 1px solid #e2e8f0; margin: 0.8rem 0 1rem 0;'></div>")

        # ----------------------------------------------------------------------
        # GRILLA TÉCNICA DE 3 COLUMNAS DE FASE (A, B, C)
        # ----------------------------------------------------------------------
        col_a, col_b, col_c = st.columns(3, gap="medium")

        # ==================== FASE A (WARM AMBER) ====================
        with col_a:
            with st.container(border=True):
                render_html(
                    """
                    <div class="phase-header-flex">
                        <div class="phase-dot-title">
                            <span class="phase-dot" style="background: #d97706;"></span>
                            <span class="phase-label-a">CANAL FASE - A</span>
                        </div>
                        <span class="tp-tc-badge-a">TP-A / TC-A</span>
                    </div>
                    """
                )

                st.number_input(
                    "Tensión Va",
                    step=0.0001,
                    format="%.4f" if st.session_state.widget_va is not None else None,
                    key="widget_va",
                    help="Tensión fase-neutro normalizada en base nominal 230/√3 kV.",
                )

                st.number_input(
                    "Corriente Ia",
                    step=0.01,
                    format="%.2f" if st.session_state.widget_ia is not None else None,
                    key="widget_ia",
                    help="Corriente instantánea RMS Dinámico registrada por el TC.",
                )

                render_html(
                    """
                    <div class="waveform-preview-box">
                        <div class="waveform-meta-row">
                            <span>Forma de Onda Instantánea A</span>
                            <span style="font-family: 'JetBrains Mono', monospace; color: #b45309; font-weight: 600;">φ = 0°</span>
                        </div>
                        <div class="waveform-svg-box-a">
                            <svg style="width: 100%; height: 28px;" preserveAspectRatio="none" viewBox="0 0 200 40">
                                <path d="M 0 20 Q 25 2, 50 20 T 100 20 T 150 20 T 200 20" fill="none" stroke="#d97706" stroke-width="1.8" stroke-linecap="round"/>
                            </svg>
                        </div>
                    </div>
                    """
                )

        # ==================== FASE B (CERULEAN / STEEL BLUE) ====================
        with col_b:
            with st.container(border=True):
                render_html(
                    """
                    <div class="phase-header-flex">
                        <div class="phase-dot-title">
                            <span class="phase-dot" style="background: #002a69;"></span>
                            <span class="phase-label-b">CANAL FASE B</span>
                        </div>
                        <span class="tp-tc-badge-b">TP-B / TC-B</span>
                    </div>
                    """
                )

                st.number_input(
                    "Tensión Vb",
                    step=0.0001,
                    format="%.4f" if st.session_state.widget_vb is not None else None,
                    key="widget_vb",
                    help="Tensión nominal desfasada -120° estándar IEEE.",
                )

                st.number_input(
                    "Corriente Ib",
                    step=0.01,
                    format="%.2f" if st.session_state.widget_ib is not None else None,
                    key="widget_ib",
                    help="Corriente instantánea RMS Dinámico registrada por el TC.",
                )

                render_html(
                    """
                    <div class="waveform-preview-box">
                        <div class="waveform-meta-row">
                            <span>Forma de Onda Instantánea B</span>
                            <span style="font-family: 'JetBrains Mono', monospace; color: #002a69; font-weight: 600;">φ = -120°</span>
                        </div>
                        <div class="waveform-svg-box-b">
                            <svg style="width: 100%; height: 28px;" preserveAspectRatio="none" viewBox="0 0 200 40">
                                <path d="M 0 32 Q 25 20, 50 4 T 100 20 T 150 36 T 200 20" fill="none" stroke="#002a69" stroke-width="1.8" stroke-linecap="round"/>
                            </svg>
                        </div>
                    </div>
                    """
                )

        # ==================== FASE C (FOREST SAGE GREEN / #558750) ====================
        with col_c:
            with st.container(border=True):
                render_html(
                    """
                    <div class="phase-header-flex">
                        <div class="phase-dot-title">
                            <span class="phase-dot" style="background: #558750;"></span>
                            <span class="phase-label-c">CANAL FASE C</span>
                        </div>
                        <span class="tp-tc-badge-c">TP-C / TC-C</span>
                    </div>
                    """
                )

                st.number_input(
                    "Tensión Vc",
                    step=0.0001,
                    format="%.4f" if st.session_state.widget_vc is not None else None,
                    key="widget_vc",
                    help="Tensión nominal desfasada +120° estándar IEEE.",
                )

                st.number_input(
                    "Corriente Ic",
                    step=0.01,
                    format="%.2f" if st.session_state.widget_ic is not None else None,
                    key="widget_ic",
                    help="Corriente instantánea RMS Dinámico registrada por el TC.",
                )

                render_html(
                    """
                    <div class="waveform-preview-box">
                        <div class="waveform-meta-row">
                            <span>Forma de Onda Instantánea C</span>
                            <span style="font-family: 'JetBrains Mono', monospace; color: #558750; font-weight: 600;">φ = +120°</span>
                        </div>
                        <div class="waveform-svg-box-c">
                            <svg style="width: 100%; height: 28px;" preserveAspectRatio="none" viewBox="0 0 200 40">
                                <path d="M 0 10 Q 25 36, 50 20 T 100 4 T 150 20 T 200 10" fill="none" stroke="#558750" stroke-width="1.8" stroke-linecap="round"/>
                            </svg>
                        </div>
                    </div>
                    """
                )

    # --------------------------------------------------------------------------
    # ALERTA DE CAMPOS INCOMPLETOS O FUERA DE RANGO DE ENTRENAMIENTO
    # --------------------------------------------------------------------------
    if st.session_state.get("mostrar_aviso_incompletos", False):
        st.warning("⚠️ Por favor ingrese valores numéricos en todas las fases antes de verificar el diagnóstico.")

    if st.session_state.get("mostrar_aviso_fuera_rango", False):
        anomalias = st.session_state.get("detalles_fuera_rango", [])
        anomalias_texto = ", ".join(anomalias)
        st.warning(
            f"⚠️ **Valor fuera del rango de entrenamiento:** {anomalias_texto}.\n\n"
            f"Este modelo solo aprendió con voltajes entre {RANGO_VOLTAJE[0]} y {RANGO_VOLTAJE[1]} p.u. "
            f"y corrientes entre {RANGO_CORRIENTE[0]:.0f} y {RANGO_CORRIENTE[1]:.0f} A. "
            "Por seguridad operativa, y evitar falsos resultados, **no se emite diagnóstico** ante valores fuera del dominio de entrenamiento."
        )

    # --------------------------------------------------------------------------
    # FILA DE ACCIONES (BOTONES LIMPIAR Y VERIFICAR CON ESPACIADO ENTRE ELLOS)
    # --------------------------------------------------------------------------
    col_spacer, col_btn_limpiar, col_btn_verificar = st.columns([6.6, 1.6, 1.8], gap="medium")

    with col_btn_limpiar:
        st.button("Limpiar", key="btn_limpiar_campos", on_click=cb_limpiar_campos, use_container_width=True)

    with col_btn_verificar:
        st.button("Verificar", key="btn_ejecutar_verificar", type="primary", on_click=cb_verificar_diagnostico, use_container_width=True)

    # --------------------------------------------------------------------------
    # RESULTADOS CONDICIONALES (SOLO TRAS HACER CLIC EN VERIFICAR)
    # --------------------------------------------------------------------------
    if not st.session_state.get("verificado", False):
        return

    # Inferencia con valores numéricos validados
    val_va = float(st.session_state.get("widget_va") or 0.0)
    val_vb = float(st.session_state.get("widget_vb") or 0.0)
    val_vc = float(st.session_state.get("widget_vc") or 0.0)
    val_ia = float(st.session_state.get("widget_ia") or 0.0)
    val_ib = float(st.session_state.get("widget_ib") or 0.0)
    val_ic = float(st.session_state.get("widget_ic") or 0.0)

    t_inicio = time.perf_counter()
    resultado = predecir_falla(
        Va=val_va, Vb=val_vb, Vc=val_vc, Ia=val_ia, Ib=val_ib, Ic=val_ic, paquete=paquete
    )
    latencia_ms = (time.perf_counter() - t_inicio) * 1000.0

    diag_clase = resultado["diagnostico"]
    confianza_pct = resultado["confianza"] * 100.0
    mensaje_operador = resultado["mensaje_operador"]
    probabilidades = resultado["probabilidades"]
    fases_afectadas = resultado.get("fases_afectadas", [])
    desc_fases = resultado.get("descripcion_fases", "")
    rotacion_ganadora = resultado.get("rotacion_utilizada", "ABC")

    # --------------------------------------------------------------------------
    # PASO 2: MONITOREO VISUAL (SINÓPTICO Y OSCILOGRAMA)
    # --------------------------------------------------------------------------
    st.markdown("<hr style='border: none; border-top: 1px solid #e2e8f0; margin: 1.25rem 0 0.75rem 0;'>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="step-heading-row">
            <span class="step-pill-badge">2</span>
            <span style="font-size: 1.05rem; font-weight: 700; color: #0f172a;">
                Monitoreo Visual de Señales: Sinóptico y Oscilograma a 60 Hz
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    corriente_n = val_ia + val_ib + val_ic
    # Sincronización estricta: Normal sale 100% en verde, y cada falla activa exactamente sus fases
    falla_a, falla_b, falla_c, falla_g = determinar_estados_fases(
        diag_clase=diag_clase,
        corriente_n=corriente_n,
        fases_afectadas=fases_afectadas,
    )

    render_html(
        f"""
        <div class="synoptic-grid">
            <div class="synoptic-cell {'synoptic-cell-fault' if falla_a else 'synoptic-cell-nominal'}">
                <div class="synoptic-title" style="color: #292929;">CONDUCTOR FASE A</div>
                <div class="synoptic-status" style="color: {'#dc2626' if falla_a else '#059669'};">
                    {'PERTURBACIÓN DETECTADA' if falla_a else 'ESTADO NOMINAL'}
                </div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #475569; margin-top: 0.2rem;">
                    Va = {val_va:.3f} p.u.
                </div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #475569; margin-top: 0.2rem;">
                    Ia = {val_ia:.1f} A
                </div>
            </div>
            <div class="synoptic-cell {'synoptic-cell-fault' if falla_b else 'synoptic-cell-nominal'}">
                <div class="synoptic-title" style="color: #292929;">CONDUCTOR FASE B</div>
                <div class="synoptic-status" style="color: {'#dc2626' if falla_b else '#059669'};">
                    {'PERTURBACIÓN DETECTADA' if falla_b else 'ESTADO NOMINAL'}
                </div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #475569; margin-top: 0.2rem;">
                    Vb = {val_vb:.3f} p.u.
                </div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #475569; margin-top: 0.2rem;">
                    Ib = {val_ib:.1f} A
                </div>
            </div>
            <div class="synoptic-cell {'synoptic-cell-fault' if falla_c else 'synoptic-cell-nominal'}">
                <div class="synoptic-title" style="color: #292929;">CONDUCTOR FASE C</div>
                <div class="synoptic-status" style="color: {'#dc2626' if falla_c else '#059669'};">
                    {'PERTURBACIÓN DETECTADA' if falla_c else 'ESTADO NOMINAL'}
                </div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #475569; margin-top: 0.2rem;">
                    Vc = {val_vc:.3f} p.u.
                </div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #475569; margin-top: 0.2rem;">
                    Ic = {val_ic:.1f} A
                </div>
            </div>
            <div class="synoptic-cell {'synoptic-cell-fault' if falla_g else 'synoptic-cell-nominal'}">
                <div class="synoptic-title" style="color: #292929;">NEUTRO / TIERRA (G)</div>
                <div class="synoptic-status" style="color: {'#dc2626' if falla_g else '#059669'};">
                    {'RETORNO POR TIERRA' if falla_g else 'AISLADO (SIN RETORNO)'}
                </div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #475569; margin-top: 0.2rem;">
                    In = {corriente_n:.1f} A
                </div>
            </div>
        </div>
        """
    )

    # Oscilograma
    t_ciclo = np.linspace(0, 0.0167, 120)
    w_rad = 2.0 * np.pi * 60.0
    df_ondas_i = pd.concat([
        pd.DataFrame({"Tiempo_ms": t_ciclo * 1000, "Canal": "Fase A (Ia)", "Corriente": val_ia * np.sin(w_rad * t_ciclo)}),
        pd.DataFrame({"Tiempo_ms": t_ciclo * 1000, "Canal": "Fase B (Ib)", "Corriente": val_ib * np.sin(w_rad * t_ciclo - 2 * np.pi / 3)}),
        pd.DataFrame({"Tiempo_ms": t_ciclo * 1000, "Canal": "Fase C (Ic)", "Corriente": val_ic * np.sin(w_rad * t_ciclo + 2 * np.pi / 3)}),
    ])

    cero_df = pd.DataFrame({"y": [0]})
    linea_cero = (
        alt.Chart(cero_df)
        .mark_rule(color="#cbd5e1", strokeDash=[4, 4], strokeWidth=1.2)
        .encode(y="y:Q")
    )

    chart_osc = (
        alt.Chart(df_ondas_i)
        .mark_line(strokeWidth=2.6)
        .encode(
            x=alt.X(
                "Tiempo_ms:Q",
                title="Tiempo en Milisegundos (1 Ciclo a 60 Hz = 16.67 ms)",
                axis=alt.Axis(grid=True, gridColor="#f1f5f9", labelFont="JetBrains Mono"),
            ),
            y=alt.Y(
                "Corriente:Q",
                title="Corriente Instantánea (Amperios, A)",
                axis=alt.Axis(grid=True, gridColor="#f1f5f9", labelFont="JetBrains Mono"),
            ),
            color=alt.Color(
                "Canal:N",
                scale=alt.Scale(
                    domain=["Fase A (Ia)", "Fase B (Ib)", "Fase C (Ic)"],
                    range=["#d97706", "#002a69", "#558750"],
                ),
                legend=alt.Legend(title="Señales Registradas (TC)", orient="top"),
            ),
            tooltip=[
                alt.Tooltip("Canal:N", title="Fase"),
                alt.Tooltip("Tiempo_ms:Q", format=".2f", title="Tiempo (ms)"),
                alt.Tooltip("Corriente:Q", format=".1f", title="Amperios (A)"),
            ],
        )
    )
    chart_final = (linea_cero + chart_osc).properties(height=360).interactive()
    st.altair_chart(chart_final, use_container_width=True)

    # --------------------------------------------------------------------------
    # PASO 3: HUD Y PROTOCOLO LADO A LADO EN 2 COLUMNAS DE 6
    # --------------------------------------------------------------------------
    st.markdown("<hr style='border: none; border-top: 1px solid #e2e8f0; margin: 1.5rem 0 1rem 0;'>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="step-heading-row">
            <span class="step-pill-badge">3</span>
            <span style="font-size: 1.05rem; font-weight: 700; color: #0f172a;">
                Diagnóstico del Sistema y Protocolo Operativo
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if diag_clase == "Normal":
        hud_css = "hud-card-normal"
        estado_badge = "ESTADO NOMINAL - RED DESPEJADA"
        titulo_diag = "Operación Normal (Sin Falla)"
        subtitulo_diag = "No se detectan cortocircuitos ni fugas a tierra. Parámetros dentro de tolerancia nominal."
        orden_rele = "MONITORIZACIÓN ACTIVA"
        paso_1 = "Continuar registro telemétrico continuo de canales trifásicos en tiempo real."
        paso_2 = "Verificar que el desbalance de tensión entre fases se mantenga bajo el 2%."
        paso_3 = "Ninguna orden de disparo requerida; interruptores 52-1 y 52-2 en posición CERRADO."
    elif diag_clase == "Trifásica":
        hud_css = "hud-card-danger"
        estado_badge = "FALLA SEVERA CRÍTICA - MÁXIMO RIESGO"
        titulo_diag = "Falla Trifásica Simétrica (A-B-C)"
        subtitulo_diag = "Cortocircuito simultáneo en las tres fases. Elevado estrés electrodinámico y térmico."
        orden_rele = "DISPARO TRIPOLAR INMEDIATO (52-1, 52-2)"
        paso_1 = "Apertura tripolar simultánea y definitiva del interruptor de cabecera de subestación."
        paso_2 = "Bloquear reenganche automático para evitar reignición violenta sobre el cortocircuito."
        paso_3 = "Despachar cuadrilla técnica con medidor de impedancia para inspección física de conductores."
    elif diag_clase == "LG":
        hud_css = "hud-card-alert"
        estado_badge = "FALLA MONOFÁSICA A TIERRA"
        titulo_diag = f"Falla Línea a Tierra (LG - {desc_fases})"
        subtitulo_diag = f"Pérdida de aislamiento entre {desc_fases.lower()} y tierra. Fuerte circulación de corriente homopolar."
        orden_rele = "DISPARO SELECTIVO DE FASE"
        paso_1 = f"Verificar disparo monopolar del relé 50/51N sobre el polo de {desc_fases}."
        paso_2 = "Monitorear elevación de tensión en fases sanas por desplazamiento del neutro."
        paso_3 = "Inspeccionar aisladores de soporte y descargadores de sobretensión en la bahía afectada."
    elif diag_clase == "LL":
        hud_css = "hud-card-alert"
        estado_badge = "FALLA BIFÁSICA ENTRE FASES"
        titulo_diag = f"Falla Línea a Línea (LL - {desc_fases})"
        subtitulo_diag = f"Cortocircuito franco entre {desc_fases.lower()} sin contacto con la malla de tierra."
        orden_rele = "DISPARO BIPOLAR DE FASES"
        paso_1 = f"Comandar apertura rápida de los polos asociados a {desc_fases}."
        paso_2 = "Comprobar que no exista contacto secundario con el conductor de guardia o tierra."
        paso_3 = "Despejar tramo y verificar distanciamiento mecánico entre conductores aéreos."
    else:
        hud_css = "hud-card-alert"
        estado_badge = "FALLA DOBLE A TIERRA"
        titulo_diag = f"Falla Doble Línea a Tierra (LLG - {desc_fases})"
        subtitulo_diag = f"Dos fases en cortocircuito simultáneo ({desc_fases.lower()}) y conectadas a la malla de tierra."
        orden_rele = "DISPARO DE PROTECCIÓN HOMOPOLAR (51N)"
        paso_1 = f"Comandar apertura rápida de los polos asociados a {desc_fases}."
        paso_2 = "Inspeccionar transformador de puesta a tierra y estado térmico del conductor de neutro."
        paso_3 = "Revisar punto de convergencia física del fallo antes de autorizar cualquier maniobra."

    es_baja_confianza = bool(confianza_pct < (UMBRAL_CONFIANZA_MINIMA * 100.0))

    if es_baja_confianza:
        st.warning(
            f"⚠️ **Diagnóstico poco confiable (Confianza: {confianza_pct:.1f}% < 80%)**: "
            "El modelo presenta baja certeza probabilística y duda ante el patrón de señales ingresado. "
            "Se recomienda verificar físicamente las lecturas o contrastar con relés de respaldo antes de ejecutar maniobras."
        )

    col_hud, col_despacho = st.columns(2, gap="medium")

    # Indicador de porcentaje de confianza y badge de fiabilidad junto al título
    color_confianza = "#dc2626" if es_baja_confianza else "#059669"
    badge_confianza_html = (
        f"<span style='font-size: 0.92rem; font-weight: 700; color: {color_confianza}; margin-left: 0.5rem;'>"
        f"— {confianza_pct:.1f}% de confianza</span>"
    )
    aviso_poco_confiable_badge = (
        "<div style='margin-top: 0.4rem;'>"
        "<span style='background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; font-size: 0.78rem; "
        "font-weight: 700; padding: 2px 10px; border-radius: 9999px;'>⚠️ Diagnóstico poco confiable (&lt; 80%)</span>"
        "</div>"
        if es_baja_confianza
        else ""
    )

    desc_hud_completa = subtitulo_diag
    if es_baja_confianza:
        desc_hud_completa += (
            f"<div style='margin-top: 0.4rem; color: #b91c1c; font-weight: 600; font-size: 0.8rem;'>"
            f"Aviso: Diagnóstico poco confiable ({confianza_pct:.1f}%). El modelo no reconoce con certeza este estado."
            f"</div>"
        )

    pill_certeza_style = "style='border-color: #fca5a5; background: #fff5f5; color: #991b1b; font-weight: 700;'" if es_baja_confianza else ""
    pill_certeza_val = f"{confianza_pct:.1f}% {'(Baja)' if es_baja_confianza else ''}"

    with col_hud:
        render_html(
            f"""
            <div class="hud-card {hud_css}">
                <div>
                    <span class="hud-badge">{estado_badge}</span>
                    <div class="hud-title">{titulo_diag} {badge_confianza_html}</div>
                    {aviso_poco_confiable_badge}
                    <div class="hud-desc">{desc_hud_completa}</div>
                </div>
                <div class="hud-pills-row">
                    <span class="hud-pill" {pill_certeza_style}><span class="hud-pill-tag">Certeza:</span><span class="hud-pill-val">{pill_certeza_val}</span></span>
                    <span class="hud-pill"><span class="hud-pill-tag">Latencia:</span><span class="hud-pill-val">{latencia_ms:.2f} ms</span></span>
                    <span class="hud-pill"><span class="hud-pill-tag">Protección:</span><span class="hud-pill-val">{orden_rele}</span></span>
                </div>
            </div>
            """
        )

    alerta_despacho_html = (
        f"""
        <div style="font-size: 0.8rem; color: #991b1b; background: #fef2f2; border: 1px solid #fecaca; border-radius: 6px; padding: 6px 10px; margin-top: 0.5rem; line-height: 1.4;">
            ⚠️ <strong>Aviso de Fiabilidad:</strong> Diagnóstico poco confiable ({confianza_pct:.1f}%). Proceda con verificación de campo antes de autorizar maniobras en interruptores.
        </div>
        """
        if es_baja_confianza
        else ""
    )

    with col_despacho:
        render_html(
            f"""
            <div class="dispatch-card">
                <div class="dispatch-header">
                    Protocolo de seguridad operativa sugerido
                </div>
                <div>
                    <div class="dispatch-step"><strong>1. Aislamiento:</strong> {paso_1}</div>
                    <div class="dispatch-step"><strong>2. Seguridad:</strong> {paso_2}</div>
                    <div class="dispatch-step"><strong>3. Inspección:</strong> {paso_3}</div>
                </div>
                {alerta_despacho_html}
                <div style="font-size: 0.78rem; color: #64748b; margin-top: 0.5rem; border-top: 1px solid #e2e8f0; padding-top: 0.4rem;">
                    Recomendación del sistema: {mensaje_operador}
                </div>
            </div>
            """
        )

    # --------------------------------------------------------------------------
    # PASO 4: EXPLICABILIDAD SHAP
    # --------------------------------------------------------------------------
    st.markdown("<hr style='border: none; border-top: 1px solid #e2e8f0; margin: 1.5rem 0 1rem 0;'>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="step-heading-row">
            <span class="step-pill-badge">4</span>
            <span style="font-size: 1.05rem; font-weight: 700; color: #0f172a;">
                Inteligencia Artificial Explicable (XAI): ¿Por qué el modelo tomó esta decisión?
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    fila_actual = pd.DataFrame(
        [{"Va": val_va, "Vb": val_vb, "Vc": val_vc, "Ia": val_ia, "Ib": val_ib, "Ic": val_ic}]
    )[COLUMNAS]

    modelo_rf = paquete["modelo"]
    clases_modelo = list(modelo_rf.classes_)
    idx_diag = clases_modelo.index(diag_clase)

    fila_evaluada = resultado.get("fila_alineada", fila_actual)
    sv_raw = explicador.shap_values(fila_evaluada)
    sv_norm = normalizar_shap(sv_raw, 1, len(COLUMNAS), len(clases_modelo))
    valores_shap_slots = sv_norm[0, :, idx_diag]
    valores_shap = mapear_shap_a_canales_fisicos(valores_shap_slots, rotacion=rotacion_ganadora)

    col_prob, col_shap = st.columns([1, 1], gap="medium")

    with col_prob:
        with st.container():
            render_html('<div class="xai-chart-card"></div>')
            render_html('<div class="xai-chart-title">Probabilidades por Estado</div>')
            df_prob = pd.DataFrame(
                [{"Clase": c, "Probabilidad": p, "Porcentaje": p * 100.0} for c, p in probabilidades.items()]
            )
            chart_p = (
                alt.Chart(df_prob)
                .mark_bar(cornerRadius=4)
                .encode(
                    x=alt.X("Porcentaje:Q", title="Probabilidad Calculada (%)", scale=alt.Scale(domain=[0, 100])),
                    y=alt.Y("Clase:N", title="", sort=ORDEN_CLASES),
                    color=alt.condition(
                        alt.datum.Clase == diag_clase,
                        alt.value("#059669" if diag_clase == "Normal" else ("#dc2626" if diag_clase == "Trifásica" else "#d97706")),
                        alt.value("#cbd5e1"),
                    ),
                    tooltip=[alt.Tooltip("Clase:N"), alt.Tooltip("Porcentaje:Q", format=".1f", title="Certeza (%)")],
                )
                .properties(height=200)
            )
            st.altair_chart(chart_p, use_container_width=True)

    with col_shap:
        with st.container():
            render_html('<div class="xai-chart-card"></div>')
            render_html(f'<div class="xai-chart-title">Aporte Marginal de Señales hacia \'{diag_clase}\'</div>')
            df_sh = pd.DataFrame({
                "Canal": [f"{c} ({fila_actual.iloc[0][c]:.2f})" for c in COLUMNAS],
                "Impacto_SHAP": valores_shap,
            })
            chart_s = (
                alt.Chart(df_sh)
                .mark_bar(cornerRadius=4)
                .encode(
                    x=alt.X("Impacto_SHAP:Q", title="Aporte Marginal SHAP (Verde = A Favor | Rojo = En Contra)"),
                    y=alt.Y("Canal:N", title="", sort="-x"),
                    color=alt.condition(
                        alt.datum.Impacto_SHAP >= 0,
                        alt.value("#059669"),
                        alt.value("#dc2626"),
                    ),
                    tooltip=[
                        alt.Tooltip("Canal:N"),
                        alt.Tooltip("Impacto_SHAP:Q", format=".4f", title="Valor SHAP"),
                    ],
                )
                .properties(height=200)
            )
            st.altair_chart(chart_s, use_container_width=True)

    # Factores Dominantes
    serie_abs = pd.Series(np.abs(valores_shap), index=COLUMNAS).sort_values(ascending=False)
    var1, var2 = serie_abs.index[0], serie_abs.index[1]
    val1, val2 = fila_actual.iloc[0][var1], fila_actual.iloc[0][var2]
    sh1, sh2 = valores_shap[COLUMNAS.index(var1)], valores_shap[COLUMNAS.index(var2)]

    st.markdown("<hr style='border: none; border-top: 1px solid #e2e8f0; margin: 1.5rem 0 1rem 0;'>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="step-heading-row">
            <span class="step-pill-badge">5</span>
            <span style="font-size: 1.05rem; font-weight: 700; color: #0f172a;">
                Síntesis Física Explicable para el Ingeniero de Subestación
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col_x1, col_x2 = st.columns(2, gap="medium")

    with col_x1:
        st.markdown(
            f"""
            <div class="factor-card" style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 1rem 1.2rem; box-shadow: 0 1px 3px rgba(0,0,0,0.04); margin-top: 0;">
                <div style="font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase;">Canal Dominante #1</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.25rem; font-weight: 700; color: #002a69; margin: 0.2rem 0;">
                    {var1} = {val1:.2f} {'A' if 'I' in var1 else 'p.u.'}
                </div>
                <div style="font-size: 0.82rem; color: #334155; line-height: 1.4;">
                    Aporte de <strong>{'+' if sh1>=0 else ''}{sh1:.3f}</strong> a la verosimilitud de <strong>{diag_clase}</strong>.
                    Representa la alteración primaria en la impedancia aparente del lazo de falla.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_x2:
        st.markdown(
            f"""
            <div class="factor-card" style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 1rem 1.2rem; box-shadow: 0 1px 3px rgba(0,0,0,0.04); margin-top: 0;">
                <div style="font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase;">Canal Dominante #2</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.25rem; font-weight: 700; color: #002a69; margin: 0.2rem 0;">
                    {var2} = {val2:.2f} {'A' if 'I' in var2 else 'p.u.'}
                </div>
                <div style="font-size: 0.82rem; color: #334155; line-height: 1.4;">
                    Aporte de <strong>{'+' if sh2>=0 else ''}{sh2:.3f}</strong> a la verosimilitud de <strong>{diag_clase}</strong>.
                    Corrobora la interacción de fase o el lazo con tierra para descartar otros estados operativos.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==============================================================================
# PÁGINA 2: PROCESAMIENTO MASIVO POR LOTE (/diagnostic-from-file)
# ==============================================================================
def pagina_procesamiento_lote():
    with st.container():
        render_html('<div class="batch-upload-card"></div>')
        col_up_title, col_up_btn = st.columns([3.8, 1.2], vertical_alignment="center")
        with col_up_title:
            render_html(
                """
                <div style="display: flex; align-items: center; gap: 0.65rem; margin-bottom: 0.35rem;">
                    <span class="step-pill-badge" style="background: #eef2fb; color: #002a69; border: 1px solid #c5d2f3;">
                        <svg style="width: 14px; height: 14px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2 1 3 3 3h10c2 0 3-1 3-3V7c0-2-1-3-3-3H7C5 4 4 5 4 7zm0 5h16M9 4v16"></path>
                        </svg>
                    </span>
                    <span style="font-size: 1.05rem; font-weight: 700; color: #0f172a;">Clasificación Masiva de Telemetría en Lote (Batch)</span>
                </div>
                <p style="color: #64748b; font-size: 0.82rem; margin-top: 0; margin-bottom: 0.35rem; line-height: 1.45;">
                    Cargue un archivo CSV con las 6 señales de telemetría trifásica registradas durante eventos de falla para procesar miles de lecturas en milisegundos.
                </p>
                """
            )
        with col_up_btn:
            if st.button("Datos de prueba", key="btn_cargar_ejemplo_batch", use_container_width=True):
                st.session_state["usar_ejemplo_batch"] = True

        archivo_csv = st.file_uploader(
            "Arrastre o seleccione su archivo CSV (columnas obligatorias: Va, Vb, Vc, Ia, Ib, Ic):",
            type=["csv"],
        )

    df_lote = None
    nombre_archivo = None

    if archivo_csv is not None:
        try:
            df_lote = pd.read_csv(archivo_csv)
            nombre_archivo = archivo_csv.name
            st.session_state["usar_ejemplo_batch"] = False
        except Exception as e:
            st.error(f"Error al leer el archivo CSV cargado: {e}")
    elif st.session_state.get("usar_ejemplo_batch", False):
        ruta_ej = obtener_ruta_datos_procesados("ejemplos_prueba.csv")
        if ruta_ej.exists():
            df_lote = pd.read_csv(ruta_ej)
            nombre_archivo = "ejemplos_prueba.csv"

    if df_lote is not None:
        try:
            faltantes = [c for c in COLUMNAS if c not in df_lote.columns]
            if faltantes:
                st.error(f"El archivo cargado no contiene las columnas necesarias: {faltantes}")
            else:
                st.success(f"Archivo validado exitosamente ({nombre_archivo}): **{len(df_lote):,} registros** detectados.")

                if st.button("PROCESAR LOTE COMPLETO AHORA", type="primary", use_container_width=True):
                    X_lote = df_lote[COLUMNAS].copy()

                    t_ini = time.perf_counter()
                    modelo = paquete["modelo"]
                    predicciones = modelo.predict(X_lote)
                    probs_matriz = modelo.predict_proba(X_lote)
                    t_total = time.perf_counter() - t_ini

                    confianzas = np.max(probs_matriz, axis=1) * 100.0
                    muestras_seg = len(X_lote) / t_total if t_total > 0 else 0.0

                    df_res_lote = df_lote.copy()
                    df_res_lote["Diagnostico"] = predicciones
                    df_res_lote["Confianza (%)"] = np.round(confianzas, 1)
                    df_res_lote["Protocolo Operativo"] = [
                        paquete["mensajes_operador"].get(p, "Verificar protocolo.")
                        for p in predicciones
                    ]

                    st.session_state["resultado_lote"] = {
                        "df_res_lote": df_res_lote,
                        "t_total": t_total,
                        "muestras_seg": muestras_seg,
                        "pct_anomalo": ((df_res_lote["Diagnostico"] != "Normal").sum() / len(df_lote)) * 100.0,
                        "num_anomalos": int((df_res_lote["Diagnostico"] != "Normal").sum()),
                        "volumen": len(df_lote),
                        "nombre_archivo": nombre_archivo,
                    }

                res_lote = st.session_state.get("resultado_lote")
                if res_lote is not None and res_lote.get("nombre_archivo") == nombre_archivo:
                    df_res = res_lote["df_res_lote"]
                    t_total = res_lote["t_total"]
                    muestras_seg = res_lote["muestras_seg"]
                    pct_anomalo = res_lote["pct_anomalo"]
                    num_anomalos = res_lote["num_anomalos"]
                    volumen = res_lote["volumen"]

                    # Métricas de Rendimiento Industrial (4 Cards intuitivos)
                    render_html(
                        """
                        <div style="font-size: 0.95rem; font-weight: 700; color: #0f172a; margin-top: 1.35rem; margin-bottom: 0.65rem;">
                            Rendimiento del Procesamiento Industrial
                        </div>
                        """
                    )
                    m1, m2, m3, m4 = st.columns(4, gap="medium")

                    with m1:
                        render_html(
                            f"""
                            <div class="kpi-card-v2">
                                <div class="kpi-top-row">
                                    <span class="kpi-label">Volumen Analizado</span>
                                    <span class="kpi-icon-badge" style="background: rgba(0, 42, 105, 0.08); border: 1px solid rgba(0, 42, 105, 0.18); color: #002a69;">
                                        <svg style="width: 17px; height: 17px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                                        </svg>
                                    </span>
                                </div>
                                <div>
                                    <div class="kpi-value-row">
                                        <span class="kpi-value">{volumen:,}</span>
                                        <span class="kpi-unit">oscilogramas</span>
                                    </div>
                                    <div class="kpi-footer-text">
                                        <svg style="width: 13px; height: 13px; color: #059669;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"></path></svg>
                                        <span>Telemetría validada</span>
                                    </div>
                                </div>
                            </div>
                            """
                        )

                    with m2:
                        render_html(
                            f"""
                            <div class="kpi-card-v2">
                                <div class="kpi-top-row">
                                    <span class="kpi-label">Tiempo de Inferencia</span>
                                    <span class="kpi-icon-badge" style="background: rgba(217, 119, 6, 0.1); border: 1px solid rgba(217, 119, 6, 0.22); color: #d97706;">
                                        <svg style="width: 17px; height: 17px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                        </svg>
                                    </span>
                                </div>
                                <div>
                                    <div class="kpi-value-row">
                                        <span class="kpi-value">{t_total*1000:.1f}</span>
                                        <span class="kpi-unit">ms</span>
                                    </div>
                                    <div class="kpi-footer-text">
                                        <svg style="width: 13px; height: 13px; color: #d97706;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                                        <span>Cómputo CPU local</span>
                                    </div>
                                </div>
                            </div>
                            """
                        )

                    with m3:
                        render_html(
                            f"""
                            <div class="kpi-card-v2">
                                <div class="kpi-top-row">
                                    <span class="kpi-label">Throughput en CPU</span>
                                    <span class="kpi-icon-badge" style="background: rgba(85, 135, 80, 0.1); border: 1px solid rgba(85, 135, 80, 0.25); color: #558750;">
                                        <svg style="width: 17px; height: 17px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M3 9h2m-2 6h2m14-6h2m-2 6h2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"></path>
                                        </svg>
                                    </span>
                                </div>
                                <div>
                                    <div class="kpi-value-row">
                                        <span class="kpi-value">{muestras_seg:,.0f}</span>
                                        <span class="kpi-unit">m/s</span>
                                    </div>
                                    <div class="kpi-footer-text">
                                        <svg style="width: 13px; height: 13px; color: #558750;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"></path></svg>
                                        <span>Meta SMART >= 500 m/s</span>
                                    </div>
                                </div>
                            </div>
                            """
                        )

                    with m4:
                        es_anomalo = pct_anomalo > 0
                        badge_bg = "rgba(220, 38, 38, 0.1)" if es_anomalo else "rgba(5, 150, 105, 0.1)"
                        badge_border = "rgba(220, 38, 38, 0.25)" if es_anomalo else "rgba(5, 150, 105, 0.25)"
                        accent_color = "#dc2626" if es_anomalo else "#059669"
                        icon_svg = (
                            '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>'
                            if es_anomalo else
                            '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>'
                        )
                        render_html(
                            f"""
                            <div class="kpi-card-v2">
                                <div class="kpi-top-row">
                                    <span class="kpi-label">Tasa de Eventos Anómalos</span>
                                    <span class="kpi-icon-badge" style="background: {badge_bg}; border: 1px solid {badge_border}; color: {accent_color};">
                                        <svg style="width: 17px; height: 17px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            {icon_svg}
                                        </svg>
                                    </span>
                                </div>
                                <div>
                                    <div class="kpi-value-row">
                                        <span class="kpi-value" style="color: {accent_color};">{pct_anomalo:.1f}%</span>
                                    </div>
                                    <div class="kpi-footer-text">
                                        <svg style="width: 13px; height: 13px; color: {accent_color};" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                                        <span>{num_anomalos} de {volumen} con falla</span>
                                    </div>
                                </div>
                            </div>
                            """
                        )

                    # Vista Previa del Reporte de Diagnóstico
                    render_html(
                        """
                        <div style="font-size: 0.95rem; font-weight: 700; color: #0f172a; margin-top: 1.5rem; margin-bottom: 0.65rem;">
                            Vista Previa del Reporte de Diagnóstico
                        </div>
                        """
                    )
                    st.dataframe(df_res.head(25), use_container_width=True)

                    buffer = io.StringIO()
                    df_res.to_csv(buffer, index=False)
                    st.download_button(
                        label="DESCARGAR REPORTE EN CSV",
                        data=buffer.getvalue(),
                        file_name="diagnostico_subestacion_lote.csv",
                        mime="text/csv",
                        use_container_width=True,
                    )
        except Exception as e:
            st.error(f"Error procesando el lote: {e}")
    else:
        st.info(
            "Estructura obligatoria: CSV con encabezados `Va, Vb, Vc, Ia, Ib, Ic`. "
            "Puede emplear como referencia el archivo oficial `data/processed/ejemplos_prueba.csv`."
        )


# ==============================================================================
# PÁGINA 3: AUDITORÍA DE METAS SMART Y MODELO (/info-audit-model)
# ==============================================================================
def pagina_auditoria_modelo():
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.8rem;">
            <span style="font-size: 1.05rem; font-weight: 700; color: #0f172a;">Auditoría Oficial de Rendimiento y Metas SMART</span>
        </div>
        <p style="color: #64748b; font-size: 0.85rem; margin-top: 0; margin-bottom: 1.5rem;">
            Verificación y cumplimiento formal de los criterios de aceptación del proyecto integrador (Reglas 02 y 03).
        </p>
        """,
        unsafe_allow_html=True,
    )

    if metricas_dict is not None:
        c1, c2, c3, c4 = st.columns(4, gap="medium")
        c1.metric("Accuracy en Test", f"{metricas_dict.get('accuracy_prueba', 0)*100:.2f}%")
        c2.metric("F1-Score Macro", f"{metricas_dict.get('f1_macro_prueba', 0):.4f}")
        c3.metric("Recall Mínimo por Clase", f"{metricas_dict.get('recall_minimo_por_clase', 0):.4f}")
        c4.metric("Latencia Media CPU", f"{metricas_dict.get('latencia_ms', 0):.1f} ms")

        st.markdown("##### Tabla de Cumplimiento de Metas SMART")
        cumplimiento = metricas_dict.get("cumplimiento_smart", {})
        df_smart = pd.DataFrame(list(cumplimiento.items()), columns=["Criterio de Aceptación", "Cumplimiento"])
        st.table(df_smart)

    st.markdown("##### Justificación Física de la Fusión a 5 Clases")
    st.info(
        f"**Nota de Diseño:** {NOTA_CLASES}\n\n"
        "En una falla trifásica simétrica balanceada, las tres corrientes de cortocircuito "
        "tienen idéntica magnitud y están desfasadas 120 grados, anulándose en la conexión a tierra (In = 0 A). "
        "Por ende, las seis señales de fase (Va, Vb, Vc, Ia, Ib, Ic) no contienen información física para separar "
        "LLL de LLLG, y la maniobra de protección del interruptor es idéntica en ambos casos."
    )

    st.markdown("##### Galería Oficial de Gráficos de Validación")
    col_g1, col_g2 = st.columns(2, gap="medium")
    ruta_figuras = obtener_ruta_resultados("figures")

    with col_g1:
        cm_path = ruta_figuras / "matriz_confusion.png"
        if cm_path.exists():
            st.image(str(cm_path), caption="Matriz de Confusión (Random Forest en Test)", use_container_width=True)

        f1_path = ruta_figuras / "f1_comparativa_modelos.png"
        if f1_path.exists():
            st.image(str(f1_path), caption="F1-Macro Comparativo vs Meta SMART (0.90)", use_container_width=True)

    with col_g2:
        shap_path = ruta_figuras / "shap_importancia_global.png"
        if shap_path.exists():
            st.image(str(shap_path), caption="Importancia Global de Señales (SHAP)", use_container_width=True)

        heat_path = ruta_figuras / "shap_heatmap_clases.png"
        if heat_path.exists():
            st.image(str(heat_path), caption="Mapa de Calor SHAP por Tipo de Falla", use_container_width=True)

# ==============================================================================
# ENRUTADOR PRINCIPAL SPA (ZERO-DELAY, SIN RECARGA DE PÁGINA)
# ==============================================================================
def main():
    # Inicialización de estado SPA y sincronización bidireccional con query params
    if "modulo_activo" not in st.session_state:
        st.session_state.modulo_activo = "diagnostic-real-time"

    # Sincronización solo si la URL cambió externamente (navegación directa o historial)
    modulo_url = st.query_params.get("modulo")
    url_guardada = st.session_state.get("_url_modulo_guardada")
    if (
        modulo_url
        and modulo_url != url_guardada
        and modulo_url in ["diagnostic-real-time", "diagnostic-from-file", "info-audit-model"]
    ):
        st.session_state.modulo_activo = modulo_url
        st.session_state._url_modulo_guardada = modulo_url
    else:
        st.session_state._url_modulo_guardada = st.session_state.modulo_activo

    # Estilos globales y Cabecera superior que ocupa el 100% del ancho
    aplicar_estilos_css()
    render_header()

    # Selector de módulos operativo (3 Cards centradas en 8 columnas)
    render_navbar(st.session_state.modulo_activo)

    # Renderizado dinámico del módulo seleccionado sin recargar la página
    if st.session_state.modulo_activo == "diagnostic-from-file":
        pagina_procesamiento_lote()
    elif st.session_state.modulo_activo == "info-audit-model":
        pagina_auditoria_modelo()
    else:
        pagina_diagnostico_tiempo_real()

    # Footer corporativo de ancho completo
    render_footer()


if __name__ == "__main__":
    main()