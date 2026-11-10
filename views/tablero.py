"""Tablero: filtros, distribución de precios y análisis de un artículo."""
import plotly.express as px
import streamlit as st

from src.analisis import completitud, descuento_promedio, equivalentes, filtrar, posicion_precio
from src.ui import ARTICULO_POR_DEFECTO, PALETA, cop, datos

df = datos()
st.title("📊 Tablero de precios")
st.caption("Portátiles de Alkosto · datos públicos extraídos con Selenium")

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
    izq, der = st.columns(2)
    with izq:
        fig = px.histogram(muestra, x="precio", nbins=20, labels={"precio": "Precio (COP)", "count": "Portátiles"},
                           title="Distribución de precios", color_discrete_sequence=[PALETA[0]])
        fig.add_vline(x=muestra["precio"].median(), line_dash="dash", line_color=PALETA[4],
                      annotation_text="mediana", annotation_position="top")
        fig.update_layout(bargap=0.05, yaxis_title="Portátiles", margin=dict(t=50, b=10))
        st.plotly_chart(fig, width="stretch")
    with der:
        por_marca = muestra.dropna(subset=["marca"]).groupby("marca")["precio"].median().reset_index()
        if len(por_marca):
            por_marca = por_marca.sort_values("precio")
            fig2 = px.bar(por_marca, x="precio", y="marca", orientation="h", title="Precio mediano por marca",
                          labels={"precio": "Mediana (COP)", "marca": ""}, color="marca",
                          color_discrete_sequence=PALETA)
            fig2.update_layout(showlegend=False, margin=dict(t=50, b=10))
            st.plotly_chart(fig2, width="stretch")
    dcto = muestra.dropna(subset=["descuento_pct"])
    if len(dcto):
        fig3 = px.scatter(dcto, x="precio", y="descuento_pct", color="gamer", hover_name="nombre",
                          labels={"precio": "Precio (COP)", "descuento_pct": "Descuento (%)", "gamer": "Gamer"},
                          title="Descuento según el precio", color_discrete_sequence=[PALETA[0], PALETA[2]])
        fig3.update_layout(margin=dict(t=50, b=10))
        st.plotly_chart(fig3, width="stretch")

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
    with st.container(border=True):
        st.markdown("**Frente a todos los portátiles**")
        st.write(f"Mediana de {pos['n']} equipos: {cop(pos['mediana'])}. El artículo está "
                 f"{pos['dif_vs_mediana_pct']:+.1f} % respecto de la mediana y es más barato que el "
                 f"{pos['pct_mas_barato_que']} % de la muestra.")
    if art["ram_gb"] == art["ram_gb"] and art["disco_gb"] == art["disco_gb"]:
        eq = equivalentes(df, art["ram_gb"], art["disco_gb"])
        pe = posicion_precio(eq, art["precio"])
        config = f"{int(art['ram_gb'])} GB RAM / {int(art['disco_gb'])} GB disco"
        with st.container(border=True):
            st.markdown(f"**Frente a sus {pe['n']} equivalentes** ({config})")
            st.write(f"Mediana: {cop(pe['mediana'])}. {pe['mas_baratos']} cuestan menos, {pe['iguales']} igual "
                     f"(incluye el artículo) y {pe['mas_caros']} más.")
        fig4 = px.histogram(eq, x="precio", nbins=12, title="Precios de los equivalentes",
                            labels={"precio": "Precio (COP)"}, color_discrete_sequence=[PALETA[1]])
        fig4.add_vline(x=art["precio"], line_color=PALETA[4], line_width=3, annotation_text="este artículo")
        fig4.update_layout(yaxis_title="Portátiles", margin=dict(t=50, b=10))
        st.plotly_chart(fig4, width="stretch")
    st.link_button("Ver en Alkosto", art["url"], icon="🔗")

with tab3:
    st.dataframe(muestra, width="stretch", hide_index=True)
    st.download_button("Descargar CSV filtrado", muestra.to_csv(index=False).encode("utf-8"),
                       "portatiles_filtrados.csv", "text/csv")
