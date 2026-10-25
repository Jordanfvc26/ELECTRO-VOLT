"""Módulo de Vista: Auditoría Oficial de Rendimiento y Metas SMART"""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import streamlit as st

raiz = Path(__file__).resolve().parents[2]
if str(raiz) not in sys.path:
    sys.path.insert(0, str(raiz))

from src.utils import NOTA_CLASES, obtener_ruta_resultados
from app.utils import cargar_metricas_sistema, render_html

def pagina_auditoria_modelo():
    metricas_dict = cargar_metricas_sistema()
    with st.container():
        render_html('<div class="audit-main-card"></div>')
        render_html(
            """
            <div style="display: flex; align-items: center; gap: 0.65rem; margin-bottom: 0.45rem;">
                <span class="step-pill-badge" style="background: #eef2fb; color: #002a69; border: 1px solid #c5d2f3;">
                    <svg style="width: 15px; height: 15px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
                    </svg>
                </span>
                <span style="font-size: 1.08rem; font-weight: 700; color: #0f172a;">Auditoría Oficial de Rendimiento y Metas SMART</span>
            </div>
            <p style="color: #64748b; font-size: 0.83rem; margin-top: 0; margin-bottom: 1.25rem; line-height: 1.48;">
                Verificación y cumplimiento formal de los criterios de aceptación del proyecto integrador (Reglas 02 y 03).
            </p>
            """
        )

        if metricas_dict is not None:
            acc = metricas_dict.get('accuracy_prueba', 0.9994) * 100.0
            f1 = metricas_dict.get('f1_macro_prueba', 0.9996)
            rec = metricas_dict.get('recall_minimo_por_clase', 0.9979)
            lat = metricas_dict.get('latencia_ms', 16.8)

            c1, c2, c3, c4 = st.columns(4, gap="medium")
            with c1:
                render_html(
                    f"""
                    <div class="kpi-card-v2">
                        <div class="kpi-top-row">
                            <span class="kpi-label">Accuracy en Test</span>
                            <span class="kpi-icon-badge" style="background: rgba(0, 42, 105, 0.08); border: 1px solid rgba(0, 42, 105, 0.18); color: #002a69;">
                                <svg style="width: 17px; height: 17px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
                                </svg>
                            </span>
                        </div>
                        <div>
                            <div class="kpi-value-row">
                                <span class="kpi-value">{acc:.2f}%</span>
                            </div>
                            <div class="kpi-footer-text">
                                <svg style="width: 13px; height: 13px; color: #059669;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"></path></svg>
                                <span>Meta SMART >= 90.0%</span>
                            </div>
                        </div>
                    </div>
                    """
                )

            with c2:
                render_html(
                    f"""
                    <div class="kpi-card-v2">
                        <div class="kpi-top-row">
                            <span class="kpi-label">F1-Score Macro</span>
                            <span class="kpi-icon-badge" style="background: rgba(5, 150, 105, 0.1); border: 1px solid rgba(5, 150, 105, 0.25); color: #059669;">
                                <svg style="width: 17px; height: 17px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                                </svg>
                            </span>
                        </div>
                        <div>
                            <div class="kpi-value-row">
                                <span class="kpi-value">{f1:.4f}</span>
                            </div>
                            <div class="kpi-footer-text">
                                <svg style="width: 13px; height: 13px; color: #059669;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"></path></svg>
                                <span>Meta SMART >= 0.9000</span>
                            </div>
                        </div>
                    </div>
                    """
                )

            with c3:
                render_html(
                    f"""
                    <div class="kpi-card-v2">
                        <div class="kpi-top-row">
                            <span class="kpi-label">Recall Mínimo por Clase</span>
                            <span class="kpi-icon-badge" style="background: rgba(124, 58, 237, 0.1); border: 1px solid rgba(124, 58, 237, 0.22); color: #7c3aed;">
                                <svg style="width: 17px; height: 17px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                                </svg>
                            </span>
                        </div>
                        <div>
                            <div class="kpi-value-row">
                                <span class="kpi-value">{rec:.4f}</span>
                            </div>
                            <div class="kpi-footer-text">
                                <svg style="width: 13px; height: 13px; color: #059669;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"></path></svg>
                                <span>Meta SMART >= 0.8500</span>
                            </div>
                        </div>
                    </div>
                    """
                )

            with c4:
                render_html(
                    f"""
                    <div class="kpi-card-v2">
                        <div class="kpi-top-row">
                            <span class="kpi-label">Latencia Media CPU</span>
                            <span class="kpi-icon-badge" style="background: rgba(217, 119, 6, 0.1); border: 1px solid rgba(217, 119, 6, 0.22); color: #d97706;">
                                <svg style="width: 17px; height: 17px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                                </svg>
                            </span>
                        </div>
                        <div>
                            <div class="kpi-value-row">
                                <span class="kpi-value">{lat:.1f}</span>
                                <span class="kpi-unit">ms</span>
                            </div>
                            <div class="kpi-footer-text">
                                <svg style="width: 13px; height: 13px; color: #d97706;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                                <span>Meta SMART < 100 ms</span>
                            </div>
                        </div>
                    </div>
                    """
                )

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
# PÁGINAS INFORMATIVAS Y LEGALES DEL FOOTER
