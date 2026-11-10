"""Página de inicio: presentación del proyecto, cifras clave y cómo funciona."""
import streamlit as st

from src.analisis import descuento_promedio, equivalentes, posicion_precio
from src.ui import ARTICULO_POR_DEFECTO, REPO_URL, cop, datos

df = datos()

st.markdown(
    """
    <div class="hero">
      <span class="tag">PROYECTO EA2 · DEVOPS + ANÁLISIS DE DATOS</span>
      <h1>¿Es buena oferta ese portátil?</h1>
      <p>Extraemos los precios de los portátiles de Alkosto con Selenium y los comparamos contra equipos de
      igual configuración, para saber si un descuento llamativo es realmente competitivo.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- Cifras clave ----------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Portátiles analizados", len(df))
c2.metric("Marcas identificadas", df["marca"].nunique())
c3.metric("Precio mediano", cop(df["precio"].median()))
dp = descuento_promedio(df)
c4.metric("Descuento promedio", "—" if dp is None else f"{dp} %")

st.write("")
b1, b2, _ = st.columns([1, 1, 3])
b1.page_link("views/tablero.py", label="Abrir el tablero", icon="📊")
b2.link_button("Ver el código en GitHub", REPO_URL, icon="🔗")

# ---------- Artículo destacado ----------
st.subheader("El caso: Lenovo Ideapad Slim 3")
fila = df[df["nombre"].str.contains(ARTICULO_POR_DEFECTO, regex=False, na=False)]
if not fila.empty:
    art = fila.iloc[0]
    pos = posicion_precio(df, art["precio"])
    eq = equivalentes(df, art["ram_gb"], art["disco_gb"])
    pe = posicion_precio(eq, art["precio"])
    izq, der = st.columns([3, 2])
    with izq:
        st.markdown(
            f"""<div class="destacado">
            <div class="precio">{cop(art['precio'])}<span class="viejo">{cop(art['precio_anterior'])}</span>
            <span class="badge">-{art['descuento_pct']:.0f} %</span></div>
            <div>14" OLED · Intel Core 5 · 8 GB RAM · SSD 512 GB</div></div>""",
            unsafe_allow_html=True,
        )
    with der:
        st.write(
            f"Frente a **todos** los portátiles cuesta **{abs(pos['dif_vs_mediana_pct']):.0f} % menos** "
            f"que la mediana, pero esa comparación se distorsiona por los equipos gamer. "
            f"Frente a sus **{pe['n']} equivalentes** (misma RAM y disco) su precio es justo la mediana: "
            f"{pe['mas_baratos']} cuestan menos y {pe['mas_caros']} más."
        )

# ---------- Cómo funciona ----------
st.subheader("Cómo funciona")
pasos = [
    ("1", "Extraer", "Selenium carga la categoría de Alkosto, pulsa «Ver más» y lee precios y especificaciones."),
    ("2", "Analizar", "Funciones probadas calculan mediana, posición del precio y comparación con equivalentes."),
    ("3", "Probar", "Cada cambio pasa por GitHub Actions: lint y 17+ pruebas en Python 3.11 y 3.12."),
    ("4", "Desplegar", "Al fusionar en main, Streamlit Cloud actualiza esta app automáticamente."),
]
for col, (n, titulo, texto) in zip(st.columns(4), pasos):
    col.markdown(f'<div class="paso"><div class="n">{n}</div><h4>{titulo}</h4><p>{texto}</p></div>',
                 unsafe_allow_html=True)

st.write("")
with st.expander("Nota sobre los datos y la ética del scraping"):
    st.write(
        "Solo se recolectan datos públicos de producto, sin datos personales ni inicio de sesión. El scraper consulta "
        "únicamente la categoría pública de portátiles que el `robots.txt` de Alkosto permite, se identifica con un "
        "User-Agent propio y espera 3 segundos entre acciones. Los precios cambian con frecuencia: los datos son una "
        "fotografía del día de extracción."
    )
st.caption("Marlon Andrés Mora Vaco · IU Digital de Antioquia · Programación para Análisis de Datos")
