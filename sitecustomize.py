"""Python sitecustomize hook para ejecutar parches de inicio de servidor en Render y entornos locales."""

from __future__ import annotations

try:
    from scripts.patch_seo import parchear_archivos_estaticos_streamlit
    parchear_archivos_estaticos_streamlit()
except Exception:
    pass
