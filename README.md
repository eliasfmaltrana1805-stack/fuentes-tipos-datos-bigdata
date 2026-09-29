# Fuentes y tipos de datos en Big Data

Proyecto de la Unidad I de Manejo Masivo de Datos. Somos tres integrantes: Maltrana Luna Elias Francisco, Montes Rubio Santiago Martin y Salazar Flores Alfonso.

## De qué trata

Los datos no siempre vienen de un solo lugar ni en el mismo formato. Pueden ser:

- Estructurados: filas y columnas, como un CSV.
- Semiestructurados: tienen etiquetas pero no una tabla fija, como JSON o XML.
- No estructurados: texto libre, como un log.

Para verlo en la práctica escogimos ciencia espacial y buscamos 5 fuentes reales de la NASA y de arXiv. El programa lee cada una, revisa cómo está armada, se queda con los campos que sirven, las pasa a una misma tabla y al final las junta en un solo archivo.

## Las 5 fuentes

- `data/exoplanetas.csv`: CSV del NASA Exoplanet Archive, con más de 40,000 planetas (estructurado).
- `data/imagenes_nasa.json`: búsqueda en la biblioteca de imágenes de la NASA (semiestructurado).
- API de arXiv: artículos científicos sobre exoplanetas, en XML (semiestructurado, en vivo).
- `data/nasa_access_log_jul95.gz`: log del servidor de la NASA de julio de 1995 (no estructurado).
- API NeoWs de api.nasa.gov: asteroides cercanos a la Tierra, en JSON (semiestructurado, en vivo).

Los links de donde bajamos cada una están en `data/README.md`.

Las dos APIs se consultan por internet. Si no hay conexión, o si arXiv rechaza la petición (a veces lo hace), el programa usa una copia guardada en `data/` y avisa en pantalla. El log completo tiene 1,891,714 líneas, así que el programa solo lee las primeras 5,000 para que no tarde.

## Cómo correrlo

Necesita Python 3.9 o más nuevo.

```bash
pip install -r requirements.txt
python src/main.py
```

Va imprimiendo lo que hace con cada fuente y al final genera `data/dataset_integrado.csv`.

## Qué hace el programa

1. Lee cada fuente (`csv`, `json`, `xml.etree`, `gzip` y `requests`).
2. Dice cuántos registros trae, qué campos tiene y cuántos datos le faltan.
3. Se queda con los campos que necesitamos. Del log, por ejemplo, solo el host, el código de respuesta y la fecha.
4. Los pasa a una tabla con las columnas `id`, `fuente`, `entidad`, `tipo_contenido`, `valor` y `fecha`.
5. Junta las 5 tablas y muestra un resumen.

## Resultado

Salen 45,322 registros: 40,188 exoplanetas, 4,989 líneas del log (11 de las 5,000 no siguieron el patrón), 100 imágenes, 25 asteroides y 20 artículos. En el CSV hay muchos datos faltantes reales: 36,690 planetas no tienen radio o masa, porque no todos los métodos de detección permiten calcularlos. Eso lo detecta el programa solo.

## Lo que nos costó

- Cada fuente tiene su propia estructura, hay que pasarlas a un formato común antes de juntarlas.
- Los nombres de campos no coinciden. `hostname`, `center` y `name` terminan como `entidad`.
- El log no tiene columnas, hay que sacar los datos con expresiones regulares.
- Las APIs pueden fallar, por eso el respaldo local.
- Un archivo puede ser real y estar completo, pero ser muy grande para una demo.
- Con datos de Big Data de verdad esto pasa con millones de registros y muchas más fuentes, y ahí un solo script ya no alcanza.

## Evidencias

Las capturas de la ejecución están en `docs/evidencias/`.
