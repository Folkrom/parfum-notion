---
type: config
---
# Notion — IDs y schema

## Ubicación

- Workspace page **Home**: `74912d7d99054fe28bc89fbc667e37a0`
- Database **Perfume Wish List**: `08940e4c553c4f3ca2191f607654523f`
  - URL: https://app.notion.com/p/08940e4c553c4f3ca2191f607654523f
  - Data source (para crear filas / consultar): `collection://57ab3018-ba4c-4ab5-b964-c9d20a5f38f0`
- DB hermana (otros productos, mismo estilo): **Wish List** `28644431-479b-80c4-875e-d68528e1519a`

## Vistas

| Vista | ID | Para qué |
|---|---|---|
| Quick Add | `view://d7a6637a-4801-40a3-8a6b-17a89d45724c` | Captura rápida |
| Gallery View | `view://3fe44431-479b-817d-90af-000caf8ed95d` | Activos (sin Owned / Not for Me), por prioridad |
| Main Table | `view://3fe44431-479b-8166-abaa-000cde4da90b` | Todas las columnas |
| Pipeline | `view://3fe44431-479b-812e-9b4d-000cbcc525aa` | Board por Status |
| Inbox (por completar) | `view://3fe44431-479b-81eb-81d9-000c054f490a` | Sin precio |
| By Scent Family | `view://3fe44431-479b-8183-965a-000c50bc5c38` | Board por familia |

## Propiedades (nombre exacto → tipo → valores)

| Propiedad | Tipo | Valores / notas |
|---|---|---|
| `Perfume` | title | Nombre `<Línea> <Variante>` |
| `Image` | files | Usar `[{"type":"file_upload","file_upload":{"id":"<id>"}}]` en `update_properties` |
| `Brand` | text | |
| `Concentration` | select | EDT, EDP, Parfum, Extrait, EDC, Body Mist |
| `Scent Family` | multi_select | Fresh, Citrus, Aquatic, Aromatic, Woody, Amber/Oriental, Spicy, Gourmand, Vanilla, Floral, Leather, Musky, Powdery, Fougère, Chypre |
| `Key Notes` | text | Lista separada por comas |
| `Season` | multi_select | Spring, Summer, Autumn, Winter |
| `Occasion` | multi_select | Daily, Office, Night Out, Date, Special Event |
| `Size (ml)` | number | |
| `Price` | number (MXN) | |
| `Price per ml` | formula | Automática |
| `Buy Option` | select | Full Bottle, Tester, Decant, Sample, Gift Set |
| `Store` | multi_select | Amazon, Mercado Libre, Liverpool, Palacio de Hierro, Sephora, Sanborns, Notino, Decant Shop, Other |
| `Link to Buy`, `L2B2`, `L2B3` | url | Hasta 3 opciones de compra |
| `Source` | select | Instagram, TikTok, YouTube, Reddit, Fragrantica, Friend, Store, Other |
| `Source Link` | url | Primera fuente; las demás van en el contenido de la página |
| `Priority` | select | High, Medium, Low |
| `Status` | status | Interested, Want to Test, Tested - Liked, Saving For, Waiting for Sale, Ordered, Owned, Not for Me |
| `My Rating` | select | ⭐️ … ⭐️⭐️⭐️⭐️⭐️, Not tested (solo del usuario) |
| `Target Purchase Date` | date | `date:Target Purchase Date:start` |
| `Monthly Contribution` | number (MXN) | |
| `Added` | created_time | Automática |

Multi-selects al crear filas: pasar string JSON, p. ej. `"[\"Spring\",\"Summer\"]"`.

## Contenido de página (convención)

Cada fila lleva en su contenido una línea por opinión externa:

```
Reseña del post (<autor/cuenta>): <emoji/veredicto> <contexto>
```

Al fusionar, se agregan líneas; no se reemplazan.
