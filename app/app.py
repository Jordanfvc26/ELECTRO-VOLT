"""Dashboard Web Industrial para Diagnóstico y Clasificación de Fallos Eléctricos.

ELECTROVOLT: Plataforma interactiva de soporte a la decisión operativa en subestaciones eléctricas.
Punto de entrada principal y enrutador SPA / Multi-página según estándar Streamlit.
"""

from __future__ import annotations

from pathlib import Path
import sys
import streamlit as st

# Configuración robusta de rutas: asegurar que la raíz del proyecto sea la prioridad en sys.path
raiz = str(Path(__file__).resolve().parents[1])
app_dir = str(Path(__file__).resolve().parent)

while app_dir in sys.path:
    sys.path.remove(app_dir)
if raiz not in sys.path:
    sys.path.insert(0, raiz)

# Evitar colisión si Python registró app.py como módulo simple en vez del paquete app/
if "app" in sys.modules and not hasattr(sys.modules["app"], "__path__"):
    del sys.modules["app"]

from PIL import Image

try:
    from app.seo import inyectar_seo
    from app.styles import aplicar_estilos_css
    from app.components.header import render_header
    from app.components.navbar import render_navbar
    from app.components.footer import render_footer
    from app.views.tiempo_real import pagina_diagnostico_tiempo_real
    from app.views.procesamiento_lote import pagina_procesamiento_lote
    from app.views.auditoria_smart import pagina_auditoria_modelo
    from app.views.que_es import pagina_que_es_electrovolt
    from app.views.privacidad import pagina_politica_privacidad
    from app.views.terminos import pagina_terminos_condiciones
    from app.views.not_found import pagina_error_404
except (ImportError, ModuleNotFoundError):
    from seo import inyectar_seo
    from styles import aplicar_estilos_css
    from components.header import render_header
    from components.navbar import render_navbar
    from components.footer import render_footer
    from views.tiempo_real import pagina_diagnostico_tiempo_real
    from views.procesamiento_lote import pagina_procesamiento_lote
    from views.auditoria_smart import pagina_auditoria_modelo
    from views.que_es import pagina_que_es_electrovolt
    from views.privacidad import pagina_politica_privacidad
    from views.terminos import pagina_terminos_condiciones
    from views.not_found import pagina_error_404

# ==============================================================================
# CONFIGURACIÓN DE PÁGINA (FAVICON OFICIAL Y TÍTULO SEO)
# ==============================================================================
ruta_isotipo = Path(__file__).resolve().parents[1] / "src" / "images" / "electrovolt-isotipo.png"
if ruta_isotipo.exists():
    try:
        icono_pestana = Image.open(ruta_isotipo)
    except Exception:
        icono_pestana = "⚡"
else:
    icono_pestana = "⚡"

st.set_page_config(
    page_title="ElectroVOLT — Predicción y Clasificación de Fallos Eléctricos con IA",
    page_icon=icono_pestana,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Ocultar branding de Streamlit y Community Cloud sin afectar el footer corporativo
st.markdown(
    """
    <style>
    div[class*="viewerBadge"],
    div[class*="ProfileContainer"],
    div[class*="profileContainer"],
    div[class*="manageApp"],
    div[class*="ManageApp"],
    [data-testid="manage-app-button"],
    [data-testid="stStatusWidget"] {
        display: none !important;
        visibility: hidden !important;
    }
    footer:not(.custom-footer-strip) {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
    }
    .custom-footer-strip {
        display: block !important;
        visibility: visible !important;
    }
    .stDeployButton,
    .stAppDeployButton {
        display: none !important;
        visibility: hidden !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def pagina_principal():
    """Consola Principal de Monitoreo y Diagnóstico con navegación por módulos SPA."""
    # 1. Detección proactiva de rutas no válidas (Error 404)
    rutas_registradas = {
        "",
        "que-es-electrovolt",
        "politica-privacidad-electrovolt",
        "terminos-condiciones-electrovolt",
        "404",
    }
    modulos_validos = {
        "diagnostic-real-time",
        "diagnostic-from-file",
        "info-audit-model",
        "que-es-electrovolt",
        "politica-privacidad-electrovolt",
        "terminos-condiciones-electrovolt",
        "404",
    }

    intended_route = ""
    try:
        from streamlit.runtime.scriptrunner_utils.script_run_context import get_script_run_ctx
        ctx = get_script_run_ctx()
        if ctx and hasattr(ctx, "pages_manager"):
            intended_route = (getattr(ctx.pages_manager, "intended_page_name", "") or "").strip()
    except Exception:
        intended_route = ""

    modulo_url = st.query_params.get("modulo")

    # Si el usuario intentó acceder a una ruta inexistente o parámetro módulo no reconocido
    if intended_route and intended_route not in rutas_registradas:
        pagina_error_404(ruta_invalida=intended_route)
        return

    if modulo_url and modulo_url not in modulos_validos:
        pagina_error_404(ruta_invalida=f"?modulo={modulo_url}")
        return

    inyectar_seo()

    if "modulo_activo" not in st.session_state:
        st.session_state.modulo_activo = "diagnostic-real-time"

    url_guardada = st.session_state.get("_url_modulo_guardada")
    if (
        modulo_url
        and modulo_url != url_guardada
        and modulo_url in ["diagnostic-real-time", "diagnostic-from-file", "info-audit-model"]
    ):
        st.session_state.modulo_activo = modulo_url
        st.session_state._url_modulo_guardada = modulo_url
    else:
        st.session_state._url_modulo_guardada = st.session_state.modulo_activo

    aplicar_estilos_css()
    render_header()
    render_navbar(st.session_state.modulo_activo)

    if st.session_state.modulo_activo == "diagnostic-from-file":
        pagina_procesamiento_lote()
    elif st.session_state.modulo_activo == "info-audit-model":
        pagina_auditoria_modelo()
    else:
        pagina_diagnostico_tiempo_real()

    render_footer()


def main():
    """Enrutador de nivel superior de ElectroVOLT con páginas limpias según estándar Streamlit."""
    p_main = st.Page(
        pagina_principal,
        title="ElectroVOLT — Predicción y Clasificación de Fallos Eléctricos con IA",
        url_path="",
        default=True,
    )
    p_que_es = st.Page(
        pagina_que_es_electrovolt,
        title="¿Qué es ElectroVOLT? | Plataforma Inteligente",
        url_path="que-es-electrovolt",
    )
    p_privacidad = st.Page(
        pagina_politica_privacidad,
        title="Política de Privacidad | ElectroVOLT",
        url_path="politica-privacidad-electrovolt",
    )
    p_terminos = st.Page(
        pagina_terminos_condiciones,
        title="Términos y Condiciones | ElectroVOLT",
        url_path="terminos-condiciones-electrovolt",
    )
    p_404 = st.Page(
        pagina_error_404,
        title="404 — Página no encontrada | ElectroVOLT",
        url_path="404",
    )

    # Compatibilidad con accesos previos vía query param (?modulo=...)
    modulo_url = st.query_params.get("modulo")
    if modulo_url == "que-es-electrovolt":
        st.switch_page(p_que_es)
    elif modulo_url == "politica-privacidad-electrovolt":
        st.switch_page(p_privacidad)
    elif modulo_url == "terminos-condiciones-electrovolt":
        st.switch_page(p_terminos)
    elif modulo_url == "404":
        st.switch_page(p_404)

    nav = st.navigation([p_main, p_que_es, p_privacidad, p_terminos, p_404], position="hidden")
    nav.run()


if __name__ == "__main__":
    main()