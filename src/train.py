"""Módulo de entrenamiento, validación cruzada y serialización del modelo oficial.

Ejecuta el pipeline completo de ajuste de los 3 modelos supervisados,
evaluación comparativa, validación cruzada estratificada (k=5) y exportación
del artefacto empaquetado en models/best_model.pkl y models/modelo_fallos_rf.joblib.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import StratifiedKFold, cross_val_score

from src.data_processing import (
    cargar_datos,
    dividir_datos,
    exportar_ejemplos_prueba,
    mapear_clases,
)
from src.evaluate import (
    generar_reporte_metricas,
    graficar_comparativa_f1,
    graficar_distribucion_clases,
    graficar_explicabilidad_shap_global,
    graficar_matriz_confusion,
    graficar_shap_heatmap,
    graficar_shap_local,
    guardar_metricas,
)
from src.model import crear_modelos
from src.utils import (
    COLUMNAS,
    MENSAJES_OPERADOR,
    NOTA_CLASES,
    ORDEN_6,
    ORDEN_CLASES,
    SEMILLA,
    obtener_raiz_proyecto,
    obtener_ruta_modelo,
    obtener_ruta_resultados,
)


def entrenar_modelo(
    modelo: BaseEstimator,
    X_ent: pd.DataFrame,
    y_ent: pd.Series,
) -> Tuple[BaseEstimator, float]:
    """Entrena un modelo individual y cronometra el tiempo de ajuste.

    Args:
        modelo: Estimador de scikit-learn.
        X_ent: Muestras de entrenamiento.
        y_ent: Etiquetas de entrenamiento.

    Returns:
        Tupla con (modelo_entrenado, tiempo_en_segundos).
    """
    t0 = time.time()
    modelo.fit(X_ent, y_ent)
    t_ent = time.time() - t0
    return modelo, t_ent


def entrenar_y_comparar_todos(
    X_ent: pd.DataFrame,
    y_ent: pd.Series,
    X_pru: pd.DataFrame,
    y_pru: pd.Series,
    random_state: int = SEMILLA,
) -> Tuple[pd.DataFrame, Dict[str, BaseEstimator]]:
    """Entrena los 3 modelos supervisados y construye la tabla comparativa de desempeño.

    Args:
        X_ent: Predictoras de entrenamiento.
        y_ent: Objetivo de entrenamiento.
        X_pru: Predictoras de prueba.
        y_pru: Objetivo de prueba.
        random_state: Semilla pseudoaleatoria.

    Returns:
        Tupla con (tabla_comparativa_df, modelos_entrenados_dict).
    """
    catalogo = crear_modelos(random_state=random_state)
    resultados: List[Dict[str, Any]] = []
    modelos_entrenados: Dict[str, BaseEstimator] = {}

    for nombre, modelo in catalogo.items():
        modelo_fit, t_ent = entrenar_modelo(modelo, X_ent, y_ent)
        p_ent = modelo_fit.predict(X_ent)
        p_pru = modelo_fit.predict(X_pru)

        acc_ent = float(accuracy_score(y_ent, p_ent))
        acc_pru = float(accuracy_score(y_pru, p_pru))
        gap = acc_ent - acc_pru
        f1m_pru = float(f1_score(y_pru, p_pru, average="macro"))

        resultados.append({
            "Modelo": nombre,
            "Acc. entrenamiento": acc_ent,
            "Acc. prueba": acc_pru,
            "Brecha (gap)": gap,
            "F1 macro (prueba)": f1m_pru,
            "Tiempo entrenamiento (s)": t_ent,
        })
        modelos_entrenados[nombre] = modelo_fit

    tabla = pd.DataFrame(resultados)
    return tabla, modelos_entrenados


def ejecutar_validacion_cruzada(
    modelos: Dict[str, BaseEstimator],
    X: pd.DataFrame,
    y: pd.Series,
    n_splits: int = 5,
    random_state: int = SEMILLA,
) -> Dict[str, Dict[str, Any]]:
    """Ejecuta StratifiedKFold con shuffle obligatorio y scoring f1_macro.

    Args:
        modelos: Diccionario de modelos a validar.
        X: Dataset completo de predictoras.
        y: Serie completa de etiquetas.
        n_splits: Número de pliegues (5 por defecto).
        random_state: Semilla pseudoaleatoria.

    Returns:
        Diccionario con media, desviación estándar y pliegues individuales por modelo.
    """
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    resumen_cv: Dict[str, Dict[str, Any]] = {}

    for nombre, modelo in modelos.items():
        # Clonamos o creamos instancia limpia para el cross-validation
        puntajes = cross_val_score(modelo, X, y, cv=cv, scoring="f1_macro")
        resumen_cv[nombre] = {
            "media": float(puntajes.mean()),
            "std": float(puntajes.std()),
            "pliegues": [float(p) for p in puntajes],
        }

    return resumen_cv


def serializar_paquete_modelo(
    rf_modelo: BaseEstimator,
    ruta_salida: Path | str | None = None,
    columnas: List[str] = COLUMNAS,
    mensajes_operador: Dict[str, str] = MENSAJES_OPERADOR,
    nota_clases: str = NOTA_CLASES,
    descripcion: str = "Random Forest (100 árboles) con 6 lecturas trifásicas, 5 clases",
) -> Path:
    """Serializa el modelo y su contrato de inferencia completo con joblib (compress=3).

    Guarda en models/best_model.pkl y genera réplicas de compatibilidad en
    models/modelo_fallos_rf.joblib y en la raíz del repositorio.

    Args:
        rf_modelo: Objeto RandomForestClassifier entrenado.
        ruta_salida: Ruta principal de guardado.
        columnas: Lista de columnas en orden estricto.
        mensajes_operador: Diccionario clase -> recomendación operativa.
        nota_clases: Justificación física para auditoría.
        descripcion: Texto descriptivo del modelo.

    Returns:
        Path del archivo principal generado.
    """
    paquete: Dict[str, Any] = {
        "modelo": rf_modelo,
        "columnas": columnas,
        "clases": list(rf_modelo.classes_),
        "mensajes_operador": mensajes_operador,
        "nota_clases": nota_clases,
        "descripcion": descripcion,
    }

    if ruta_salida is None:
        ruta_oficial = obtener_ruta_modelo("best_model.pkl")
    else:
        ruta_oficial = Path(ruta_salida)

    ruta_oficial.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(paquete, ruta_oficial, compress=3)

    # Réplica oficial en models/modelo_fallos_rf.joblib
    ruta_joblib = obtener_ruta_modelo("modelo_fallos_rf.joblib")
    if ruta_joblib != ruta_oficial:
        joblib.dump(paquete, ruta_joblib, compress=3)

    # Réplica en models/model_v1.pkl para versionado formal
    ruta_v1 = obtener_ruta_modelo("model_v1.pkl")
    try:
        joblib.dump(paquete, ruta_v1, compress=3)
    except Exception:
        pass

    return ruta_oficial


def ejecutar_pipeline_entrenamiento() -> Dict[str, Any]:
    """Ejecuta de principio a fin todo el flujo de entrenamiento y evaluación.

    1. Carga classData.csv y aplica auditoría.
    2. Aplica el mapeo a 5 clases físicas.
    3. Realiza la partición estratificada 80/20.
    4. Entrena y compara Regresión Logística, Random Forest y SVM.
    5. Ejecuta validación cruzada k=5.
    6. Exporta el modelo oficial a models/best_model.pkl.
    7. Genera métricas SMART y figuras de resultados.
    8. Exporta ejemplos de prueba a data/processed/ejemplos_prueba.csv.

    Returns:
        Diccionario con los resultados del pipeline.
    """
    print("=================================================================")
    print("ELECTROVOLT: Iniciando Pipeline de Entrenamiento Modular")
    print("=================================================================")

    # 1. Carga de datos
    df_crudo = cargar_datos()
    print(f"[OK] Datos cargados correctamente: {df_crudo.shape[0]} filas, {df_crudo.shape[1]} columnas.")

    # 2. Mapeo a 5 clases
    df = mapear_clases(df_crudo, modo="5_clases")
    print(f"[OK] Mapeo a 5 clases físicas completado. Clases: {ORDEN_CLASES}")

    # 3. Partición estratificada 80/20
    X_ent, X_pru, y_ent, y_pru, idx_ent, idx_pru = dividir_datos(
        df, columnas=COLUMNAS, columna_objetivo="clase", test_size=0.20, random_state=SEMILLA
    )
    print(f"[OK] Partición 80/20 completada: Train={len(X_ent)}, Test={len(X_pru)}")

    # 4. Entrenamiento y comparativa
    print("\nEntrenando catálogo de modelos supervisados...")
    tabla_comparativa, modelos_entrenados = entrenar_y_comparar_todos(
        X_ent, y_ent, X_pru, y_pru, random_state=SEMILLA
    )
    print("\n--- Tabla Comparativa de Modelos ---")
    print(tabla_comparativa.round(4).to_string(index=False))

    # 5. Validación Cruzada k=5
    print("\nEjecutando StratifiedKFold (k=5)...")
    modelos_cv = {
        "Random Forest": crear_modelos(random_state=SEMILLA)["Random Forest"],
        "SVM (RBF)": crear_modelos(random_state=SEMILLA)["SVM (RBF)"],
    }
    res_cv = ejecutar_validacion_cruzada(modelos_cv, df[COLUMNAS], df["clase"], n_splits=5)
    for m_nom, datos_cv in res_cv.items():
        print(f"[OK] CV {m_nom}: F1-macro = {datos_cv['media']:.4f} ± {datos_cv['std']:.4f}")

    # 6. Selección y serialización del modelo ganador (Random Forest)
    rf_ganador = modelos_entrenados["Random Forest"]
    ruta_modelo = serializar_paquete_modelo(rf_ganador)
    print(f"\n[OK] Modelo serializado exitosamente en: {ruta_modelo}")

    # 7. Evaluación contra Metas SMART y exportación
    t_ent_rf = float(
        tabla_comparativa.loc[tabla_comparativa["Modelo"] == "Random Forest", "Tiempo entrenamiento (s)"].iloc[0]
    )
    pred_pru = rf_ganador.predict(X_pru)
    reporte = generar_reporte_metricas(
        y_real=y_pru,
        y_pred=pred_pru,
        modelo=rf_ganador,
        X_uno=X_pru.iloc[[0]],
        X_pru=X_pru,
        tiempo_entrenamiento=t_ent_rf,
        clases=ORDEN_CLASES,
    )

    print("\n--- Cumplimiento de Metas SMART ---")
    print(reporte["tabla_smart"].to_string(index=False))

    ruta_metricas = guardar_metricas(reporte["metricas_json"])
    print(f"[OK] Métricas exportadas a: {ruta_metricas}")

    # 8. Generación de las 7 Figuras Oficiales (Rule 04)
    print("\nGenerando las 7 figuras de resultados...")
    ruta_fig = obtener_ruta_resultados("figures")
    graficar_distribucion_clases(
        df, columna="clase_6", orden=ORDEN_6,
        titulo="Muestras por Clase Original (6 Clases)", color="steelblue",
        ruta_guardado=ruta_fig / "distribucion_6_clases.png",
    )
    graficar_distribucion_clases(
        df, columna="clase", orden=ORDEN_CLASES,
        titulo="Muestras por Clase Ajustada (5 Clases)", color="seagreen",
        ruta_guardado=ruta_fig / "distribucion_5_clases.png",
    )
    graficar_matriz_confusion(y_pru, pred_pru, clases=ORDEN_CLASES, ruta_guardado=ruta_fig / "matriz_confusion.png")
    graficar_comparativa_f1(tabla_comparativa, ruta_guardado=ruta_fig / "f1_comparativa_modelos.png")
    graficar_explicabilidad_shap_global(rf_ganador, X_pru, clases=ORDEN_CLASES, columnas=COLUMNAS, ruta_guardado=ruta_fig / "shap_importancia_global.png")
    graficar_shap_heatmap(rf_ganador, X_pru, clases=ORDEN_CLASES, columnas=COLUMNAS, ruta_guardado=ruta_fig / "shap_heatmap_clases.png")

    # Muestra representativa de prueba para SHAP local (una falla trifásica)
    idx_ejemplo = y_pru[y_pru == "Trifásica"].index[0]
    fila_ejemplo = X_pru.loc[[idx_ejemplo]]
    graficar_shap_local(rf_ganador, fila_ejemplo, clases=ORDEN_CLASES, columnas=COLUMNAS, ruta_guardado=ruta_fig / "shap_explicacion_local.png")
    print(f"[OK] 7 figuras generadas y guardadas en {ruta_fig}")

    # 9. Ejemplos de prueba para la interfaz web
    ejemplos = exportar_ejemplos_prueba(df, idx_pru, n_por_clase=3)
    print(f"[OK] {len(ejemplos)} ejemplos de prueba guardados en data/processed/ejemplos_prueba.csv")

    print("\n=================================================================")
    print("Pipeline de Entrenamiento finalizado con éxito.")
    print("=================================================================")

    return {
        "tabla_comparativa": tabla_comparativa,
        "resumen_cv": res_cv,
        "reporte_metricas": reporte,
    }


if __name__ == "__main__":
    ejecutar_pipeline_entrenamiento()
