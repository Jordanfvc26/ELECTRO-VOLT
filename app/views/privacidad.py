"""Módulo de Vista: Política de Privacidad y Tratamiento de Telemetría."""

from __future__ import annotations

import streamlit as st
from app.styles import aplicar_estilos_css
from app.utils import render_html
from app.components.header import render_header
from app.components.footer import render_footer

def pagina_politica_privacidad():
    """Página de Política de Privacidad y Tratamiento de Datos (/politica-privacidad-electrovolt)."""
    aplicar_estilos_css()
    render_header()

    with st.container():
        render_html(
            """
            <div class="info-page-container">
                <div style="margin-bottom: 1.25rem;">
                    <a href="/" target="_self" class="footer-back-link">
                        <svg style="width: 16px; height: 16px; margin-right: 6px;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
                        Volver a la consola
                    </a>
                </div>

                <div class="info-page-card">
                    <h1 class="info-page-title">Política de Privacidad</h1>

                    <div class="info-section-heading">
                        <span style="display: inline-block; width: 4px; height: 18px; background: #002a69; border-radius: 2px;"></span>
                        1. Distinción fundamental: Datos industriales vs. Datos personales
                    </div>
                    <p class="info-text-p">
                        Las variables procesadas por la plataforma ElectroVOLT corresponden exclusivamente a <strong>señales físicas electromecánicas de sistemas de potencia</strong>: tensiones instantáneas de fase (Va, Vb, Vc en p.u.), corrientes registradas por transformadores de corriente (Ia, Ib, Ic en Amperios), frecuencia nominal a 60 Hz e impedancias de línea.
                    </p>
                    <p class="info-text-p">
                        ElectroVOLT no solicita, no recopila ni almacena información personal o de contacto. Las magnitudes evaluadas en la plataforma son puramente operativas e industriales, por lo que su procesamiento no compromete la privacidad, identidad ni los derechos individuales de los usuarios.
                    </p>

                    <div class="info-section-heading">
                        <span style="display: inline-block; width: 4px; height: 18px; background: #002a69; border-radius: 2px;"></span>
                        2. Trazabilidad técnica y logs de conexión
                    </div>
                    <p class="info-text-p">
                        Para salvaguardar la estabilidad del servicio, prevenir ataques informáticos y mantener un registro técnico de los diagnósticos ejecutados, el servidor registra únicamente metadatos básicos de conexión:
                    </p>
                    <ul style="color: #334155; font-size: 0.88rem; line-height: 1.7; margin-bottom: 1rem;">
                        <li><strong>Marcas de tiempo (timestamps UTC):</strong> Registro del momento exacto en que se solicita una inferencia o carga de lote.</li>
                        <li><strong>Parámetros fasoriales de entrada:</strong> Conservación transitoria de lecturas para auditoría de diagnósticos en sesión.</li>
                        <li><strong>Dirección IP y cabeceras de red:</strong> Empleadas exclusivamente para mitigación de tráfico abusivo (rate limiting) y balanceo de carga.</li>
                    </ul>

                    <div class="info-section-heading">
                        <span style="display: inline-block; width: 4px; height: 18px; background: #002a69; border-radius: 2px;"></span>
                        3. Ciclo de vida y destrucción de archivos en memoria (Cero retención)
                    </div>
                    <p class="info-text-p">
                        ElectroVOLT adopta una arquitectura estricta de <strong>cero retención en almacenamiento no volátil</strong>. Los archivos .csv cargados en el módulo de procesamiento masivo residen únicamente en la memoria de trabajo temporal (RAM) de la sesión activa del navegador. Una vez cerrada la sesión, descargado el reporte o limpiados los datos mediante los botones correspondientes, la memoria se libera de inmediato sin dejar copias residuales en el servidor. Bajo ninguna circunstancia almacenamos tus archivos o datos en bases de datos permanentes.
                    </p>

                    <div class="info-section-heading">
                        <span style="display: inline-block; width: 4px; height: 18px; background: #002a69; border-radius: 2px;"></span>
                        4. Ausencia de cookies publicitarias y rastreadores de terceros
                    </div>
                    <p class="info-text-p">
                        La plataforma no utiliza cookies de seguimiento comercial, herramientas invasivas de analítica publicitaria ni tecnologías de perfilamiento de terceros. Se emplean exclusivamente las cookies técnicas y de sesión estrictamente necesarias para el correcto funcionamiento del framework web (como el mantenimiento de la selección de pestañas y widgets de visualización).
                    </p>

                    <div class="info-section-heading">
                        <span style="display: inline-block; width: 4px; height: 18px; background: #002a69; border-radius: 2px;"></span>
                        5. Ciberseguridad y recomendación para redes operativas (OT / SCADA)
                    </div>
                    <p class="info-text-p">
                        Esta versión web es de acceso público y constituye un entorno de validación académica y demostrativa. Conforme a las buenas prácticas de ciberseguridad industrial, para una futura integración productiva en subestaciones o empresas eléctricas, el código fuente está diseñado para desplegarse localmente como microservicio contenerizado en <strong>Docker dentro de redes privadas aisladas (air-gap)</strong>, sin conexión a internet público.
                    </p>
                </div>
            </div>
            """
        )

    render_footer()

