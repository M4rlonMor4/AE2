# Flujo de trabajo DevOps del proyecto

Este documento explica cómo se trabaja en el repositorio, qué automatiza cada _workflow_ y cómo se llega del código a la
app desplegada.

## 1. Ciclo DevOps aplicado

| Fase | Qué se hace en este proyecto | Herramienta |
|---|---|---|
| Planear | Pregunta de negocio: ¿qué tan competitivo es el precio de un portátil frente a equivalentes? | Issues de GitHub |
| Codificar | Scraper, análisis y tablero en ramas cortas | Git, GitHub |
| Construir | Instalación reproducible de dependencias con `requirements*.txt` | pip, caché de Actions |
| Probar | Lint con `ruff`; 17 pruebas con `pytest` (unitarias + prueba de humo de la app con `streamlit.testing`) | GitHub Actions |
| Liberar | Fusión a `main` por Pull Request con CI en verde | Pull Requests |
| Desplegar | Streamlit Community Cloud redespliega la app al cambiar `main` | Streamlit Cloud |
| Operar / Monitorear | Datos actualizados cada semana; si el scraper falla, el job queda en rojo en la pestaña Actions | `actualizar_datos.yml` |

## 2. Estrategia de ramas (GitHub Flow)

- `main` siempre está desplegable.
- Cada cambio nace en una rama corta con prefijo: `feature/`, `fix/`, `docs/`, `data/`, `ci/`.
- Nadie hace _push_ directo a `main`: todo entra por Pull Request.

Ramas usadas en este proyecto:

| Rama | Contenido |
|---|---|
| `feature/analisis-precios` | Módulo `src/analisis.py` y sus pruebas |
| `feature/scraper-selenium` | Módulo `src/scraper.py` (extracción con Selenium) y pruebas de parseo |
| `feature/app-streamlit` | Tablero `app.py` y prueba de humo |
| `ci/github-actions` | Workflows de CI y de actualización de datos |
| `docs/flujo-devops` | README y este documento |

## 3. Convención de commits

Formato `tipo: descripción en imperativo` (Conventional Commits): `feat`, `fix`, `test`, `ci`, `docs`, `data`, `chore`.
Ejemplo: `feat: calcula posición del precio frente a equivalentes`.

## 4. Pipeline de CI (`.github/workflows/ci.yml`)

Se ejecuta en cada _push_ y en cada Pull Request hacia `main`.

1. **lint** — instala dependencias y ejecuta `ruff check .`.
2. **test** (depende de lint) — corre `pytest -q` en una matriz **Python 3.11 y 3.12**. Incluye la prueba de humo que
   arranca la app de Streamlit en memoria con los datos reales del repositorio.

Detalles: caché de `pip`, cancelación de ejecuciones antiguas de la misma rama (`concurrency`) y `fail-fast: false` para ver
fallos en ambas versiones.

## 5. Despliegue continuo (CD)

Streamlit Community Cloud está conectado a la rama `main`. Cuando un PR se fusiona, la plataforma detecta el cambio, instala
`requirements.txt` y reinicia la app. Como solo se puede fusionar con CI en verde, **lo que llega a producción siempre pasó las
pruebas**.

## 6. Actualización automática de datos (`actualizar_datos.yml`)

- Se dispara cada lunes a las 12:00 UTC (`cron`) o manualmente (`workflow_dispatch`).
- Instala Selenium y ejecuta `python -m src.scraper`. Chrome ya viene instalado en `ubuntu-latest`.
- El scraper **no guarda** si obtiene menos de 20 filas (protege los datos buenos de una extracción fallida).
- Si el CSV cambió, crea una rama `datos/actualizacion-AAAAMMDD` y abre un **Pull Request**; así los datos nuevos también pasan por
  el CI y por revisión antes de llegar a la app.

> Requisito en GitHub: _Settings → Actions → General → Workflow permissions_ debe permitir
> **Read and write** y **Allow GitHub Actions to create and approve pull requests**.

## 7. Configuración recomendada del repositorio

_Settings → Branches → Add rule_ para `main`:

- Require a pull request before merging.
- Require status checks to pass (`Lint (ruff)` y `Pruebas (Python 3.11/3.12)`).
- Require branches to be up to date before merging.

## 8. Lista de verificación de un Pull Request

- [ ] La rama parte de `main` actualizado.
- [ ] Commits pequeños y con mensaje claro.
- [ ] `ruff check .` y `pytest -q` pasan en local.
- [ ] El CI está en verde.
- [ ] Se actualizó la documentación si cambió el comportamiento.
