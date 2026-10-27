"""Script de post-instalación para inyectar metadatos SEO y verificación de Google Search Console

en los archivos estáticos servidos nativamente por Streamlit (index.html, robots.txt, sitemap.xml).
Garantiza que Googlebot y los rastreadores reciban la etiqueta meta en el HTML crudo inicial (HTTP GET /)
sin depender del montaje dinámico por WebSocket.
"""

from __future__ import annotations

import pathlib
import shutil
import sys

import streamlit

def parchear_archivos_estaticos_streamlit() -> None:
    raiz = pathlib.Path(__file__).resolve().parents[1]
    static_dir = pathlib.Path(streamlit.__file__).resolve().parent / "static"
    index_html_path = static_dir / "index.html"

    if not index_html_path.exists():
        print(f"[SEO-PATCH] No se encontró {index_html_path}")
        return

    # 1. Inyectar Metaetiquetas directamente en el <head> de index.html
    html_content = index_html_path.read_text(encoding="utf-8")
    meta_tag_gsc = '<meta name="google-site-verification" content="g2l5IovdAV37gpevFBB48YWyrJ_zcRh7wAa1zKhiyMs" />'

    if meta_tag_gsc not in html_content:
        bloque_seo = f"""    <!-- GOOGLE SEARCH CONSOLE Y SEO CRÍTICO -->
    {meta_tag_gsc}
    <meta name="description" content="ElectroVOLT: Plataforma web inteligente de costo cero para la predicción, detección y clasificación multiclase de fallos eléctricos con Machine Learning y SHAP." />
    <meta name="keywords" content="predicción de fallos eléctricos, detección de fallas eléctricas, clasificación de fallos trifásicos, ElectroVOLT, machine learning, XAI, SHAP" />
    <link rel="canonical" href="https://electro-volt.onrender.com/" />
"""
        html_content = html_content.replace("<head>", f"<head>\n{bloque_seo}")
        index_html_path.write_text(html_content, encoding="utf-8")
        print(f"[SEO-PATCH] Metaetiqueta de verificación inyectada exitosamente en {index_html_path}")
    else:
        print("[SEO-PATCH] La metaetiqueta ya existe en index.html")

    # 2. Copiar robots.txt a static_dir para que Streamlit lo sirva en /robots.txt
    robots_orig = raiz / "robots.txt"
    if robots_orig.exists():
        shutil.copy2(robots_orig, static_dir / "robots.txt")
        print(f"[SEO-PATCH] robots.txt copiado a {static_dir / 'robots.txt'}")

    # 3. Copiar sitemap.xml a static_dir para que Streamlit lo sirva en /sitemap.xml
    sitemap_orig = raiz / "sitemap.xml"
    if sitemap_orig.exists():
        shutil.copy2(sitemap_orig, static_dir / "sitemap.xml")
        print(f"[SEO-PATCH] sitemap.xml copiado a {static_dir / 'sitemap.xml'}")

    # 4. Crear archivo de verificación HTML por si el usuario usa ese método alternativo
    html_verif = static_dir / "googleg2l5IovdAV37gpevFBB48YWyrJ_zcRh7wAa1zKhiyMs.html"
    html_verif.write_text("google-site-verification: googleg2l5IovdAV37gpevFBB48YWyrJ_zcRh7wAa1zKhiyMs.html", encoding="utf-8")

if __name__ == "__main__":
    parchear_archivos_estaticos_streamlit()
