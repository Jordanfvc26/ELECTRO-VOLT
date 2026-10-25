"""Componente de pie de página corporativo."""

from __future__ import annotations

import streamlit as st
from app.utils import obtener_logo_base64, render_html

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
                            <a href="/" target="_self" style="text-decoration: none; display: flex; align-items: center;">
                                {logo_html}
                            </a>
                        </div>
                    </div>

                    <!-- COLUMNA 2: NAVEGACIÓN -->
                    <div>
                        <div class="footer-heading">NAVEGACIÓN</div>
                        <div style="display: flex; flex-direction: column; gap: 0.35rem;">
                            <a href="/?modulo=diagnostic-real-time" target="_self" class="footer-text-item">Tiempo real</a>
                            <a href="/?modulo=diagnostic-from-file" target="_self" class="footer-text-item">Desde archivo</a>
                            <a href="/?modulo=info-audit-model" target="_self" class="footer-text-item">Metas SMART</a>
                        </div>
                    </div>

                    <!-- COLUMNA 3: INFORMACIÓN -->
                    <div>
                        <div class="footer-heading">INFORMACIÓN</div>
                        <div style="display: flex; flex-direction: column; gap: 0.35rem;">
                            <a href="/que-es-electrovolt" target="_self" class="footer-text-item">¿Qué es ElectroVOLT?</a>
                            <a href="/politica-privacidad-electrovolt" target="_self" class="footer-text-item">Política de Privacidad</a>
                            <a href="/terminos-condiciones-electrovolt" target="_self" class="footer-text-item">Términos y Condiciones</a>
                        </div>
                    </div>

                    <!-- COLUMNA 4: CONTACTO -->
                    <div>
                        <div class="footer-heading">CONTACTO</div>
                        <div style="display: flex; flex-direction: column; gap: 0.85rem;">
                            <!-- Jordan Vera Coello -->
                            <div class="footer-author-group">
                                <a href="https://www.linkedin.com/in/jordanfvc26" target="_blank" rel="noopener noreferrer" class="footer-author-name-link" title="Ver perfil en LinkedIn">
                                    <div class="footer-contact-icon">
                                        <svg style="width: 14px; height: 14px;" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24">
                                            <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path>
                                            <rect x="2" y="9" width="4" height="12"></rect>
                                            <circle cx="4" cy="4" r="2"></circle>
                                        </svg>
                                    </div>
                                    <span>Jordan Vera Coello</span>
                                </a>
                                <a href="mailto:jordan.verac@uees.edu.ec" class="footer-author-mail-link" title="Enviar correo a jordan.verac@uees.edu.ec">
                                    <div class="footer-contact-icon">
                                        <svg style="width: 14px; height: 14px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                                        </svg>
                                    </div>
                                    <span class="footer-contact-text">jordan.verac@uees.edu.ec</span>
                                </a>
                            </div>

                            <!-- Jorge Estrella Frere -->
                            <div class="footer-author-group">
                                <a href="https://www.linkedin.com/in/jorgeestrella" target="_blank" rel="noopener noreferrer" class="footer-author-name-link" title="Ver perfil en LinkedIn">
                                    <div class="footer-contact-icon">
                                        <svg style="width: 14px; height: 14px;" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24">
                                            <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path>
                                            <rect x="2" y="9" width="4" height="12"></rect>
                                            <circle cx="4" cy="4" r="2"></circle>
                                        </svg>
                                    </div>
                                    <span>Jorge Estrella Frere</span>
                                </a>
                                <a href="mailto:jestrella@uees.edu.ec" class="footer-author-mail-link" title="Enviar correo a jestrella@uees.edu.ec">
                                    <div class="footer-contact-icon">
                                        <svg style="width: 14px; height: 14px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                                        </svg>
                                    </div>
                                    <span class="footer-contact-text">jestrella@uees.edu.ec</span>
                                </a>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="footer-copyright">
                    © 2026 ElectroVOLT. Todos los derechos reservados
                </div>
            </div>
        </footer>
        """
    )
