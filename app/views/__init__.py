"""Módulos de vistas"""

from app.views.tiempo_real import pagina_diagnostico_tiempo_real
from app.views.procesamiento_lote import pagina_procesamiento_lote
from app.views.auditoria_smart import pagina_auditoria_modelo
from app.views.que_es import pagina_que_es_electrovolt
from app.views.privacidad import pagina_politica_privacidad
from app.views.terminos import pagina_terminos_condiciones

__all__ = [
    "pagina_diagnostico_tiempo_real",
    "pagina_procesamiento_lote",
    "pagina_auditoria_modelo",
    "pagina_que_es_electrovolt",
    "pagina_politica_privacidad",
    "pagina_terminos_condiciones",
]
