"""Pruebas unitarias para el módulo de configuración y logging centralizado (src/config.py).

Verifica la carga del archivo config.yaml, la fusión con la configuración por defecto,
la sobreescritura mediante variables de entorno, la resolución de rutas relativas
y la inicialización consistente del sistema de logging.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
import pytest

from src.config import (
    CONFIGURACION_POR_DEFECTO,
    cargar_configuracion,
    obtener_logger,
    obtener_raiz_proyecto,
)
from src.utils import (
    COLUMNAS,
    RANGO_CORRIENTE,
    RANGO_VOLTAJE,
    SEMILLA,
    UMBRAL_CONFIANZA_MINIMA,
    UMBRAL_RETORNO_TIERRA_A,
)


def test_obtener_raiz_proyecto() -> None:
    """Verifica que la raíz del proyecto sea un directorio existente y contenga archivos clave."""
    raiz = obtener_raiz_proyecto()
    assert isinstance(raiz, Path)
    assert raiz.exists()
    assert raiz.is_dir()
    assert (raiz / "config.yaml").exists(), "Debe existir config.yaml en la raíz del proyecto"
    assert (raiz / "requirements.txt").exists(), "Debe existir requirements.txt en la raíz del proyecto"


def test_cargar_configuracion_desde_yaml() -> None:
    """Verifica que config.yaml se parsea correctamente y contiene todas las secciones obligatorias."""
    config = cargar_configuracion(recargar=True)
    assert isinstance(config, dict)

    secciones_requeridas = {"proyecto", "semilla", "datos", "modelos", "operacion", "metas_smart", "logging"}
    assert secciones_requeridas.issubset(set(config.keys()))

    assert config["semilla"] == 42
    assert config["datos"]["test_size"] == 0.20
    assert config["operacion"]["umbral_confianza_minima"] == 0.80
    assert config["metas_smart"]["accuracy_minimo"] == 0.90


def test_constantes_utils_sincronizadas_con_config() -> None:
    """Verifica que las constantes expuestas en src/utils.py reflejen la configuración."""
    config = cargar_configuracion()
    assert SEMILLA == config["semilla"]
    assert COLUMNAS == config["datos"]["columnas_modelo"]
    assert UMBRAL_CONFIANZA_MINIMA == config["operacion"]["umbral_confianza_minima"]
    assert UMBRAL_RETORNO_TIERRA_A == config["operacion"]["umbral_retorno_tierra_amperios"]
    assert RANGO_VOLTAJE == (
        config["operacion"]["rango_voltaje_pu"]["min"],
        config["operacion"]["rango_voltaje_pu"]["max"],
    )
    assert RANGO_CORRIENTE == (
        config["operacion"]["rango_corriente_amperios"]["min"],
        config["operacion"]["rango_corriente_amperios"]["max"],
    )


def test_sobreescritura_por_variables_de_entorno(monkeypatch) -> None:
    """Verifica que variables de entorno como ELECTROVOLT_SEMILLA sobreescriban la configuración."""
    monkeypatch.setenv("ELECTROVOLT_SEMILLA", "99")
    monkeypatch.setenv("ELECTROVOLT_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("ELECTROVOLT_UMBRAL_CONFIANZA", "0.85")

    config = cargar_configuracion(recargar=True)
    assert config["semilla"] == 99
    assert config["logging"]["nivel"] == "DEBUG"
    assert config["operacion"]["umbral_confianza_minima"] == 0.85

    # Restaurar recargando sin variables de entorno
    monkeypatch.delenv("ELECTROVOLT_SEMILLA", raising=False)
    monkeypatch.delenv("ELECTROVOLT_LOG_LEVEL", raising=False)
    monkeypatch.delenv("ELECTROVOLT_UMBRAL_CONFIANZA", raising=False)
    cargar_configuracion(recargar=True)


def test_obtener_logger_configuracion() -> None:
    """Verifica que obtener_logger retorne un logger configurado adecuadamente."""
    test_logger = obtener_logger("test_module")
    assert isinstance(test_logger, logging.Logger)
    assert test_logger.name == "test_module"
    assert len(test_logger.handlers) >= 1

