# 💻 Precios de portátiles en Alkosto — Proyecto DevOps (EA2)

Proyecto de la asignatura **Programación para Análisis de Datos** (IU Digital de Antioquia), continuación de la
Evidencia de Aprendizaje 1. Toma el scraping con **Selenium** de los portátiles de [Alkosto](https://www.alkosto.com)
y lo convierte en un proyecto de software con **Git/GitHub**, **CI/CD con GitHub Actions** y **despliegue continuo en
Streamlit Community Cloud**.

**Autor:** Marlon Andrés Mora Vaco

| | |
|---|---|
| App desplegada | _(pega aquí la URL de Streamlit, p. ej. `https://TU-APP.streamlit.app`)_ |
| Repositorio | _(pega aquí la URL del repositorio de GitHub)_ |

## ¿Qué hace?

- **`src/scraper.py`** — extrae con Selenium el listado dinámico de portátiles (botón «Ver más»): nombre, marca,
  precio, precio anterior, descuento, RAM, disco y pantalla. Respeta `robots.txt`, usa un User-Agent identificado y
  pausas entre acciones.
- **`src/analisis.py`** — funciones puras de análisis: filtros, posición de un precio en la muestra (mediana,
  percentil, más baratos/iguales/más caros), descuento promedio y completitud de datos.
- **`app.py`** — tablero Streamlit con filtros, distribución de precios, análisis de un artículo
  (por defecto el *Lenovo Ideapad Slim 3*, el de la EA1) y descarga del CSV filtrado.
- **`data/portatiles_alkosto.csv`** — datos extraídos (100 portátiles).

## Estructura

```
├── app.py                         # tablero Streamlit (lo que se despliega)
├── src/
│   ├── analisis.py                # lógica de análisis (probada)
│   └── scraper.py                 # extracción con Selenium
├── tests/                         # pytest: unitarias + prueba de humo de la app
├── data/portatiles_alkosto.csv
├── .github/workflows/
│   ├── ci.yml                     # lint + pruebas en cada push y PR
│   └── actualizar_datos.yml       # scraping semanal -> abre un PR con el CSV nuevo
├── docs/flujo_devops.md           # explicación detallada del flujo de trabajo
└── requirements*.txt
```

## Cómo ejecutarlo en local

```bash
python -m venv .venv && source .venv/bin/activate      # en Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pytest -q                 # pruebas
ruff check .              # estilo
streamlit run app.py      # tablero en http://localhost:8501

# opcional: volver a extraer datos (requiere Chrome instalado)
pip install -r requirements-scraper.txt
python -m src.scraper --clics 3
```

## Flujo de trabajo (resumen)

1. **Rama** desde `main` (`feature/...`, `fix/...`, `docs/...`, `data/...`).
2. **Commits** pequeños con mensajes en formato _Conventional Commits_ (`feat:`, `fix:`, `test:`, `ci:`, `docs:`, `data:`).
3. **Pull Request** hacia `main`: el **CI** corre `ruff` y `pytest` (Python 3.11 y 3.12).
4. **Fusión** solo si el CI está en verde.
5. **Despliegue continuo:** Streamlit Community Cloud redespliega la app en cada cambio en `main`.
6. **Datos frescos:** cada lunes `actualizar_datos.yml` ejecuta el scraper y abre un PR con el CSV nuevo.

Detalle completo en [`docs/flujo_devops.md`](docs/flujo_devops.md).

## Despliegue en Streamlit Community Cloud

1. Sube el repositorio a GitHub (público).
2. Entra a <https://share.streamlit.io>, inicia sesión con GitHub y pulsa **Create app**.
3. Elige el repositorio, la rama `main` y el archivo principal `app.py`.
4. Pulsa **Deploy**. Desde entonces cada `git push` / PR fusionado a `main` actualiza la app.

## Nota ética sobre los datos

Solo se recolectan datos públicos de producto (sin datos personales ni sesión de usuario). El scraper consulta únicamente la
categoría pública de portátiles, que `robots.txt` de Alkosto permite, con pausas de 3 s. Los precios cambian con frecuencia:
los datos del repositorio son una fotografía del día de extracción.
