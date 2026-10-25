"""Componente de barra de navegación superior (Header)."""

from __future__ import annotations

import streamlit as st
from app.utils import obtener_logo_base64, render_html

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
                <a href="/" target="_self" style="text-decoration: none; display: flex; align-items: center; cursor: pointer;">
                    {logo_html}
                </a>
            </div>
            <div class="header-avatar-circle">
                OP
            </div>
        </div>
        """
    )

