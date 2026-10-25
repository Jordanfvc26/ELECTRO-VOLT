"""Componentes visuales y de navegación"""

from app.components.header import render_header
from app.components.navbar import cb_cambiar_modulo, render_navbar
from app.components.footer import render_footer

__all__ = ["render_header", "cb_cambiar_modulo", "render_navbar", "render_footer"]
