"""Módulo de Vista: Procesamiento Masivo por Lote"""

from __future__ import annotations

from pathlib import Path
import sys
import time

import numpy as np
import pandas as pd
import streamlit as st

raiz = Path(__file__).resolve().parents[2]
if str(raiz) not in sys.path:
    sys.path.insert(0, str(raiz))

from src.model import predecir_falla
from src.utils import (
    COLUMNAS,
    ORDEN_CLASES,
    UMBRAL_CONFIANZA_MINIMA,
    UMBRAL_RETORNO_TIERRA_A,
    determinar_estados_fases,
    obtener_ruta_datos_procesados,
    validar_rango_senales,
)
from app.utils import cargar_recursos_modelo, cargar_ejemplos_prueba, render_html
from app.exports import render_barra_descargas

def pagina_procesamiento_lote():
    paquete, _ = cargar_recursos_modelo()
    df_ejemplos = cargar_ejemplos_prueba()
    # 1. Resolver el origen de datos (Archivo subido por usuario o Datos de prueba)
    if "uploader_key_version" not in st.session_state:
        st.session_state["uploader_key_version"] = 0
    uploader_key = f"uploader_csv_lote_{st.session_state['uploader_key_version']}"

    archivo_csv_state = st.session_state.get(uploader_key)
    usar_ejemplo = st.session_state.get("usar_ejemplo_batch", False)

    df_lote = None
    nombre_archivo = None
    error_carga = None

    if archivo_csv_state is not None:
        try:
            archivo_csv_state.seek(0)
            df_lote = pd.read_csv(archivo_csv_state)
            nombre_archivo = archivo_csv_state.name
            st.session_state["usar_ejemplo_batch"] = False
        except Exception as e:
            error_carga = f"Error al leer el archivo CSV cargado: {e}"
    elif usar_ejemplo:
        if df_ejemplos is not None:
            df_lote = df_ejemplos.copy()
            nombre_archivo = "ejemplos_prueba.csv"
        else:
            ruta_ej = obtener_ruta_datos_procesados("ejemplos_prueba.csv")
            if ruta_ej.exists():
                df_lote = pd.read_csv(ruta_ej)
                nombre_archivo = "ejemplos_prueba.csv"

    # Validar si las columnas obligatorias están presentes
    columnas_validas = False
    faltantes = []
    if df_lote is not None:
        faltantes = [c for c in COLUMNAS if c not in df_lote.columns]
        if not faltantes:
            columnas_validas = True

    ejecutar_lote = False

    with st.container():
        render_html('<div class="batch-upload-card"></div>')
        col_izq, col_der = st.columns([1.18, 1.0], gap="large", vertical_alignment="center")
        with col_izq:
            render_html(
                """
                <div style="display: flex; align-items: center; gap: 0.65rem; margin-bottom: 0.45rem;">
                    <span class="step-pill-badge" style="background: #eef2fb; color: #002a69; border: 1px solid #c5d2f3;">
                        <svg style="width: 15px; height: 15px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2 1 3 3 3h10c2 0 3-1 3-3V7c0-2-1-3-3-3H7C5 4 4 5 4 7zm0 5h16M9 4v16"></path>
                        </svg>
                    </span>
                    <span style="font-size: 1.08rem; font-weight: 700; color: #0f172a;">Clasificación Masiva de Telemetría en Lote (Batch)</span>
                </div>
                <p style="color: #64748b; font-size: 0.83rem; margin-top: 0; margin-bottom: 0.65rem; line-height: 1.48;">
                    Cargue un archivo CSV con las 6 señales trifásica (<code>Va, Vb, Vc, Ia, Ib, Ic</code>) registradas durante eventos de falla para procesar miles de lecturas en milisegundos.
                </p>
                <br/>
                """
            )
            col_b_izq, col_ico1, col_ico2, col_resto = st.columns([1.4, 0.28, 0.28, 0.85], gap="small", vertical_alignment="top")
            with col_b_izq:
                if st.button("Datos de prueba", key="btn_cargar_ejemplo_batch", use_container_width=True):
                    st.session_state["usar_ejemplo_batch"] = True
                    st.rerun()

                # Botón "Procesar ahora": ajustado exactamente al ancho del botón "Datos de prueba" y pegado verticalmente
                if df_lote is not None and columnas_validas:
                    if st.button("Procesar ahora", type="primary", use_container_width=True, key="btn_procesar_ahora_batch"):
                        ejecutar_lote = True

            if df_lote is not None:
                # Botones de icono justo al lado de Datos de prueba
                with col_ico1:
                    if st.button("", icon=":material/delete:", help="Limpiar datos", key="btn_limpiar_batch"):
                        st.session_state["uploader_key_version"] = st.session_state.get("uploader_key_version", 0) + 1
                        st.session_state["usar_ejemplo_batch"] = False
                        st.session_state["resultado_lote"] = None
                        st.rerun()
                with col_ico2:
                    csv_datos_lote = df_lote.to_csv(index=False)
                    st.download_button(
                        "",
                        data=csv_datos_lote,
                        file_name=f"{nombre_archivo or 'telemetria_lote.csv'}",
                        mime="text/csv",
                        icon=":material/download:",
                        help="Descargar datos en .csv",
                        key="btn_descargar_csv_batch",
                    )

        with col_der:
            archivo_csv = st.file_uploader(
                "Arrastre o seleccione su archivo CSV",
                type=["csv"],
                label_visibility="collapsed",
                key=uploader_key,
            )
            if archivo_csv is not None and archivo_csv_state is None:
                st.rerun()

    # Banner de validación y estado (con icono de check si es éxito, o icono de error si no se pudo cargar)
    if error_carga:
        render_html(
            f"""
            <div class="batch-status-banner batch-status-error">
                <span class="batch-status-icon">
                    <svg style="width: 13px; height: 13px;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </span>
                <span>{error_carga}</span>
            </div>
            """
        )
    elif df_lote is not None and faltantes:
        render_html(
            f"""
            <div class="batch-status-banner batch-status-error">
                <span class="batch-status-icon">
                    <svg style="width: 13px; height: 13px;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </span>
                <span>El archivo cargado no contiene las columnas necesarias: <strong>{', '.join(faltantes)}</strong> (Obligatorias: <code>Va, Vb, Vc, Ia, Ib, Ic</code>).</span>
            </div>
            """
        )
    elif df_lote is not None and columnas_validas:
        render_html(
            f"""
            <div class="batch-status-banner batch-status-success">
                <span class="batch-status-icon">
                    <svg style="width: 14px; height: 14px;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="20 6 9 17 4 12"></polyline>
                    </svg>
                </span>
                <span>Archivo validado exitosamente (<strong>{nombre_archivo}</strong>): <strong>{len(df_lote):,} registros</strong> detectados.</span>
            </div>
            """
        )

    # Inferencia y resultados
    if df_lote is not None and columnas_validas:
        try:
            if ejecutar_lote:
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
                        Rendimiento del procesamiento
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
                        Vista previa del reporte de diagnóstico
                    </div>
                    """
                )
                st.dataframe(df_res.head(25), use_container_width=True)

                # Barra de descarga multi-formato con iconos y tooltips
                render_barra_descargas(df_res)

        except Exception as e:
            st.error(f"Error procesando el lote: {e}")


# ==============================================================================
# PÁGINA 3: AUDITORÍA DE METAS SMART Y MODELO (/info-audit-model)
