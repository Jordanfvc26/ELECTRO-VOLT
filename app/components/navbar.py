"""Componente selector de módulos operativos."""

from __future__ import annotations

import streamlit as st
from app.utils import render_html

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

