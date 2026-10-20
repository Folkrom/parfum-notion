---
type: doc
updated: 2026-10-20
---
# Enriquecer perfumes con datos externos

Objetivo: completar o validar `Key Notes`, acordes, temporada y concentración sin depender
de lo que diga (o se equivoque) un post. Hoy el agente usa conocimiento general cuando la
fuente no trae notas; una fuente estructurada lo haría verificable.

## Fragrantica

- **No tiene API pública oficial ni MCP propio.**
- Opciones de scraping (Apify, Decodo, scripts propios): la página está detrás de protección
  anti-bots y sus términos de uso no permiten scraping. Si se usa, que sea manual y puntual
  (una ficha a la vez, a petición del usuario), nunca masivo.
- Uso tolerable sin scraping: el usuario pega el link o una captura de la ficha y el agente
  la lee como cualquier otra fuente (`sources/fragrantica-<slug>.md`).

## Alternativas con API / MCP (por evaluar)

| Servicio | Tipo | Notas |
|---|---|---|
| Fragella | REST API (API key) | JSON con notas, acordes con %, longevidad, estela, temporada, ocasión, imágenes. Plan gratuito por confirmar. |
| Noteboxd | MCP + REST (API key gratis, 50 llamadas/día) | Fragancias, notas, acordes, perfumistas, búsqueda por similitud. Proyecto joven, MIT. |
| Perfume Picks MCP | MCP (sin key) | ~13k fragancias, pirámide de notas, acordes, dupes. Solo lectura. |
| Scentrev MCP | MCP + REST | Dice tener 126k fragancias. Sin verificar. |

Ninguno es Fragrantica; los datos pueden variar entre fuentes. Antes de integrar uno,
revisa precio, límites y licencia de los datos.

## Cómo integrarlo cuando se elija uno

1. Si es MCP: agrégalo al cliente del agente; documenta sus tools en `config/`.
   Si es REST: script `scripts/enrich.py "<brand> <name>"` con la key en una variable de
   entorno (`.env`, ignorado por git), que devuelva JSON con el formato de `upsert_note.py`.
2. Paso nuevo en `workflows/ingest-social-post.md`, después de leer las slides: enriquecer
   cada perfume nuevo; si la fuente social y la API chocan, gana la API para notas y
   concentración, y la diferencia se anota como opinión.
3. Guarda el origen de los datos: `sources: ["fragella"]` en la nota del perfume.
