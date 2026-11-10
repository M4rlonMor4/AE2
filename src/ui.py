"""Elementos de interfaz compartidos por las páginas de la app (compatibles con tema claro y oscuro)."""
from html import escape
from pathlib import Path

import streamlit as st

from src.analisis import cargar_datos

RUTA_DATOS = Path(__file__).resolve().parents[1] / "data" / "portatiles_alkosto.csv"
ARTICULO_POR_DEFECTO = 'Ideapad Slim 3 - 14" Pulgadas OLED'
REPO_URL = "https://github.com/M4rlonMor4/AE2"
PALETA = ["#1F5FBF", "#18A999", "#F4A259", "#8E6BBF", "#E4572E", "#5B6C8F"]

# Las superficies usan grises translúcidos y el acento un azul de contraste medio: se ven bien en tema claro y oscuro.
ESTILOS = """
<style>
:root { --borde: rgba(128,128,128,.28); --suave: rgba(128,128,128,.13); }
.hero {
    background: linear-gradient(135deg, #12306B 0%, #1F5FBF 55%, #18A999 100%);
    color: #fff; padding: 2.4rem 2.2rem; border-radius: 18px; margin-bottom: 1.4rem;
}
.hero h1 { color: #fff; font-size: 2.3rem; margin: 0 0 .4rem 0; padding: 0; }
.hero p { color: #E6EEFB; font-size: 1.08rem; margin: 0; max-width: 46rem; }
.hero .tag { display: inline-block; background: rgba(255,255,255,.18); border-radius: 999px;
             padding: .15rem .8rem; font-size: .8rem; margin-bottom: .8rem; letter-spacing: .03em; }
.paso { background: var(--suave); border-radius: 14px; padding: 1rem 1.1rem;
        height: 100%; border: 1px solid var(--borde); }
.paso .n { font-size: 1.6rem; font-weight: 700; color: #3F7DE0; }
.paso h4 { margin: .1rem 0 .3rem 0; font-size: 1.02rem; }
.paso p { margin: 0; font-size: .9rem; opacity: .8; }
.destacado { border-left: 6px solid #18A999; background: var(--suave);
             border-radius: 10px; padding: 1rem 1.2rem; }
.destacado .precio { font-size: 1.9rem; font-weight: 700; }
.destacado .viejo, .card .viejo { text-decoration: line-through; opacity: .55; margin-left: .5rem; font-weight: 400; }
.badge { background: #18A999; color: #fff; border-radius: 6px; padding: .1rem .5rem;
         font-weight: 600; margin-left: .5rem; font-size: .85rem; }
[data-testid="stMetric"] { background: var(--suave); border: 1px solid var(--borde);
                           border-radius: 12px; padding: .7rem 1rem; }
.card { background: var(--suave); border: 1px solid var(--borde); border-radius: 14px;
        padding: 1rem 1.1rem; margin-bottom: 1rem; min-height: 11.5rem; transition: transform .15s, box-shadow .15s; }
.card:hover { transform: translateY(-3px); box-shadow: 0 8px 22px rgba(0,0,0,.18); }
.card .marca { font-size: .72rem; letter-spacing: .08em; font-weight: 700; color: #3F7DE0; }
.card .nombre { font-size: .9rem; line-height: 1.25; margin: .25rem 0 .6rem 0; min-height: 3.4rem; }
.card .precio { font-size: 1.35rem; font-weight: 700; }
.chip { display: inline-block; background: var(--suave); border-radius: 999px; padding: .08rem .6rem;
        font-size: .74rem; margin: .5rem .3rem 0 0; }
.veredicto { border-radius: 12px; padding: .9rem 1.2rem; color: #fff; margin: .6rem 0 1rem 0; }
.veredicto b { font-size: 1.25rem; }
.veredicto.buena { background: #18A999; }
.veredicto.normal { background: #C98A1B; }
.veredicto.caro { background: #D64933; }
.veredicto.sin_datos { background: #5B6C8F; }
.pie { border-top: 1px solid var(--borde); margin-top: 2.2rem; padding-top: .8rem; font-size: .82rem; opacity: .75; }
.pie a { color: inherit; }
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


def fecha_datos(df):
    """Fecha de extracción más reciente registrada en los datos, o None."""
    if "fecha_extraccion" not in df.columns or df["fecha_extraccion"].dropna().empty:
        return None
    return str(df["fecha_extraccion"].dropna().max())


def tarjeta_html(fila) -> str:
    """HTML de una tarjeta de producto (todos los textos se escapan)."""
    def ok(v):
        return v == v and v is not None

    viejo = f'<span class="viejo">{cop(fila["precio_anterior"])}</span>' if ok(fila["precio_anterior"]) else ""
    badge = f'<span class="badge">-{fila["descuento_pct"]:.0f} %</span>' if ok(fila["descuento_pct"]) else ""
    chips = []
    if ok(fila["ram_gb"]):
        chips.append(f'{int(fila["ram_gb"])} GB RAM')
    if ok(fila["disco_gb"]):
        chips.append(f'{int(fila["disco_gb"])} GB disco')
    if ok(fila["pantalla_in"]):
        chips.append(f'{fila["pantalla_in"]:g}"')
    if fila.get("gamer"):
        chips.append("Gamer")
    chips_html = "".join(f'<span class="chip">{escape(c)}</span>' for c in chips)
    marca = escape(str(fila["marca"])) if isinstance(fila["marca"], str) else "SIN MARCA"
    nombre = escape(str(fila["nombre"]).replace("Computador Portátil ", ""))
    return (f'<div class="card"><div class="marca">{marca}</div><div class="nombre">{nombre}</div>'
            f'<div class="precio">{cop(fila["precio"])}{viejo}{badge}</div>{chips_html}</div>')


def pie_de_pagina(df):
    fecha = fecha_datos(df)
    texto_fecha = f"Datos extraídos el {fecha}" if fecha else "Fecha de extracción no registrada"
    st.markdown(
        f'<div class="pie">{texto_fecha} · Datos públicos de Alkosto, solo con fines académicos · '
        f'<a href="{REPO_URL}" target="_blank">Código en GitHub</a> · '
        f'Marlon Andrés Mora Vaco · IU Digital de Antioquia</div>',
        unsafe_allow_html=True,
    )
