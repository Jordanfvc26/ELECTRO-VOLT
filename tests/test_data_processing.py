"""Pruebas unitarias para el módulo de procesamiento de datos (src/data_processing.py).

Verifica la integridad de carga de classData.csv, calidad de datos (0 nulos, 0 duplicados),
mapeo de 6 y 5 clases físicas, partición estratificada 80/20 y feature engineering.
"""

from __future__ import annotations

import pandas as pd
import pytest

from src.data_processing import (
    agregar_feature_engineering,
    cargar_datos,
    dividir_datos,
    exportar_ejemplos_prueba,
    mapear_clases,
    verificar_calidad_datos,
)
from src.utils import (
    COLUMNAS,
    COLUMNAS_FE_13,
    MAPA_6,
    ORDEN_6,
    ORDEN_CLASES,
    SEMILLA,
    obtener_ruta_datos_procesados,
)


@pytest.fixture(scope="module")
def df_crudo() -> pd.DataFrame:
    """Fixture que carga el dataset crudo una sola vez para la suite de pruebas."""
    return cargar_datos()


def test_cargar_datos_valido(df_crudo: pd.DataFrame) -> None:
    """Verifica que classData.csv se carga con 7,861 filas y las 10 columnas obligatorias."""
    assert isinstance(df_crudo, pd.DataFrame), "El objeto cargado debe ser un DataFrame de pandas"
    assert df_crudo.shape[0] == 7861, f"Se esperaban 7,861 filas, se obtuvieron {df_crudo.shape[0]}"
    columnas_esperadas = {"G", "C", "B", "A", "Ia", "Ib", "Ic", "Va", "Vb", "Vc"}
    assert columnas_esperadas.issubset(set(df_crudo.columns)), "Faltan columnas requeridas en el dataset"


def test_calidad_datos_sin_nulos_ni_duplicados(df_crudo: pd.DataFrame) -> None:
    """Verifica la ausencia total de valores nulos y registros duplicados."""
    calidad = verificar_calidad_datos(df_crudo)
    assert calidad["valores_nulos"] == 0, "No deben existir valores nulos en classData.csv"
    assert calidad["filas_duplicadas"] == 0, "No deben existir filas duplicadas en classData.csv"
    assert calidad["bloques_secuenciales"] is None or calidad["bloques_secuenciales"] > 0


def test_mapeo_6_clases(df_crudo: pd.DataFrame) -> None:
    """Verifica que el mapeo a 6 clases asigna correctamente las tuplas (G, C, B, A)."""
    df_6 = mapear_clases(df_crudo, modo="6_clases")
    assert "clase_6" in df_6.columns
    assert "clase" in df_6.columns

    clases_detectadas = set(df_6["clase_6"].unique())
    assert clases_detectadas == set(ORDEN_6), f"Las clases detectadas {clases_detectadas} no coinciden con {ORDEN_6}"

    # Validar tupla específica (0, 0, 0, 0) -> Normal
    normales = df_6[(df_6["G"] == 0) & (df_6["C"] == 0) & (df_6["B"] == 0) & (df_6["A"] == 0)]
    assert (normales["clase_6"] == "Normal").all()

    # Validar tupla (1, 1, 1, 1) -> LLLG
    lllg = df_6[(df_6["G"] == 1) & (df_6["C"] == 1) & (df_6["B"] == 1) & (df_6["A"] == 1)]
    assert (lllg["clase_6"] == "LLLG").all()


def test_mapeo_5_clases_fusion_trifasica(df_crudo: pd.DataFrame) -> None:
    """Verifica que en 5 clases LLL y LLLG se fusionen en la clase 'Trifásica'."""
    df_5 = mapear_clases(df_crudo, modo="5_clases")
    assert "clase" in df_5.columns

    clases_5 = set(df_5["clase"].unique())
    assert clases_5 == set(ORDEN_CLASES), f"Las clases 5 {clases_5} deben coincidir con {ORDEN_CLASES}"

    # Verificar que no queden etiquetas LLL o LLLG sueltas en la columna de producción
    assert "LLL" not in clases_5
    assert "LLLG" not in clases_5

    # Comprobar la suma de muestras en Trifásica (1,096 LLL + 1,133 LLLG = 2,229)
    conteo_trifasica = int((df_5["clase"] == "Trifásica").sum())
    assert conteo_trifasica == 2229, f"Se esperaban 2,229 muestras trifásicas, se obtuvieron {conteo_trifasica}"


def test_dividir_datos_estratificacion_y_proporcion(df_crudo: pd.DataFrame) -> None:
    """Verifica que la partición 80/20 preserva la proporción de clases y shuffle=True."""
    df_5 = mapear_clases(df_crudo, modo="5_clases")
    X_ent, X_pru, y_ent, y_pru, idx_ent, idx_pru = dividir_datos(
        df_5, columnas=COLUMNAS, columna_objetivo="clase", test_size=0.20, random_state=SEMILLA
    )

    total = len(df_5)
    assert len(X_ent) == 6288, f"Train debe tener 6,288 muestras, tiene {len(X_ent)}"
    assert len(X_pru) == 1573, f"Test debe tener 1,573 muestras, tiene {len(X_pru)}"
    assert len(idx_ent) + len(idx_pru) == total
    assert len(set(idx_ent).intersection(set(idx_pru))) == 0, "No debe haber solapamiento entre train y test"

    # Verificar estratificación (proporción similar en train y test)
    prop_ent = y_ent.value_counts(normalize=True).to_dict()
    prop_pru = y_pru.value_counts(normalize=True).to_dict()
    for c in ORDEN_CLASES:
        assert abs(prop_ent[c] - prop_pru[c]) < 0.01, f"Desbalance estratificado en clase {c}"


def test_feature_engineering_13_variables(df_crudo: pd.DataFrame) -> None:
    """Verifica que agregar_feature_engineering añada las 7 variables residuales y extremas."""
    df_fe = agregar_feature_engineering(df_crudo)
    for col in COLUMNAS_FE_13:
        assert col in df_fe.columns, f"Falta la columna generada: {col}"

    # Comprobar fórmula de I0
    i0_calculado = df_fe["Ia"] + df_fe["Ib"] + df_fe["Ic"]
    pd.testing.assert_series_equal(df_fe["I0"], i0_calculado, check_names=False)

    # Comprobar que abs_I0 sea no-negativo
    assert (df_fe["abs_I0"] >= 0).all()


def test_exportar_ejemplos_prueba(df_crudo: pd.DataFrame, tmp_path) -> None:
    """Verifica que la exportación de ejemplos genere un CSV con 3 muestras por clase."""
    df_5 = mapear_clases(df_crudo, modo="5_clases")
    _, _, _, _, _, idx_pru = dividir_datos(df_5, test_size=0.20, random_state=SEMILLA)

    ruta_tmp = tmp_path / "ejemplos_test.csv"
    ejemplos = exportar_ejemplos_prueba(df_5, idx_pru, ruta_salida=ruta_tmp, n_por_clase=3)

    assert ruta_tmp.exists(), "El archivo de ejemplos debe haberse creado"
    assert len(ejemplos) == 15, f"Deben ser 15 muestras (3 × 5 clases), se obtuvieron {len(ejemplos)}"
    assert list(ejemplos.columns) == COLUMNAS + ["clase"]
