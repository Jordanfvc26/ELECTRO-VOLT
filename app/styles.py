"""Módulo de estilos CSS globales y diseño SCADA industrial"""

from __future__ import annotations

import streamlit as st

def aplicar_estilos_css(tema_oscuro: bool | None = None):
    tema_param = st.query_params.get('theme')
    if tema_param == 'dark':
        st.session_state.tema_oscuro = True
    elif tema_param == 'light':
        st.session_state.tema_oscuro = False
    elif 'tema_oscuro' not in st.session_state:
        st.session_state.tema_oscuro = False

    if tema_oscuro is None:
        tema_oscuro = bool(st.session_state.get('tema_oscuro', False))
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
        .header-theme-toggle {
            width: 36px;
            height: 36px;
            border-radius: 9999px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
        }
        .header-theme-toggle-light {
            background: #f1f5f9;
            border: 1px solid #cbd5e1;
        }
        .header-theme-toggle-dark {
            background: #1e293b;
            border: 1px solid #334155;
            box-shadow: 0 0 12px rgba(251, 191, 36, 0.25);
        }

        /* Overlay interactivo del botón Streamlit sobre el conmutador de tema */
        div[class*="st-key-btn_toggle_theme"] {
            position: fixed !important;
            top: 11px !important;
            right: 2rem !important;
            width: 36px !important;
            height: 36px !important;
            z-index: 100002 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        div[class*="st-key-btn_toggle_theme"] div[data-testid="stButton"],
        div[class*="st-key-btn_toggle_theme"] button {
            width: 36px !important;
            height: 36px !important;
            min-height: 36px !important;
            border-radius: 9999px !important;
            opacity: 0 !important;
            cursor: pointer !important;
            border: none !important;
            background: transparent !important;
            padding: 0 !important;
            margin: 0 !important;
            box-shadow: none !important;
        }
        body:has(div[class*="st-key-btn_toggle_theme"] button:hover) .header-theme-toggle {
            transform: scale(1.1) !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.18) !important;
        }
        @media (max-width: 768px) {
            div[class*="st-key-btn_toggle_theme"] {
                right: 1rem !important;
            }
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
        div[data-testid="stElementContainer"]:has(.batch-upload-card),
        div[data-testid="stElementContainer"]:has(.audit-main-card) {
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

        /* Contenedor Exterior Blanco de Auditoría SMART (Página 3) */
        div[data-testid="stMainBlockContainer"] > div[data-testid="stVerticalBlock"] > div:has(.audit-main-card) {
            background-color: #ffffff !important;
            background: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 16px !important;
            padding: 1.4rem 1.6rem 1.6rem 1.6rem !important;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04) !important;
            margin-top: 0 !important;
            margin-bottom: 1.25rem !important;
        }

        /* Contenedores para Páginas de Información y Legales */
        div[data-testid="stMainBlockContainer"] > div[data-testid="stVerticalBlock"] > div:has(.info-page-card) {
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
        }
        .info-page-container {
            max-width: 1080px;
            margin: 0 auto;
            padding: 0.5rem 0 2rem 0;
        }
        .info-page-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 2.2rem 2.4rem;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
            margin-bottom: 2rem;
        }
        .footer-back-link {
            display: inline-flex;
            align-items: center;
            background: #ffffff;
            border: 1px solid #cbd5e1;
            color: #002a69 !important;
            padding: 0.45rem 1rem;
            border-radius: 8px;
            font-size: 0.82rem;
            font-weight: 700;
            text-decoration: none !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
            transition: all 0.2s ease;
            margin-bottom: 1.25rem;
        }
        .footer-back-link:hover {
            background: #f8fafc;
            border-color: #002a69;
            color: #002a69 !important;
            transform: translateX(-3px);
            text-decoration: none !important;
        }
        .info-badge-tag {
            display: inline-block;
            font-size: 0.72rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            background: rgba(0, 42, 105, 0.07);
            color: #002a69;
            border: 1px solid rgba(0, 42, 105, 0.18);
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            margin-bottom: 0.65rem;
        }
        .info-page-title {
            font-size: 1.85rem;
            font-weight: 800;
            color: #0f172a;
            letter-spacing: -0.02em;
            line-height: 1.2;
            margin-bottom: 0.5rem;
        }
        .info-page-subtitle {
            font-size: 0.95rem;
            color: #64748b;
            line-height: 1.5;
            margin-bottom: 1.75rem;
            padding-bottom: 1.25rem;
            border-bottom: 1px solid #f1f5f9;
        }
        .info-section-heading {
            font-size: 1.12rem;
            font-weight: 700;
            color: #0f172a;
            margin-top: 1.75rem;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .info-text-p {
            font-size: 0.9rem;
            color: #334155;
            line-height: 1.65;
            margin-bottom: 0.9rem;
        }
        .info-callout-box {
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-left: 4px solid #002a69;
            border-radius: 8px;
            padding: 1.1rem 1.35rem;
            margin: 1.25rem 0;
        }
        .warning-callout-box {
            background-color: #fffbeb;
            border: 1px solid #fde68a;
            border-left: 4px solid #d97706;
            border-radius: 8px;
            padding: 1.1rem 1.35rem;
            margin: 1.25rem 0;
        }
        .danger-callout-box {
            background-color: #fef2f2;
            border: 1px solid #fecaca;
            border-left: 4px solid #dc2626;
            border-radius: 8px;
            padding: 1.1rem 1.35rem;
            margin: 1.25rem 0;
        }
        .info-grid-2 {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1.25rem;
            margin: 1.25rem 0;
        }
        .info-feature-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 1.1rem 1.25rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        }
        @media (max-width: 768px) {
            .info-grid-2 {
                grid-template-columns: 1fr !important;
            }
            .info-page-card {
                padding: 1.5rem 1.2rem !important;
            }
            .info-page-title {
                font-size: 1.45rem !important;
            }
            .kpi-grid-4 {
                grid-template-columns: 1fr !important;
            }
            .error-404-card {
                padding: 1.75rem 1.25rem !important;
            }
            .error-hero-number {
                font-size: 4rem !important;
            }
            .error-hero-spark {
                font-size: 3rem !important;
            }
            .error-title {
                font-size: 1.45rem !important;
            }
            .error-nav-grid {
                grid-template-columns: 1fr !important;
            }
        }

        /* ==============================================================================
           ESTILOS SCADA PARA PÁGINA 404 (ERROR DE RUTA / TOPOLOGÍA)
           ============================================================================== */
        body:has(.error-404-container) div[data-testid="stDialog"],
        body:has(.error-404-container) div[role="dialog"],
        body:has(.error-404-container) div[data-baseweb="modal"],
        body:has(.error-404-container) div[data-baseweb="backdrop"] {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            pointer-events: none !important;
            height: 0 !important;
            width: 0 !important;
        }

        .error-404-container {
            max-width: 1080px;
            margin: 0 auto;
            padding: 0.5rem 0 2rem 0;
        }
        .error-404-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 2.5rem 2.4rem;
            box-shadow: 0 4px 20px -2px rgba(0, 42, 105, 0.08);
            margin-bottom: 2rem;
            text-align: center;
        }
        .error-badge-tag {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            font-size: 0.75rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            background: rgba(220, 38, 38, 0.08);
            color: #dc2626;
            border: 1px solid rgba(220, 38, 38, 0.25);
            padding: 0.35rem 0.85rem;
            border-radius: 9999px;
            margin-bottom: 1.25rem;
        }
        .error-badge-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #dc2626;
            animation: pulse404 1.8s infinite;
        }
        @keyframes pulse404 {
            0% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.6); }
            70% { box-shadow: 0 0 0 8px rgba(220, 38, 38, 0); }
            100% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0); }
        }
        .error-hero-number {
            font-size: 5.5rem;
            font-weight: 900;
            line-height: 1;
            letter-spacing: -0.04em;
            background: linear-gradient(135deg, #002a69 0%, #1e40af 45%, #f59e0b 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0.25rem 0 0.5rem 0;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.15rem;
        }
        .error-hero-spark {
            display: inline-block;
            font-size: 4.2rem;
            filter: drop-shadow(0 0 12px rgba(245, 158, 11, 0.6));
            -webkit-text-fill-color: #f59e0b;
            animation: floatSpark 2.5s ease-in-out infinite;
        }
        @keyframes floatSpark {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-6px); }
        }
        .error-title {
            font-size: 1.85rem;
            font-weight: 800;
            color: #0f172a;
            margin-bottom: 0.5rem;
        }
        .error-subtitle {
            font-size: 0.98rem;
            color: #64748b;
            max-width: 680px;
            margin: 0 auto 1.75rem auto;
            line-height: 1.6;
        }
        .error-telemetry-box {
            background: #0f172a;
            color: #e2e8f0;
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            text-align: left;
            max-width: 720px;
            margin: 0 auto 2rem auto;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.82rem;
            border-left: 4px solid #f59e0b;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.25);
        }
        .error-code-highlight {
            color: #f87171;
            font-weight: 700;
            background: rgba(239, 68, 68, 0.15);
            padding: 0.15rem 0.5rem;
            border-radius: 4px;
        }
        .error-nav-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 1.5rem auto 2rem auto;
            text-align: left;
            max-width: 900px;
        }
        .error-nav-card {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1.15rem;
            text-decoration: none !important;
            color: #0f172a !important;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            flex-direction: column;
            gap: 0.35rem;
        }
        .error-nav-card:hover {
            background: #ffffff;
            border-color: #002a69;
            box-shadow: 0 8px 16px -4px rgba(0, 42, 105, 0.12);
            transform: translateY(-3px);
        }
        .error-nav-card-title {
            font-weight: 700;
            font-size: 0.92rem;
            color: #002a69;
            display: flex;
            align-items: center;
            gap: 0.45rem;
        }
        .error-nav-card-desc {
            font-size: 0.78rem;
            color: #64748b;
            line-height: 1.45;
        }
        .error-btn-primary {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #002a69 0%, #1e40af 100%);
            color: #ffffff !important;
            padding: 0.75rem 1.75rem;
            border-radius: 10px;
            font-weight: 700;
            font-size: 0.95rem;
            text-decoration: none !important;
            box-shadow: 0 4px 14px rgba(0, 42, 105, 0.25);
            transition: all 0.2s ease;
            cursor: pointer;
        }
        .error-btn-primary:hover {
            background: linear-gradient(135deg, #001e4d 0%, #1d4ed8 100%);
            transform: translateY(-2px);
            box-shadow: 0 6px 18px rgba(0, 42, 105, 0.35);
            color: #ffffff !important;
            text-decoration: none !important;
        }

        /* Estilización del File Uploader de Streamlit en Formato Dropzone */
        div[data-testid="stFileUploader"] {
            margin: 0 !important;
            padding: 0 !important;
        }
        div[data-testid="stFileUploader"] > label {
            display: none !important;
        }
        section[data-testid="stFileUploaderDropzone"] {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            text-align: center !important;
            background-color: #f8fafc !important;
            border: 2px dashed #94a3b8 !important;
            border-radius: 12px !important;
            padding: 1.5rem 1.25rem !important;
            min-height: 165px !important;
            cursor: pointer !important;
            transition: all 0.25s ease !important;
        }
        section[data-testid="stFileUploaderDropzone"]:hover {
            border-color: #002a69 !important;
            background-color: #f1f5f9 !important;
            box-shadow: 0 4px 12px rgba(0, 42, 105, 0.08) !important;
        }
        /* Icono de subida en el centro del dropzone (aumentado +25px: 63x63px) */
        section[data-testid="stFileUploaderDropzone"]::before {
            content: '';
            display: block;
            width: 63px;
            height: 63px;
            margin-bottom: 0.65rem;
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%23002a69' stroke-width='1.8'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12'/%3E%3C/svg%3E") no-repeat center;
            background-size: contain;
            transition: transform 0.2s ease;
        }
        section[data-testid="stFileUploaderDropzone"]:hover::before {
            transform: translateY(-2px);
        }
        /* Ocultar el botón upload dentro del dropzone (la zona completa ya permite click y arrastrar) */
        section[data-testid="stFileUploaderDropzone"] [data-testid="stBaseButton-secondary"],
        section[data-testid="stFileUploaderDropzone"] button {
            display: none !important;
        }
        section[data-testid="stFileUploaderDropzone"] span {
            font-size: 0.85rem !important;
            font-weight: 600 !important;
            color: #334155 !important;
            margin-top: 0.35rem !important;
            text-align: center !important;
        }
        section[data-testid="stFileUploaderDropzone"] small {
            font-size: 0.74rem !important;
            color: #64748b !important;
            margin-top: 0.2rem !important;
            text-align: center !important;
            display: block !important;
            width: 100% !important;
        }

        /* Banner de validación y estado de carga de lote (con icono de check/error) */
        .batch-status-banner {
            display: flex;
            align-items: center;
            gap: 0.85rem;
            padding: 0.85rem 1.25rem;
            border-radius: 10px;
            font-size: 0.88rem;
            line-height: 1.45;
            margin-top: 0.75rem;
            margin-bottom: 0.85rem;
            box-sizing: border-box;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
            transition: all 0.25s ease;
        }
        .batch-status-success {
            background-color: #ecfdf5;
            border: 1.5px solid #a7f3d0;
            color: #065f46;
        }
        .batch-status-error {
            background-color: #fef2f2;
            border: 1.5px solid #fecaca;
            color: #991b1b;
        }
        .batch-status-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 22px;
            height: 22px;
            border-radius: 50%;
            flex-shrink: 0;
        }
        .batch-status-success .batch-status-icon {
            background: #10b981;
            color: #ffffff;
        }
        .batch-status-error .batch-status-icon {
            background: #ef4444;
            color: #ffffff;
        }

        /* Botones de acción rápida por lote: cuadrados redondeados con icono */
        div[class*="st-key-btn_limpiar_batch"],
        div[class*="st-key-btn_descargar_csv_batch"] {
            display: flex !important;
            justify-content: flex-start !important;
            align-items: center !important;
            width: 100% !important;
        }
        div[class*="st-key-btn_limpiar_batch"] button,
        div[class*="st-key-btn_descargar_csv_batch"] button {
            width: 42px !important;
            height: 42px !important;
            min-width: 42px !important;
            max-width: 42px !important;
            min-height: 42px !important;
            max-height: 42px !important;
            padding: 0 !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            border-radius: 10px !important;
            border: 1.5px solid #cbd5e1 !important;
            background: #ffffff !important;
            color: #475569 !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        div[class*="st-key-btn_limpiar_batch"] button:hover {
            border-color: #ef4444 !important;
            background: #fef2f2 !important;
            color: #dc2626 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 8px rgba(220, 38, 38, 0.12) !important;
        }
        div[class*="st-key-btn_descargar_csv_batch"] button:hover {
            border-color: #002a69 !important;
            background: #f0f4fd !important;
            color: #002a69 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 8px rgba(0, 42, 105, 0.12) !important;
        }
        div[class*="st-key-btn_limpiar_batch"] button span,
        div[class*="st-key-btn_descargar_csv_batch"] button span {
            font-size: 1.25rem !important;
            line-height: 1 !important;
        }

        /* Espaciado calibrado entre Datos de prueba y Procesar ahora (+10px) */
        div[data-testid="stColumn"]:has([class*="st-key-btn_cargar_ejemplo_batch"]) > div[data-testid="stVerticalBlock"] {
            gap: 0.5rem !important;
        }
        div[class*="st-key-btn_procesar_ahora_batch"] {
            margin-top: 10px !important;
        }

        /* Barra de Descarga Multi-Formato en Lote (CSV, XLSX, PDF) */
        .download-action-bar {
            display: inline-flex;
            align-items: center;
            gap: 1rem;
            margin-top: 1.15rem;
            margin-bottom: 1.5rem;
            padding: 0.65rem 1.15rem;
            background: #ffffff;
            border: 1.5px solid #e2e8f0;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        }
        .download-action-label {
            font-size: 0.88rem;
            font-weight: 700;
            color: #0f172a;
            letter-spacing: -0.01em;
            margin-right: 0.2rem;
        }
        .download-icon-group {
            display: flex;
            align-items: center;
            gap: 0.65rem;
        }
        .download-icon-btn {
            position: relative;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 44px;
            height: 44px;
            background: #f8fafc;
            border: 1.5px solid #cbd5e1;
            border-radius: 10px;
            cursor: pointer;
            text-decoration: none !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .download-icon-btn:hover {
            background: #ffffff;
            border-color: #002a69;
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(0, 42, 105, 0.12);
        }
        .download-icon-btn:active {
            transform: translateY(0);
        }
        /* Tooltip flotante al pasar el cursor */
        .download-icon-btn .btn-tooltip {
            visibility: hidden;
            opacity: 0;
            position: absolute;
            bottom: calc(100% + 8px);
            left: 50%;
            transform: translateX(-50%);
            background-color: #0f172a;
            color: #ffffff;
            font-size: 0.72rem;
            font-weight: 600;
            white-space: nowrap;
            padding: 0.35rem 0.65rem;
            border-radius: 6px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
            pointer-events: none;
            transition: opacity 0.2s ease, transform 0.2s ease;
            z-index: 1000;
        }
        .download-icon-btn .btn-tooltip::after {
            content: '';
            position: absolute;
            top: 100%;
            left: 50%;
            transform: translateX(-50%);
            border-width: 5px;
            border-style: solid;
            border-color: #0f172a transparent transparent transparent;
        }
        .download-icon-btn:hover .btn-tooltip {
            visibility: visible;
            opacity: 1;
            transform: translateX(-50%) translateY(-2px);
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

        /* Sinóptico Industrial SCADA (Paso 2) */
        .synoptic-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
            margin-top: 0.75rem;
            margin-bottom: 1.25rem;
        }
        .synoptic-card, .synoptic-cell {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1.15rem 1.2rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-sizing: border-box;
            transition: all 0.2s ease;
            position: relative;
            text-align: left;
        }
        .synoptic-card:hover, .synoptic-cell:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.07);
        }
        .synoptic-card-fault, .synoptic-cell-fault {
            border-color: #fecaca !important;
            border-top: 3px solid #ef4444 !important;
            background: #ffffff !important;
            box-shadow: 0 1px 4px rgba(239, 68, 68, 0.06);
        }
        .synoptic-card-fault:hover, .synoptic-cell-fault:hover {
            border-color: #fca5a5 !important;
            box-shadow: 0 4px 14px rgba(239, 68, 68, 0.12) !important;
        }
        .synoptic-card-nominal, .synoptic-cell-nominal {
            border-color: #e2e8f0 !important;
            border-top: 3px solid #10b981 !important;
            background: #ffffff !important;
        }
        .synoptic-card-nominal:hover, .synoptic-cell-nominal:hover {
            border-color: #cbd5e1 !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.07) !important;
        }
        .synoptic-top-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 0.65rem;
        }
        .synoptic-title-wrap {
            display: flex;
            align-items: center;
            gap: 0.45rem;
        }
        .synoptic-phase-dot {
            width: 8px;
            height: 8px;
            border-radius: 9999px;
            flex-shrink: 0;
        }
        .synoptic-title {
            font-size: 0.74rem;
            font-weight: 700;
            color: #1e293b;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        .synoptic-status-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            padding: 0.22rem 0.65rem;
            border-radius: 9999px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            width: fit-content;
        }
        .synoptic-status-nominal {
            background: #f0fdf4;
            color: #15803d;
            border: 1px solid #bbf7d0;
        }
        .synoptic-status-fault {
            background: #fef2f2;
            color: #b91c1c;
            border: 1px solid #fecaca;
        }
        .synoptic-status-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            display: inline-block;
            flex-shrink: 0;
        }
        .dot-nominal {
            background-color: #16a34a;
        }
        .dot-fault {
            background-color: #dc2626;
            box-shadow: 0 0 0 2px rgba(220, 38, 38, 0.25);
            animation: synoptic-pulse 2s infinite;
        }
        @keyframes synoptic-pulse {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.4); }
            70% { transform: scale(1); box-shadow: 0 0 0 4px rgba(220, 38, 38, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(220, 38, 38, 0); }
        }
        .synoptic-telemetry-box {
            background: #f8fafc;
            border: 1px solid #f1f5f9;
            border-radius: 8px;
            padding: 0.5rem 0.75rem;
            display: flex;
            flex-direction: column;
            gap: 0.35rem;
            margin-top: 0.75rem;
        }
        .synoptic-telemetry-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .synoptic-telemetry-label {
            font-size: 0.71rem;
            font-weight: 600;
            color: #64748b;
        }
        .synoptic-telemetry-val {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.82rem;
            font-weight: 700;
            color: #0f172a;
        }
        .synoptic-telemetry-val.val-fault {
            color: #dc2626;
            font-weight: 800;
        }
        .synoptic-telemetry-unit {
            font-size: 0.68rem;
            font-weight: 500;
            color: #64748b;
            margin-left: 2px;
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
            line-height: 1.8 !important;
            text-decoration: none !important;
            display: inline-block !important;
            width: fit-content !important;
            cursor: pointer !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        .footer-text-item:hover {
            color: #ffffff !important;
            text-decoration: underline !important;
            text-shadow: 0 0 10px rgba(255, 255, 255, 0.75), 0 2px 6px rgba(0, 0, 0, 0.5) !important;
        }
        .footer-author-group {
            display: flex !important;
            flex-direction: column !important;
            gap: 0.35rem !important;
            margin-bottom: 0.85rem !important;
        }
        .footer-author-name-link {
            display: inline-flex !important;
            align-items: center !important;
            gap: 0.65rem !important;
            color: #ffffff !important;
            font-size: 0.88rem !important;
            font-weight: 600 !important;
            text-decoration: none !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            cursor: pointer !important;
            width: fit-content !important;
        }
        .footer-author-name-link:hover {
            text-decoration: underline !important;
            color: #ffffff !important;
            text-shadow: 0 0 10px rgba(255, 255, 255, 0.75), 0 2px 6px rgba(0, 0, 0, 0.5) !important;
        }
        .footer-author-mail-link {
            display: inline-flex !important;
            align-items: center !important;
            gap: 0.65rem !important;
            color: #cbd5e1 !important;
            font-size: 0.82rem !important;
            font-weight: 400 !important;
            text-decoration: none !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            cursor: pointer !important;
            width: fit-content !important;
        }
        .footer-author-mail-link:hover {
            text-decoration: underline !important;
            color: #ffffff !important;
            text-shadow: 0 0 10px rgba(255, 255, 255, 0.7), 0 2px 6px rgba(0, 0, 0, 0.5) !important;
        }
        .footer-contact-item {
            display: flex !important;
            align-items: center !important;
            gap: 0.85rem !important;
            margin-bottom: 0.85rem !important;
        }
        .footer-contact-icon {
            width: 28px !important;
            height: 28px !important;
            border-radius: 6px !important;
            background: rgba(255, 255, 255, 0.14) !important;
            border: 1px solid rgba(255, 255, 255, 0.28) !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            color: #ffffff !important;
            flex-shrink: 0 !important;
            transition: all 0.2s ease !important;
        }
        .footer-author-name-link:hover .footer-contact-icon,
        .footer-author-mail-link:hover .footer-contact-icon {
            background: rgba(255, 255, 255, 0.28) !important;
            border-color: rgba(255, 255, 255, 0.55) !important;
            box-shadow: 0 0 8px rgba(255, 255, 255, 0.4) !important;
            color: #ffffff !important;
        }
        .footer-contact-text {
            color: inherit !important;
            font-size: 0.82rem !important;
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

            /* Dropzone en móvil: centrado absoluto de icono y texto '200MB per file...' */
            section[data-testid="stFileUploaderDropzone"] {
                text-align: center !important;
                align-items: center !important;
                justify-content: center !important;
                padding: 1.25rem 1rem !important;
            }
            section[data-testid="stFileUploaderDropzone"] small {
                display: block !important;
                width: 100% !important;
                text-align: center !important;
                margin-left: auto !important;
                margin-right: auto !important;
            }
            section[data-testid="stFileUploaderDropzone"] span {
                text-align: center !important;
            }
            section[data-testid="stFileUploaderDropzone"] div {
                text-align: center !important;
                align-items: center !important;
                justify-content: center !important;
                width: 100% !important;
            }

            /* Barra de descarga en lote: ocupa el mismo ancho completo que la tabla en móvil */
            .download-action-bar {
                display: flex !important;
                width: 100% !important;
                max-width: 100% !important;
                box-sizing: border-box !important;
                justify-content: space-between !important;
                align-items: center !important;
                padding: 0.85rem 1.15rem !important;
            }

            /* Fila de acciones por lote en móvil: Datos de prueba e iconos justo al lado */
            div[data-testid="stHorizontalBlock"]:has([class*="st-key-btn_cargar_ejemplo_batch"]) {
                display: flex !important;
                flex-direction: row !important;
                align-items: flex-start !important;
                justify-content: flex-start !important;
                gap: 0.5rem !important;
            }
            div[data-testid="stColumn"]:has([class*="st-key-btn_cargar_ejemplo_batch"]) {
                flex: 0 1 auto !important;
                min-width: 140px !important;
            }
            div[data-testid="stColumn"]:has([class*="st-key-btn_limpiar_batch"]),
            div[data-testid="stColumn"]:has([class*="st-key-btn_descargar_csv_batch"]) {
                flex: 0 0 42px !important;
                width: 42px !important;
                min-width: 42px !important;
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
            .download-action-bar {
                flex-direction: column !important;
                align-items: stretch !important;
                gap: 0.75rem !important;
                text-align: center !important;
            }
            .download-action-label {
                text-align: center !important;
                margin-right: 0 !important;
            }
            .download-icon-group {
                justify-content: center !important;
            }
            div[class*="st-key-btn_limpiar_batch"] button,
            div[class*="st-key-btn_descargar_csv_batch"] button {
                width: 38px !important;
                height: 38px !important;
                min-width: 38px !important;
                max-width: 38px !important;
                min-height: 38px !important;
                max-height: 38px !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    if tema_oscuro:
        st.markdown(
            """
            <style>
            /* ==============================================================================
               TEMA OSCURO INDUSTRIAL DE ALTO CONTRASTE (DARK MODE)
               ============================================================================== */
            html, body, .stApp, div[data-testid="stAppViewContainer"] {
                background-color: #0b0f19 !important;
                color: #e2e8f0 !important;
            }

            /* Encabezados y Tipografía en Modo Oscuro */
            h1, h2, h3, h4, h5,
            [data-testid="stMarkdownContainer"] h1,
            [data-testid="stMarkdownContainer"] h2,
            [data-testid="stMarkdownContainer"] h3,
            [data-testid="stMarkdownContainer"] h4,
            [data-testid="stMarkdownContainer"] h5 {
                color: #f8fafc !important;
            }

            p, span, [data-testid="stMarkdownContainer"] p {
                color: #cbd5e1;
            }

            .module-section-title {
                color: #94a3b8 !important;
            }

            /* Top Header Sticky Bar */
            .top-navbar-strip {
                background: #111827 !important;
                border-bottom: 1px solid #1e293b !important;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.45) !important;
            }

            /* Tarjetas de Módulos (Selector 1, 2, 3) */
            .module-card-v3 {
                background: #131b2e !important;
                border: 1px solid #1e293b !important;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
            }
            .module-card-v3:hover {
                background: #17233d !important;
                border-color: #3b82f6 !important;
                box-shadow: 0 4px 14px rgba(59, 130, 246, 0.2) !important;
            }
            .module-card-v3-active {
                border: 2px solid #3b82f6 !important;
                background: #17233d !important;
                box-shadow: 0 4px 18px rgba(59, 130, 246, 0.28) !important;
            }
            .module-title-v3 {
                color: #e2e8f0 !important;
            }
            .module-title-v3-active {
                color: #ffffff !important;
            }
            .module-desc-v3 {
                color: #94a3b8 !important;
            }
            .module-icon-v3 {
                background: #1e293b !important;
                border: 1px solid #334155 !important;
                color: #94a3b8 !important;
            }
            .module-icon-v3-active {
                background: rgba(59, 130, 246, 0.2) !important;
                border: 1px solid #3b82f6 !important;
                color: #60a5fa !important;
            }
            .module-foot-v3 {
                color: #64748b !important;
            }
            .module-foot-v3-active {
                color: #60a5fa !important;
            }

            /* Tarjetas Principales del Sistema */
            .factor-card,
            .telemetry-main-card,
            .xai-chart-card,
            .batch-upload-card,
            .audit-main-card,
            .kpi-card-v2,
            .info-page-card,
            .info-glass-card,
            .privacy-card,
            .terms-card,
            .not-found-card {
                background: #131b2e !important;
                border: 1px solid #1e293b !important;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
            }

            .kpi-card-v2:hover {
                border-color: #3b82f6 !important;
            }
            .kpi-label {
                color: #94a3b8 !important;
            }
            .kpi-value {
                color: #ffffff !important;
            }
            .kpi-footer-text {
                color: #a7f3d0 !important;
            }

            /* Sinóptico Eléctrico / SLD */
            .synoptic-card-nominal, .synoptic-cell-nominal {
                background: rgba(6, 78, 59, 0.35) !important;
                border: 1px solid #059669 !important;
            }
            .synoptic-card-nominal .synoptic-title {
                color: #34d399 !important;
            }
            .synoptic-card-fault, .synoptic-cell-fault {
                background: rgba(153, 27, 27, 0.35) !important;
                border: 1px solid #dc2626 !important;
            }
            .synoptic-card-fault .synoptic-title {
                color: #f87171 !important;
            }
            .synoptic-telemetry-box {
                background: #0b0f19 !important;
                border: 1px solid #1e293b !important;
            }
            .synoptic-telemetry-label {
                color: #94a3b8 !important;
            }
            .synoptic-telemetry-val {
                color: #f1f5f9 !important;
            }
            .synoptic-telemetry-val.val-fault {
                color: #f87171 !important;
            }
            .synoptic-telemetry-unit {
                color: #64748b !important;
            }
            .synoptic-status-nominal {
                background: rgba(16, 185, 129, 0.2) !important;
                color: #34d399 !important;
                border: 1px solid rgba(16, 185, 129, 0.4) !important;
            }
            .synoptic-status-fault {
                background: rgba(239, 68, 68, 0.2) !important;
                color: #f87171 !important;
                border: 1px solid rgba(239, 68, 68, 0.4) !important;
            }

            /* Inputs y Controles de Formulario */
            div[data-baseweb="input"] {
                background-color: #1e293b !important;
                border-color: #334155 !important;
            }
            div[data-baseweb="input"]:focus-within {
                border-color: #3b82f6 !important;
                box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3) !important;
            }
            input, [data-testid="stNumberInput"] input {
                background-color: #1e293b !important;
                color: #ffffff !important;
            }
            label[data-testid="stWidgetLabel"] p {
                color: #e2e8f0 !important;
                font-weight: 500 !important;
            }
            div[data-testid="stNumberInput"] button {
                background-color: #1e293b !important;
                color: #94a3b8 !important;
                border-color: #334155 !important;
            }
            div[data-testid="stNumberInput"] button:hover {
                background-color: #334155 !important;
                color: #ffffff !important;
            }
            div[data-testid="stFileUploader"] section {
                background-color: #131b2e !important;
                border-color: #334155 !important;
            }
            div[data-testid="stFileUploader"] span, div[data-testid="stFileUploader"] small {
                color: #94a3b8 !important;
            }

            /* Botones en Modo Oscuro */
            button[kind="secondary"] {
                background-color: #1e293b !important;
                color: #f1f5f9 !important;
                border: 1px solid #334155 !important;
            }
            button[kind="secondary"]:hover {
                background-color: #334155 !important;
                color: #ffffff !important;
                border-color: #475569 !important;
            }
            button[kind="primary"] {
                background-color: #2563eb !important;
                color: #ffffff !important;
            }
            button[kind="primary"]:hover {
                background-color: #1d4ed8 !important;
            }

            /* Banner de Diagnóstico */
            .diagnosis-banner-normal {
                background: rgba(6, 78, 59, 0.35) !important;
                border-color: #059669 !important;
            }
            .diagnosis-banner-fault {
                background: rgba(153, 27, 27, 0.35) !important;
                border-color: #dc2626 !important;
            }
            .step-pill-badge {
                background: #1e293b !important;
                color: #60a5fa !important;
                border: 1px solid #334155 !important;
            }
            hr {
                border-top-color: #1e293b !important;
            }

            /* Gráficos de Telemetría y Oscilogramas */
            div[data-testid="stVegaLiteChart"] {
                background: #131b2e !important;
                border: 1px solid #1e293b !important;
                border-radius: 10px !important;
                padding: 8px !important;
            }

            /* Tablas y Resultados en Lote */
            [data-testid="stDataFrame"] {
                background: #131b2e !important;
                border-color: #1e293b !important;
            }
            div[data-testid="stTable"] table {
                background-color: #131b2e !important;
                color: #e2e8f0 !important;
                border-color: #1e293b !important;
            }
            div[data-testid="stTable"] th {
                background-color: #1e293b !important;
                color: #f8fafc !important;
                border-color: #334155 !important;
            }
            div[data-testid="stTable"] td {
                border-color: #1e293b !important;
                color: #cbd5e1 !important;
            }

            /* Barra de Descargas */
            .download-action-bar {
                background: #131b2e !important;
                border-color: #1e293b !important;
            }
            .download-action-label {
                color: #94a3b8 !important;
            }

            /* Footer en Modo Oscuro */
            .custom-footer-strip {
                background: #111827 !important;
                border-top: 1px solid #1f2937 !important;
                color: #94a3b8 !important;
            }
            .footer-heading {
                color: #ffffff !important;
            }
            .footer-brand-desc, .footer-copy, .footer-partner-label {
                color: #94a3b8 !important;
            }
            .footer-link {
                color: #60a5fa !important;
            }
            .footer-link:hover {
                color: #93c5fd !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )



