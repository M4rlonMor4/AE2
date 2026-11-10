"""Punto de entrada de la app Streamlit: navegación entre Inicio y Tablero."""
import streamlit as st

from src.ui import inyectar_estilos

st.set_page_config(page_title="Portátiles Alkosto · Análisis de precios", page_icon="💻", layout="wide")
inyectar_estilos()

paginas = st.navigation([
    st.Page("views/inicio.py", title="Inicio", icon="🏠", default=True),
    st.Page("views/tablero.py", title="Tablero de precios", icon="📊"),
])
st.sidebar.caption("EA2 · Programación para Análisis de Datos\n\nIU Digital de Antioquia")
paginas.run()
