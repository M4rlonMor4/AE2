"""Funciones de análisis de precios de portátiles (puras y probadas con pytest)."""
from __future__ import annotations

import pandas as pd

CAMPOS_CLAVE = ["nombre", "marca", "precio", "ram_gb", "disco_gb"]
COLUMNAS_NUMERICAS = ["precio", "precio_anterior", "descuento_pct", "calificacion", "ram_gb", "disco_gb", "pantalla_in"]


def cargar_datos(ruta: str) -> pd.DataFrame:
    """Lee el CSV extraído con Selenium y deja solo portátiles con precio válido."""
    df = pd.read_csv(ruta)
    for col in COLUMNAS_NUMERICAS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "gamer" in df.columns:
        df["gamer"] = df["gamer"].astype(str).str.lower().eq("true")
    df = df.dropna(subset=["precio"]).drop_duplicates(subset="url").reset_index(drop=True)
    return df


def calcular_descuento(precio: float, precio_anterior: float) -> float | None:
    """Porcentaje de descuento del precio actual frente al anterior (None si no hay dato válido)."""
    if precio is None or precio_anterior is None or pd.isna(precio) or pd.isna(precio_anterior) or precio_anterior <= 0:
        return None
    return round((1 - precio / precio_anterior) * 100, 1)


def filtrar(
    df: pd.DataFrame,
    marcas: list[str] | None = None,
    ram_gb: list[int] | None = None,
    disco_gb: list[int] | None = None,
    incluir_gamer: bool = True,
    precio_min: float | None = None,
    precio_max: float | None = None,
) -> pd.DataFrame:
    """Aplica los filtros de la barra lateral; un filtro vacío o None no restringe."""
    r = df
    if marcas:
        r = r[r["marca"].isin(marcas)]
    if ram_gb:
        r = r[r["ram_gb"].isin(ram_gb)]
    if disco_gb:
        r = r[r["disco_gb"].isin(disco_gb)]
    if not incluir_gamer and "gamer" in r.columns:
        r = r[~r["gamer"]]
    if precio_min is not None:
        r = r[r["precio"] >= precio_min]
    if precio_max is not None:
        r = r[r["precio"] <= precio_max]
    return r.reset_index(drop=True)


def posicion_precio(df: pd.DataFrame, precio: float) -> dict:
    """Posición de un precio dentro de una muestra de portátiles."""
    n = len(df)
    if n == 0:
        return {"n": 0, "mediana": None, "mas_baratos": 0, "iguales": 0, "mas_caros": 0,
                "pct_mas_barato_que": None, "dif_vs_mediana_pct": None}
    mediana = float(df["precio"].median())
    mas_baratos = int((df["precio"] < precio).sum())
    iguales = int((df["precio"] == precio).sum())
    return {
        "n": n,
        "mediana": mediana,
        "mas_baratos": mas_baratos,
        "iguales": iguales,
        "mas_caros": n - mas_baratos - iguales,
        "pct_mas_barato_que": round(float((df["precio"] > precio).mean() * 100), 1),
        "dif_vs_mediana_pct": round((precio / mediana - 1) * 100, 1),
    }


def descuento_promedio(df: pd.DataFrame) -> float | None:
    """Descuento promedio (%) de la muestra; None si no hay datos."""
    serie = df["descuento_pct"].dropna() if "descuento_pct" in df.columns else pd.Series(dtype=float)
    return round(float(serie.mean()), 1) if len(serie) else None


def completitud(df: pd.DataFrame, campos: list[str] | None = None) -> float:
    """Porcentaje de celdas con dato en los campos clave."""
    campos = campos or CAMPOS_CLAVE
    campos = [c for c in campos if c in df.columns]
    if df.empty or not campos:
        return 0.0
    return round(float(100 * (1 - df[campos].isna().mean().mean())), 1)


def equivalentes(df: pd.DataFrame, ram_gb: float, disco_gb: float) -> pd.DataFrame:
    """Portátiles con la misma RAM y capacidad de disco."""
    return df[(df["ram_gb"] == ram_gb) & (df["disco_gb"] == disco_gb)].reset_index(drop=True)
