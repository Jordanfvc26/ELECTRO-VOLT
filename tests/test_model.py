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
from src.utils import (
    COLUMNAS,
    ORDEN_CLASES,
    SEMILLA,
    UMBRAL_CONFIANZA_MINIMA,
    UMBRAL_RETORNO_TIERRA_A,
    determinar_estados_fases,
    obtener_ruta_modelo,
    validar_rango_senales,
)


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


def test_validar_rango_senales_ood() -> None:
    """Verifica que validar_rango_senales detecte correctamente valores fuera del dominio de entrenamiento."""
    # Señal nominal típica dentro del rango [-0.65, 0.65] p.u. y [-900, 900] A
    valido, anomalias = validar_rango_senales(0.1, -0.1, 0.0, 100.0, -100.0, 0.0)
    assert valido is True
    assert len(anomalias) == 0

    # Prueba Jorge: Vc = -1.2 (fuera de rango)
    valido_vc, anomalias_vc = validar_rango_senales(0.0, 0.0, -1.2, 0.0, 0.0, 0.0)
    assert valido_vc is False
    assert any("Vc" in a for a in anomalias_vc)

    # Corriente anómala fuera de [-900, 900]
    valido_ia, anomalias_ia = validar_rango_senales(0.0, 0.0, 0.0, 1200.0, 0.0, 0.0)
    assert valido_ia is False
    assert any("Ia" in a for a in anomalias_ia)


def test_deteccion_baja_confianza_con_ceros(paquete_modelo) -> None:
    """Verifica que cuando las señales son todas 0, el modelo registre confianza < 80% y flag de baja fiabilidad."""
    res = predecir_falla(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, paquete=paquete_modelo)
    assert res["confianza"] < UMBRAL_CONFIANZA_MINIMA, f"La confianza ({res['confianza']}) debería ser < 0.80"
    assert res["confianza_baja"] is True


def test_umbral_retorno_tierra_observacion_jorge() -> None:
    """Verifica que corrientes residuales |In| > 20 A indiquen retorno por tierra."""
    # Prueba Jorge: Ia = 32, Ib = -32, Ic = 55 (suma In = 55 A > 20 A)
    ia, ib, ic = 32.0, -32.0, 55.0
    corriente_n = ia + ib + ic
    assert abs(corriente_n) > UMBRAL_RETORNO_TIERRA_A, f"In ({corriente_n} A) debe superar el umbral de {UMBRAL_RETORNO_TIERRA_A} A"


def test_determinar_estados_fases_coherencia() -> None:
    """Verifica que las tarjetas de fases y el diagnóstico nunca se contradigan (Jorge Obs 5)."""
    # 1. Normal debe salir 100% en verde
    fa, fb, fc, fg = determinar_estados_fases("Normal", corriente_n=50.0)
    assert not fa and not fb and not fc and not fg, "Normal debe tener todas las fases en verde (nominal)"

    # 2. LG: Fase A y Tierra en alarma
    fa, fb, fc, fg = determinar_estados_fases("LG", corriente_n=100.0)
    assert fa and fg and not fb and not fc, "LG debe activar Fase A y Tierra"

    # 3. LL: Fases B y C en alarma, tierra aislada
    fa, fb, fc, fg = determinar_estados_fases("LL", corriente_n=0.0)
    assert fb and fc and not fa and not fg, "LL debe activar Fases B y C sin tierra"

    # 4. LLG: Fases A, B y Tierra en alarma
    fa, fb, fc, fg = determinar_estados_fases("LLG", corriente_n=80.0)
    assert fa and fb and fg and not fc, "LLG debe activar Fases A, B y Tierra"

    # 5. Trifásica: Las tres fases A, B, C en alarma
    fa, fb, fc, fg = determinar_estados_fases("Trifásica", corriente_n=0.0)
    assert fa and fb and fc, "Trifásica debe activar Fases A, B y C"


def test_alineacion_fases_rotacion_multicapa(paquete_modelo) -> None:
    """Verifica que fallas en Fase B y Fase C sean reconocidas con alta confianza mediante alineación rotacional."""
    from src.data_processing import cargar_datos, mapear_clases
    from src.utils import obtener_ruta_datos_raw

    df_raw = cargar_datos(obtener_ruta_datos_raw())
    df_proc = mapear_clases(df_raw)

    # 1. Caso LG original en Fase A
    lg_original = df_proc[df_proc["clase"] == "LG"].iloc[5]
    va, vb, vc = lg_original["Va"], lg_original["Vb"], lg_original["Vc"]
    ia, ib, ic = lg_original["Ia"], lg_original["Ib"], lg_original["Ic"]

    res_lg_a = predecir_falla(va, vb, vc, ia, ib, ic, paquete=paquete_modelo)
    assert res_lg_a["diagnostico"] == "LG"
    assert res_lg_a["fases_afectadas"] == ["A"]
    assert "Fase A" in res_lg_a["descripcion_fases"]

    # 2. Caso LG rotado a Fase B (B<-A, C<-B, A<-C)
    res_lg_b = predecir_falla(vc, va, vb, ic, ia, ib, paquete=paquete_modelo)
    assert res_lg_b["diagnostico"] == "LG", f"Falla en Fase B debe reconocerse como LG, obtuvo {res_lg_b['diagnostico']}"
    assert res_lg_b["fases_afectadas"] == ["B"], f"Fase afectada debe ser B, obtuvo {res_lg_b['fases_afectadas']}"
    assert res_lg_b["confianza"] >= 0.70
    assert "Fase B" in res_lg_b["descripcion_fases"]

    # 3. Caso LG rotado a Fase C (C<-A, A<-B, B<-C)
    res_lg_c = predecir_falla(vb, vc, va, ib, ic, ia, paquete=paquete_modelo)
    assert res_lg_c["diagnostico"] == "LG"
    assert res_lg_c["fases_afectadas"] == ["C"]
    assert res_lg_c["confianza"] >= 0.70
    assert "Fase C" in res_lg_c["descripcion_fases"]

    # 4. Verificar que el sinóptico active únicamente la Fase B para LG en B
    fa, fb, fc, fg = determinar_estados_fases("LG", corriente_n=100.0, fases_afectadas=res_lg_b["fases_afectadas"])
    assert not fa and fb and not fc and fg, "Para LG en Fase B, únicamente B y Tierra deben estar en rojo"






def test_predecir_falla_validacion_inputs_nulos_o_invalidos() -> None:
    """Verifica que predecir_falla valide los tipos y levante TypeError ante inputs inválidos."""
    with pytest.raises(TypeError, match="no puede ser nula"):
        predecir_falla(None, 0.0, 0.0, 0.0, 0.0, 0.0)

    with pytest.raises(TypeError, match="debe ser un valor numérico real"):
        predecir_falla("invalido", 0.0, 0.0, 0.0, 0.0, 0.0)


def test_cargar_paquete_modelo_archivo_inexistente() -> None:
    """Verifica que cargar_paquete_modelo levante FileNotFoundError si no existe el archivo."""
    with pytest.raises(FileNotFoundError, match="No se encontró un modelo"):
        cargar_paquete_modelo("ruta_falsa/modelo.pkl")
