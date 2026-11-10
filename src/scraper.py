"""Extracción de portátiles de Alkosto con Selenium (continuación de la EA1).

Uso:  python -m src.scraper --clics 3 --salida data/portatiles_alkosto.csv
Respeta robots.txt: solo visita la categoría pública de portátiles, con User-Agent identificado y pausas.
"""
from __future__ import annotations

import argparse
import re
import sys
import time
from datetime import date

import pandas as pd

BASE = "https://www.alkosto.com"
URL_LISTADO = f"{BASE}/computadores-tablet/portatiles/c/BI_104_ALKOS"
USER_AGENT = "EA1-IUDigital-academic-scraper (proyecto academico)"
CARD = "li.product__item"
MARCAS = ["LENOVO", "HP", "ASUS", "ACER", "MSI", "DELL", "APPLE", "SAMSUNG", "HUAWEI", "GIGABYTE",
          "MICROSOFT", "XIAOMI", "HONOR", "LG", "RAZER", "ALIENWARE", "VAIO", "TECNO"]


def num(txt: str | None) -> int | None:
    """'$ 2.299.070' -> 2299070 (None si no hay dígitos)."""
    d = re.sub(r"[^0-9]", "", txt or "")
    return int(d) if d else None


def detectar_marca(titulo: str | None) -> str | None:
    """Primera marca conocida que aparece en el título (ignora la palabra 'Gamer')."""
    tu = (titulo or "").upper()
    return next((m for m in MARCAS if re.search(r"\b" + m + r"\b", tu)), None)


def parse_specs(texto: str) -> dict:
    """Extrae RAM, disco y pantalla del texto de una tarjeta de producto."""
    t = " ".join((texto or "").split())
    ram = re.search(r"Memoria RAM\s*(\d+)\s*GB", t)
    disco = re.search(r"Capacidad de Disco\s*(?:Estado Solido SSD|Disco Duro|HDD|SSD)?\s*(\d+)\s*(GB|TB)", t)
    pant = re.search(r"Tama[ñn]o Pantalla\s*([\d.,]+)\s*Pulgadas", t)
    return {
        "ram_gb": int(ram.group(1)) if ram else None,
        "disco_gb": (int(disco.group(1)) * (1000 if disco.group(2) == "TB" else 1)) if disco else None,
        "pantalla_in": float(pant.group(1).replace(",", ".")) if pant else None,
    }


def crear_driver():
    from selenium import webdriver

    o = webdriver.ChromeOptions()
    for a in ("--headless=new", "--no-sandbox", "--disable-dev-shm-usage", "--window-size=1400,1000",
              f"--user-agent={USER_AGENT}"):
        o.add_argument(a)
    return webdriver.Chrome(options=o)


def _texto(el, css):
    from selenium.webdriver.common.by import By

    try:
        return el.find_element(By.CSS_SELECTOR, css).get_attribute("textContent").strip()
    except Exception:
        return None


def leer_tarjeta(el) -> dict:
    from selenium.webdriver.common.by import By

    titulo = _texto(el, "h3.product__item__top__title")
    url = el.find_element(By.CSS_SELECTOR, "h3.product__item__top__title").get_attribute("data-url")
    desc = _texto(el, ".label-offer")
    cal = _texto(el, ".averageNumber")
    return {
        "nombre": titulo,
        "url": BASE + url if url else None,
        "marca": detectar_marca(titulo),
        "gamer": "GAMER" in (titulo or "").upper(),
        "precio": num(_texto(el, "p.product__price--discounts__price span.price")),
        "precio_anterior": num(_texto(el, "p.product__price--discounts__old")),
        "descuento_pct": num(desc),
        "calificacion": float(cal) if cal else None,
        **parse_specs(el.get_attribute("textContent")),
    }


def extraer(clics: int = 3, pausa: float = 3.0) -> pd.DataFrame:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    driver = crear_driver()
    filas = []
    try:
        driver.get(URL_LISTADO)
        WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.CSS_SELECTOR, CARD)))
        for _ in range(clics):
            antes = len(driver.find_elements(By.CSS_SELECTOR, CARD))
            boton = driver.find_element(By.CSS_SELECTOR, "button.js-load-more")
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", boton)
            driver.execute_script("arguments[0].click();", boton)
            try:
                WebDriverWait(driver, 20).until(lambda d: len(d.find_elements(By.CSS_SELECTOR, CARD)) > antes)
            except Exception:
                break
            time.sleep(pausa)
        for el in driver.find_elements(By.CSS_SELECTOR, CARD):
            try:
                filas.append(leer_tarjeta(el))
            except Exception:
                continue
    finally:
        driver.quit()
    df = pd.DataFrame(filas).drop_duplicates(subset="url").reset_index(drop=True)
    df["fecha_extraccion"] = date.today().isoformat()
    return df


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--clics", type=int, default=3)
    ap.add_argument("--salida", default="data/portatiles_alkosto.csv")
    args = ap.parse_args(argv)
    df = extraer(args.clics)
    if len(df) < 20:   # protección: no sobreescribir datos buenos con una extracción fallida
        print(f"Extracción sospechosa ({len(df)} filas); no se guarda.", file=sys.stderr)
        return 1
    df.to_csv(args.salida, index=False, encoding="utf-8")
    print(f"{len(df)} portátiles guardados en {args.salida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
