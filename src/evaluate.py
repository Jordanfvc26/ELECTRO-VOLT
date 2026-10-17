"""Módulo de evaluación de modelos, benchmarking de inferencia, métricas SMART y XAI.

Calcula métricas de clasificación multiclase, evalúa el cumplimiento de metas SMART,
mide latencia (<100 ms) y throughput (muestras/s), normaliza tensores SHAP y exporta
figuras de alta resolución a results/figures/ y métricas a results/metrics/metricas.json.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.base import BaseEstimator
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    recall_score,
)

from src.utils import (
    COLUMNAS,
    NOTA_CLASES,
    ORDEN_CLASES,
    SEMILLA,
    guardar_json,
    obtener_raiz_proyecto,
    obtener_ruta_resultados,
)


def normalizar_shap(
    sv: Any,
    n_muestras: int,
    n_vars: int,
    n_clases: int,
) -> np.ndarray:
    """Homogeneiza las dimensiones del arreglo de valores SHAP a (n_muestras, n_vars, n_clases).

    Maneja diferencias entre versiones de shap y scikit-learn (listas de arrays o
    tensores 3D transcurridos).

    Args:
        sv: Salida cruda de explicador.shap_values(X).
        n_muestras: Número esperado de muestras.
        n_vars: Número esperado de variables.
        n_clases: Número esperado de clases.

    Returns:
        Arreglo tridimensional con forma (n_muestras, n_vars, n_clases).

    Raises:
        ValueError: Si la forma obtenida no se puede adecuar al tensor objetivo.
    """
    if isinstance(sv, list):
        sv = np.stack(sv, axis=-1)
    sv = np.asarray(sv)

    if sv.shape == (n_muestras, n_vars, n_clases):
        return sv
    if sv.shape == (n_clases, n_muestras, n_vars):
        return np.transpose(sv, (1, 2, 0))

    raise ValueError(
        f"Forma inesperada de valores SHAP: {sv.shape}. "
        f"Se esperaba transposición hacia ({n_muestras}, {n_vars}, {n_clases})."
    )


def medir_latencia_y_throughput(
    modelo: BaseEstimator,
    X_uno: pd.DataFrame,
    X_lote: pd.DataFrame,
    n_iteraciones: int = 100,
) -> Tuple[float, float]:
    """Mide el rendimiento computacional de inferencia en CPU estándar.

    Calcula la latencia media por predicción individual en milisegundos
    y la capacidad de procesamiento por segundo (throughput) en lote.

    Args:
        modelo: Estimador o Pipeline entrenado.
        X_uno: DataFrame con una sola muestra (1 fila).
        X_lote: DataFrame con el lote completo de prueba.
        n_iteraciones: Número de repeticiones para promediar la latencia individual.

    Returns:
        Tupla con (latencia_ms, throughput_muestras_seg).
    """
    # Medición de latencia individual con predict_proba
    t0 = time.time()
    for _ in range(n_iteraciones):
        modelo.predict_proba(X_uno)
    latencia_ms = ((time.time() - t0) / n_iteraciones) * 1000.0

    # Medición de throughput con predicción por lote
    t0 = time.time()
    modelo.predict(X_lote)
    tiempo_lote = time.time() - t0
    throughput = len(X_lote) / tiempo_lote if tiempo_lote > 0 else 0.0

    return float(latencia_ms), float(throughput)


def evaluar_metas_smart(
    acc: float,
    f1m: float,
    recall_min: float,
    lat_ms: float,
    muestras_seg: float,
    t_ent: float,
) -> pd.DataFrame:
    """Verifica formalmente el cumplimiento de los umbrales de éxito SMART del proyecto.

    Args:
        acc: Accuracy en el conjunto de prueba.
        f1m: F1-Score macro en el conjunto de prueba.
        recall_min: Recall mínimo obtenido entre todas las clases.
        lat_ms: Latencia media individual en milisegundos.
        muestras_seg: Throughput en muestras por segundo.
        t_ent: Tiempo de entrenamiento del modelo en segundos.

    Returns:
        DataFrame con la columna de estado '¿Cumple?' (Sí / No).
    """
    metas = [
        ("Accuracy ≥ 0.90", f"{acc:.3f}", acc >= 0.90),
        ("F1 macro ≥ 0.90", f"{f1m:.3f}", f1m >= 0.90),
        ("Recall mínimo por clase ≥ 0.85", f"{recall_min:.3f}", recall_min >= 0.85),
        ("Latencia por predicción < 100 ms", f"{lat_ms:.1f} ms", lat_ms < 100.0),
        ("Throughput ≥ 500 muestras/s", f"{muestras_seg:,.0f}/s", muestras_seg >= 500.0),
        ("Tiempo de entrenamiento < 5 min", f"{t_ent:.1f} s", t_ent < 300.0),
    ]

    resumen = pd.DataFrame(metas, columns=["Meta SMART", "Resultado", "¿Cumple?"])
    resumen["¿Cumple?"] = resumen["¿Cumple?"].map({True: "Sí", False: "No"})
    return resumen


def generar_reporte_metricas(
    y_real: pd.Series,
    y_pred: np.ndarray | pd.Series,
    modelo: BaseEstimator,
    X_uno: pd.DataFrame,
    X_pru: pd.DataFrame,
    tiempo_entrenamiento: float,
    clases: List[str] = ORDEN_CLASES,
) -> Dict[str, Any]:
    """Genera el diccionario integral de métricas y la auditoría SMART.

    Args:
        y_real: Etiquetas verdaderas de prueba.
        y_pred: Etiquetas predichas por el modelo.
        modelo: Estimador entrenado.
        X_uno: DataFrame con 1 fila de prueba para benchmark.
        X_pru: DataFrame de prueba completo.
        tiempo_entrenamiento: Tiempo en segundos que tomó el entrenamiento.
        clases: Lista de clases ordenadas.

    Returns:
        Diccionario con métricas numéricas, reporte de clasificación y tabla SMART.
    """
    acc = float(accuracy_score(y_real, y_pred))
    f1m = float(f1_score(y_real, y_pred, average="macro"))
    recalls = recall_score(y_real, y_pred, average=None, labels=clases)
    recall_min = float(np.min(recalls))

    lat_ms, throughput = medir_latencia_y_throughput(modelo, X_uno, X_pru)

    tabla_smart = evaluar_metas_smart(
        acc=acc,
        f1m=f1m,
        recall_min=recall_min,
        lat_ms=lat_ms,
        muestras_seg=throughput,
        t_ent=tiempo_entrenamiento,
    )

    metricas_exportables = {
        "modelo": "Random Forest",
        "clases": clases,
        "variables_entrada": COLUMNAS,
        "accuracy_prueba": round(acc, 4),
        "f1_macro_prueba": round(f1m, 4),
        "recall_minimo_por_clase": round(recall_min, 4),
        "latencia_ms": round(lat_ms, 2),
        "throughput_muestras_por_segundo": round(throughput, 1),
        "tiempo_entrenamiento_s": round(tiempo_entrenamiento, 2),
        "nota_clases": NOTA_CLASES,
        "cumplimiento_smart": {
            row["Meta SMART"]: row["¿Cumple?"] for _, row in tabla_smart.iterrows()
        },
    }

    return {
        "metricas_json": metricas_exportables,
        "tabla_smart": tabla_smart,
        "reporte_clasificacion": classification_report(y_real, y_pred, labels=clases, digits=3),
        "matriz_confusion": confusion_matrix(y_real, y_pred, labels=clases),
    }


def guardar_metricas(
    metricas_dict: Dict[str, Any],
    ruta_salida: Path | str | None = None,
) -> Path:
    """Serializa el JSON oficial de métricas en results/metrics/metricas.json.

    Args:
        metricas_dict: Diccionario de métricas generado.
        ruta_salida: Ruta personalizada opcional.

    Returns:
        Path del archivo creado.
    """
    if ruta_salida is None:
        ruta_oficial = obtener_ruta_resultados("metrics") / "metricas.json"
    else:
        ruta_oficial = Path(ruta_salida)

    guardar_json(metricas_dict, ruta_oficial)
    return ruta_oficial


def graficar_matriz_confusion(
    y_real: pd.Series,
    y_pred: np.ndarray | pd.Series,
    clases: List[str] = ORDEN_CLASES,
    ruta_guardado: Path | str | None = None,
) -> plt.Figure:
    """Genera y guarda el mapa de calor de la Matriz de Confusión."""
    cm = confusion_matrix(y_real, y_pred, labels=clases)
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Greens",
        xticklabels=clases,
        yticklabels=clases,
        ax=ax,
    )
    ax.set_title("Matriz de Confusión — Modelo Final")
    ax.set_xlabel("Predicho")
    ax.set_ylabel("Real")
    plt.tight_layout()

    if ruta_guardado is None:
        ruta_guardado = obtener_ruta_resultados("figures") / "matriz_confusion.png"
    Path(ruta_guardado).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(ruta_guardado, dpi=300)
    return fig


def graficar_comparativa_f1(
    tabla_modelos: pd.DataFrame,
    ruta_guardado: Path | str | None = None,
) -> plt.Figure:
    """Genera y guarda el gráfico de barras comparativo de F1 macro vs la Meta SMART."""
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(
        data=tabla_modelos,
        x="Modelo",
        y="F1 macro (prueba)",
        color="steelblue",
        ax=ax,
    )
    ax.axhline(0.90, color="red", ls="--", label="Meta SMART (0.90)")
    ax.set_ylim(0, 1.05)
    ax.legend(loc="lower right")
    ax.set_title("F1 Macro en Conjunto de Prueba (5 Clases)")
    plt.tight_layout()

    if ruta_guardado is None:
        ruta_guardado = obtener_ruta_resultados("figures") / "f1_comparativa_modelos.png"
    Path(ruta_guardado).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(ruta_guardado, dpi=300)
    return fig


def graficar_explicabilidad_shap_global(
    rf_modelo: BaseEstimator,
    X_pru: pd.DataFrame,
    clases: List[str] = ORDEN_CLASES,
    columnas: List[str] = COLUMNAS,
    n_muestras: int = 100,
    ruta_guardado: Path | str | None = None,
) -> plt.Figure | None:
    """Genera y guarda los gráficos globales de SHAP (importancia global y mapa de calor)."""
    try:
        import shap

        if hasattr(rf_modelo, "named_steps"):
            estimador = rf_modelo.named_steps.get("randomforestclassifier", rf_modelo)
        else:
            estimador = rf_modelo

        muestra = X_pru.sample(min(n_muestras, len(X_pru)), random_state=SEMILLA)
        explicador = shap.TreeExplainer(estimador)
        sv_raw = explicador.shap_values(muestra)
        sv = normalizar_shap(sv_raw, len(muestra), len(columnas), len(clases))

        imp = pd.DataFrame(np.abs(sv).mean(axis=0), index=columnas, columns=list(estimador.classes_))

        fig, ejes = plt.subplots(1, 2, figsize=(14, 4.5))
        imp.mean(axis=1).sort_values().plot(kind="barh", color="teal", ax=ejes[0])
        ejes[0].set_title("Importancia Global (promedio |SHAP|)")
        ejes[0].set_xlabel("Impacto en la predicción")

        sns.heatmap(imp.loc[:, clases], annot=True, fmt=".2f", cmap="YlOrRd", ax=ejes[1])
        ejes[1].set_title("Importancia por Tipo de Falla")
        plt.tight_layout()

        if ruta_guardado is None:
            ruta_guardado = obtener_ruta_resultados("figures") / "shap_importancia_global.png"
        Path(ruta_guardado).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(ruta_guardado, dpi=300)
        return fig
    except Exception as e:
        print(f"No fue posible generar gráficos globales SHAP: {e}")
        return None


def graficar_distribucion_clases(
    df: pd.DataFrame,
    columna: str = "clase",
    orden: List[str] | None = None,
    titulo: str = "Muestras por Clase",
    color: str = "steelblue",
    ruta_guardado: Path | str | None = None,
) -> plt.Figure:
    """Genera y guarda el gráfico de barras de distribución de clases."""
    conteo = df[columna].value_counts()
    if orden is not None:
        conteo = conteo.reindex(orden)

    fig, ax = plt.subplots(figsize=(8, 4))
    conteo.plot(kind="bar", color=color, ax=ax)
    ax.set_title(titulo)
    ax.set_ylabel("Muestras")
    ax.set_xlabel("Clase")
    plt.xticks(rotation=0)
    plt.tight_layout()

    if ruta_guardado is not None:
        Path(ruta_guardado).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(ruta_guardado, dpi=300)

    return fig


def graficar_shap_heatmap(
    rf_modelo: BaseEstimator,
    X_pru: pd.DataFrame,
    clases: List[str] = ORDEN_CLASES,
    columnas: List[str] = COLUMNAS,
    n_muestras: int = 100,
    ruta_guardado: Path | str | None = None,
) -> plt.Figure | None:
    """Genera y guarda específicamente el heatmap de atribución SHAP por tipo de falla."""
    try:
        import shap

        if hasattr(rf_modelo, "named_steps"):
            estimador = rf_modelo.named_steps.get("randomforestclassifier", rf_modelo)
        else:
            estimador = rf_modelo

        muestra = X_pru.sample(min(n_muestras, len(X_pru)), random_state=SEMILLA)
        explicador = shap.TreeExplainer(estimador)
        sv_raw = explicador.shap_values(muestra)
        sv = normalizar_shap(sv_raw, len(muestra), len(columnas), len(clases))

        imp = pd.DataFrame(np.abs(sv).mean(axis=0), index=columnas, columns=list(estimador.classes_))

        fig, ax = plt.subplots(figsize=(7, 4.5))
        sns.heatmap(imp.loc[:, clases], annot=True, fmt=".2f", cmap="YlOrRd", ax=ax)
        ax.set_title("Mapa de Calor SHAP por Tipo de Falla")
        ax.set_xlabel("Tipo de Falla")
        ax.set_ylabel("Variable de Fase")
        plt.tight_layout()

        if ruta_guardado is None:
            ruta_guardado = obtener_ruta_resultados("figures") / "shap_heatmap_clases.png"
        Path(ruta_guardado).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(ruta_guardado, dpi=300)
        return fig
    except Exception as e:
        print(f"No fue posible generar heatmap SHAP: {e}")
        return None


def graficar_shap_local(
    rf_modelo: BaseEstimator,
    fila_df: pd.DataFrame,
    clases: List[str] = ORDEN_CLASES,
    columnas: List[str] = COLUMNAS,
    clase_objetivo: str | None = None,
    ruta_guardado: Path | str | None = None,
) -> plt.Figure | None:
    """Genera y guarda la explicación SHAP local para una lectura individual (muestra de operador)."""
    try:
        import shap

        if hasattr(rf_modelo, "named_steps"):
            estimador = rf_modelo.named_steps.get("randomforestclassifier", rf_modelo)
        else:
            estimador = rf_modelo

        fila_ord = fila_df[columnas].copy()
        explicador = shap.TreeExplainer(estimador)
        sv_uno = normalizar_shap(explicador.shap_values(fila_ord), 1, len(columnas), len(clases))

        clase_eval = clase_objetivo if clase_objetivo is not None else str(estimador.predict(fila_ord)[0])
        idx_c = list(estimador.classes_).index(clase_eval)
        valores = sv_uno[0, :, idx_c]

        serie = pd.Series(
            valores,
            index=[f"{c} = {fila_ord.iloc[0][c]:.2f}" for c in columnas],
        ).sort_values()

        colores = ["firebrick" if v < 0 else "seagreen" for v in serie.values]
        fig, ax = plt.subplots(figsize=(8, 4))
        serie.plot(kind="barh", color=colores, ax=ax)
        ax.set_title(
            f"Explicación SHAP Local: Diagnóstico {clase_eval}\n"
            f"(verde = empuja hacia {clase_eval}, rojo = empuja en contra)"
        )
        ax.set_xlabel("Valor SHAP (Impacto Marginal)")
        plt.tight_layout()

        if ruta_guardado is None:
            ruta_guardado = obtener_ruta_resultados("figures") / "shap_explicacion_local.png"
        Path(ruta_guardado).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(ruta_guardado, dpi=300)
        return fig
    except Exception as e:
        print(f"No fue posible generar gráfico SHAP local: {e}")
        return None
