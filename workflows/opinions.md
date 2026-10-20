---
type: workflow
---
# Opiniones, ratings y compras del usuario

Cuando el usuario cuenta algo de un perfume ("lo probé", "huele a…", "lo compré", "no me gustó"):

1. Localiza la nota: `python3 scripts/vault_index.py match "<texto>"`.
2. Actualiza Notion según el caso:

| Usuario dice | Notion |
|---|---|
| Lo probó y le gustó | `Status` = `Tested - Liked`, `My Rating` si da calificación |
| Lo probó y no le gustó | `Status` = `Not for Me`, `My Rating` |
| Quiere probarlo | `Status` = `Want to Test` |
| Ahorrando / esperando oferta | `Saving For` / `Waiting for Sale` (+ `Target Purchase Date`, `Monthly Contribution` si los da) |
| Lo pidió / lo compró | `Ordered` / `Owned` (+ `Price`, `Store`, `Buy Option`, `Size (ml)` si los da) |
| Precio o link | `Price`, `Link to Buy` / `L2B2` / `L2B3`, `Store` |

3. Agrega su comentario al contenido de la página en Notion:
   `Mi opinión (<YYYY-MM-DD>): <texto>`.
4. En la nota del vault, agrégalo en `## Mis notas` con fecha (o usa `upsert_note.py` con
   `my_notes`), y actualiza el frontmatter (`status`, `my_rating`, `price_mxn`…).

Si el perfume no existe todavía, créalo (ingest manual: sin fuente social, `Source` = `Friend`/`Store`/`Other`).
