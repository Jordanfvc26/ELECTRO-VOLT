"""Módulo de Vista: Página 404 Personalizada de Ruta No Encontrada (SCADA / Red Eléctrica).

Gestiona los accesos a rutas inexistentes, parámetros de consulta alterados o
alimentadores lógicos no registrados en la plataforma ElectroVOLT.
"""

from __future__ import annotations

import html
from pathlib import Path
import sys
import streamlit as st

try:
    from app.seo import inyectar_seo
    from app.styles import aplicar_estilos_css
    from app.utils import render_html
    from app.components.header import render_header
    from app.components.footer import render_footer
except (ImportError, ModuleNotFoundError):
    from seo import inyectar_seo
    from styles import aplicar_estilos_css
    from utils import render_html
    from components.header import render_header
    from components.footer import render_footer


def pagina_error_404(ruta_invalida: str = "") -> None:
    """Página 404 Personalizada de ElectroVOLT para rutas inexistentes o erróneas."""
    # Obtener la ruta o parámetro solicitado si no se pasó explícitamente
    if not ruta_invalida:
        try:
            from streamlit.runtime.scriptrunner_utils.script_run_context import get_script_run_ctx
            ctx = get_script_run_ctx()
            if ctx and hasattr(ctx, "pages_manager"):
                ruta_invalida = getattr(ctx.pages_manager, "intended_page_name", "") or ""
        except Exception:
            ruta_invalida = ""

        if not ruta_invalida:
            ruta_invalida = st.query_params.get("modulo", "")

    # Sanitizar la ruta para visualización segura
    ruta_limpia = html.escape(str(ruta_invalida).strip())
    if ruta_limpia and not ruta_limpia.startswith("/") and not ruta_limpia.startswith("?"):
        ruta_display = f"/{ruta_limpia}"
    elif ruta_limpia:
        ruta_display = ruta_limpia
    else:
        ruta_display = "/ruta-no-encontrada"

    inyectar_seo(
        titulo="404 — Ruta No Encontrada | ElectroVOLT",
        descripcion=(
            "La ruta o alimentador solicitado no existe en la consola de supervisión de ElectroVOLT. "
            "Retorne a la consola principal de diagnóstico."
        ),
        url_relativa="404",
    )
    aplicar_estilos_css()
    render_header()

    with st.container():
        render_html(
            f"""
            <div class="error-404-container">
                <div style="margin-bottom: 1.25rem;">
                    <a href="/" target="_self" class="footer-back-link">
                        <svg style="width: 16px; height: 16px; margin-right: 6px;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
                        Volver a la consola principal
                    </a>
                </div>

                <div class="error-404-card">
                    <div class="error-hero-number">
                        <span>4</span><span class="error-hero-spark">⚡</span><span>4</span>
                    </div>

                    <h1 class="error-title">Ruta no encontrada</h1>
                </div>
            </div>
            """
        )

    render_footer()
