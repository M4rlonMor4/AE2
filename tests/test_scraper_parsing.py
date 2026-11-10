"""Pruebas de las funciones de parseo del scraper (no abren navegador ni usan la red)."""
from src.scraper import detectar_marca, num, parse_specs


def test_num_convierte_precios_colombianos():
    assert num("$ 2.299.070") == 2299070
    assert num("-43%") == 43
    assert num("sin precio") is None
    assert num(None) is None


def test_detectar_marca_ignora_gamer():
    assert detectar_marca('Computador Portátil Gamer ASUS TUF F16"') == "ASUS"
    assert detectar_marca("Computador Portátil LENOVO Ideapad Slim 3") == "LENOVO"
    assert detectar_marca("Computador Portátil Genérico") is None


def test_parse_specs_ssd_y_ram():
    texto = (
        "Procesador Intel Core I5 Capacidad de Disco Estado Solido SSD 512 GB "
        "Memoria RAM 8 GB Tamaño Pantalla 14 Pulgadas"
    )
    assert parse_specs(texto) == {"ram_gb": 8, "disco_gb": 512, "pantalla_in": 14.0}


def test_parse_specs_terabytes_y_pantalla_decimal():
    texto = "Capacidad de Disco SSD 1 TB Memoria RAM 16 GB Tamaño Pantalla 15,6 Pulgadas"
    assert parse_specs(texto) == {"ram_gb": 16, "disco_gb": 1000, "pantalla_in": 15.6}


def test_parse_specs_texto_vacio():
    assert parse_specs("") == {"ram_gb": None, "disco_gb": None, "pantalla_in": None}
