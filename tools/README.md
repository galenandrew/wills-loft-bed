# tools/

Figure generators that render inline SVG straight from the yaml — the seed of `drawings.py`.

- `svgview.py` — orthographic `View` helper (plan / elevation / section, dimension strings, hatching).
- `sketch_U.py <yaml> <out.json>` — Rev U landing figures (plan, side section, y=20 section). Run from the repo root: `python3 tools/sketch_U.py dimensions.yaml /tmp/figs.json`.
- `sketch_T.py <out.json> [yaml]` — the Rev T as-drawn figures, from `archive/dimensions-T.yaml`.

Both import `verify.py` for the member expansion and stair geometry, so a figure can never disagree with the checker.
