---
type: workflow
---
# Detectar y fusionar repetidos

## Cuándo dos entradas son el mismo perfume

Mismo **Brand** + misma **línea** + misma **variante/concentración**.

| Caso | ¿Mismo? |
|---|---|
| "Sauvage Elixir" vs "Dior Sauvage Elixir" | Sí |
| "Bleu de Chanel EDT" vs "Bleu de Chanel EDP" | No (variantes distintas) |
| "Light Blue Intense" vs "Light Blue Eau Intense Pour Homme" | Sí |
| "Y EDP" vs "Y Eau de Parfum" | Sí |
| "Imagination" en dos slides distintas | Sí |
| Versión reformulada / "NEW 2025" con mismo nombre | Sí, anota la reformulación |
| Pour Homme vs Pour Femme | No |
| "Uomo Born in Roma" (sin sufijo) vs "Born in Roma Uomo EDT" | Sí (sin sufijo = original/EDT) |
| "Le Beau Le Parfum" vs "Le Male Le Parfum" | No (líneas distintas, aunque el score salga alto) |

Herramienta: `python3 scripts/vault_index.py match "<texto>"`. Revisa el top 5; el score es
orientativo, decide por las reglas de arriba. Dentro de un mismo post, agrupa repetidos antes
de buscar en el vault.

## Cómo fusionar

Fila **existente** en Notion = la que se conserva. Nunca crees una segunda.

1. Compara campo por campo (fuente nueva vs existente):
   - `Key Notes`: unión, sin repetir, notas principales primero. Si se contradicen, conserva
     las de la fuente más legible/confiable y anota la diferencia en la página.
   - `Scent Family`, `Season`, `Occasion`: unión (máx. ~3 familias; elige las dominantes).
   - `Concentration`: si estaba vacía y la nueva fuente la confirma, llénala. Si chocan, no la
     cambies; anota la duda.
   - `Price`, `Priority`, `Status`, `My Rating`, links: **no tocar** (son del usuario).
   - `Source Link`: se queda la primera. Las nuevas fuentes van en el contenido.
   - `Image`: se queda la existente salvo que no tenga o la nueva sea claramente mejor.
2. `notion-update-page` → `update_properties` con los campos cambiados.
3. `notion-update-page` → `insert_content` (al final) con la línea de opinión de la nueva fuente:
   `Reseña del post (<cuenta>): <veredicto> <contexto>`.
4. Vault: `scripts/upsert_note.py` sobre la misma nota (une listas, agrega opinión y fuente).
5. En `sources/<post>.md`, acción = `fusionado con [[nota]]` + qué cambió.

## Duplicados ya creados por error

Si encuentras dos filas del mismo perfume en Notion: fusiona en la más antigua (`Added`),
y pide confirmación al usuario antes de borrar la otra.
