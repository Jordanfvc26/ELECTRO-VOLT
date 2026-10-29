"""Módulo de modelado y funciones de inferencia de fallos eléctricos.

Define la arquitectura de los modelos supervisados (Regresión Logística,
Random Forest, SVM RBF), el contrato de inferencia para operadores de subestación
con Alineación Rotacional de Fases (grupo C3) y la explicabilidad local con SHAP.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from src.config import cargar_configuracion, obtener_logger, obtener_raiz_proyecto
from src.utils import (
    COLUMNAS,
    MENSAJES_OPERADOR,
    NOTA_CLASES,
    ORDEN_CLASES,
    SEMILLA,
    UMBRAL_CONFIANZA_MINIMA,
    obtener_ruta_modelo,
    validar_rango_senales,
)

logger = obtener_logger(__name__)


def crear_modelos(random_state: int = SEMILLA) -> Dict[str, BaseEstimator]:
    """Instancia el catálogo de los 3 modelos supervisados comparados en el proyecto.

    Configura el escalado StandardScaler dentro de Pipelines para evitar data leakage
    y pondera las clases mediante class_weight='balanced'. Los hiperparámetros
    se leen dinámicamente desde config.yaml con respaldo de valores por defecto.

    Args:
        random_state: Semilla pseudoaleatoria para reproducibilidad.

    Returns:
        Diccionario con las instancias de Regresión Logística, Random Forest y SVM.
    """
    config = cargar_configuracion()
    cfg_modelos = config.get("modelos", {})

    cfg_rf = cfg_modelos.get("random_forest", {})
    cfg_lr = cfg_modelos.get("regresion_logistica", {})
    cfg_svm = cfg_modelos.get("svm_rbf", {})

    rf_estimators = int(cfg_rf.get("n_estimators", 100))
    rf_weight = cfg_rf.get("class_weight", "balanced")
    rf_jobs = cfg_rf.get("n_jobs", -1)

    lr_max_iter = int(cfg_lr.get("max_iter", 2000))
    lr_weight = cfg_lr.get("class_weight", "balanced")

    svm_c = float(cfg_svm.get("C", 10.0))
    svm_gamma = cfg_svm.get("gamma", "scale")
    svm_weight = cfg_svm.get("class_weight", "balanced")

    logger.debug(
        f"Instanciando catálogo de modelos con semilla {random_state}: "
        f"RF(n_est={rf_estimators}), LR(max_iter={lr_max_iter}), SVM(C={svm_c})"
    )

    return {
        "Regresión Logística": make_pipeline(
            StandardScaler(),
            LogisticRegression(
                max_iter=lr_max_iter,
                class_weight=lr_weight,
                random_state=random_state,
            ),
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=rf_estimators,
            class_weight=rf_weight,
            random_state=random_state,
            n_jobs=rf_jobs,
        ),
        "SVM (RBF)": make_pipeline(
            StandardScaler(),
            SVC(
                kernel="rbf",
                C=svm_c,
                gamma=svm_gamma,
                class_weight=svm_weight,
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
        ValueError: Si el archivo está corrupto o no se puede deserializar.
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
        logger.error(f"No se encontró un modelo serializado en las rutas candidatas:\n{rutas_txt}")
        raise FileNotFoundError(
            f"No se encontró un modelo serializado válido en las rutas esperadas:\n{rutas_txt}"
        )

    try:
        paquete = joblib.load(ruta_valida)
    except Exception as err:
        logger.error(f"Error al deserializar el modelo en {ruta_valida}: {err}")
        raise ValueError(f"No se pudo cargar el archivo serializado en {ruta_valida}: {err}") from err

    if not isinstance(paquete, dict):
        raise ValueError(f"El artefacto en {ruta_valida} no es un diccionario válido.")

    # Validar llaves obligatorias del contrato
    llaves_requeridas = ["modelo", "columnas", "clases", "mensajes_operador"]
    faltantes = [k for k in llaves_requeridas if k not in paquete]
    if faltantes:
        logger.error(f"Contrato de modelo incompleto en {ruta_valida}. Faltan: {faltantes}")
        raise KeyError(f"El paquete del modelo en {ruta_valida} no contiene las llaves requeridas: {faltantes}")

    logger.debug(f"Paquete del modelo cargado exitosamente desde: {ruta_valida}")
    return paquete


def mapear_shap_a_canales_fisicos(
    valores_shap_slots: np.ndarray,
    rotacion: str = "ABC",
) -> np.ndarray:
    """Mapea las atribuciones SHAP desde los slots del modelo hacia los canales físicos (Va, Vb, Vc, Ia, Ib, Ic).

    En la alineación rotacional C3:
    - ABC: Va'=Va, Vb'=Vb, Vc'=Vc (identidad directa).
    - BCA: Slot A' recibió Fase B, Slot B' recibió Fase C, Slot C' recibió Fase A.
      Por lo tanto, la atribución para Fase A proviene del Slot C', Fase B del Slot A', etc.
    - CAB: Slot A' recibió Fase C, Slot B' recibió Fase A, Slot C' recibió Fase B.
      Por lo tanto, la atribución para Fase A proviene del Slot B', Fase B del Slot C', etc.

    Args:
        valores_shap_slots: Array 1D de 6 valores SHAP calculados sobre los slots del modelo.
        rotacion: Identificador de la rotación cíclica utilizada ('ABC', 'BCA', 'CAB').

    Returns:
        Array 1D de 6 valores SHAP ordenados según los conductores físicos canónicos.

    Raises:
        ValueError: Si la dimensión del array no es de longitud 6 o la rotación es inválida.
    """
    if len(valores_shap_slots) != 6:
        raise ValueError(f"Se esperaban 6 valores SHAP, se recibieron {len(valores_shap_slots)}")

    if rotacion == "ABC":
        return valores_shap_slots
    elif rotacion == "BCA":
        # Slot A'<-B, Slot B'<-C, Slot C'<-A
        return np.array([
            valores_shap_slots[2],  # Va = Vc'
            valores_shap_slots[0],  # Vb = Va'
            valores_shap_slots[1],  # Vc = Vb'
            valores_shap_slots[5],  # Ia = Ic'
            valores_shap_slots[3],  # Ib = Ia'
            valores_shap_slots[4],  # Ic = Ib'
        ])
    elif rotacion == "CAB":
        # Slot A'<-C, Slot B'<-A, Slot C'<-B
        return np.array([
            valores_shap_slots[1],  # Va = Vb'
            valores_shap_slots[2],  # Vb = Vc'
            valores_shap_slots[0],  # Vc = Va'
            valores_shap_slots[4],  # Ia = Ib'
            valores_shap_slots[5],  # Ib = Ic'
            valores_shap_slots[3],  # Ic = Ia'
        ])
    else:
        logger.warning(f"Rotación desconocida '{rotacion}'. Se mantiene mapeo canónico ABC.")
        return valores_shap_slots


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

    Aplica Alineación Rotacional de Fases en Inferencia (Test-Time Phase Alignment) para resolver
    el sesgo topológico del dataset (que solo contenía LG en A, LL en BC y LLG en AB).
    Evalúa las 3 permutaciones cíclicas directas (+120° y +240°) preservando la secuencia positiva
    e identifica con exactitud la clase de fallo y las fases involucradas.

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
        - confianza_baja: Booleano True si confianza < 0.80.
        - probabilidades: Diccionario clase -> probabilidad.
        - mensaje_operador: Recomendación técnica para el operador.
        - fases_afectadas: Lista de fases comprometidas (ej. ['B'], ['A', 'B'], ['A', 'B', 'C'], []).
        - descripcion_fases: Texto legible de fases (ej. 'Fase B a Tierra', 'Fases A-B', etc.).
        - rotacion_utilizada: Identificador de la permutación ganadora ('ABC', 'BCA', 'CAB').
        - fila_alineada: DataFrame de 1 fila con las señales alineadas al marco de referencia del modelo.

    Raises:
        TypeError: Si alguna de las entradas no es numérica convertible a float.
        ValueError: Si alguna de las entradas es NaN o infinita.
    """
    # Validación estricta de inputs
    entradas = [("Va", Va), ("Vb", Vb), ("Vc", Vc), ("Ia", Ia), ("Ib", Ib), ("Ic", Ic)]
    valores_numericos: Dict[str, float] = {}

    for nom, val in entradas:
        if val is None:
            raise TypeError(f"La señal {nom} no puede ser nula (None).")
        try:
            val_f = float(val)
        except (ValueError, TypeError) as err:
            raise TypeError(f"La señal {nom} debe ser un valor numérico real. Recibido: {val}") from err
        if math.isnan(val_f) or math.isinf(val_f):
            raise ValueError(f"La señal {nom} contiene un valor no numérico o infinito ({val_f}).")
        valores_numericos[nom] = val_f

    v_a = valores_numericos["Va"]
    v_b = valores_numericos["Vb"]
    v_c = valores_numericos["Vc"]
    i_a = valores_numericos["Ia"]
    i_b = valores_numericos["Ib"]
    i_c = valores_numericos["Ic"]

    if paquete is None:
        paquete = cargar_paquete_modelo()

    columnas = paquete.get("columnas", COLUMNAS)
    modelo = paquete["modelo"]

    # Validación de dominio físico de entrenamiento (OOD)
    es_valido, anomalias = validar_rango_senales(v_a, v_b, v_c, i_a, i_b, i_c)
    if not es_valido:
        logger.warning(f"Inferencia ejecutada sobre lecturas fuera de rango (OOD): {anomalias}")

    # 3 permutaciones cíclicas directas del grupo C3 (preservan secuencia positiva)
    rotaciones = [
        {"rotacion": "ABC", "mapping": ("A", "B", "C"), "Va": v_a, "Vb": v_b, "Vc": v_c, "Ia": i_a, "Ib": i_b, "Ic": i_c},
        {"rotacion": "BCA", "mapping": ("B", "C", "A"), "Va": v_b, "Vb": v_c, "Vc": v_a, "Ia": i_b, "Ib": i_c, "Ic": i_a},
        {"rotacion": "CAB", "mapping": ("C", "A", "B"), "Va": v_c, "Vb": v_a, "Vc": v_b, "Ia": i_c, "Ib": i_a, "Ic": i_b},
    ]

    df_candidatos = pd.DataFrame(rotaciones)[columnas]
    probs_todos = modelo.predict_proba(df_candidatos)

    candidatos_evaluados = []
    for i, rot in enumerate(rotaciones):
        probs_i = probs_todos[i]
        k_i = int(np.argmax(probs_i))
        diag_i = str(modelo.classes_[k_i])
        conf_i = round(float(probs_i[k_i]), 4)
        mapping_i = rot["mapping"]

        # Identificación de topología física de fases según el entrenamiento del dataset
        if diag_i == "Normal":
            fases_i: List[str] = []
            desc_i = "Ninguna (Operación Normal)"
        elif diag_i == "LG":
            # En el dataset, LG ocurre exclusivamente en el slot A' a tierra
            fases_i = [mapping_i[0]]
            desc_i = f"Fase {mapping_i[0]} a Tierra"
        elif diag_i == "LL":
            # En el dataset, LL ocurre exclusivamente entre slots B' y C'
            fases_i = sorted([mapping_i[1], mapping_i[2]])
            desc_i = f"Fases {fases_i[0]}-{fases_i[1]}"
        elif diag_i == "LLG":
            # En el dataset, LLG ocurre exclusivamente entre slots A' y B' a tierra
            fases_i = sorted([mapping_i[0], mapping_i[1]])
            desc_i = f"Fases {fases_i[0]}-{fases_i[1]} a Tierra"
        elif diag_i == "Trifásica":
            fases_i = ["A", "B", "C"]
            desc_i = "Fases A-B-C"
        else:
            fases_i = []
            desc_i = diag_i

        candidatos_evaluados.append({
            "rotacion": rot["rotacion"],
            "mapping": mapping_i,
            "diagnostico": diag_i,
            "confianza": conf_i,
            "confianza_baja": bool(conf_i < UMBRAL_CONFIANZA_MINIMA),
            "probabilidades": {str(c): round(float(p), 4) for c, p in zip(modelo.classes_, probs_i)},
            "fases_afectadas": fases_i,
            "descripcion_fases": desc_i,
            "fila_alineada": df_candidatos.iloc[[i]],
        })

    # Criterio de Selección del Ganador:
    # 1. Si el candidato canónico ABC detecta Normal con confianza >= UMBRAL_CONFIANZA_MINIMA, la red está nominal.
    cand_abc = candidatos_evaluados[0]
    if cand_abc["diagnostico"] == "Normal" and cand_abc["confianza"] >= UMBRAL_CONFIANZA_MINIMA:
        ganador = cand_abc
    else:
        # Entre los candidatos que detectan perturbación (falla), seleccionar el de mayor confianza.
        cands_falla = [c for c in candidatos_evaluados if c["diagnostico"] != "Normal"]
        if cands_falla:
            ganador = max(cands_falla, key=lambda c: c["confianza"])
        else:
            ganador = max(candidatos_evaluados, key=lambda c: c["confianza"])

    mensajes = paquete.get("mensajes_operador", MENSAJES_OPERADOR)
    diag_final = ganador["diagnostico"]
    mensaje_op = mensajes.get(diag_final, f"Falla detectada: {diag_final}. Proceder según protocolo.")

    logger.info(
        f"Inferencia completada: diagnóstico='{diag_final}', confianza={ganador['confianza']:.2%}, "
        f"rotación='{ganador['rotacion']}', fases={ganador['fases_afectadas']}"
    )

    return {
        "diagnostico": diag_final,
        "confianza": ganador["confianza"],
        "confianza_baja": ganador["confianza_baja"],
        "probabilidades": ganador["probabilidades"],
        "mensaje_operador": mensaje_op,
        "fases_afectadas": ganador["fases_afectadas"],
        "descripcion_fases": ganador["descripcion_fases"],
        "rotacion_utilizada": ganador["rotacion"],
        "fila_alineada": ganador["fila_alineada"],
    }


def explicar_prediccion_shap(
    paquete: Dict[str, Any],
    fila_df: pd.DataFrame,
    explicador: Any | None = None,
    rotacion: str = "ABC",
) -> pd.Series:
    """Calcula la atribución de importancia local (SHAP) para una lectura individual.

    Responde por qué el modelo emitió cierto diagnóstico y qué variables de fase
    contribuyeron positiva o negativamente a la decisión. Si se empleó alineación de fases,
    mapea los aportes de los slots a las variables físicas reales.

    Args:
        paquete: Diccionario del modelo serializado.
        fila_df: DataFrame con exactamente 1 fila y las 6 columnas canónicas o alineadas.
        explicador: TreeExplainer opcional pre-instanciado para optimizar latencia.
        rotacion: Cadena con la rotación empleada ('ABC', 'BCA', 'CAB').

    Returns:
        Series de pandas con los valores SHAP por variable para la clase predicha.

    Raises:
        TypeError: Si fila_df no es pd.DataFrame o paquete no es diccionario.
        ValueError: Si fila_df no tiene exactamente 1 fila o faltan columnas.
    """
    if not isinstance(paquete, dict):
        raise TypeError("paquete debe ser un diccionario.")
    if not isinstance(fila_df, pd.DataFrame):
        raise TypeError("fila_df debe ser un pd.DataFrame.")
    if len(fila_df) != 1:
        raise ValueError(f"fila_df debe contener exactamente 1 fila. Recibidas: {len(fila_df)}")

    import shap
    from src.evaluate import normalizar_shap

    columnas = paquete.get("columnas", COLUMNAS)
    faltantes = [c for c in columnas if c not in fila_df.columns]
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas en fila_df para SHAP: {faltantes}")

    fila_ordenada = fila_df[columnas].copy()
    modelo = paquete["modelo"]

    if hasattr(modelo, "named_steps"):
        modelo_estimador = modelo.named_steps.get("randomforestclassifier", modelo)
    else:
        modelo_estimador = modelo

    if explicador is None:
        try:
            explicador = shap.TreeExplainer(modelo_estimador)
        except Exception as err:
            logger.error(f"Error al instanciar TreeExplainer: {err}")
            raise ValueError(f"No se pudo crear el explicador SHAP: {err}") from err

    clases = list(modelo.classes_)
    pred_clase = str(modelo.predict(fila_ordenada)[0])
    idx_clase = clases.index(pred_clase)

    try:
        sv_crudo = explicador.shap_values(fila_ordenada)
        sv_norm = normalizar_shap(sv_crudo, 1, len(columnas), len(clases))
        valores_clase_slots = sv_norm[0, :, idx_clase]
    except Exception as err:
        logger.error(f"Error durante el cómputo de valores SHAP: {err}")
        raise ValueError(f"Fallo en la inferencia explicable SHAP: {err}") from err

    # Mapear a canales físicos reales si hubo rotación
    valores_clase = mapear_shap_a_canales_fisicos(valores_clase_slots, rotacion=rotacion)

    etiquetas_variables = [
        f"{c} = {fila_ordenada.iloc[0][c]:.2f}" for c in columnas
    ]

    logger.debug(f"Explicación SHAP generada exitosamente para clase '{pred_clase}'.")
    return pd.Series(valores_clase, index=etiquetas_variables)
