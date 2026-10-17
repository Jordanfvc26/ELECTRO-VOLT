"""Pruebas unitarias para el modelo, inferencia en tiempo real y explicabilidad XAI (src/model.py).

Verifica la carga del paquete serializado (models/best_model.pkl y models/modelo_fallos_rf.joblib),
el contrato de predicción para la app web, el benchmark de latencia (<100 ms),
el cumplimiento de umbrales SMART y la salida consistente de SHAP.
"""

from __future__ import annotations

import time
import pandas as pd
import pytest
from sklearn.metrics import accuracy_score, f1_score, recall_score

from src.data_processing import cargar_datos, dividir_datos, mapear_clases
from src.evaluate import medir_latencia_y_throughput
from src.model import cargar_paquete_modelo, crear_modelos, explicar_prediccion_shap, predecir_falla
from src.utils import COLUMNAS, ORDEN_CLASES, SEMILLA, obtener_ruta_modelo


@pytest.fixture(scope="module")
def paquete_modelo():
    """Carga el modelo serializado oficial una sola vez para las pruebas."""
    return cargar_paquete_modelo()


@pytest.fixture(scope="module")
def datos_prueba():
    """Genera el conjunto de prueba 80/20 sobre classData.csv para auditoría."""
    df = mapear_clases(cargar_datos(), modo="5_clases")
    X_ent, X_pru, y_ent, y_pru, _, _ = dividir_datos(df, test_size=0.20, random_state=SEMILLA)
    return X_ent, X_pru, y_ent, y_pru


def test_paquete_modelo_estructura_y_llaves(paquete_modelo) -> None:
    """Verifica que el paquete serializado cumpla el contrato oficial de estructura."""
    assert isinstance(paquete_modelo, dict), "El paquete debe ser un diccionario"
    llaves_requeridas = {"modelo", "columnas", "clases", "mensajes_operador", "nota_clases"}
    assert llaves_requeridas.issubset(set(paquete_modelo.keys())), "Faltan llaves en el paquete"

    assert paquete_modelo["columnas"] == COLUMNAS
    assert set(paquete_modelo["clases"]) == set(ORDEN_CLASES)
    for c in ORDEN_CLASES:
        assert c in paquete_modelo["mensajes_operador"], f"Falta mensaje operativo para la clase {c}"


def test_paquete_modelo_carga_desde_ambas_rutas() -> None:
    """Verifica que tanto best_model.pkl como modelo_fallos_rf.joblib sean válidos."""
    ruta_best = obtener_ruta_modelo("best_model.pkl")
    ruta_rf = obtener_ruta_modelo("modelo_fallos_rf.joblib")

    assert ruta_best.exists(), f"No existe {ruta_best}"
    assert ruta_rf.exists(), f"No existe {ruta_rf}"

    p1 = cargar_paquete_modelo(ruta_best)
    p2 = cargar_paquete_modelo(ruta_rf)
    assert p1["clases"] == p2["clases"]


def test_catalogo_modelos_crear_modelos() -> None:
    """Verifica la instanciación de los 3 modelos supervisados requeridos."""
    modelos = crear_modelos(random_state=SEMILLA)
    assert set(modelos.keys()) == {"Regresión Logística", "Random Forest", "SVM (RBF)"}


def test_predecir_falla_contrato_y_probabilidades(paquete_modelo) -> None:
    """Verifica que predecir_falla devuelva diagnóstico, confianza y mensaje correctos."""
    # Señal sintética de prueba
    res = predecir_falla(
        Va=0.1, Vb=-0.1, Vc=0.0,
        Ia=500.0, Ib=-500.0, Ic=0.0,
        paquete=paquete_modelo,
    )

    assert isinstance(res, dict)
    assert "diagnostico" in res
    assert "confianza" in res
    assert "probabilidades" in res
    assert "mensaje_operador" in res

    assert res["diagnostico"] in ORDEN_CLASES
    assert 0.0 <= res["confianza"] <= 1.0

    probs = res["probabilidades"]
    assert set(probs.keys()) == set(ORDEN_CLASES)
    suma_probs = sum(probs.values())
    assert abs(suma_probs - 1.0) < 0.02, f"La suma de probabilidades {suma_probs} debe ser ~1.0"

    assert len(res["mensaje_operador"]) > 10, "El mensaje para el operador debe ser descriptivo"


def test_metricas_smart_superan_umbrales(paquete_modelo, datos_prueba) -> None:
    """Verifica que el modelo final supere los umbrales mínimos SMART en test."""
    _, X_pru, _, y_pru = datos_prueba
    rf = paquete_modelo["modelo"]
    pred = rf.predict(X_pru)

    acc = accuracy_score(y_pru, pred)
    f1m = f1_score(y_pru, pred, average="macro")
    recall_min = recall_score(y_pru, pred, average=None, labels=ORDEN_CLASES).min()

    assert acc >= 0.90, f"Accuracy ({acc:.4f}) debe ser >= 0.90"
    assert f1m >= 0.90, f"F1-macro ({f1m:.4f}) debe ser >= 0.90"
    assert recall_min >= 0.85, f"Recall mínimo ({recall_min:.4f}) debe ser >= 0.85"


def test_latencia_individual_menor_a_100ms(paquete_modelo, datos_prueba) -> None:
    """Verifica que el tiempo promedio de inferencia por muestra en CPU sea < 100 ms."""
    _, X_pru, _, _ = datos_prueba
    rf = paquete_modelo["modelo"]
    X_uno = X_pru.iloc[[0]]

    lat_ms, throughput = medir_latencia_y_throughput(rf, X_uno, X_pru, n_iteraciones=50)
    assert lat_ms < 100.0, f"Latencia media ({lat_ms:.2f} ms) debe ser inferior a 100 ms"
    assert throughput >= 500.0, f"Throughput ({throughput:.1f}/s) debe ser >= 500 muestras/s"


def test_explicar_prediccion_shap_consistencia(paquete_modelo, datos_prueba) -> None:
    """Verifica que explicar_prediccion_shap devuelva 6 valores atribuidos a las señales."""
    _, X_pru, _, _ = datos_prueba
    fila_individual = X_pru.iloc[[0]]

    shap_series = explicar_prediccion_shap(paquete_modelo, fila_individual)
    assert isinstance(shap_series, pd.Series)
    assert len(shap_series) == 6, "SHAP debe devolver exactamente 6 valores de importancia"
    assert not shap_series.isna().any(), "No debe haber valores NaN en la explicación SHAP"
