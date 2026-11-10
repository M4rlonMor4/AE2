"""Tablero Streamlit: posicionamiento de precios de portátiles en Alkosto."""
from pathlib import Path

import plotly.express as px
import streamlit as st

from src.analisis import (
    cargar_datos,
    completitud,
    descuento_promedio,
    equivalentes,
    filtrar,
    posicion_precio,
)

RUTA_DATOS = Path(__file__).parent / "data" / "portatiles_alkosto.csv"
ARTICULO_POR_DEFECTO = "Ideapad Slim 3 - 14\" Pulgadas OLED"

st.set_page_config(page_title="Portátiles Alkosto", page_icon="💻", layout="wide")


@st.cache_data
def datos():
    return cargar_datos(str(RUTA_DATOS))


def cop(v):
    return "—" if v is None else f"${v:,.0f}".replace(",", ".")


df = datos()
st.title("💻 Precios de portátiles en Alkosto")
st.caption("Proyecto EA2 · Programación para Análisis de Datos · IU Digital de Antioquia · "
           "Datos públicos extraídos con Selenium (EA1)")

# ---------- Barra lateral: filtros ----------
st.sidebar.header("Filtros")
marcas = st.sidebar.multiselect("Marca", sorted(df["marca"].dropna().unique()))
rams = st.sidebar.multiselect("RAM (GB)", sorted(df["ram_gb"].dropna().astype(int).unique()))
discos = st.sidebar.multiselect("Disco (GB)", sorted(df["disco_gb"].dropna().astype(int).unique()))
gamer = st.sidebar.checkbox("Incluir portátiles gamer", value=True)
pmin, pmax = int(df["precio"].min()), int(df["precio"].max())
rango = st.sidebar.slider("Rango de precio (COP)", pmin, pmax, (pmin, pmax), step=50_000)

muestra = filtrar(df, marcas, rams, discos, gamer, rango[0], rango[1])

c1, c2, c3, c4 = st.columns(4)
c1.metric("Portátiles en la muestra", len(muestra))
c2.metric("Precio mediano", cop(muestra["precio"].median()) if len(muestra) else "—")
dp = descuento_promedio(muestra)
c3.metric("Descuento promedio", "—" if dp is None else f"{dp} %")
c4.metric("Completitud de datos", f"{completitud(muestra)} %")

if muestra.empty:
    st.warning("Ningún portátil cumple los filtros. Ajusta la selección.")
    st.stop()

tab1, tab2, tab3 = st.tabs(["📊 Distribución", "🎯 Mi artículo", "📋 Datos"])

with tab1:
    fig = px.histogram(muestra, x="precio", nbins=20, labels={"precio": "Precio (COP)"},
                       title="Distribución de precios")
    st.plotly_chart(fig, width="stretch")
    por_marca = muestra.dropna(subset=["marca"]).groupby("marca")["precio"].median().reset_index()
    if len(por_marca):
        st.plotly_chart(px.bar(por_marca, x="marca", y="precio", title="Precio mediano por marca",
                               labels={"precio": "Mediana (COP)"}), width="stretch")

with tab2:
    nombres = df["nombre"].tolist()
    idx = next((i for i, n in enumerate(nombres) if ARTICULO_POR_DEFECTO in n), 0)
    elegido = st.selectbox("Artículo a analizar", nombres, index=idx)
    art = df[df["nombre"] == elegido].iloc[0]
    st.subheader(art["nombre"])
    a1, a2, a3 = st.columns(3)
    a1.metric("Precio", cop(art["precio"]))
    ant, desc = art["precio_anterior"], art["descuento_pct"]
    a2.metric("Precio anterior", cop(ant) if ant == ant else "—")
    a3.metric("Descuento", f"{desc:.0f} %" if desc == desc else "—")

    pos = posicion_precio(df, art["precio"])
    st.write(f"Frente a **todos** los portátiles ({pos['n']}): mediana {cop(pos['mediana'])}; "
             f"el artículo está {pos['dif_vs_mediana_pct']:+.1f} % respecto de la mediana y es más barato "
             f"que el {pos['pct_mas_barato_que']} % de la muestra.")
    if art["ram_gb"] == art["ram_gb"] and art["disco_gb"] == art["disco_gb"]:
        eq = equivalentes(df, art["ram_gb"], art["disco_gb"])
        pe = posicion_precio(eq, art["precio"])
        config = f"{int(art['ram_gb'])} GB RAM / {int(art['disco_gb'])} GB disco"
        st.write(f"Frente a los **{pe['n']} equivalentes** ({config}): "
                 f"mediana {cop(pe['mediana'])}; {pe['mas_baratos']} más baratos, {pe['iguales']} iguales "
                 f"(incluye el artículo) y {pe['mas_caros']} más caros.")
    st.caption(art["url"])

with tab3:
    st.dataframe(muestra, width="stretch", hide_index=True)
    st.download_button("Descargar CSV filtrado", muestra.to_csv(index=False).encode("utf-8"),
                       "portatiles_filtrados.csv", "text/csv")
