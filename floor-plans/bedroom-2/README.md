# Bedroom 2 furniture layouts

Redrawn from the builder's main-level plan, in the same black-line style, with a
king bed, an 84" TV console and an 86" sofa placed two ways.

| File | Layout |
| --- | --- |
| `option-a-sofa-at-nook.png` | Sofa centered on the front nook |
| `option-b-sofa-on-bath-wall.png` | Sofa on the Bath 2 wall, next to the entry |
| `options-side-by-side.png` | Both options on one sheet |

## The front nook (bump-out)

- About **7'-0½" wide × 2'-3" deep** (≈ 84½" × 27"), centered on the front wall
  with about 3'-2" of wall on each side. It holds a twin window about 5'-3" wide.
- An **86" sofa does not fit inside it.** It's about 1½" wider than the nook,
  and baseboards take roughly another inch at the floor. Option A shows the sofa
  pushed back against the opening instead, which puts it 3'-2" into the room.
- A sofa about 82" wide or less would slide in. A typical 35–40" deep sofa would
  still stick out 8–13" because the nook is only 27" deep.

These sizes are scaled from the marketing plan, not field-measured. The scale was
calibrated so the room matches its labeled 13'-4" × 16'-4". The Study, Dining
and Master Suite labels agree with that scale to within 0.3%. Measure the nook
wall-to-wall before buying anything for it.

## Furniture sizes used

King bed 80" × 86" (76" × 80" mattress) · nightstands 22" × 16" ·
TV console 84" × 18" · sofa 86" × 38" deep (depth assumed).

## Regenerating

```sh
python3 generate.py                     # writes the .svg sheets
NODE_PATH=$(npm root -g) node render.cjs  # renders each .svg to a 2x .png (Playwright)
```

Furniture positions and notes live in `OPTIONS` near the top of `generate.py`.
All coordinates are in inches from the room's northwest interior corner.
