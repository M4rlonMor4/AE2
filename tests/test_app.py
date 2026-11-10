"""Prueba de humo: la app de Streamlit se ejecuta sin excepciones con los datos del repositorio."""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from src.analisis import cargar_datos

RAIZ = Path(__file__).resolve().parents[1]
APP = str(RAIZ / "app.py")


def test_app_arranca_sin_errores():
    at = AppTest.from_file(APP, default_timeout=60).run()
    assert not at.exception
    assert at.title[0].value.startswith("💻")
    assert len(at.metric) >= 4


def test_app_con_filtro_imposible_muestra_aviso():
    # La combinación marca + RAM sin resultados se calcula con los datos actuales (el CSV cambia cada semana).
    df = cargar_datos(str(RAIZ / "data" / "portatiles_alkosto.csv"))
    marcas = sorted(df["marca"].dropna().unique())
    rams = sorted(df["ram_gb"].dropna().astype(int).unique())
    vacia = next(((m, r) for m in marcas for r in rams if df[(df["marca"] == m) & (df["ram_gb"] == r)].empty), None)
    if vacia is None:
        pytest.skip("Todas las combinaciones marca/RAM tienen resultados")
    at = AppTest.from_file(APP, default_timeout=60).run()
    at.sidebar.multiselect[0].select(vacia[0]).run()
    at.sidebar.multiselect[1].select(vacia[1]).run()
    assert not at.exception
    assert any("Ningún portátil" in w.value for w in at.warning)
