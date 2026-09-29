# Proyecto Unidad I - Fuentes y tipos de datos en Big Data
# Tema: ciencia espacial, con datos abiertos de la NASA y arXiv.
# Cada funcion lee una
# fuente y la deja como tabla con las mismas columnas (id, fuente, entidad,
# tipo_contenido, valor, fecha) para poder juntarlas al final.

import csv
import gzip
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd
import requests

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
COLUMNAS_COMUNES = ["id", "fuente", "entidad", "tipo_contenido", "valor", "fecha"]

# El log tiene mas de 1.8 millones de lineas, asi que solo leemos las
# primeras para que la demo no tarde.
LIMITE_LOG = 5000


def encabezado(titulo):
    print("\n" + titulo)


def describir_estructura(nombre_fuente, tipo_dato, registros_crudos, columnas):
    print(f"Fuente: {nombre_fuente}")
    print(f"Tipo de dato: {tipo_dato}")
    print(f"Registros encontrados: {registros_crudos}")
    print(f"Campos disponibles: {columnas}")


# Fuente 1: CSV (estructurado), exoplanetas del NASA Exoplanet Archive
def lee_csv_exoplanetas():
    encabezado("FUENTE 1: CSV - exoplanetas.csv")
    ruta = DATA_DIR / "exoplanetas.csv"

    with open(ruta, newline="", encoding="utf-8") as f:
        filas_crudas = [fila for fila in csv.DictReader(f) if fila.get("pl_name")]

    describir_estructura(
        "exoplanetas.csv",
        "Estructurado (tabla con filas y columnas fijas)",
        len(filas_crudas),
        list(filas_crudas[0].keys()) if filas_crudas else [],
    )

    faltantes = sum(1 for fila in filas_crudas if not fila["pl_rade"] or not fila["pl_bmasse"])
    print(f"Valores faltantes (radio o masa): {faltantes}")

    filas_transformadas = []
    for fila in filas_crudas:
        filas_transformadas.append({
            "id": fila["pl_name"],
            "fuente": "CSV-exoplanetas",
            "entidad": fila["hostname"],
            "tipo_contenido": fila["discoverymethod"] or "metodo_desconocido",
            "valor": float(fila["pl_rade"]) if fila["pl_rade"] else 0,
            "fecha": fila["disc_year"],
        })

    return pd.DataFrame(filas_transformadas, columns=COLUMNAS_COMUNES)


# Fuente 2: JSON (semiestructurado), busqueda en la biblioteca de imagenes de la NASA
def lee_json_imagenes():
    encabezado("FUENTE 2: JSON - imagenes_nasa.json")
    ruta = DATA_DIR / "imagenes_nasa.json"

    with open(ruta, encoding="utf-8") as f:
        respuesta = json.load(f)

    items = [item["data"][0] for item in respuesta["collection"]["items"] if item.get("data")]

    describir_estructura(
        "imagenes_nasa.json",
        "Semiestructurado (JSON)",
        len(items),
        list(items[0].keys()) if items else [],
    )

    sin_keywords = sum(1 for i in items if not i.get("keywords"))
    print(f"Valores faltantes (sin palabras clave): {sin_keywords}")

    filas_transformadas = []
    for i, item in enumerate(items):
        filas_transformadas.append({
            "id": item.get("nasa_id", f"img_{i}"),
            "fuente": "JSON-imagenes",
            "entidad": item.get("center") or "centro_desconocido",
            "tipo_contenido": item.get("media_type", "desconocido"),
            "valor": len(item.get("keywords", [])),
            "fecha": (item.get("date_created") or "")[:10] or None,
        })

    return pd.DataFrame(filas_transformadas, columns=COLUMNAS_COMUNES)


# Fuente 3: XML (semiestructurado), API de arXiv, categoria astro-ph.EP
def lee_xml_articulos():
    encabezado("FUENTE 3: XML - API de arXiv (astro-ph.EP)")
    url = "https://export.arxiv.org/api/query"
    parametros = {"search_query": "cat:astro-ph.EP", "start": 0, "max_results": 20}
    ns = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}

    try:
        # con el User-Agent normal de requests arXiv da error 406, por eso ponemos uno propio
        cabeceras = {"User-Agent": "proyecto-big-data-unidad1/1.0"}
        respuesta = requests.get(url, params=parametros, headers=cabeceras, timeout=10)
        respuesta.raise_for_status()
        raiz = ET.fromstring(respuesta.content)
        print("Conectado a arXiv, datos en vivo.")
    except requests.RequestException as error:
        print(f"No se pudo conectar a la API de arXiv ({error}).")
        print("Usando respaldo local: data/articulos_arxiv_cache.xml")
        raiz = ET.parse(DATA_DIR / "articulos_arxiv_cache.xml").getroot()

    entradas = raiz.findall("a:entry", ns)
    describir_estructura(
        "API de arXiv",
        "Semiestructurado (XML de una API)",
        len(entradas),
        ["id", "title", "category", "published"],
    )
    print("Valores faltantes: 0")

    filas_transformadas = []
    for entrada in entradas:
        categoria = entrada.find("a:category", ns)
        filas_transformadas.append({
            "id": entrada.find("a:id", ns).text.rsplit("/", 1)[-1],
            "fuente": "XML-arxiv",
            "entidad": "arxiv.org",
            "tipo_contenido": categoria.attrib.get("term") if categoria is not None else "sin_categoria",
            "valor": len(entrada.find("a:summary", ns).text or ""),
            "fecha": entrada.find("a:published", ns).text[:10],
        })

    return pd.DataFrame(filas_transformadas, columns=COLUMNAS_COMUNES)


# Fuente 4: log de texto (no estructurado), accesos al servidor de la NASA en julio de 1995
PATRON_LOG = re.compile(
    r'^(?P<host>\S+) \S+ \S+ \[(?P<dia>\d+)/(?P<mes>\w+)/(?P<anio>\d+):[\d:]+ [+-]\d+\] '
    r'"(?P<metodo>\w+) (?P<recurso>\S+) \S+" (?P<estado>\d+) (?P<bytes>\S+)'
)


def lee_log_nasa():
    encabezado("FUENTE 4: TXT (log) - nasa_access_log_jul95.gz")
    ruta = DATA_DIR / "nasa_access_log_jul95.gz"

    lineas = []
    with gzip.open(ruta, "rt", encoding="utf-8", errors="replace") as f:
        for i, linea in enumerate(f):
            if i >= LIMITE_LOG:
                break
            linea = linea.strip()
            if linea:
                lineas.append(linea)

    describir_estructura(
        "nasa_access_log_jul95.gz",
        "No estructurado (texto plano)",
        len(lineas),
        ["(texto libre, sin columnas)"],
    )
    print(f"Solo se leen las primeras {LIMITE_LOG} lineas (el archivo tiene 1,891,714).")

    filas_transformadas = []
    lineas_no_reconocidas = 0
    for i, linea in enumerate(lineas):
        coincidencia = PATRON_LOG.match(linea)
        if not coincidencia:
            lineas_no_reconocidas += 1
            continue
        datos = coincidencia.groupdict()
        filas_transformadas.append({
            "id": f"log_{i}",
            "fuente": "TXT-log",
            "entidad": datos["host"],
            "tipo_contenido": f"http_{datos['estado']}",
            "valor": int(datos["bytes"]) if datos["bytes"].isdigit() else 0,
            "fecha": f"{datos['anio']}-{datos['mes']}-{datos['dia']}",
        })

    print(f"Lineas que no coinciden con el patron: {lineas_no_reconocidas}")

    return pd.DataFrame(filas_transformadas, columns=COLUMNAS_COMUNES)


# Fuente 5: API NeoWs de la NASA (semiestructurado), asteroides cerca de la Tierra.
# Usa DEMO_KEY, la llave de pruebas que no pide registro.
def lee_api_asteroides():
    encabezado("FUENTE 5: API - asteroides cercanos (NeoWs, NASA)")
    url = "https://api.nasa.gov/neo/rest/v1/feed"
    parametros = {"start_date": "2024-01-01", "end_date": "2024-01-03", "api_key": "DEMO_KEY"}

    try:
        respuesta = requests.get(url, params=parametros, timeout=10)
        respuesta.raise_for_status()
        datos = respuesta.json()
        print("Conectado a la API de la NASA, datos en vivo.")
    except requests.RequestException as error:
        print(f"No se pudo conectar a la API de la NASA ({error}).")
        print("Usando respaldo local: data/neows_cache.json")
        with open(DATA_DIR / "neows_cache.json", encoding="utf-8") as f:
            datos = json.load(f)

    asteroides = [a for lista in datos["near_earth_objects"].values() for a in lista]

    describir_estructura(
        "API NeoWs (NASA)",
        "Semiestructurado (JSON de una API)",
        len(asteroides),
        ["id", "name", "estimated_diameter", "close_approach_data", "is_potentially_hazardous_asteroid"],
    )
    print("Los datos vienen anidados (diametro, acercamiento), hay que entrar a cada nivel.")

    filas_transformadas = []
    for a in asteroides:
        acercamiento = a["close_approach_data"][0] if a["close_approach_data"] else {}
        filas_transformadas.append({
            "id": a["id"],
            "fuente": "API-asteroides",
            "entidad": a["name"],
            "tipo_contenido": "peligroso" if a["is_potentially_hazardous_asteroid"] else "no_peligroso",
            "valor": a["estimated_diameter"]["meters"]["estimated_diameter_max"],
            "fecha": acercamiento.get("close_approach_date"),
        })

    return pd.DataFrame(filas_transformadas, columns=COLUMNAS_COMUNES)


# Junta las 5 tablas y muestra el resumen
def integrar_y_resumir(tablas):
    encabezado("INTEGRACION DE LAS 5 FUENTES")
    dataset_integrado = pd.concat(tablas, ignore_index=True)

    print(f"Total de registros integrados: {len(dataset_integrado)}")
    print("\nRegistros por fuente:")
    print(dataset_integrado["fuente"].value_counts().to_string())

    print("\nTipos de datos por columna (dtype de pandas):")
    print(dataset_integrado.dtypes.to_string())

    print("\nValores faltantes por columna en el dataset ya integrado:")
    print(dataset_integrado.isna().sum().to_string())

    print("\nVista previa del dataset integrado:")
    print(dataset_integrado.head(10).to_string(index=False))

    salida = DATA_DIR / "dataset_integrado.csv"
    dataset_integrado.to_csv(salida, index=False)
    print(f"\nDataset integrado guardado en: {salida}")

    return dataset_integrado


def main():
    tabla_csv = lee_csv_exoplanetas()
    tabla_json = lee_json_imagenes()
    tabla_xml = lee_xml_articulos()
    tabla_log = lee_log_nasa()
    tabla_api = lee_api_asteroides()

    dataset_integrado = integrar_y_resumir(
        [tabla_csv, tabla_json, tabla_xml, tabla_log, tabla_api]
    )

    encabezado("RESULTADO FINAL")
    print("Listo: las 5 fuentes (CSV, JSON, XML, log y API) quedaron en un solo dataset.")
    print(f"Entidad mas frecuente: "
          f"{dataset_integrado['entidad'].value_counts().idxmax()}")


if __name__ == "__main__":
    main()
