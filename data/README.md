# Datos

Todos los archivos son reales y los bajamos de su fuente original, no los escribimos nosotros.

- `exoplanetas.csv`: del [NASA Exoplanet Archive](https://exoplanetarchive.ipac.caltech.edu), más de 40,000 planetas.
- `imagenes_nasa.json`: de la [NASA Image and Video Library](https://images.nasa.gov), 100 resultados (es el límite de la API).
- `nasa_access_log_jul95.gz`: log del servidor de la NASA de julio de 1995, del [Internet Traffic Archive](https://ita.ee.lbl.gov/html/contrib/NASA-HTTP.html), 1,891,714 líneas.
- `articulos_arxiv_cache.xml`: copia de una respuesta real de la [API de arXiv](https://info.arxiv.org/help/api/index.html). Solo se usa si no hay internet o arXiv rechaza la conexión.
- `neows_cache.json`: copia de una respuesta real de [NeoWs](https://api.nasa.gov). Solo se usa si no hay internet.
- `dataset_integrado.csv`: lo genera el programa al correr `src/main.py`.

Las fuentes de arXiv y NeoWs se piden por internet cada vez que corre el programa.

## El log viene comprimido

El log pesa cerca de 200 MB sin comprimir. Lo dejamos en `.gz` tal como lo entrega la fuente (unos 20 MB) y el programa lo abre así, con `gzip`. Solo procesa las primeras 5,000 líneas para que la demo corra en segundos. El archivo no se modifica.

## Links directos

Exoplanetas (CSV):
```
https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+pl_name,hostname,discoverymethod,disc_year,pl_orbper,pl_rade,pl_bmasse,st_teff+from+ps&format=csv
```

Imágenes de la NASA:
```
https://images-api.nasa.gov/search?q=apollo&media_type=image
```

Artículos de arXiv:
```
https://export.arxiv.org/api/query?search_query=cat:astro-ph.EP&start=0&max_results=20
```

Log del servidor de la NASA:
```
https://ita.ee.lbl.gov/traces/NASA_access_log_Jul95.gz
```

Asteroides (NeoWs, con la llave de pruebas):
```
https://api.nasa.gov/neo/rest/v1/feed?start_date=2024-01-01&end_date=2024-01-03&api_key=DEMO_KEY
```
