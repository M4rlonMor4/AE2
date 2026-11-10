"""Elementos de interfaz compartidos por las páginas de la app."""
from pathlib import Path

import streamlit as st

from src.analisis import cargar_datos

RUTA_DATOS = Path(__file__).resolve().parents[1] / "data" / "portatiles_alkosto.csv"
ARTICULO_POR_DEFECTO = 'Ideapad Slim 3 - 14" Pulgadas OLED'
REPO_URL = "https://github.com/M4rlonMor4/AE2"
PALETA = ["#1F5FBF", "#18A999", "#F4A259", "#8E6BBF", "#E4572E", "#5B6C8F"]

ESTILOS = """
<style>
.hero {
    background: linear-gradient(135deg, #12306B 0%, #1F5FBF 55%, #18A999 100%);
    color: #fff; padding: 2.4rem 2.2rem; border-radius: 18px; margin-bottom: 1.4rem;
}
.hero h1 { color: #fff; font-size: 2.3rem; margin: 0 0 .4rem 0; padding: 0; }
.hero p { color: #E6EEFB; font-size: 1.08rem; margin: 0; max-width: 46rem; }
.hero .tag { display: inline-block; background: rgba(255,255,255,.18); border-radius: 999px;
             padding: .15rem .8rem; font-size: .8rem; margin-bottom: .8rem; letter-spacing: .03em; }
.paso { background: #F2F6FC; border-radius: 14px; padding: 1rem 1.1rem; height: 100%; border: 1px solid #DCE6F5; }
.paso .n { font-size: 1.6rem; font-weight: 700; color: #1F5FBF; }
.paso h4 { margin: .1rem 0 .3rem 0; font-size: 1.02rem; }
.paso p { margin: 0; font-size: .9rem; color: #43536E; }
.destacado { border-left: 6px solid #18A999; background: #F2F6FC; border-radius: 10px; padding: 1rem 1.2rem; }
.destacado .precio { font-size: 1.9rem; font-weight: 700; color: #12306B; }
.destacado .viejo { text-decoration: line-through; color: #7C8AA3; margin-left: .6rem; }
.destacado .badge { background: #18A999; color: #fff; border-radius: 6px; padding: .1rem .5rem;
                    font-weight: 600; margin-left: .6rem; font-size: .9rem; }
[data-testid="stMetric"] { background: #F2F6FC; border: 1px solid #DCE6F5; border-radius: 12px; padding: .7rem 1rem; }
</style>
"""


def inyectar_estilos():
    st.markdown(ESTILOS, unsafe_allow_html=True)


@st.cache_data
def datos():
    return cargar_datos(str(RUTA_DATOS))


def cop(v):
    """Formatea pesos colombianos: 2299070 -> $2.299.070."""
    return "—" if v is None or v != v else f"${v:,.0f}".replace(",", ".")
