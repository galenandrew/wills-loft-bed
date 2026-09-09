"""sheets.site — assemble docs/: pages of figures, each with its own switch board.

The toolbar is generated from what each figure actually drew, so it cannot list a
component the drawing does not contain, or miss one it does. Switching is pure
CSS on the figure's own root element — no redraw, no second copy of the geometry,
and it prints exactly what is on screen.
"""
import datetime
import html
import json
import os
import re

from drawings.model import REV, RX, RY, CEILING, DECK, fr, E
# The reference pages render through the Rev U card builders rather than a second
# copy of them: content/ is the source for both sets, so an edit to open-items.yaml
# or revisions.json shows up in v1 and v2 without either being kept in step by hand.
from drawings.site import (card_fasteners, card_locked, card_revisions,
                           card_schedule, card_sequencing, card_structure,
                           cards_open)
from . import cutlist
from . import taxonomy as tx
from .style import BG, CARD, DIM, INK, INK2, INK3, LINE, svg_css

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs")

# A page is either drawings (a list of sheet modules) or reference (REF).
REF = "reference"

PAGES = [
    ("index",     "Overview",      ["s1_isometric", "s2_front_elevation", "s3_floor_plan"]),
    ("stairs",    "Stairs & nook", ["s4_stair_section", "s5_stair_framing", "s6_tread_detail"]),
    ("halfwall",  "Half wall",     ["s7_half_wall", "s12_panel_layout"]),
    ("loft",      "Loft & screen", ["s8_loft_section", "s9_loft_framing",
                                    "s10_beam_end", "s11_ledge_detail"]),
    ("cutlist",   "Cut list",      REF),
    ("schedule",  "Schedule",      REF),
    ("fasteners", "Fasteners",     REF),
    ("open",      "Open items",    REF),
    ("appendix",  "Appendix",      REF),
    ("revisions", "Revisions",     REF),
]


def card_summary():
    """"The design in one line" — the summary from open-items.yaml. It sits at the
    foot of the Overview rather than on the Open Items page: it is what the build
    IS, not something outstanding about it."""
    return next(h for a, _l, h in cards_open() if a == "open-summary")


def reference_cards(slug):
    """The pages that are prose and tables rather than drawings."""
    if slug == "open":
        return [h for a, _l, h in cards_open() if a != "open-summary"]
    if slug == "cutlist":
        return cutlist.cards()
    if slug == "schedule":
        return [card_locked(), card_schedule()]
    if slug == "fasteners":
        return [card_fasteners()]
    if slug == "appendix":
        return [card_sequencing(), card_structure()]
    if slug == "revisions":
        return [card_revisions()]
    raise KeyError(slug)

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
nav.tabs a:focus-visible{{outline:2px solid {DIM};outline-offset:1px}}
nav.tabs a.arrow{{font-size:18px;padding:5px 12px;border:1px solid {LINE};background:{CARD};color:{INK};line-height:1.1}}
nav.tabs a.arrow:hover{{background:#f1efe9}}
nav.tabs a.arrow.off{{opacity:.3;pointer-events:none}}
nav.tabs .sp{{flex:1}}
.pn{{display:flex;justify-content:space-between;align-items:baseline;gap:16px;font-size:13px;margin-top:4px}}
.pn a{{color:{DIM};text-decoration:none;padding:8px 0}}
.pn a:hover{{text-decoration:underline}}
.pn .hint{{color:{INK3};font-size:12px}}
kbd{{font:11px ui-monospace,Menlo,monospace;border:1px solid {LINE};border-radius:3px;padding:0 4px;background:{CARD}}}
.dwg{{background:{CARD};border:1px solid {LINE};border-radius:10px;padding:16px 18px 14px;margin-bottom:22px}}
.dwg h2{{font-size:13px;text-transform:uppercase;letter-spacing:.08em;color:{INK2};margin:0 0 10px;font-weight:700}}
.dwg h2 b{{color:{INK};font-size:14px;text-transform:none;letter-spacing:0}}
.cap{{color:{INK2};font-size:12.5px;margin:12px 2px 0;max-width:82ch}}
.tools{{display:flex;flex-direction:column;gap:8px;border:1px solid {LINE};
  border-radius:8px;padding:8px 10px;margin-bottom:12px;background:#fcfbf9}}
.trow{{display:flex;flex-wrap:wrap;gap:14px;align-items:center}}
.grp{{display:flex;gap:5px;align-items:center;flex-wrap:wrap}}
.grp>span.gl{{font-size:10px;text-transform:uppercase;letter-spacing:.07em;color:{INK3};margin-right:2px;display:inline-block;min-width:76px}}
.chip{{font:inherit;font-size:12px;line-height:1;border:1px solid {LINE};background:#fff;color:{INK2};
  border-radius:99px;padding:5px 10px;cursor:pointer;user-select:none}}
.chip:hover{{border-color:{INK3}}}
.chip[aria-pressed="true"]{{background:{INK};border-color:{INK};color:#fff}}
.chip.rst{{border-style:dashed}}
figure{{margin:0;overflow-x:auto}}
nav.tabs{{flex-wrap:wrap}}

/* --- reference pages: open items, schedule, fasteners, appendix, revisions.
   The HTML comes from the Rev U card builders (drawings/site.py); these are the
   same classes in this set's palette, so content/ stays the single source. --- */
.card{{background:{CARD};border:1px solid {LINE};border-radius:10px;padding:18px 20px;margin-bottom:20px}}
.card h2{{font-size:12px;text-transform:uppercase;letter-spacing:.09em;color:{INK2};margin:0 0 12px;font-weight:700}}
.card h2.section{{font-size:15px;text-transform:none;letter-spacing:0;color:{INK};border-bottom:2px solid {INK};padding-bottom:6px;margin:30px 0 16px}}
.specs{{display:grid;grid-template-columns:repeat(auto-fit,minmax(168px,1fr));gap:1px;background:{LINE};border:1px solid {LINE};border-radius:8px;overflow:hidden;margin:0}}
.spec{{background:{CARD};padding:11px 13px}}
.spec dt{{font-size:11px;color:{INK3};text-transform:uppercase;letter-spacing:.05em;margin-bottom:3px}}
.spec dd{{margin:0;font-size:16px;font-weight:650;font-variant-numeric:tabular-nums}}
.spec dd span{{font-size:11.5px;font-weight:400;color:{INK2};display:block;margin-top:1px}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
th,td{{text-align:left;padding:7px 10px;border-bottom:1px solid {LINE};vertical-align:top;overflow-wrap:break-word}}
th{{font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:{INK3};font-weight:700}}
td.n{{font-variant-numeric:tabular-nums;white-space:nowrap}}
tr:last-child td{{border-bottom:none}}
td .cap{{display:inline;margin:0;font-size:12px}}
.miss{{color:#a3241c}}
code{{font-size:12.5px;background:#f1efe9;padding:1px 4px;border-radius:3px}}
.note{{border-left:3px solid #c0392b;background:#fdf4f2;padding:11px 14px;border-radius:0 6px 6px 0;font-size:13px;margin-top:14px}}
.note b{{color:#c0392b}}
.card ul{{margin:0;padding-left:19px}}
.card li{{margin-bottom:7px}}
ul.todo{{list-style:none;padding-left:2px;font-size:13.5px}}
ul.todo li{{margin-bottom:6px;padding-left:24px;position:relative;line-height:1.45}}
ul.todo li::before{{content:"";position:absolute;left:0;top:2px;width:12px;height:12px;border:1.5px solid {INK3};border-radius:3px;background:{BG}}}
ul.todo li b{{font-weight:600}}
.why{{color:{INK2};font-weight:400;font-size:12.5px;display:block;margin-top:1px}}
.tag{{display:inline-block;font-size:10.5px;font-weight:700;letter-spacing:.05em;padding:1.5px 7px;border-radius:4px;vertical-align:1px}}
.t-open{{background:#fdf1e3;color:#b07d1a}}.t-lock{{background:#e8f0e9;color:#4a7c4e}}.t-chk{{background:#fbe9e7;color:#c0392b}}
details.done summary{{cursor:pointer;font-size:12.5px;color:{INK2};display:flex;gap:9px;align-items:baseline;list-style:none}}
details.done summary::-webkit-details-marker{{display:none}}
details.done summary::before{{content:"▸";color:{INK3};font-size:11px;line-height:1.4}}
details.done[open] summary::before{{content:"▾"}}
details.done ul{{margin-top:11px;font-size:12.5px;color:{INK2}}}
.sum{{margin:-2px 0 0;font-size:12.5px;color:{INK2};max-width:none}}

/* --- cut list page: the nest tiles, the lightbox, and the wide takeoff tables --- */
.nesth{{font-size:12.5px;font-weight:700;color:{INK};margin:20px 0 8px}}
.nesth:first-of-type{{margin-top:4px}}
.nestgrid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(186px,1fr));
  gap:15px;margin-bottom:6px}}
.nestcell{{display:block;width:100%;padding:0;border:0;background:none;font:inherit;
  color:inherit;text-align:left;cursor:zoom-in}}
.nestcell>svg{{display:block;width:100%;height:auto;border-radius:5px;
  font-family:ui-sans-serif,system-ui,sans-serif;fill:{INK}}}
.nestcell:hover>svg{{outline:2px solid {DIM};outline-offset:2px}}
.nestcell:focus-visible>svg{{outline:2px solid {DIM};outline-offset:2px}}
.nestcap{{display:flex;justify-content:space-between;gap:8px;font-size:11.5px;
  color:{INK2};margin-top:6px}}
.nestcap b{{color:{INK};font-weight:700;font-variant-numeric:tabular-nums}}
.lb{{position:fixed;inset:0;z-index:60;background:rgba(28,26,22,.95);
  display:flex;align-items:center;justify-content:center;gap:8px;padding:52px 12px 16px}}
.lb[hidden]{{display:none}}
.lbbar{{position:absolute;top:0;left:0;right:0;display:flex;align-items:center;gap:14px;
  padding:11px 14px;color:#fff;font-size:13px}}
.lbcap{{font-weight:650}}
.lbn{{color:#bfb9ad;font-size:12px;flex:1;font-variant-numeric:tabular-nums}}
.lbbtn{{font:inherit;background:rgba(255,255,255,.1);color:#fff;border:1px solid rgba(255,255,255,.25);
  border-radius:7px;cursor:pointer;line-height:1;padding:9px 13px}}
.lbbtn:hover{{background:rgba(255,255,255,.2)}}
.lbbtn:disabled{{opacity:.28;cursor:default}}
.lbx{{font-size:19px;padding:5px 12px}}
.lbnav{{font-size:21px;flex:0 0 auto}}
.lbstage{{flex:1;height:100%;display:flex;align-items:center;justify-content:center;min-width:0}}
.lbstage svg{{max-height:100%;max-width:100%;width:auto;height:100%;
  font-family:ui-sans-serif,system-ui,sans-serif;fill:{INK};
  background:{CARD};border-radius:6px}}
.scroll{{overflow-x:auto}}
#cutlist td,#layout td,#buy td{{font-size:12.5px}}
{svg_css()}
@media print{{
  nav.tabs,.tools,header .meta,.pn{{display:none}}
  body{{background:#fff}}
  .dwg{{border:none;padding:0;break-inside:avoid;page-break-after:always;margin:0 0 8px}}
  .card{{border:none;padding:0;break-inside:avoid}}
  .nestgrid{{grid-template-columns:repeat(4,1fr);break-inside:avoid}}
  .nestcell{{cursor:default}}
  .lb{{display:none!important}}
  details.done{{display:none}}
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

// The sheet nest, enlarged. Each tile is its own <svg>, so the lightbox shows the
// tile's own node cloned rather than a second rendering of it — the enlarged sheet
// IS the thumbnail, and there is nothing to keep in step.
(function(){
  var lb = document.getElementById('lb');
  if (!lb) return;
  var cells = [].slice.call(document.querySelectorAll('.nestcell'));
  var stage = lb.querySelector('.lbstage'), cap = lb.querySelector('.lbcap'),
      num = lb.querySelector('.lbn'),
      prev = lb.querySelector('.lbprev'), next = lb.querySelector('.lbnext');
  var at = -1, opener = null;
  function show(i){
    if (i < 0 || i >= cells.length) return;
    at = i;
    stage.replaceChildren(cells[i].querySelector('.nestbig svg').cloneNode(true));
    cap.textContent = cells[i].dataset.cap;
    num.textContent = (i + 1) + ' of ' + cells.length;
    prev.disabled = i === 0;
    next.disabled = i === cells.length - 1;
  }
  function open(i){
    opener = cells[i];
    lb.hidden = false;
    show(i);
    next.disabled ? (prev.disabled ? lb.querySelector('.lbx') : prev).focus() : next.focus();
  }
  function close(){
    lb.hidden = true;
    stage.replaceChildren();
    if (opener) opener.focus();
  }
  cells.forEach(function(c, i){ c.addEventListener('click', function(){ open(i); }); });
  prev.addEventListener('click', function(){ show(at - 1); });
  next.addEventListener('click', function(){ show(at + 1); });
  lb.querySelector('.lbx').addEventListener('click', close);
  // Clicking the backdrop closes; clicking the sheet itself does not.
  lb.addEventListener('click', function(e){ if (e.target === lb || e.target === stage) close(); });
  document.addEventListener('keydown', function(e){
    if (lb.hidden || e.altKey || e.ctrlKey || e.metaKey) return;
    if (e.key === 'Escape') { e.preventDefault(); close(); }
    else if (e.key === 'ArrowLeft') { e.preventDefault(); show(at - 1); }
    else if (e.key === 'ArrowRight') { e.preventDefault(); show(at + 1); }
    else if (e.key === 'Tab') {  // keep focus inside the dialog while it is open
      var f = [].slice.call(lb.querySelectorAll('button:not(:disabled)'));
      var i = f.indexOf(document.activeElement) + (e.shiftKey ? -1 : 1);
      e.preventDefault();
      f[(i + f.length) % f.length].focus();
    }
  });
})();

// ← / → switch pages, the same keys the Rev U set uses. The destinations come
// off the <nav>, so the keys and the arrow buttons cannot drift apart.
(function(){
  var n = document.querySelector('nav.tabs');
  if (!n) return;
  document.addEventListener('keydown', function(e){
    if (e.altKey || e.ctrlKey || e.metaKey || e.shiftKey) return;
    if (e.target.closest('input,textarea,select,[contenteditable]')) return;
    // While the lightbox is up the arrows step through sheets, not pages.
    var lb = document.getElementById('lb');
    if (lb && !lb.hidden) return;
    var t = e.key === 'ArrowLeft' ? n.dataset.prev
          : e.key === 'ArrowRight' ? n.dataset.next : '';
    if (t) { e.preventDefault(); location.href = t + '.html'; }
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
    # One row per axis: what is drawn, what kind of thing it is, and what is
    # written about it. Each row's label sits at its head, so the three read as a
    # list rather than as a wall of chips.
    def row(label, chips):
        return (f'<div class="trow"><div class="grp"><span class="gl">{label}</span>'
                + "".join(chips) + "</div></div>")

    rows = []
    if fig.components:
        rows.append(row("Components",
                        [chip(f"off-c-{c}", tx.LABEL[c]) for c in fig.components]))
    if len(fig.layers) > 1 or (fig.layers and fig.layers[0] != "context"):
        rows.append(row("Layers",
                        [chip(f"off-l-{l}", tx.LAYER_LABEL.get(l, l.title()))
                         for l in fig.layers if l != "context"]))
    rows.append(row("Annotation",
                    [chip("off-labels", "Labels"), chip("off-dims", "Dimensions"),
                     '<button class="chip rst" type="button">Reset</button>']))
    return '<div class="tools">' + "".join(rows) + "</div>"


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


def _neighbours(slug):
    names = [s for s, _t, _s in PAGES]
    i = names.index(slug)
    return (names[i - 1] if i > 0 else None,
            names[i + 1] if i + 1 < len(names) else None)


def nav(slug):
    """Sticky page tabs with ← / → on the ends, the way the Rev U set reads.

    The arrows carry the destination on the <nav> as data-prev/data-next, so the
    keyboard handler and the buttons cannot disagree about where they go."""
    labels = {s: t for s, t, _s in PAGES}
    prv, nxt = _neighbours(slug)

    def arrow(target, cls, sym):
        if not target:
            return f'<a class="arrow {cls} off" aria-disabled="true">{sym}</a>'
        return (f'<a class="arrow {cls}" href="{target}.html" '
                f'aria-label="{cls.capitalize()} page: {E(labels[target])}" '
                f'title="{E(labels[target])}">{sym}</a>')

    tabs = "".join(
        f'<a href="{s}.html"{" class=\"here\" aria-current=\"page\"" if s == slug else ""}>'
        f'{E(t)}</a>' for s, t, _s in PAGES)
    return (f'<nav class="tabs" aria-label="pages" data-prev="{prv or ""}" '
            f'data-next="{nxt or ""}">{arrow(prv, "prev", "←")}{tabs}'
            f'<span class="sp"></span>{arrow(nxt, "next", "→")}</nav>')


def prev_next(slug):
    labels = {s: t for s, t, _s in PAGES}
    prv, nxt = _neighbours(slug)
    a = f'<a href="{prv}.html">← {E(labels[prv])}</a>' if prv else "<span></span>"
    b = f'<a href="{nxt}.html">{E(labels[nxt])} →</a>' if nxt else "<span></span>"
    return (f'<div class="pn">{a}<span class="hint"><kbd>←</kbd> <kbd>→</kbd> '
            f'switch pages</span>{b}</div>')


def page(slug, title, cards, today):
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>Loft Bed Design - {E(title)}</title>'
            f'<link rel="stylesheet" href="style.css"></head><body><div class="wrap">'
            f'<header><h1>Loft Bed Design • {E(title)}</h1><div class="meta">'
            f'<span class="rev">REV {E(REV)}</span>'
            f'<span>{fr(RX)} × {fr(RY)} room · {fr(CEILING)} ceiling · deck {fr(DECK)} AFF</span>'
            f'<span>generated {today} from dimensions.yaml</span></div></header>'
            f'{nav(slug)}{"".join(cards)}{prev_next(slug)}</div>'
            f'<script>{JS}</script></body></html>')


def check_ids(slug, html):
    """No two elements on a page may share an id.

    Every figure is a separate <svg> in one document, so their <defs> share an id
    namespace and `url(#name)` resolves to the FIRST match in the document — not
    the one inside the same svg. That silently clipped seven figures to another
    figure's frame before anyone noticed the drawings were losing their right-hand
    side. Cheap invariant, so it is asserted on every build."""
    ids = re.findall(r'\sid="([^"]+)"', html)
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        raise AssertionError(
            f"docs/{slug}.html: duplicate element ids {dupes} — an svg def is "
            f"shadowing another figure's; give it a per-canvas id")


def build(verbose=True):
    import importlib
    os.makedirs(OUT, exist_ok=True)
    today = datetime.date.today().isoformat()
    figs = {}
    for slug, title, spec in PAGES:
        cards = []
        if spec is REF:
            cards = reference_cards(slug)
        else:
            for name in spec:
                mod = importlib.import_module(f"sheets.{name}")
                for key, fn in mod.FIGURES:
                    fig = fn()
                    figs[key] = fig
                    cards.append(figure_card(mod, fig))
            if slug == "index":
                cards.append(card_summary())
        html = page(slug, title, cards, today)
        check_ids(slug, html)
        open(os.path.join(OUT, f"{slug}.html"), "w").write(html)
    open(os.path.join(OUT, "style.css"), "w").write(CSS + "\n" + hide_rules() + "\n")
    return figs
