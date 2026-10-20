---
type: memory
updated: 2026-10-20
---
# Gotchas técnicos

## yt-dlp
- El paquete de apt (2024.04) ya no funciona con YouTube ("No video formats found").
  Usa una versión reciente (`pipx install yt-dlp` o el binario oficial de GitHub releases)
  y que quede primero en el PATH.

## Instagram
- Sin login, IG casi siempre bloquea. Usa `--cookies-from-browser <navegador>` (sesión iniciada en ese navegador).
- Carruseles de imágenes: `gallery-dl` los baja mejor que yt-dlp (que se enfoca en video).
- No probado todavía en este setup: si falla, pide capturas al usuario.

## TikTok
- `yt-dlp` NO soporta URLs `/photo/<id>`. Cambia a `/video/<id>` (mismo id) y funciona.
- `yt-dlp --dump-json` solo trae la portada. Las slides vienen en la respuesta cruda de la API:
  usar `--write-pages`; el `.dump` con `aweme_list[].image_post_info.images[].display_image.url_list`.
  `scripts/fetch_post.py` ya hace todo esto.
- `--write-pages` escribe los `.dump` en el **cwd**, no en `-o`. El script corre yt-dlp con `cwd=raw/`.
- El HTML de tiktok.com no trae datos sin JS (`__UNIVERSAL_DATA_FOR_REHYDRATION__` vacío). No sirve curl.
- El caption puede venir en otro idioma y no listar perfumes: los nombres salen de las slides.
- Slides: WebP 1200x1600. Convertir con ffmpeg a JPG.

## ffmpeg
- Dentro de `while read` usa `ffmpeg -nostdin`, si no se come el stdin del loop y trunca nombres.
- `tile` falla con imágenes de tamaños distintos: normaliza con `scale`+`pad` antes.

## Recorte de botellas (plantilla "Perfume & Diamond")
- Botellas en franja y≈390..890 (de 1600), columnas iguales (3 o 4 por slide).
- Margen lateral 12% por columna para quitar los "VS".
- Algunas traen "NEW 2025" arriba; aceptable.
- Otras plantillas: verifica con la hoja (`crops_sheet.jpg`) y ajusta `--y`, `--h`, `--margin`.
- Plantilla "Warm days / Cold days" (@f_fragrance_7): una botella partida entre dos perfumes.
  Usa modo `box` del mapa (`nombre slide box x y w h`) para recortar cada mitad.
- Slides de tamaños distintos: `fetch_post.py` normaliza miniaturas antes de armar la hoja.

## Contenido de los posts
- Barras de colores estilo Fragrantica = **acordes**, no notas. Guárdalos en la opinión;
  las notas (`Key Notes`) van aparte.
- Los creadores a veces ponen los acordes de otro flanker (p. ej. Born in Roma Intense con
  acordes de tabaco/pachulí). Si no cuadran, no cambies las notas y déjalo anotado.

## Notion MCP
- Subir imagen: `notion-create-file-upload` → POST multipart al `upload_url` con el header
  `authorization` devuelto → `notion-update-page` `update_properties`
  `{"Image":[{"type":"file_upload","file_upload":{"id":"<id>"}}]}`.
- El slot de `notion-create-file-upload` expira ~10 min después de crearlo (ver `expires_at`):
  crea slots en lotes de ~10, sube de inmediato y adjunta en el mismo turno.
- `rtk` (proxy de comandos) puede resumir la salida JSON de curl. Verifica con el HTTP code
  (`-w '%{http_code}'`), como hace `scripts/upload_notion.sh`.
- `update_properties` exige `properties`; no sirve para cambiar solo el ícono de una database.
- `create_database` con `parent` = Home pone la DB al final de Home.
- Sort por select es alfabético, no por orden de opciones.
- Crear hasta ~50 páginas en una sola llamada `notion-create-pages` funciona.
