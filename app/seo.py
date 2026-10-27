"""Módulo integral de SEO, Metadatos de Redes Sociales y Optimización para Motores de Búsqueda e IA.

Proporciona etiquetas meta enriquecidas, Open Graph (WhatsApp, LinkedIn, Facebook),
Twitter Cards, Favicon dinámico basado en el isotipo oficial, Schema.org JSON-LD (WebApplication, FAQPage)
y palabras clave exhaustivas para posicionamiento en Google, Bing y motores de IA (SearchGPT, Perplexity, Copilot).
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

import streamlit as st

raiz = Path(__file__).resolve().parents[1]
if str(raiz) not in sys.path:
    sys.path.insert(0, str(raiz))

from app.utils import obtener_isotipo_base64, obtener_logo_base64, render_html

# ==============================================================================
# PALABRAS CLAVE ESTRATÉGICAS (KEYWORDS SEO DE ALTA INTENCIÓN)
# ==============================================================================
PALABRAS_CLAVE_OFICIALES = [
    # Intención Principal y Diagnóstico
    "predicción de fallos eléctricos",
    "prediccion de fallos electricos",
    "detección de fallos eléctricos",
    "deteccion de fallas electricas",
    "clasificación de fallas eléctricas",
    "clasificacion de fallos trifasicos",
    "diagnóstico de fallas en redes de distribución",
    "localización de fallas eléctricas",
    "detección de cortocircuitos eléctricos",
    "monitoreo de fallas eléctricas en tiempo real",
    "análisis fasorial en tiempo real",
    "oscilograma de fallas eléctricas 60 Hz",
    # Topologías y Tipos de Fallas
    "falla a tierra",
    "falla monofásica a tierra LG",
    "falla bifásica entre fases LL",
    "falla bifásica a tierra LLG",
    "falla trifásica simétrica LLL",
    "cortocircuito trifásico a tierra",
    "corrientes de cortocircuito",
    "sobretensión y subtensión en fallas",
    "componentes simétricas de fase",
    "secuencia positiva negativa cero",
    # Inteligencia Artificial y Machine Learning
    "inteligencia artificial para redes eléctricas",
    "machine learning en sistemas de potencia",
    "random forest para fallas eléctricas",
    "IA explicable en energía eléctrica",
    "XAI sistemas eléctricos",
    "SHAP para fallos eléctricos",
    "TreeExplainer telemetría eléctrica",
    "interpretabilidad de modelos de IA",
    "algoritmos de clasificación supervisada eléctrica",
    "smart grid machine learning",
    # Sistemas de Potencia y Subestaciones
    "subestaciones eléctricas",
    "transformadores de potencia",
    "relés de protección numérica",
    "relé de sobrecorriente 50 51 51N",
    "calidad de energía eléctrica",
    "analizador de redes eléctricas",
    "índices de continuidad SAIDI SAIFI",
    "reducción de apagones y tiempos de interrupción",
    "soporte a la decisión operativa DSS",
    "seguridad eléctrica en subestaciones",
    # Marca y Académico
    "ElectroVOLT",
    "Electro-Volt",
    "Electro VOLT plataforma eléctrica",
    "Jordan Fabian Vera Coello",
    "Jorge Rafael Estrella Frere",
    "Maestría en Inteligencia Artificial UEES",
    "Universidad de Especialidades Espíritu Santo",
]

KEYWORDS_STR = ", ".join(PALABRAS_CLAVE_OFICIALES)


def inyectar_seo(
    titulo: str = "ElectroVOLT — Predicción y Clasificación de Fallos Eléctricos con IA",
    descripcion: str = (
        "Plataforma inteligente de costo cero ($0 USD) para la predicción, detección "
        "y clasificación multiclase de fallos eléctricos (LG, LL, LLG, Trifásica) en redes de "
        "distribución y subestaciones mediante Machine Learning e Inteligencia Artificial Explicable (SHAP)."
    ),
    url_relativa: str = "",
    tipo_pagina: str = "website",
) -> None:
    """Inyecta metadatos SEO completos en el DOM: Favicon, OpenGraph, Twitter Cards, Schema.org y FAQPage."""
    logo_b64 = obtener_logo_base64()
    iso_b64 = obtener_isotipo_base64()

    url_base = "https://electro-volt.onrender.com"
    url_completa = f"{url_base}/{url_relativa.lstrip('/')}" if url_relativa else f"{url_base}/"

    # Imagen para compartir en redes sociales (Data URI fallback + URL estática)
    img_og_src = f"data:image/png;base64,{logo_b64}" if logo_b64 else f"{url_base}/electrovolt-logotipo.png"
    favicon_src = f"data:image/png;base64,{iso_b64}" if iso_b64 else ""

    # Schema.org JSON-LD estructurado
    schema_data = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebApplication",
                "@id": f"{url_base}/#webapp",
                "name": "ElectroVOLT",
                "alternateName": ["Electro-Volt", "Electro VOLT"],
                "url": url_base,
                "applicationCategory": "EngineeringApplication",
                "operatingSystem": "All (Web Browser)",
                "browserRequirements": "Requires JavaScript. HTML5 compatible.",
                "description": descripcion,
                "image": img_og_src,
                "inLanguage": "es",
                "license": "https://opensource.org/licenses/MIT",
                "offers": {
                    "@type": "Offer",
                    "price": "0",
                    "priceCurrency": "USD",
                    "availability": "https://schema.org/InStock",
                },
                "author": [
                    {
                        "@type": "Person",
                        "name": "Jordan Fabian Vera Coello",
                        "jobTitle": "Product Owner & ML Engineer",
                        "sameAs": "https://www.linkedin.com/in/jordanfvc26",
                        "email": "jordan.verac@uees.edu.ec",
                    },
                    {
                        "@type": "Person",
                        "name": "Jorge Rafael Estrella Frere",
                        "jobTitle": "Tech Lead & Electrical Domain Expert",
                        "sameAs": "https://www.linkedin.com/in/jorgeestrella",
                        "email": "jestrella@uees.edu.ec",
                    },
                ],
                "provider": {
                    "@type": "EducationalOrganization",
                    "name": "Universidad de Especialidades Espíritu Santo (UEES)",
                    "url": "https://www.uees.edu.ec",
                    "address": {
                        "@type": "PostalAddress",
                        "addressLocality": "Samborondón",
                        "addressCountry": "Ecuador",
                    },
                },
                "featureList": [
                    "Diagnóstico instantáneo en tiempo real (< 100 ms)",
                    "Clasificación de 5 estados: Normal, Fase a Tierra (LG), Línea a Línea (LL), Doble Línea a Tierra (LLG), Falla Trifásica",
                    "Explicabilidad física basada en SHAP TreeExplainer",
                    "Procesamiento masivo por lote de archivos CSV (> 50,000 muestras/s)",
                    "Exportación de reportes ejecutivos en formato Excel (.xlsx) y PDF formal con ReportLab",
                    "Arquitectura de Cero Retención en RAM para máxima privacidad",
                ],
            },
            {
                "@type": "FAQPage",
                "@id": f"{url_base}/#faq",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": "¿Qué es ElectroVOLT y cómo predice fallos eléctricos?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": (
                                "ElectroVOLT es una plataforma web inteligente de soporte a la decisión operativa "
                                "para subestaciones y redes eléctricas de distribución. Utiliza un modelo de Machine Learning "
                                "supervisado (Random Forest Classifier calibrado) capaz de predecir y clasificar fallos en milisegundos "
                                "a partir de 6 lecturas trifásicas continuas (tensiones Va, Vb, Vc y corrientes Ia, Ib, Ic)."
                            ),
                        },
                    },
                    {
                        "@type": "Question",
                        "name": "¿Cuáles son las 5 clases de fallos eléctricos que clasifica la plataforma?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": (
                                "El modelo clasifica con exactitud del 99.9% entre: 1) Operación Normal, "
                                "2) Falla de Línea a Tierra (LG), 3) Falla de Línea a Línea (LL), "
                                "4) Falla de Doble Línea a Tierra (LLG) y 5) Falla Trifásica simétrica."
                            ),
                        },
                    },
                    {
                        "@type": "Question",
                        "name": "¿Cómo explica la inteligencia artificial sus predicciones con SHAP?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": (
                                "A diferencia de las cajas negras tradicionales, ElectroVOLT integra SHAP (SHapley Additive exPlanations) "
                                "mediante TreeExplainer. El sistema descompone la contribución fasorial exacta de cada tensión y corriente, "
                                "mostrando qué magnitudes físicas específicas forzaron la clasificación del fallo."
                            ),
                        },
                    },
                    {
                        "@type": "Question",
                        "name": "¿Cómo ayuda ElectroVOLT a reducir los índices SAIDI y SAIFI?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": (
                                "Permite reducir el tiempo de diagnóstico inicial de contingencias en un 80% (pasando de ~2 horas de "
                                "inspección manual en campo a fracciones de segundo), permitiendo aislar tramos fallados rápidamente y "
                                "disminuir la duración media (SAIDI) y frecuencia (SAIFI) de interrupciones eléctricas."
                            ),
                        },
                    },
                    {
                        "@type": "Question",
                        "name": "¿Qué costo tiene el uso de ElectroVOLT?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": (
                                "ElectroVOLT es una contribución 100% de costo cero ($0 USD) y código abierto bajo Licencia MIT, "
                                "desarrollada en el marco de la Maestría en Inteligencia Artificial de la UEES para libre uso de la comunidad."
                            ),
                        },
                    },
                ],
            },
        ],
    }

    schema_json_str = json.dumps(schema_data, ensure_ascii=False)

    # Inyección de favicon y verificación dinámica vía JavaScript
    js_head_scripts = f"""
    <script>
    (function() {{
        function inyectarMetas() {{
            var faviconUrl = '{favicon_src}';
            if (faviconUrl) {{
                var links = document.querySelectorAll("link[rel*='icon']");
                links.forEach(function(el) {{ el.remove(); }});
                var nuevoLink = document.createElement('link');
                nuevoLink.type = 'image/png';
                nuevoLink.rel = 'icon';
                nuevoLink.href = faviconUrl;
                document.head.appendChild(nuevoLink);

                var appleLink = document.createElement('link');
                appleLink.rel = 'apple-touch-icon';
                appleLink.href = faviconUrl;
                document.head.appendChild(appleLink);
            }}

            var metaGSC = document.querySelector("meta[name='google-site-verification']");
            if (!metaGSC) {{
                var m = document.createElement('meta');
                m.name = 'google-site-verification';
                m.content = 'g2l5IovdAV37gpevFBB48YWyrJ_zcRh7wAa1zKhiyMs';
                document.head.appendChild(m);
            }}
            try {{
                if (window.parent && window.parent.document && window.parent.document.head) {{
                    var mParent = window.parent.document.querySelector("meta[name='google-site-verification']");
                    if (!mParent) {{
                        var mp = window.parent.document.createElement('meta');
                        mp.name = 'google-site-verification';
                        mp.content = 'g2l5IovdAV37gpevFBB48YWyrJ_zcRh7wAa1zKhiyMs';
                        window.parent.document.head.appendChild(mp);
                    }}
                }}
            }} catch(e) {{}}
        }}
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', inyectarMetas);
        }} else {{
            inyectarMetas();
        }}
        setTimeout(inyectarMetas, 400);
        setTimeout(inyectarMetas, 1200);
    }})();
    </script>
    """

    # Bloque HTML con etiquetas meta y Schema.org
    meta_html = f"""
    <!-- VERIFICACIÓN OFICIAL DE GOOGLE SEARCH CONSOLE -->
    <meta name="google-site-verification" content="g2l5IovdAV37gpevFBB48YWyrJ_zcRh7wAa1zKhiyMs" />

    <!-- META TAGS SEO PRINCIPALES -->
    <meta name="description" content="{descripcion}" />
    <meta name="keywords" content="{KEYWORDS_STR}" />
    <meta name="author" content="Jordan Fabian Vera Coello, Jorge Rafael Estrella Frere — Maestría en Inteligencia Artificial UEES" />
    <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1" />
    <meta name="googlebot" content="index, follow, max-snippet:-1, max-image-preview:large" />
    <meta name="bingbot" content="index, follow, max-snippet:-1, max-image-preview:large" />
    <meta name="theme-color" content="#002a69" />
    <link rel="canonical" href="{url_completa}" />

    <!-- OPEN GRAPH (FACEBOOK, LINKEDIN, WHATSAPP) -->
    <meta property="og:locale" content="es_EC" />
    <meta property="og:type" content="{tipo_pagina}" />
    <meta property="og:title" content="{titulo}" />
    <meta property="og:description" content="{descripcion}" />
    <meta property="og:url" content="{url_completa}" />
    <meta property="og:site_name" content="ElectroVOLT" />
    <meta property="og:image" content="{img_og_src}" />
    <meta property="og:image:type" content="image/png" />
    <meta property="og:image:alt" content="ElectroVOLT — Plataforma de Detección y Clasificación de Fallos Eléctricos con IA" />

    <!-- TWITTER / X CARDS -->
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{titulo}" />
    <meta name="twitter:description" content="{descripcion}" />
    <meta name="twitter:image" content="{img_og_src}" />
    <meta name="twitter:image:alt" content="ElectroVOLT" />

    <!-- SCHEMA.ORG RICH SNIPPETS JSON-LD (GOOGLE, BING, PERPLEXITY, CHATGPT) -->
    <script type="application/ld+json">
    {schema_json_str}
    </script>

    {js_head_scripts}

    <!-- BLOQUE SEMÁNTICO DE RASTREO INDEXABLE PARA MOTORES DE BÚSQUEDA Y AGENTES IA -->
    <div style="position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0); border: 0;" aria-hidden="false">
        <h1>ElectroVOLT: Detección y Clasificación Multiclase de Fallos Eléctricos con Machine Learning e IA Explicable</h1>
        <p>
            Plataforma interactiva orientada al sector eléctrico para la identificación inmediata de fallas monofásicas a tierra (LG),
            bifásicas (LL), bifásicas a tierra (LLG) y trifásicas (LLL) a partir de tensiones y corrientes trifásicas.
            Desarrollada por Jordan Fabian Vera Coello y Jorge Rafael Estrella Frere para la Universidad de Especialidades Espíritu Santo (UEES, 2026).
        </p>
        <h2>Metodología de Inteligencia Artificial</h2>
        <p>
            Modelo entrenado con Random Forest Classifier sobre 7,861 registros con validación cruzada estratificada (StratifiedKFold k=5).
            Exactitud en Test: 99.94%, F1-Score Macro: 0.9996, Recall mínimo: 99.79%, Latencia de inferencia: 16.8 ms por muestra.
            Explicabilidad transparente mediante SHAP TreeExplainer para validación fasorial física antes de maniobras en subestación.
        </p>
    </div>
    """

    render_html(meta_html)
