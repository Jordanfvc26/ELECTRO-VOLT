"""Módulo de Vista: Diagnóstico en Tiempo Real"""

from __future__ import annotations

from pathlib import Path
import sys
import time

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

raiz = Path(__file__).resolve().parents[2]
if str(raiz) not in sys.path:
    sys.path.insert(0, str(raiz))

from src.evaluate import normalizar_shap
from src.model import predecir_falla, mapear_shap_a_canales_fisicos
from src.utils import (
    COLUMNAS,
    ORDEN_CLASES,
    RANGO_CORRIENTE,
    RANGO_VOLTAJE,
    UMBRAL_CONFIANZA_MINIMA,
    UMBRAL_RETORNO_TIERRA_A,
    determinar_estados_fases,
    validar_rango_senales,
)
from app.utils import cargar_recursos_modelo, cargar_ejemplos_prueba, render_html

def pagina_diagnostico_tiempo_real():
    paquete, explicador = cargar_recursos_modelo()
    df_ejemplos = cargar_ejemplos_prueba()
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
                    "Tensión Va (p.u.)",
                    min_value=-3.0,
                    max_value=3.0,
                    step=0.0001,
                    format="%.4f" if st.session_state.widget_va is not None else None,
                    key="widget_va",
                    help="Tensión fase-neutro normalizada en base nominal 230/√3 kV.",
                )

                st.number_input(
                    "Corriente Ia (A)",
                    min_value=-10000.0,
                    max_value=10000.0,
                    step=0.01,
                    format="%.2f" if st.session_state.widget_ia is not None else None,
                    key="widget_ia",
                    help="Corriente instantánea registrada por el TC.",
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
                    "Tensión Vb (p.u.)",
                    min_value=-3.0,
                    max_value=3.0,
                    step=0.0001,
                    format="%.4f" if st.session_state.widget_vb is not None else None,
                    key="widget_vb",
                    help="Tensión nominal desfasada -120° estándar IEEE.",
                )

                st.number_input(
                    "Corriente Ib (A)",
                    min_value=-10000.0,
                    max_value=10000.0,
                    step=0.01,
                    format="%.2f" if st.session_state.widget_ib is not None else None,
                    key="widget_ib",
                    help="Corriente instantánea registrada por el TC.",
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
                    "Tensión Vc (p.u.)",
                    min_value=-3.0,
                    max_value=3.0,
                    step=0.0001,
                    format="%.4f" if st.session_state.widget_vc is not None else None,
                    key="widget_vc",
                    help="Tensión nominal desfasada +120° estándar IEEE.",
                )

                st.number_input(
                    "Corriente Ic (A)",
                    min_value=-10000.0,
                    max_value=10000.0,
                    step=0.01,
                    format="%.2f" if st.session_state.widget_ic is not None else None,
                    key="widget_ic",
                    help="Corriente instantánea registrada por el TC.",
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

    # Iconos SVG y estilos SCADA para tarjetas sinópticas
    icon_nominal_svg = """<svg style="width: 17px; height: 17px;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path></svg>"""
    icon_fault_svg = """<svg style="width: 17px; height: 17px;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>"""
    icon_ground_nominal_svg = """<svg style="width: 17px; height: 17px;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v9m-7 0h14m-11 4h8m-5 4h2"></path></svg>"""
    icon_ground_fault_svg = """<svg style="width: 17px; height: 17px;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v9m-7 0h14m-11 4h8m-5 4h2"></path></svg>"""

    badge_nom_style = "background: rgba(5, 150, 105, 0.08); border: 1px solid rgba(5, 150, 105, 0.22); color: #059669;"
    badge_flt_style = "background: rgba(220, 38, 38, 0.08); border: 1px solid rgba(220, 38, 38, 0.25); color: #dc2626;"
    badge_g_nom_style = "background: rgba(100, 116, 139, 0.08); border: 1px solid rgba(100, 116, 139, 0.22); color: #475569;"

    render_html(
        f"""
        <div class="synoptic-grid">
            <!-- CONDUCTOR FASE A -->
            <div class="synoptic-card {'synoptic-card-fault' if falla_a else 'synoptic-card-nominal'}">
                <div class="synoptic-top-row">
                    <div class="synoptic-title-wrap">
                        <span class="synoptic-phase-dot" style="background: #d97706;"></span>
                        <span class="synoptic-title">CONDUCTOR FASE A</span>
                    </div>
                    <span class="kpi-icon-badge" style="{badge_flt_style if falla_a else badge_nom_style}">
                        {icon_fault_svg if falla_a else icon_nominal_svg}
                    </span>
                </div>
                <div>
                    <span class="synoptic-status-pill {'synoptic-status-fault' if falla_a else 'synoptic-status-nominal'}">
                        <span class="synoptic-status-dot {'dot-fault' if falla_a else 'dot-nominal'}"></span>
                        {'PERTURBACIÓN DETECTADA' if falla_a else 'ESTADO NOMINAL'}
                    </span>
                </div>
                <div class="synoptic-telemetry-box">
                    <div class="synoptic-telemetry-row">
                        <span class="synoptic-telemetry-label">Tensión (Va)</span>
                        <span class="synoptic-telemetry-val">{val_va:.3f} <span class="synoptic-telemetry-unit">p.u.</span></span>
                    </div>
                    <div class="synoptic-telemetry-row">
                        <span class="synoptic-telemetry-label">Corriente (Ia)</span>
                        <span class="synoptic-telemetry-val {'val-fault' if falla_a else ''}">{val_ia:.1f} <span class="synoptic-telemetry-unit">A</span></span>
                    </div>
                </div>
            </div>

            <!-- CONDUCTOR FASE B -->
            <div class="synoptic-card {'synoptic-card-fault' if falla_b else 'synoptic-card-nominal'}">
                <div class="synoptic-top-row">
                    <div class="synoptic-title-wrap">
                        <span class="synoptic-phase-dot" style="background: #002a69;"></span>
                        <span class="synoptic-title">CONDUCTOR FASE B</span>
                    </div>
                    <span class="kpi-icon-badge" style="{badge_flt_style if falla_b else badge_nom_style}">
                        {icon_fault_svg if falla_b else icon_nominal_svg}
                    </span>
                </div>
                <div>
                    <span class="synoptic-status-pill {'synoptic-status-fault' if falla_b else 'synoptic-status-nominal'}">
                        <span class="synoptic-status-dot {'dot-fault' if falla_b else 'dot-nominal'}"></span>
                        {'PERTURBACIÓN DETECTADA' if falla_b else 'ESTADO NOMINAL'}
                    </span>
                </div>
                <div class="synoptic-telemetry-box">
                    <div class="synoptic-telemetry-row">
                        <span class="synoptic-telemetry-label">Tensión (Vb)</span>
                        <span class="synoptic-telemetry-val">{val_vb:.3f} <span class="synoptic-telemetry-unit">p.u.</span></span>
                    </div>
                    <div class="synoptic-telemetry-row">
                        <span class="synoptic-telemetry-label">Corriente (Ib)</span>
                        <span class="synoptic-telemetry-val {'val-fault' if falla_b else ''}">{val_ib:.1f} <span class="synoptic-telemetry-unit">A</span></span>
                    </div>
                </div>
            </div>

            <!-- CONDUCTOR FASE C -->
            <div class="synoptic-card {'synoptic-card-fault' if falla_c else 'synoptic-card-nominal'}">
                <div class="synoptic-top-row">
                    <div class="synoptic-title-wrap">
                        <span class="synoptic-phase-dot" style="background: #558750;"></span>
                        <span class="synoptic-title">CONDUCTOR FASE C</span>
                    </div>
                    <span class="kpi-icon-badge" style="{badge_flt_style if falla_c else badge_nom_style}">
                        {icon_fault_svg if falla_c else icon_nominal_svg}
                    </span>
                </div>
                <div>
                    <span class="synoptic-status-pill {'synoptic-status-fault' if falla_c else 'synoptic-status-nominal'}">
                        <span class="synoptic-status-dot {'dot-fault' if falla_c else 'dot-nominal'}"></span>
                        {'PERTURBACIÓN DETECTADA' if falla_c else 'ESTADO NOMINAL'}
                    </span>
                </div>
                <div class="synoptic-telemetry-box">
                    <div class="synoptic-telemetry-row">
                        <span class="synoptic-telemetry-label">Tensión (Vc)</span>
                        <span class="synoptic-telemetry-val">{val_vc:.3f} <span class="synoptic-telemetry-unit">p.u.</span></span>
                    </div>
                    <div class="synoptic-telemetry-row">
                        <span class="synoptic-telemetry-label">Corriente (Ic)</span>
                        <span class="synoptic-telemetry-val {'val-fault' if falla_c else ''}">{val_ic:.1f} <span class="synoptic-telemetry-unit">A</span></span>
                    </div>
                </div>
            </div>

            <!-- NEUTRO / TIERRA (G) -->
            <div class="synoptic-card {'synoptic-card-fault' if falla_g else 'synoptic-card-nominal'}">
                <div class="synoptic-top-row">
                    <div class="synoptic-title-wrap">
                        <span class="synoptic-phase-dot" style="background: #64748b;"></span>
                        <span class="synoptic-title">NEUTRO / TIERRA (G)</span>
                    </div>
                    <span class="kpi-icon-badge" style="{badge_flt_style if falla_g else badge_g_nom_style}">
                        {icon_ground_fault_svg if falla_g else icon_ground_nominal_svg}
                    </span>
                </div>
                <div>
                    <span class="synoptic-status-pill {'synoptic-status-fault' if falla_g else 'synoptic-status-nominal'}">
                        <span class="synoptic-status-dot {'dot-fault' if falla_g else 'dot-nominal'}"></span>
                        {'RETORNO POR TIERRA' if falla_g else 'AISLADO (SIN RETORNO)'}
                    </span>
                </div>
                <div class="synoptic-telemetry-box">
                    <div class="synoptic-telemetry-row">
                        <span class="synoptic-telemetry-label">Corriente Residual (In)</span>
                        <span class="synoptic-telemetry-val {'val-fault' if falla_g else ''}">{corriente_n:.1f} <span class="synoptic-telemetry-unit">A</span></span>
                    </div>
                    <div class="synoptic-telemetry-row">
                        <span class="synoptic-telemetry-label">Flujo a Tierra</span>
                        <span class="synoptic-telemetry-val" style="font-size: 0.72rem; color: {'#dc2626' if falla_g else '#059669'}; font-weight: 700;">
                            {'ACTIVO (FALLA)' if falla_g else 'NULO / BALANCE'}
                        </span>
                    </div>
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
                Diagnóstico del sistema y protocolo operativo
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
                Síntesis física explicable para el ingeniero de subestación
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


