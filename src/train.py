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

from src.config import cargar_configuracion, obtener_logger, obtener_raiz_proyecto
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
    obtener_ruta_modelo,
    obtener_ruta_resultados,
)

logger = obtener_logger(__name__)


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

    Raises:
        TypeError: Si X_ent o y_ent no son estructuras válidas de pandas.
    """
    if not isinstance(X_ent, pd.DataFrame):
        raise TypeError(f"X_ent debe ser pd.DataFrame. Recibido: {type(X_ent)}")
    if not isinstance(y_ent, pd.Series):
        raise TypeError(f"y_ent debe ser pd.Series. Recibido: {type(y_ent)}")

    t0 = time.time()
    modelo.fit(X_ent, y_ent)
    t_ent = time.time() - t0
    logger.debug(f"Ajuste de modelo completado en {t_ent:.3f} s.")
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

    Raises:
        ValueError: Si los DataFrames de entrada están vacíos o las dimensiones no coinciden.
    """
    if X_ent.empty or y_ent.empty or X_pru.empty or y_pru.empty:
        raise ValueError("Los conjuntos de entrenamiento o prueba no pueden estar vacíos.")

    catalogo = crear_modelos(random_state=random_state)
    resultados: List[Dict[str, Any]] = []
    modelos_entrenados: Dict[str, BaseEstimator] = {}

    logger.info(f"Iniciando entrenamiento comparativo de {len(catalogo)} modelos...")

    for nombre, modelo in catalogo.items():
        logger.info(f"Entrenando modelo: {nombre}...")
        modelo_fit, t_ent = entrenar_modelo(modelo, X_ent, y_ent)
        p_ent = modelo_fit.predict(X_ent)
        p_pru = modelo_fit.predict(X_pru)

        acc_ent = float(accuracy_score(y_ent, p_ent))
        acc_pru = float(accuracy_score(y_pru, p_pru))
        gap = acc_ent - acc_pru
        f1m_pru = float(f1_score(y_pru, p_pru, average="macro"))

        logger.info(
            f"Resultado {nombre}: Acc_Train={acc_ent:.4f}, Acc_Test={acc_pru:.4f}, "
            f"F1_Macro={f1m_pru:.4f}, Gap={gap:.4f}, Tiempo={t_ent:.2f}s"
        )

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

    Raises:
        ValueError: Si n_splits < 2 o X e y difieren en longitud.
    """
    if n_splits < 2:
        raise ValueError(f"n_splits debe ser al menos 2. Recibido: {n_splits}")
    if len(X) != len(y):
        raise ValueError(f"Longitudes dispares entre X ({len(X)}) e y ({len(y)})")

    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    resumen_cv: Dict[str, Dict[str, Any]] = {}

    logger.info(f"Ejecutando validación cruzada estratificada (k={n_splits}, shuffle=True)...")

    for nombre, modelo in modelos.items():
        puntajes = cross_val_score(modelo, X, y, cv=cv, scoring="f1_macro")
        resumen_cv[nombre] = {
            "media": float(puntajes.mean()),
            "std": float(puntajes.std()),
            "pliegues": [float(p) for p in puntajes],
        }
        logger.info(f"CV {nombre}: F1-macro = {puntajes.mean():.4f} (+/- {puntajes.std():.4f})")

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

    Raises:
        IOError: Si no se puede escribir el archivo en disco.
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
    try:
        joblib.dump(paquete, ruta_oficial, compress=3)
        logger.info(f"Modelo principal serializado exitosamente en: {ruta_oficial}")
    except Exception as err:
        logger.error(f"Error crítico al serializar el modelo en {ruta_oficial}: {err}")
        raise IOError(f"Fallo al guardar {ruta_oficial}: {err}") from err

    # Réplica oficial en models/modelo_fallos_rf.joblib
    ruta_joblib = obtener_ruta_modelo("modelo_fallos_rf.joblib")
    if ruta_joblib != ruta_oficial:
        try:
            joblib.dump(paquete, ruta_joblib, compress=3)
            logger.debug(f"Réplica joblib guardada en: {ruta_joblib}")
        except Exception as err:
            logger.warning(f"No se pudo escribir la réplica joblib en {ruta_joblib}: {err}")

    # Réplica en models/model_v1.pkl para versionado formal
    ruta_v1 = obtener_ruta_modelo("model_v1.pkl")
    try:
        joblib.dump(paquete, ruta_v1, compress=3)
        logger.debug(f"Réplica de versión guardada en: {ruta_v1}")
    except Exception as err:
        logger.warning(f"No se pudo escribir la réplica v1 en {ruta_v1}: {err}")

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
    config = cargar_configuracion()
    cfg_datos = config.get("datos", {})
    cfg_cv = config.get("modelos", {}).get("validacion_cruzada", {})

    test_size = float(cfg_datos.get("test_size", 0.20))
    cv_splits = int(cfg_cv.get("n_splits", 5))

    logger.info("=================================================================")
    logger.info("ELECTROVOLT: Iniciando Pipeline de Entrenamiento Modular")
    logger.info("=================================================================")

    # 1. Carga de datos
    df_crudo = cargar_datos()
    logger.info(f"Datos cargados: {df_crudo.shape[0]} filas, {df_crudo.shape[1]} columnas.")

    # 2. Mapeo a 5 clases
    df = mapear_clases(df_crudo, modo="5_clases")
    logger.info(f"Mapeo a 5 clases físicas completado. Clases: {ORDEN_CLASES}")

    # 3. Partición estratificada 80/20
    X_ent, X_pru, y_ent, y_pru, idx_ent, idx_pru = dividir_datos(
        df, columnas=COLUMNAS, columna_objetivo="clase", test_size=test_size, random_state=SEMILLA
    )
    logger.info(f"Partición {int((1-test_size)*100)}/{int(test_size*100)} completada: Train={len(X_ent)}, Test={len(X_pru)}")

    # 4. Entrenamiento y comparativa
    tabla_comparativa, modelos_entrenados = entrenar_y_comparar_todos(
        X_ent, y_ent, X_pru, y_pru, random_state=SEMILLA
    )
    logger.info(f"\n--- Tabla Comparativa de Modelos ---\n{tabla_comparativa.round(4).to_string(index=False)}")

    # 5. Validación Cruzada k=5
    modelos_cv = {
        "Random Forest": crear_modelos(random_state=SEMILLA)["Random Forest"],
        "SVM (RBF)": crear_modelos(random_state=SEMILLA)["SVM (RBF)"],
    }
    res_cv = ejecutar_validacion_cruzada(modelos_cv, df[COLUMNAS], df["clase"], n_splits=cv_splits)

    # 6. Selección y serialización del modelo ganador (Random Forest)
    rf_ganador = modelos_entrenados["Random Forest"]
    ruta_modelo = serializar_paquete_modelo(rf_ganador)
    logger.info(f"Modelo serializado exitosamente en: {ruta_modelo}")

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

    logger.info(f"\n--- Cumplimiento de Metas SMART ---\n{reporte['tabla_smart'].to_string(index=False)}")

    ruta_metricas = guardar_metricas(reporte["metricas_json"])
    logger.info(f"Métricas exportadas a: {ruta_metricas}")

    # 8. Generación de las 7 Figuras Oficiales
    logger.info("Generando las 7 figuras de resultados...")
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
    logger.info(f"7 figuras generadas y guardadas en: {ruta_fig}")

    # 9. Ejemplos de prueba para la interfaz web
    ejemplos = exportar_ejemplos_prueba(df, idx_pru, n_por_clase=3)
    logger.info(f"{len(ejemplos)} ejemplos de prueba guardados en data/processed/ejemplos_prueba.csv")

    logger.info("=================================================================")
    logger.info("Pipeline de Entrenamiento finalizado con éxito.")
    logger.info("=================================================================")

    return {
        "tabla_comparativa": tabla_comparativa,
        "resumen_cv": res_cv,
        "reporte_metricas": reporte,
    }


if __name__ == "__main__":
    ejecutar_pipeline_entrenamiento()
