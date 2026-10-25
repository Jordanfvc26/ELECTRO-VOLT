"""Pruebas unitarias para la aplicación web y componentes del dashboard (app/app.py).

Verifica la carga de recursos cacheados (modelo y explicador SHAP), la integridad
del archivo de ejemplos de prueba y el procesamiento por lote.
"""

from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from src.data_processing import cargar_datos, mapear_clases
from src.evaluate import normalizar_shap
from src.model import cargar_paquete_modelo, predecir_falla
from src.utils import COLUMNAS, ORDEN_CLASES, obtener_ruta_datos_procesados


def test_archivo_ejemplos_prueba_valido() -> None:
    """Verifica que data/processed/ejemplos_prueba.csv exista y contenga las 6 columnas y clase."""
    ruta_ejemplos = obtener_ruta_datos_procesados("ejemplos_prueba.csv")
    assert ruta_ejemplos.exists(), f"No se encuentra el archivo en {ruta_ejemplos}"

    df = pd.read_csv(ruta_ejemplos)
    assert len(df) >= 5, "El archivo de ejemplos debe contener al menos 5 filas"
    for col in COLUMNAS:
        assert col in df.columns, f"Falta la columna requerida {col} en ejemplos_prueba.csv"
    assert "clase" in df.columns, "Debe contener la columna 'clase'"

    clases_presentes = set(df["clase"].unique())
    assert clases_presentes.issubset(set(ORDEN_CLASES)), "Contiene clases fuera del catalogo de 5 clases"


def test_paquete_modelo_para_app() -> None:
    """Verifica que el modelo cargado para la app tenga el estimador y mensajes operativos."""
    paquete = cargar_paquete_modelo()
    assert "modelo" in paquete
    assert "columnas" in paquete
    assert "mensajes_operador" in paquete

    # Probar inferencia individual sobre la primera muestra de ejemplos
    ruta_ejemplos = obtener_ruta_datos_procesados("ejemplos_prueba.csv")
    df_ej = pd.read_csv(ruta_ejemplos)
    primera = df_ej.iloc[0]

    resultado = predecir_falla(
        Va=primera["Va"], Vb=primera["Vb"], Vc=primera["Vc"],
        Ia=primera["Ia"], Ib=primera["Ib"], Ic=primera["Ic"],
        paquete=paquete,
    )

    assert resultado["diagnostico"] in ORDEN_CLASES
    assert 0.0 <= resultado["confianza"] <= 1.0
    assert len(resultado["mensaje_operador"]) > 0


def test_inferencia_por_lote() -> None:
    """Simula la funcionalidad de la pestaña de procesamiento masivo CSV."""
    paquete = cargar_paquete_modelo()
    modelo = paquete["modelo"]

    ruta_ejemplos = obtener_ruta_datos_procesados("ejemplos_prueba.csv")
    df_lote = pd.read_csv(ruta_ejemplos)[COLUMNAS]

    predicciones = modelo.predict(df_lote)
    probabilidades = modelo.predict_proba(df_lote)

    assert len(predicciones) == len(df_lote)
    assert probabilidades.shape == (len(df_lote), len(modelo.classes_))


def test_shap_explicador_unitaria_dimensiones() -> None:
    """Verifica que la explicación local devuelva exactamente un tensor de 6 valores numéricos."""
    import shap

    paquete = cargar_paquete_modelo()
    modelo = paquete["modelo"]
    if hasattr(modelo, "named_steps"):
        estimador = modelo.named_steps.get("randomforestclassifier", modelo)
    else:
        estimador = modelo

    explicador = shap.TreeExplainer(estimador)
    fila_test = pd.DataFrame([{
        "Va": 0.40, "Vb": -0.13, "Vc": -0.27,
        "Ia": -151.29, "Ib": -9.68, "Ic": 85.80,
    }])[COLUMNAS]

    sv_raw = explicador.shap_values(fila_test)
    clases = list(estimador.classes_)
    sv_norm = normalizar_shap(sv_raw, 1, len(COLUMNAS), len(clases))

    assert sv_norm.shape == (1, 6, len(clases)), f"Forma inesperada {sv_norm.shape}"
    valores_clase = sv_norm[0, :, 0]
    assert len(valores_clase) == 6
    assert not np.isnan(valores_clase).any()


def test_pagina_error_404_modulo() -> None:
    """Verifica que la página personalizada 404 importe correctamente y sea ejecutable."""
    from app.views.not_found import pagina_error_404
    from app.views import pagina_error_404 as pagina_error_exportada

    assert callable(pagina_error_404), "pagina_error_404 debe ser una función ejecutable"
    assert pagina_error_404 is pagina_error_exportada, "Debe estar exportada en app.views"

