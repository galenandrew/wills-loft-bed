"""sheets.site — assemble site-v2/: pages of figures, each with its own switch board.

The toolbar is generated from what each figure actually drew, so it cannot list a
component the drawing does not contain, or miss one it does. Switching is pure
CSS on the figure's own root element — no redraw, no second copy of the geometry,
and it prints exactly what is on screen.
"""
import datetime
import html
import json
import os

from drawings.model import REV, RX, RY, CEILING, DECK, fr, E
from . import taxonomy as tx
from .style import BG, CARD, INK, INK2, INK3, LINE, svg_css

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "site-v2")

PAGES = [
    ("index",    "Overview",        ["s1_isometric", "s2_front_elevation", "s3_floor_plan"]),
    ("stairs",   "Stairs & nook",   ["s4_stair_section", "s5_stair_framing", "s6_tread_detail"]),
    ("halfwall", "Half wall",       ["s7_half_wall", "s12_panel_layout"]),
    ("loft",     "Loft & screen",   ["s8_loft_section", "s9_loft_framing",
                                     "s10_beam_end", "s11_ledge_detail"]),
]

CSS = f"""
*{{box-sizing:border-box}}
body{{margin:0;background:{BG};color:{INK};font:14px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}}
.wrap{{max-width:1180px;margin:0 auto;padding:26px 22px 80px}}
header{{border-bottom:2px solid {INK};padding-bottom:13px;margin-bottom:18px}}
h1{{font-size:21px;margin:0 0 4px}}
.meta{{color:{INK2};font-size:12.5px;display:flex;gap:15px;flex-wrap:wrap;align-items:center}}
.rev{{background:{INK};color:#fff;padding:2px 9px;border-radius:99px;font-weight:700;font-size:11.5px;letter-spacing:.04em}}
nav.tabs{{position:sticky;top:0;z-index:20;background:{BG};display:flex;gap:6px;padding:9px 0;margin:-4px 0 18px;border-bottom:1px solid {LINE}}}
nav.tabs a{{color:{INK2};text-decoration:none;padding:7px 13px;border-radius:6px;font-size:13.5px;font-weight:600}}
nav.tabs a:hover{{background:#f1efe9;color:{INK}}}
nav.tabs a.here{{background:{INK};color:#fff}}
.dwg{{background:{CARD};border:1px solid {LINE};border-radius:10px;padding:16px 18px 14px;margin-bottom:22px}}
.dwg h2{{font-size:13px;text-transform:uppercase;letter-spacing:.08em;color:{INK2};margin:0 0 10px;font-weight:700}}
.dwg h2 b{{color:{INK};font-size:14px;text-transform:none;letter-spacing:0}}
.cap{{color:{INK2};font-size:12.5px;margin:12px 2px 0;max-width:82ch}}
.tools{{display:flex;flex-wrap:wrap;gap:14px;align-items:center;border:1px solid {LINE};
  border-radius:8px;padding:8px 10px;margin-bottom:12px;background:#fcfbf9}}
.grp{{display:flex;gap:5px;align-items:center;flex-wrap:wrap}}
.grp>span.gl{{font-size:10px;text-transform:uppercase;letter-spacing:.07em;color:{INK3};margin-right:2px}}
.chip{{font:inherit;font-size:12px;line-height:1;border:1px solid {LINE};background:#fff;color:{INK2};
  border-radius:99px;padding:5px 10px;cursor:pointer;user-select:none}}
.chip:hover{{border-color:{INK3}}}
.chip[aria-pressed="true"]{{background:{INK};border-color:{INK};color:#fff}}
.chip.rst{{border-style:dashed}}
figure{{margin:0;overflow-x:auto}}
{svg_css()}
@media print{{
  nav.tabs,.tools,header .meta{{display:none}}
  body{{background:#fff}}
  .dwg{{border:none;padding:0;break-inside:avoid;page-break-after:always;margin:0 0 8px}}
  .wrap{{max-width:none;padding:0}}
}}
"""

JS = """
(function(){
  function apply(fig, st){
    fig.className = 'dwg' + (st.length ? ' ' + st.join(' ') : '');
  }
  document.querySelectorAll('.dwg[data-fig]').forEach(function(fig){
    // The stored state is keyed by the figure AND by its defaults, so a sheet
    // whose default switches change starts fresh instead of restoring a state
    // that no longer means anything.
    var key = 'dwg2:' + fig.dataset.fig + ':' + (fig.dataset.off || '');
    var saved = null;
    try { saved = JSON.parse(localStorage.getItem(key)); } catch(e) {}
    var state = saved || JSON.parse(fig.dataset.off || '[]');
    apply(fig, state);
    function sync(){
      fig.querySelectorAll('.chip[data-cls]').forEach(function(b){
        b.setAttribute('aria-pressed', state.indexOf(b.dataset.cls) < 0 ? 'true' : 'false');
      });
      apply(fig, state);
      try { localStorage.setItem(key, JSON.stringify(state)); } catch(e) {}
    }
    fig.querySelectorAll('.chip[data-cls]').forEach(function(b){
      b.addEventListener('click', function(){
        var c = b.dataset.cls, i = state.indexOf(c);
        if (i < 0) state.push(c); else state.splice(i, 1);
        sync();
      });
    });
    var rst = fig.querySelector('.chip.rst');
    if (rst) rst.addEventListener('click', function(){
      state = JSON.parse(fig.dataset.off || '[]'); sync();
    });
    sync();
  });
})();
"""


def hide_rules():
    """One CSS rule per switch — generated, so a new component cannot be added to
    the taxonomy and left unswitchable."""
    out = []
    for c in tx.COMPONENTS:
        out.append(f'.off-c-{c} [data-c="{c}"]{{display:none}}')
    for l in tx.LAYERS + ["context"]:
        out.append(f'.off-l-{l} [data-l="{l}"]{{display:none}}')
    out.append(".off-labels .lay-labels{display:none}")
    out.append(".off-dims .lay-dims{display:none}")
    return "\n".join(out)


def toolbar(fig):
    def chip(cls, label):
        return f'<button class="chip" type="button" data-cls="{cls}">{E(label)}</button>'
    groups = []
    if fig.components:
        groups.append('<div class="grp"><span class="gl">Components</span>'
                      + "".join(chip(f"off-c-{c}", tx.LABEL[c]) for c in fig.components) + "</div>")
    if len(fig.layers) > 1 or (fig.layers and fig.layers[0] != "context"):
        groups.append('<div class="grp"><span class="gl">Layers</span>'
                      + "".join(chip(f"off-l-{l}", tx.LAYER_LABEL.get(l, l.title()))
                                for l in fig.layers if l != "context") + "</div>")
    groups.append('<div class="grp"><span class="gl">Annotation</span>'
                  + chip("off-labels", "Labels") + chip("off-dims", "Dimensions")
                  + '<button class="chip rst" type="button">Reset</button></div>')
    return '<div class="tools">' + "".join(groups) + "</div>"


def figure_card(sheet, fig):
    off = json.dumps(fig.off)          # already chip classes, not bare names
    title = fig.title or sheet.TITLE
    # The default state is in the class attribute as well as in data-off, so the
    # figure is right before any script runs — and prints right from a cold load.
    cls = " ".join(["dwg"] + fig.off)
    return (f'<div class="{cls}" id="{fig.key}" data-fig="{fig.key}" data-off=\'{off}\'>'
            f'<h2>{sheet.NUMBER} — <b>{E(title)}</b></h2>'
            f'{toolbar(fig)}<figure>{fig.svg}</figure>'
            f'<p class="cap">{sheet.CAPTION}</p></div>')


def page(slug, title, cards, today):
    tabs = "".join(
        f'<a href="{s}.html"{" class=\"here\"" if s == slug else ""}>{E(t)}</a>'
        for s, t, _ in PAGES)
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{E(title)} · Rev {E(REV)}</title>'
            f'<link rel="stylesheet" href="style.css"></head><body><div class="wrap">'
            f'<header><h1>Loft bed · {E(title)}</h1><div class="meta">'
            f'<span class="rev">REV {E(REV)}</span>'
            f'<span>{fr(RX)} × {fr(RY)} room · {fr(CEILING)} ceiling · deck {fr(DECK)} AFF</span>'
            f'<span>generated {today} from dimensions.yaml</span></div></header>'
            f'<nav class="tabs">{tabs}</nav>{"".join(cards)}</div>'
            f'<script>{JS}</script></body></html>')


def build(verbose=True):
    import importlib
    os.makedirs(OUT, exist_ok=True)
    today = datetime.date.today().isoformat()
    figs = {}
    for slug, title, mods in PAGES:
        cards = []
        for name in mods:
            mod = importlib.import_module(f"sheets.{name}")
            for key, fn in mod.FIGURES:
                fig = fn()
                figs[key] = fig
                cards.append(figure_card(mod, fig))
        open(os.path.join(OUT, f"{slug}.html"), "w").write(page(slug, title, cards, today))
    open(os.path.join(OUT, "style.css"), "w").write(CSS + "\n" + hide_rules() + "\n")
    return figs
