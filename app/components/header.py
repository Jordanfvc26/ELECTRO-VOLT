"""Componente de barra de navegación superior (Header) con selector de modo claro/oscuro."""

from __future__ import annotations

import streamlit as st
from app.utils import obtener_logo_base64, render_html


def cb_alternar_tema():
    """Alterna el modo claro y oscuro del sistema en session_state y query_params."""
    st.session_state.tema_oscuro = not st.session_state.get("tema_oscuro", False)
    st.query_params["theme"] = "dark" if st.session_state.tema_oscuro else "light"


def obtener_url_toggle_tema(proximo_tema: str) -> str:
    """Construye la URL relativa para alternar el tema preservando los parámetros activos."""
    params: dict[str, str] = {}
    for k, v in st.query_params.items():
        params[k] = v

    if "modulo" not in params:
        mod = st.session_state.get("modulo_activo")
        if mod and mod in ["diagnostic-real-time", "diagnostic-from-file", "info-audit-model"]:
            params["modulo"] = mod

    params["theme"] = proximo_tema
    query_str = "&".join(f"{k}={v}" for k, v in params.items())
    return f"?{query_str}"


def render_header():
    """Renderiza el TopHeader sticky que ocupa el 100% del ancho con el logotipo oficial y el conmutador de tema."""
    # Sincronización proactiva desde query_params
    tema_param = st.query_params.get("theme")
    if tema_param == "dark":
        st.session_state.tema_oscuro = True
    elif tema_param == "light":
        st.session_state.tema_oscuro = False
    elif "tema_oscuro" not in st.session_state:
        st.session_state.tema_oscuro = False

    tema_oscuro = bool(st.session_state.get("tema_oscuro", False))
    proximo_tema = "light" if tema_oscuro else "dark"
    url_toggle = obtener_url_toggle_tema(proximo_tema)

    logo_b64 = obtener_logo_base64()
    if logo_b64:
        logo_html = f'<img src="data:image/png;base64,{logo_b64}" alt="ElectroVOLT" style="height: 38px; width: auto; object-fit: contain; display: block;" />'
    else:
        color_texto = "#ffffff" if tema_oscuro else "#002a69"
        logo_html = f'<span style="font-weight: 800; font-size: 1.2rem; color: {color_texto};">Electro<span style="color: #f59e0b;">VOLT</span></span>'

    # Icono del tema: Sol en modo oscuro (para pasar a claro) y Luna en modo claro (para pasar a oscuro)
    if tema_oscuro:
        icono_tema_svg = """
        <svg style="width: 19px; height: 19px; color: #fbbf24;" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path>
        </svg>
        """
        tooltip = "Cambiar a Modo Claro"
        clase_toggle = "header-theme-toggle header-theme-toggle-dark"
    else:
        icono_tema_svg = """
        <svg style="width: 18px; height: 18px; color: #334155;" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path>
        </svg>
        """
        tooltip = "Cambiar a Modo Oscuro"
        clase_toggle = "header-theme-toggle header-theme-toggle-light"

    render_html(
        f"""
        <div class="top-navbar-strip">
            <div style="display: flex; align-items: center;">
                <a href="/" target="_self" style="text-decoration: none; display: flex; align-items: center; cursor: pointer;">
                    {logo_html}
                </a>
            </div>
            <a href="{url_toggle}" target="_self" class="{clase_toggle}" title="{tooltip}" style="text-decoration: none;">
                {icono_tema_svg}
            </a>
        </div>
        """
    )
