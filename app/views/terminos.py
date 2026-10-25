"""Módulo de Vista: Términos y Condiciones de Uso y Seguridad Operativa"""

from __future__ import annotations

import streamlit as st
from app.seo import inyectar_seo
from app.styles import aplicar_estilos_css
from app.utils import render_html
from app.components.header import render_header
from app.components.footer import render_footer

def pagina_terminos_condiciones():
    """Página de Términos y Condiciones de uso (/terminos-condiciones-electrovolt)."""
    inyectar_seo(
        titulo="Términos y Condiciones de Uso Operativo | ElectroVOLT",
        descripcion=(
            "Términos de uso, carácter consultivo (DSS), reglas de seguridad eléctrica "
            "y deslinde de responsabilidades operativas en la plataforma ElectroVOLT."
        ),
        url_relativa="terminos-condiciones-electrovolt",
    )
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
                    <h1 class="info-page-title">Términos y Condiciones de Uso</h1>

                    <p class="info-text-p">
                        ElectroVOLT es estrictamente una plataforma de <strong>soporte para consultas y aprendizaje</strong>. Bajo ningún concepto el software interactúa con relés de disparo físico ni acciona interruptores en subestaciones. La responsabilidad técnica y operativa de cualquier maniobra recae exclusivamente en el operador o especialista humano a cargo.
                    </p>

                    <div class="info-section-heading">
                        <span style="display: inline-block; width: 4px; height: 18px; background: #002a69; border-radius: 2px;"></span>
                        1. Carácter consultivo y criterio operativo
                    </div>
                    <p class="info-text-p">
                        Ningún trabajador, ingeniero o técnico puede autorizar traslados a campo, energización o apertura de circuitos amparándose únicamente en el dictamen probabilístico emitido por la plataforma ElectroVOLT.
                    </p>
                    <p class="info-text-p">
                        Toda maniobra en redes eléctricas exige la verificación física en los instrumentos de medición primarios y el cumplimiento irrestricto de las <strong>Reglas de Seguridad Eléctrica</strong>:
                    </p>
                    <ol style="color: #334155; font-size: 0.88rem; line-height: 1.75; margin-bottom: 1.25rem;">
                        <li><strong>Corte efectivo</strong> de todas las fuentes de tensión mediante apertura visible de seccionadores o interruptores.</li>
                        <li><strong>Bloqueo y señalización</strong> de los aparatos de corte para evitar reconexiones intempestivas.</li>
                        <li><strong>Comprobación de ausencia de tensión</strong> con detector calibrado en todos los conductores y fases.</li>
                        <li><strong>Puesta a tierra y en cortocircuito</strong> de todas las fases de la instalación a intervenir.</li>
                        <li><strong>Señalización y delimitación</strong> precisa de la zona de trabajo de la cuadrilla técnica.</li>
                    </ol>

                    <div class="info-section-heading">
                        <span style="display: inline-block; width: 4px; height: 18px; background: #002a69; border-radius: 2px;"></span>
                        2. Propósito educativo, investigativo y de uso libre
                    </div>
                    <p class="info-text-p">
                        ElectroVOLT fue concebido y desarrollado con fines puramente <strong>formativos, académicos y de divulgación científica</strong>. Cualquier estudiante, docente, investigador o entusiasta del sector eléctrico puede explorar la plataforma, realizar pruebas con archivos propios o precargados y analizar las visualizaciones de IA Explicable (SHAP) con absoluta libertad y a costo cero ($0 USD).
                    </p>

                    <div class="info-section-heading">
                        <span style="display: inline-block; width: 4px; height: 18px; background: #002a69; border-radius: 2px;"></span>
                        3. Exención de responsabilidades operativas
                    </div>
                    <p class="info-text-p">
                        Al ser una herramienta abierta de carácter demostrativo, los autores, colaboradores e instituciones académicas participantes <strong>no asumen ninguna responsabilidad</strong> por el uso que se haga de las predicciones ni por consecuencias derivadas de su interpretación. Esto incluye, entre otros: maniobras indebidas, daños a transformadores o equipamiento de red, interrupciones de suministro eléctrico o incidentes de seguridad laboral. El uso de la información corre enteramente por cuenta y riesgo del usuario.
                    </p>

                    <div class="info-section-heading">
                        <span style="display: inline-block; width: 4px; height: 18px; background: #002a69; border-radius: 2px;"></span>
                        4. Sin garantías comerciales o de infalibilidad
                    </div>
                    <p class="info-text-p">
                        Aunque el modelo de Machine Learning ha sido entrenado con rigurosidad y validado con métricas de alta precisión, los resultados generados constituyen estimaciones matemáticas que no deben tomarse como verdades absolutas ni sustituyen a relés de protección industrial certificados. La herramienta se ofrece tal como está, sin compromisos de disponibilidad ininterrumpida ni garantías para fines comerciales o de misión crítica.
                    </p>

                    <div class="info-section-heading">
                        <span style="display: inline-block; width: 4px; height: 18px; background: #002a69; border-radius: 2px;"></span>
                        5. Uso ético y colaborativo
                    </div>
                    <p class="info-text-p">
                        Invitamos a toda la comunidad a utilizar la plataforma con un sentido ético, responsable y constructivo. El valor de proyectos como ElectroVOLT reside en democratizar el conocimiento de la Inteligencia Artificial aplicada a la ingeniería, impulsando el aprendizaje continuo y la innovación tecnológica accesible para todos.
                    </p>
                </div>
            </div>
            """
        )

    render_footer()
