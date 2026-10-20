---
type: workflow
---
# Procesar un post de redes

Entrada: link de un post o capturas de pantalla.

## 1. Descargar

```bash
python3 scripts/fetch_post.py "<url>"                                  # TikTok, YouTube, otros
python3 scripts/fetch_post.py "<url>" --cookies-from-browser firefox   # Instagram (suele pedir login)
```

Deja en `inbox/<platform>-<id>/`: `slides/sNN.jpg`, `sheet.jpg`, `meta.json` (caption, cuenta,
fecha) y `transcript.txt` si hay subtítulos.

| Tipo de post | Qué sale en `slides/` | Dónde están los nombres |
|---|---|---|
| TikTok de fotos / carrusel IG | Cada slide en resolución completa | Texto de las slides |
| Video (TikTok, Reel, YouTube, Short) | Frames en cada cambio de escena (o cada `--every` s) | Frames + `transcript.txt` + caption |
| Capturas del usuario | Ponlas tú en `inbox/manual-<fecha>/slides/s01.jpg…` | Capturas |

Si el script sale con código 2, revisa `inbox/_staging-<platform>/raw/` (login, versión de yt-dlp).
En videos, los frames suelen ser muchos y parecidos: elige los que muestran cada botella con
claridad y úsalos para el mapa de recortes (`slide` = número del frame).

## 2. Leer las slides

- Mira `sheet.jpg`; si el texto es chico, abre slides individuales.
- Por cada perfume anota: línea, variante, marca, concentración, veredicto del reseñador,
  notas (top/mid/base), íconos de temporada si son legibles.
- Arma lista numerada con códigos: `<slide><letra>` (1a, 1b…). Marca los que se repiten
  dentro del mismo post.

## 3. Elegir

- Si el usuario ya dijo cuáles (o "todos"), úsalo. Si no, muéstrale la lista y pregunta.

## 4. Buscar duplicados

Para cada elegido:

```bash
python3 scripts/vault_index.py match "<Brand> <Perfume>"
```

- Score alto + misma concentración/variante → es el mismo: va a `dedupe-merge.md`.
- Misma línea pero otra variante (EDT vs EDP) → perfume distinto, se crea.

## 5. Crear en Notion (solo los nuevos)

`notion-create-pages` con `parent.data_source_id` de `config/notion.md`. Una llamada para todos.
Propiedades mínimas: Perfume, Brand, Concentration, Key Notes, Scent Family, Season, Occasion,
Source, Source Link, Status=`Interested`, My Rating=`Not tested`.
Contenido: `Reseña del post (<cuenta>): <veredicto> <contexto>`.

Guarda los `page_id` devueltos.

## 6. Imágenes

1. Escribe un mapa `inbox/<post>/map.txt`: `nombre-archivo slide ncols index` (index base 0).
2. `python3 scripts/crop_bottles.py --slides inbox/<post>/slides --map inbox/<post>/map.txt --out inbox/<post>/crops`
3. Revisa `inbox/<post>/crops/crops_sheet.jpg` (en el orden del mapa). Ajusta y repite si hace falta.
4. Copia los recortes a `attachments/`.
5. Por cada imagen: `notion-create-file-upload` (filename = `<nombre>.jpg`), junta
   líneas `nombre id token` y sube en lote: `scripts/upload_notion.sh inbox/<post>/crops < lines.txt`.
   Todas deben dar `200`.
6. `notion-update-page` → `update_properties` → `Image` con el `file_upload` id. Hazlo en el mismo turno.

## 7. Vault

1. `scripts/upsert_note.py` con un JSON por perfume (nuevos y fusionados), incluyendo
   `notion_page_id`, `image`, `sources` y `opinions`. Ver formato en `--help`.
2. Crea `sources/<platform>-<id>.md` con la plantilla de abajo.

## 8. Reporte

Corto: cuántos creados, cuáles fusionados (y qué cambió), dudas, pendientes (precio/prioridad).

---

## Plantilla `sources/<platform>-<id>.md`

```markdown
---
type: source
platform: tiktok
post_id: "<id>"
url: <url>
account: <@cuenta>
reviewer: <marca de agua / autor de la reseña>
processed: <YYYY-MM-DD>
slides: <n>
---
# <título descriptivo>

<qué tipo de post es, leyenda de veredictos si aplica>

| Código | Perfume | Veredicto | Acción |
|---|---|---|---|
| 1a | [[Brand - Name]] | ❤️ | creado / fusionado / omitido |
```
