"""Módulo de Vista: ¿Qué es ElectroVOLT?"""

from __future__ import annotations

import streamlit as st
from app.styles import aplicar_estilos_css
from app.utils import render_html
from app.components.header import render_header
from app.components.footer import render_footer

def pagina_que_es_electrovolt():
    """Página Institucional: ¿Qué es ElectroVOLT? (/que-es-electrovolt)."""
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
                    <h1 class="info-page-title">¿Qué es ElectroVOLT?</h1>
                    <p class="info-page-subtitle">
                        Plataforma inteligente de soporte a la decisión operativa en subestaciones y redes eléctricas de distribución, basada en Machine Learning e Inteligencia Artificial Explicable (XAI).
                    </p>

                    <div class="info-section-heading">
                        <span style="display: inline-block; width: 4px; height: 18px; background: #002a69; border-radius: 2px;"></span>
                        1. El desafío operativo en las redes de distribución eléctrica
                    </div>
                    <p class="info-text-p">
                        Las interrupciones no programadas del suministro eléctrico causadas por cortocircuitos entre fases y fallas a tierra generan elevados costos económicos, penalizaciones regulatorias asociadas a los índices de continuidad, y severo estrés electrodinámico sobre transformadores de subestación.
                    </p>
                    <p class="info-text-p">
                        Actualmente, la localización y diagnóstico de estas contingencias depende en gran medida de inspecciones manuales reactivas en campo que toman en promedio <strong>2 horas</strong>. Si bien los relés de protección electromecánicos y numéricos tradicionales (funciones IEEE 50/51/51N) despejan el circuito ante sobrecorrientes, <strong>no proporcionan al operador una clasificación topológica inmediata</strong> de la falla ni una justificación física de qué conductores están interactuando.
                    </p>

                    <p class="info-text-p">
                        La propuesta de ElectroVOLT es cerrar esta brecha analítica ofreciendo una plataforma de costo cero ($0 USD) que procesa 5 señales trifásicas en milisegundos, identifica la topología del fallo con exactitud del 99.9% y entrega una explicación auditable basada en Inteligencia Artificial Explicable (SHAP) para asistir al operador antes de ejecutar maniobras críticas.
                    </p>

                    <div class="info-section-heading">
                        <span style="display: inline-block; width: 4px; height: 18px; background: #002a69; border-radius: 2px;"></span>
                        2. Catálogo de topologías físicas clasificadas
                    </div>
                    <p class="info-text-p">
                        El sistema clasifica el estado de la línea en cinco clases operativas formalmente validadas bajo principios de ingeniería eléctrica:
                    </p>

                    <div class="info-grid-2">
                        <div class="info-feature-card" style="border-left: 4px solid #059669;">
                            <div style="font-weight: 700; color: #059669; font-size: 0.95rem; margin-bottom: 0.25rem;">1. Operación Normal (Red Despejada)</div>
                            <div style="font-size: 0.84rem; color: #475569; line-height: 1.5;">Tensiones nominales balanceadas (~1.0 p.u.), corrientes dentro del límite térmico de diseño y corriente neutra nula (In = 0 A). Sin presencia de cortocircuito.</div>
                        </div>

                        <div class="info-feature-card" style="border-left: 4px solid #d97706;">
                            <div style="font-weight: 700; color: #d97706; font-size: 0.95rem; margin-bottom: 0.25rem;">2. Falla Monofásica a Tierra (LG)</div>
                            <div style="font-size: 0.84rem; color: #475569; line-height: 1.5;">Pérdida de aislamiento entre un solo conductor de fase y tierra (A-G, B-G o C-G). Representa ~70% de las fallas reales. Genera fuerte corriente homopolar en el neutro.</div>
                        </div>

                        <div class="info-feature-card" style="border-left: 4px solid #2563eb;">
                            <div style="font-weight: 700; color: #2563eb; font-size: 0.95rem; margin-bottom: 0.25rem;">3. Falla Bifásica entre Fases (LL)</div>
                            <div style="font-size: 0.84rem; color: #475569; line-height: 1.5;">Cortocircuito franco entre dos conductores de fase (A-B, B-C o C-A) sin contacto con la malla de tierra. Corrientes elevadas opuestas y corriente residual neutra prácticamente nula.</div>
                        </div>

                        <div class="info-feature-card" style="border-left: 4px solid #b45309;">
                            <div style="font-weight: 700; color: #b45309; font-size: 0.95rem; margin-bottom: 0.25rem;">4. Falla Doble Línea a Tierra (LLG)</div>
                            <div style="font-size: 0.84rem; color: #475569; line-height: 1.5;">Dos fases en cortocircuito simultáneo con contacto directo a la malla de tierra (A-B-G, B-C-G o C-A-G). Circulación combinada de corrientes de secuencia positiva, negativa y cero.</div>
                        </div>

                        <div class="info-feature-card" style="grid-column: span 2; border-left: 4px solid #dc2626;">
                            <div style="font-weight: 700; color: #dc2626; font-size: 0.95rem; margin-bottom: 0.25rem;">5. Falla Trifásica Simétrica (Trifásica A-B-C)</div>
                            <div style="font-size: 0.84rem; color: #475569; line-height: 1.5;">Cortocircuito severo simultáneo en las tres fases. Por simetría trifásica (corrientes desfasadas 120°), la suma fasorial en el neutro es cero (In = 0 A), por lo cual las señales de fase no contienen información física para diferenciar LLL de LLLG. La maniobra de protección es idéntica: apertura tripolar inmediata.</div>
                        </div>
                    </div>

                    <div class="info-section-heading">
                        <span style="display: inline-block; width: 4px; height: 18px; background: #002a69; border-radius: 2px;"></span>
                        3. Inteligencia Artificial Explicable (XAI con SHAP)
                    </div>
                    <p class="info-text-p">
                        A diferencia de los modelos tradicionales de caja negra, ElectroVOLT integra <strong>SHAP (SHapley Additive exPlanations)</strong> mediante el algoritmo <code>TreeExplainer</code>. Para cada oscilograma o muestra analizada, el sistema descompone la contribución individual de cada tensión (Va, Vb, Vc) y corriente (Ia, Ib, Ic), mostrando al operador con transparencia fasorial matemática qué magnitud física empujó la decisión diagnóstica hacia la clase clasificada.
                    </p>
                </div>
            </div>
            """
        )

    render_footer()

