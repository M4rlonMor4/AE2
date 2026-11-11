import pandas as pd

from src.ui import cop, fecha_datos, tarjeta_html


def test_cop_formatea_pesos():
    assert cop(2299070) == "$2.299.070"
    assert cop(None) == "—"


def test_fecha_datos():
    assert fecha_datos(pd.DataFrame({"fecha_extraccion": ["2026-11-03", "2026-11-10"]})) == "2026-11-10"
    assert fecha_datos(pd.DataFrame({"a": [1]})) is None


def test_tarjeta_escapa_html_y_muestra_datos():
    fila = {"nombre": 'Computador Portátil <script>x</script> 14"', "marca": "HP", "precio": 1000000,
            "precio_anterior": 2000000, "descuento_pct": 50.0, "ram_gb": 8, "disco_gb": 512,
            "pantalla_in": 14.0, "gamer": False}
    html = tarjeta_html(fila)
    assert "<script>" not in html and "&lt;script&gt;" in html
    assert "$1.000.000" in html and "-50 %" in html and "8 GB RAM" in html


def test_tarjeta_tolera_datos_faltantes():
    fila = {"nombre": "X", "marca": None, "precio": 5, "precio_anterior": float("nan"),
            "descuento_pct": float("nan"), "ram_gb": float("nan"), "disco_gb": float("nan"),
            "pantalla_in": float("nan"), "gamer": True}
    html = tarjeta_html(fila)
    assert "SIN MARCA" in html and "Gamer" in html and "badge" not in html
