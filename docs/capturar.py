"""Toma capturas de la app local para la documentación (requiere Chrome y selenium)."""
import subprocess
import sys
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By

RAIZ = Path(__file__).resolve().parents[1]
PUERTO = 8766
proc = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless", "true",
                         "--server.port", str(PUERTO)], cwd=RAIZ, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    time.sleep(10)
    o = webdriver.ChromeOptions()
    for a in ("--headless=new", "--no-sandbox", "--window-size=1500,1250"):
        o.add_argument(a)
    d = webdriver.Chrome(options=o)
    d.get(f"http://localhost:{PUERTO}")
    time.sleep(8)
    d.save_screenshot(str(RAIZ / "docs" / "captura_distribucion.png"))
    tab = d.find_element(By.XPATH, "//*[contains(text(), 'Mi artículo')]")
    d.execute_script("arguments[0].click();", tab)
    time.sleep(3)
    d.save_screenshot(str(RAIZ / "docs" / "captura_articulo.png"))
    d.quit()
finally:
    proc.terminate()
