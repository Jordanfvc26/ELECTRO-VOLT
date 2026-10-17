"""Módulo de modelado y funciones de inferencia de fallos eléctricos.

Define la arquitectura de los modelos supervisados (Regresión Logística,
Random Forest, SVM RBF), el contrato de inferencia para operadores de subestación
y la explicabilidad local con SHAP.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from src.utils import (
    COLUMNAS,
    MENSAJES_OPERADOR,
    NOTA_CLASES,
    ORDEN_CLASES,
    SEMILLA,
    obtener_raiz_proyecto,
    obtener_ruta_modelo,
)


def crear_modelos(random_state: int = SEMILLA) -> Dict[str, BaseEstimator]:
    """Instancia el catálogo de los 3 modelos supervisados comparados en el proyecto.

    Configura el escalado StandardScaler dentro de Pipelines para evitar data leakage
    y pondera las clases mediante class_weight='balanced'.

    Args:
        random_state: Semilla pseudoaleatoria para reproducibilidad.

    Returns:
        Diccionario con las instancias de Regresión Logística, Random Forest y SVM.
    """
    return {
        "Regresión Logística": make_pipeline(
            StandardScaler(),
            LogisticRegression(
                max_iter=2000,
                class_weight="balanced",
                random_state=random_state,
            ),
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=100,
            class_weight="balanced",
            random_state=random_state,
        ),
        "SVM (RBF)": make_pipeline(
            StandardScaler(),
            SVC(
                kernel="rbf",
                C=10,
                gamma="scale",
                class_weight="balanced",
                probability=True,
                random_state=random_state,
            ),
        ),
    }


def cargar_paquete_modelo(ruta_modelo: Path | str | None = None) -> Dict[str, Any]:
    """Carga el paquete del modelo serializado (.pkl o .joblib).

    Verifica la existencia del archivo en models/best_model.pkl,
    models/modelo_fallos_rf.joblib o en la raíz del proyecto.

    Args:
        ruta_modelo: Ruta explícita al archivo del modelo.

    Returns:
        Diccionario con el modelo entrenado y metadatos operativos.

    Raises:
        FileNotFoundError: Si no se localiza ningún modelo serializado.
        KeyError: Si el paquete no cumple con el contrato mínimo de estructura.
    """
    if ruta_modelo is not None:
        candidatas = [Path(ruta_modelo)]
    else:
        raiz = obtener_raiz_proyecto()
        candidatas = [
            obtener_ruta_modelo("best_model.pkl"),
            obtener_ruta_modelo("modelo_fallos_rf.joblib"),
            raiz / "modelo_fallos_rf.joblib",
            raiz / "best_model.pkl",
            Path("models/best_model.pkl"),
            Path("models/modelo_fallos_rf.joblib"),
        ]

    ruta_valida = next((p for p in candidatas if p.exists() and p.stat().st_size > 0), None)
    if ruta_valida is None:
        rutas_txt = "\n".join(f" - {p}" for p in candidatas)
        raise FileNotFoundError(
            f"No se encontró un modelo serializado válido en las rutas esperadas:\n{rutas_txt}"
        )

    paquete = joblib.load(ruta_valida)

    # Validar llaves obligatorias del contrato
    llaves_requeridas = ["modelo", "columnas", "clases", "mensajes_operador"]
    for k in llaves_requeridas:
        if k not in paquete:
            raise KeyError(f"El paquete del modelo en {ruta_valida} no contiene la llave requerida '{k}'.")

    return paquete


def predecir_falla(
    Va: float,
    Vb: float,
    Vc: float,
    Ia: float,
    Ib: float,
    Ic: float,
    paquete: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Ejecuta la inferencia diagnóstica a partir de las 6 señales eléctricas trifásicas.

    Función idéntica al contrato de la celda c24 de Jorge. Calcula la predicción,
    confianza probabilística y extrae el mensaje de maniobra técnica para el operador.

    Args:
        Va: Tensión Fase A (en p.u.)
        Vb: Tensión Fase B (en p.u.)
        Vc: Tensión Fase C (en p.u.)
        Ia: Corriente Fase A (en Amperios)
        Ib: Corriente Fase B (en Amperios)
        Ic: Corriente Fase C (en Amperios)
        paquete: Diccionario con el modelo cargado (si es None, se carga automáticamente).

    Returns:
        Diccionario con las claves:
        - diagnostico: Etiqueta de la falla detectada ('Normal', 'LG', 'LL', 'LLG', 'Trifásica').
        - confianza: Nivel de certeza de la clase ganadora (entre 0.0 y 1.0).
        - probabilidades: Diccionario clase -> probabilidad.
        - mensaje_operador: Recomendación técnica para el operador.
    """
    if paquete is None:
        paquete = cargar_paquete_modelo()

    columnas = paquete.get("columnas", COLUMNAS)
    fila = pd.DataFrame([{"Va": Va, "Vb": Vb, "Vc": Vc, "Ia": Ia, "Ib": Ib, "Ic": Ic}])[columnas]

    modelo = paquete["modelo"]
    probs = modelo.predict_proba(fila)[0]
    k = int(np.argmax(probs))
    diag = str(modelo.classes_[k])

    mensajes = paquete.get("mensajes_operador", MENSAJES_OPERADOR)
    mensaje_op = mensajes.get(diag, f"Falla detectada: {diag}. Proceder según protocolo.")

    return {
        "diagnostico": diag,
        "confianza": round(float(probs[k]), 4),
        "probabilidades": {str(c): round(float(p), 4) for c, p in zip(modelo.classes_, probs)},
        "mensaje_operador": mensaje_op,
    }


def explicar_prediccion_shap(
    paquete: Dict[str, Any],
    fila_df: pd.DataFrame,
    explicador: Any | None = None,
) -> pd.Series:
    """Calcula la atribución de importancia local (SHAP) para una lectura individual.

    Responde por qué el modelo emitió cierto diagnóstico y qué variables de fase
    contribuyeron positiva o negativamente a la decisión.

    Args:
        paquete: Diccionario del modelo serializado.
        fila_df: DataFrame con exactamente 1 fila y las 6 columnas en el orden canónico.
        explicador: TreeExplainer opcional pre-instanciado para optimizar latencia.

    Returns:
        Series de pandas con los valores SHAP por variable para la clase predicha.
    """
    import shap
    from src.evaluate import normalizar_shap

    columnas = paquete.get("columnas", COLUMNAS)
    fila_ordenada = fila_df[columnas].copy()

    modelo = paquete["modelo"]
    if hasattr(modelo, "named_steps"):
        modelo_estimador = modelo.named_steps.get("randomforestclassifier", modelo)
    else:
        modelo_estimador = modelo

    if explicador is None:
        explicador = shap.TreeExplainer(modelo_estimador)

    clases = list(modelo.classes_)
    pred_clase = str(modelo.predict(fila_ordenada)[0])
    idx_clase = clases.index(pred_clase)

    sv_crudo = explicador.shap_values(fila_ordenada)
    sv_norm = normalizar_shap(sv_crudo, 1, len(columnas), len(clases))
    valores_clase = sv_norm[0, :, idx_clase]

    etiquetas_variables = [
        f"{c} = {fila_ordenada.iloc[0][c]:.2f}" for c in columnas
    ]

    return pd.Series(valores_clase, index=etiquetas_variables)
