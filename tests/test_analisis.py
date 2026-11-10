import pandas as pd
import pytest

from src.analisis import (
    calcular_descuento,
    cargar_datos,
    completitud,
    descuento_promedio,
    equivalentes,
    filtrar,
    posicion_precio,
)


@pytest.fixture
def df():
    return pd.DataFrame({
        "nombre": ["A", "B", "C", "D"],
        "url": ["u1", "u2", "u3", "u4"],
        "marca": ["LENOVO", "HP", "HP", None],
        "gamer": [False, False, True, False],
        "precio": [1_000_000, 2_000_000, 3_000_000, 2_000_000],
        "precio_anterior": [2_000_000, 2_500_000, 6_000_000, None],
        "descuento_pct": [50.0, 20.0, 50.0, None],
        "ram_gb": [8, 8, 16, 8],
        "disco_gb": [512, 512, 1000, 256],
    })


def test_calcular_descuento():
    assert calcular_descuento(2_299_070, 4_099_000) == 43.9
    assert calcular_descuento(100, 0) is None
    assert calcular_descuento(None, 100) is None


def test_filtrar_por_marca_y_gamer(df):
    assert list(filtrar(df, marcas=["HP"])["nombre"]) == ["B", "C"]
    assert list(filtrar(df, marcas=["HP"], incluir_gamer=False)["nombre"]) == ["B"]


def test_filtrar_por_rango_y_specs(df):
    r = filtrar(df, ram_gb=[8], disco_gb=[512], precio_max=1_500_000)
    assert list(r["nombre"]) == ["A"]


def test_filtrar_sin_filtros_devuelve_todo(df):
    assert len(filtrar(df)) == 4


def test_posicion_precio(df):
    p = posicion_precio(df, 2_000_000)
    assert p["n"] == 4 and p["mas_baratos"] == 1 and p["iguales"] == 2 and p["mas_caros"] == 1
    assert p["mediana"] == 2_000_000
    assert p["dif_vs_mediana_pct"] == 0.0
    assert p["pct_mas_barato_que"] == 25.0


def test_posicion_precio_muestra_vacia(df):
    assert posicion_precio(df.iloc[0:0], 1)["n"] == 0


def test_descuento_promedio_ignora_nulos(df):
    assert descuento_promedio(df) == 40.0
    assert descuento_promedio(df.iloc[0:0]) is None


def test_completitud(df):
    # 20 celdas en campos clave (4 filas x 5 columnas), 1 nula (marca) -> 95 %
    assert completitud(df) == 95.0


def test_equivalentes(df):
    assert list(equivalentes(df, 8, 512)["nombre"]) == ["A", "B"]


def test_cargar_datos_limpia_y_convierte(tmp_path):
    ruta = tmp_path / "d.csv"
    pd.DataFrame({
        "nombre": ["x", "y", "y"], "url": ["a", "b", "b"], "marca": ["HP"] * 3, "gamer": ["True", "False", "False"],
        "precio": [100, None, 200], "ram_gb": [8, 8, 8], "disco_gb": [512] * 3,
    }).to_csv(ruta, index=False)
    r = cargar_datos(str(ruta))
    assert len(r) == 2                 # se descarta la fila sin precio
    assert r["gamer"].dtype == bool and bool(r.loc[0, "gamer"]) is True
