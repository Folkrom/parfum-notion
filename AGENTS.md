# Parfum Notion — instrucciones para agentes

Vault de Obsidian + flujo agéntico para mantener la wish list de perfumes del usuario.
Cualquier agente (Claude, otro modelo) debe leer este archivo completo antes de actuar.

## Qué es esto

- **Notion** = interfaz principal del usuario. DB `Perfume Wish List` (IDs en `config/notion.md`).
- **Este vault** = memoria del agente y espejo de Notion: una nota por perfume con su
  `notion_page_id`, opiniones de cada fuente, y una nota por cada post procesado.
  Sirve para detectar duplicados sin consultar Notion y para guardar contexto que no cabe en la DB.
- Regla: todo perfume que exista en Notion tiene nota en `perfumes/`, y viceversa.
  Si cambias uno, actualiza el otro en el mismo turno.

## Mapa del vault

| Ruta | Contenido |
|---|---|
| `Home.md` | Entrada del vault (Obsidian) |
| `config/notion.md` | IDs de Notion, schema, opciones válidas, vistas |
| `memory/user-preferences.md` | Preferencias y decisiones del usuario. **Léelo siempre.** |
| `memory/gotchas.md` | Problemas técnicos conocidos y su solución |
| `workflows/ingest-social-post.md` | Procesar un post (TikTok, Instagram, YouTube, capturas) de punta a punta |
| `docs/enrichment.md` | Fuentes de datos de perfumes (Fragrantica y APIs alternativas) |
| `workflows/dedupe-merge.md` | Detectar y fusionar repetidos |
| `workflows/opinions.md` | Registrar opiniones, ratings y compras del usuario |
| `perfumes/<Brand> - <Name>.md` | Una nota por perfume (frontmatter = propiedades) |
| `sources/<platform>-<id>.md` | Una nota por post procesado |
| `attachments/` | Imágenes de botellas (las mismas que se suben a Notion) |
| `inbox/` | Descargas crudas de posts (temporal, no versionar) |
| `scripts/` | Herramientas (ver abajo) |

## Herramientas

Requisitos: `python3`, `yt-dlp` **reciente** (las versiones de apt fallan con YouTube/TikTok),
`ffmpeg`, `curl`, y el **MCP de Notion** conectado. Opcional: `gallery-dl` para carruseles de Instagram.

| Script | Uso |
|---|---|
| `scripts/fetch_post.py URL` | Descarga slides o frames + caption + transcript de TikTok / Instagram / YouTube a `inbox/<platform>-<id>/` y arma `sheet.jpg` |
| `scripts/crop_bottles.py --slides DIR --map FILE --out DIR` | Recorta botellas según un mapa y arma hoja de verificación |
| `scripts/vault_index.py list` / `match "texto"` | Lista perfumes del vault / busca candidatos duplicados (fuzzy) |
| `scripts/upsert_note.py < data.json` | Crea o fusiona notas de perfume (no pisa datos existentes salvo `--overwrite`) |
| `scripts/upload_notion.sh DIR < lines` | Sube imágenes a los slots de `notion-create-file-upload` |

Corre los scripts desde la raíz del vault. Lee el `--help` de cada uno antes de usarlo.

## Reglas

1. Responde al usuario en español. Moneda: MXN.
2. Antes de crear un perfume, busca duplicados: `scripts/vault_index.py match "<brand> <name>"`.
   Si hay match, sigue `workflows/dedupe-merge.md`; nunca crees una fila duplicada en Notion.
3. Nombres: `<Línea> <Variante>` como lo nombra la marca (p. ej. `Sauvage Elixir`, `Y EDP Intense`).
   `Brand` aparte. Concentración en su propiedad, no repetida en el nombre salvo que sea parte
   del nombre oficial (p. ej. `Bleu de Chanel EDP` sí, para distinguir variantes).
4. `My Rating` es SOLO del usuario. Las calificaciones de reseñadores van como opinión
   (contenido de la página en Notion + sección `## Opiniones` en la nota).
5. No inventes precios. `Price`, `Priority`, `Link to Buy` los llena el usuario o se buscan
   solo si él lo pide.
6. Notas olfativas: usa lo que dice la fuente; complementa con conocimiento general solo si
   la fuente es ilegible, y dilo en el reporte.
7. Si un dato es dudoso (p. ej. concentración ambigua), déjalo vacío y anótalo en la página.
8. Pregunta antes de borrar filas en Notion. Fusionar = actualizar la fila existente
   y borrar (o mover a `Not for Me`) solo la duplicada que tú creaste, con confirmación.
9. Al terminar un post: nota en `sources/`, notas de perfumes actualizadas, filas en Notion
   con imagen, y reporte corto al usuario (qué se creó, qué se fusionó, qué quedó pendiente).
