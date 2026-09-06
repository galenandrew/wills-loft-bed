"""
drawings.site — assemble site/ (one page per sheet) and, on request, a single-file set.

Each page is built from the same fragments, so the multi-page site and the
single file cannot disagree. Figures are also written standalone to
site/figs/<key>.svg with the SVG styles embedded, and site/manifest.json
records a hash per figure so build.py can say what changed.
"""
import hashlib, importlib, json, os, re, pathlib, collections
from .model import *
from . import schedule as _sched

SHEET_MODULES = ["d1_floor_plan", "d2_front_elevation", "d3_platform_section", "d4_stair_section", "d5_nook",
                 "d6_platform_framing", "d7_half_wall", "d8_landing_framing", "d9_framing_overlay"]
SHEETS = [importlib.import_module(f"drawings.{n}") for n in SHEET_MODULES]
CONTENT = os.path.join(ROOT, "content")

def content(name):
    return yaml.safe_load(open(os.path.join(CONTENT, name)))
def fill(s):
    """Substitute {name} placeholders from VALS. Unknown names raise — prose must not drift silently."""
    return s.format_map(VALS)

# --------------------------------------------------------------------------- CSS (page / svg split so figs/*.svg can embed theirs)
CSS_VARS = """--ink:#23231f;--ink2:#5f5d56;--ink3:#8a877e;--bg:#fbfaf7;--card:#fff;--line:#e0ddd4;
--lum:#e8d6ae;--lum2:#f1e6cc;--lumline:#7a6238;--sheet:#cfc4ac;--fin:#b98d57;--wall:#3b352c;--ghost:#eee9dd;
--blue:#5b8fc7;--blue2:#dce7f3;--blueink:#2b4a6b;--pencil:#1f4e9c;--red:#c0392b;--green:#4a7c4e;--green2:#cfe0cf;--amber:#b07d1a"""
CSS_PAGE = """*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;font-size:14px;line-height:1.55}
.wrap{max-width:1040px;margin:0 auto;padding:28px 22px 72px}header{border-bottom:2px solid var(--ink);padding-bottom:14px;margin-bottom:22px}
h1{font-size:22px;margin:0 0 4px}.meta{color:var(--ink2);font-size:12.5px;display:flex;gap:16px;flex-wrap:wrap;align-items:center}
.rev{background:var(--ink);color:#fff;padding:2px 9px;border-radius:99px;font-weight:700;font-size:11.5px;letter-spacing:.04em}
nav.tabs{position:sticky;top:0;z-index:5;background:var(--bg);display:flex;align-items:center;gap:6px;padding:10px 0;margin:-4px 0 18px;border-bottom:1px solid var(--line)}
nav.tabs a{color:var(--ink2);text-decoration:none;padding:8px 14px;border-radius:6px;font-size:13.5px;font-weight:600;line-height:1.2}
nav.tabs a:hover{background:#f1efe9;color:var(--ink)}nav.tabs a.here{background:var(--ink);color:#fff}nav.tabs a:focus-visible{outline:2px solid var(--pencil);outline-offset:1px}
nav.tabs a.arrow{font-size:18px;padding:6px 12px;border:1px solid var(--line);background:var(--card);color:var(--ink)}nav.tabs a.arrow:hover{background:#f1efe9}
nav.tabs a.arrow.off{opacity:.3;pointer-events:none}nav.tabs .sp{flex:1}
.contents{font-size:12.5px;color:var(--ink2);margin:-6px 0 18px 2px;display:flex;flex-wrap:wrap;gap:4px 14px}.contents a{color:var(--pencil);text-decoration:none}.contents a:hover{text-decoration:underline}
.pn{display:flex;justify-content:space-between;font-size:13px;margin-top:8px}.pn a{color:var(--pencil);text-decoration:none;padding:8px 0}.pn a:hover{text-decoration:underline}
kbd{font:11px ui-monospace,Menlo,monospace;border:1px solid var(--line);border-radius:3px;padding:0 4px;background:var(--card)}
h2{font-size:12px;text-transform:uppercase;letter-spacing:.09em;color:var(--ink2);margin:0 0 12px;font-weight:700}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:18px 20px;margin-bottom:20px}
.specs{display:grid;grid-template-columns:repeat(auto-fit,minmax(168px,1fr));gap:1px;background:var(--line);border:1px solid var(--line);border-radius:8px;overflow:hidden;margin:0}
.spec{background:var(--card);padding:11px 13px}.spec dt{font-size:11px;color:var(--ink3);text-transform:uppercase;letter-spacing:.05em;margin-bottom:3px}
.spec dd{margin:0;font-size:16px;font-weight:650;font-variant-numeric:tabular-nums}.spec dd span{font-size:11.5px;font-weight:400;color:var(--ink2);display:block;margin-top:1px}
figure{margin:0 0 12px;overflow-x:auto}figure svg{display:block;width:100%;height:auto}.cap{color:var(--ink2);font-size:12.5px;margin:10px 2px 0}
table{width:100%;border-collapse:collapse;font-size:13px}th,td{text-align:left;padding:7px 10px;border-bottom:1px solid var(--line);vertical-align:top;overflow-wrap:break-word}
th{font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:var(--ink3);font-weight:700}td.n{font-variant-numeric:tabular-nums;white-space:nowrap}tr:last-child td{border-bottom:none}
ul{margin:0;padding-left:19px}li{margin-bottom:7px}code{font-size:12.5px;background:#f1efe9;padding:1px 4px;border-radius:3px}
.note{border-left:3px solid var(--red);background:#fdf4f2;padding:11px 14px;border-radius:0 6px 6px 0;font-size:13px;margin-top:14px}.note b{color:var(--red)}
.tag{display:inline-block;font-size:10.5px;font-weight:700;letter-spacing:.05em;padding:1.5px 7px;border-radius:4px;vertical-align:1px}.t-open{background:#fdf1e3;color:var(--amber)}.t-lock{background:#e8f0e9;color:var(--green)}.t-chk{background:#fbe9e7;color:var(--red)}
h2.section{font-size:15px;text-transform:none;letter-spacing:0;color:var(--ink);border-bottom:2px solid var(--ink);padding-bottom:6px;margin:30px 0 16px}"""
CSS_SVG = """svg text{font-family:ui-sans-serif,system-ui,sans-serif;font-size:11.5px;fill:var(--ink)}
.lab{font-weight:650;font-size:12px}.labs{font-size:10.5px;fill:var(--ink2)}.labk{font-weight:650;font-size:11.5px;fill:var(--pencil)}.labb{font-weight:650;font-size:11px;fill:var(--red)}.labw{font-size:10.5px;fill:var(--ghost)}
.lum{fill:var(--lum);stroke:var(--lumline);stroke-width:1}.lum2{fill:var(--lum2);stroke:var(--lumline);stroke-width:.8}.blk{fill:#e6d9bd;stroke:var(--red);stroke-width:1}
.sheet{fill:var(--sheet);stroke:var(--lumline);stroke-width:.6}.fin{fill:var(--fin);stroke:var(--lumline);stroke-width:.8}.wall{fill:var(--wall);stroke:none}.ghost{fill:var(--ghost);stroke:none}
.room{fill:#fff;stroke:var(--ink);stroke-width:4}.deck{fill:var(--blue2);stroke:var(--blue);stroke-width:1.4}.ledge{fill:#eef3f9;stroke:var(--blue);stroke-width:1}.matt{fill:#c8daed;stroke:var(--blue);stroke-width:1}
.beamplan{fill:var(--lum);stroke:var(--lumline);stroke-width:1.2}.landing{fill:var(--green2);stroke:var(--green);stroke-width:1.6}.tread{fill:#efeee8;stroke:var(--ink);stroke-width:1.2}.exist{fill:#efeee8;stroke:var(--ink);stroke-width:1.4}
.hid{fill:none;stroke:var(--ink2);stroke-width:1.4;stroke-dasharray:8 5}.dashfill{fill:none;stroke:var(--ink2);stroke-width:1;stroke-dasharray:5 3}.door{stroke:var(--ink);stroke-width:3}.window{stroke:var(--blue);stroke-width:5}
.green{fill:var(--green2);fill-opacity:.85;stroke:#2c4a2e;stroke-width:1.5}.greend{fill:none;stroke:#2c4a2e;stroke-width:1.2;stroke-dasharray:5 3}.flat{fill:#fdf6e3;stroke:var(--fin);stroke-width:1.2}.rake{fill:#f6f2e6;stroke:var(--fin);stroke-width:.8;stroke-dasharray:4 3}
.hanger{fill:none;stroke:var(--pencil);stroke-width:2.2}.strap{fill:none;stroke:var(--red);stroke-width:2}.light{fill:none;stroke:var(--red);stroke-width:2}.co{fill:var(--red)}.cot{fill:#fff;font-weight:700;font-size:11.5px}
.hatchline{stroke:var(--lumline);stroke-width:.6}.badline{stroke:var(--red);stroke-width:1}.bad{fill:url(#bad);stroke:var(--red);stroke-width:1}
.ink{stroke:var(--ink);stroke-width:1}.dash{stroke:var(--ink2);stroke-width:1;stroke-dasharray:6 4}.ghostl{stroke:var(--ink2);stroke-width:.9;stroke-dasharray:3 3;fill:none}.floor{stroke:var(--wall);stroke-width:3}.redline{stroke:var(--red);stroke-width:1.6;stroke-dasharray:7 4}
.soffit{fill:none;stroke:var(--fin);stroke-width:3}polyline.hanger{fill:none}
.dim line{stroke:var(--pencil);stroke-width:.9}.dim text{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:10.5px;fill:var(--pencil)}marker path{fill:var(--pencil)}"""
CSS = f":root{{color-scheme:light;{CSS_VARS}}}\n{CSS_PAGE}\n{CSS_SVG}\n"
CSS_STANDALONE_SVG = f"svg{{{CSS_VARS}}}\n{CSS_SVG}"

# --------------------------------------------------------------------------- fragments (shared by site pages and the single file)
def tbl(rows, head, num=(1, 2)): return _sched.tbl(rows, head, num)

def render_figures():
    """[(sheet, key, svg)] in sheet order — each figure rendered exactly once per build."""
    return [(s, k, fn()) for s in SHEETS for k, fn in s.FIGURES]

def meta_line(today):
    return (f'<div class="meta"><span class="rev">REV {E(REV)}</span><span>Twin loft · {fr(RX)} × {fr(RY)} room · {fr(CEILING)} ceiling</span>'
            f'<span>Deck {fr(DECK)} AFF · post-free 107 span · stairs locked</span><span>generated {today} from {E(os.path.basename(YAML))} by build.py</span></div>')

def card_conventions():
    c = content("conventions.yaml")
    return '<div class="card" id="conventions"><h2>Conventions</h2><ul>' + "".join(f"<li>{fill(x)}</li>" for x in c["items"]) + "</ul></div>"

def card_locked():
    return f'<div class="card" id="locked"><h2>Locked dimensions</h2><dl class="specs">{_sched.cards()}</dl></div>'

def card_schedule():
    note = fill(content("conventions.yaml")["schedule_note"])
    return (f'<div class="card" id="schedule"><h2>Dimension schedule — the controlling reference</h2>'
            f'<p class="cap" style="margin:0 0 14px">Every number below is computed by <code>verify.py</code> from the member extents, never typed. All heights are above finished floor; plan positions are from the <b>window wall</b> (x) and the <b>bed wall</b> (y) to finished wall faces.</p>'
            f'{_sched.schedule()}<div class="note">{note}</div></div>')

def card_drawing(sheet, svgs):
    body = "".join(f"<figure>{svgs[k]}</figure>" for k, _ in sheet.FIGURES)
    return f'<div class="card" id="d{sheet.NUMBER}"><h2>{sheet.NUMBER} — {E(sheet.TITLE)}</h2>{body}<p class="cap">{sheet.CAPTION}</p></div>'

def card_structure():
    c = content("structure.yaml")
    rows = [(fill(r["member"]), fill(r["spec"]), fill(r["check"])) for r in c["rows"]]
    return f'<div class="card" id="structure"><h2>Structure &amp; load path</h2>{tbl(rows, ["Member", "Spec", "Check"], num=())}<div class="note">{fill(c["ceiling_note"])}</div></div>'

def card_open():
    items = content("open-items.yaml")["items"]
    li = "".join(f'<li><span class="tag {"t-lock" if i["tag"] == "LOCKED" else "t-chk"}">{E(i["tag"])}</span> {fill(i["text"])}</li>' for i in items)
    return f'<div class="card" id="open"><h2>Open items</h2><ul>{li}</ul></div>'

def card_revisions():
    rows = json.load(open(os.path.join(CONTENT, "revisions.json")))
    body = "".join(f'<tr><td class="n"><b>{E(r)}</b></td><td>{fill(t)}</td></tr>' for r, t in rows)
    return (f'<div class="card" id="revisions"><h2>Revisions</h2><p class="cap" style="margin:0 0 10px">Drawing numbers in entries below refer to the numbering in force at the time.</p>'
            f'<table><tr><th>Rev</th><th>Change</th></tr>{body}</table></div>')

# --------------------------------------------------------------------------- pages
# Four scrolling pages, so views of the same assembly sit together. Drawing numbers are unchanged.
PAGES = [("index", "Overview"), ("stairs", "Stairs & Nook"), ("loft", "Loft Bed"), ("appendix", "Appendix")]
PAGE_SHEETS = {"index": ["1", "2"], "stairs": ["4", "5", "8", "9"], "loft": ["3", "6", "7"], "appendix": []}
assert sorted(n for v in PAGE_SHEETS.values() for n in v) == sorted(s.NUMBER for s in SHEETS), "every sheet must be on exactly one page"

def sheet(n): return next(s for s in SHEETS if s.NUMBER == n)

def page_parts(name, svgs):
    """[(anchor id, contents label, html)] for one page, in order."""
    dr = lambda n: (f"d{n}", f"{n} {sheet(n).TITLE}", card_drawing(sheet(n), svgs))
    if name == "index":
        return [("conventions", "Conventions", card_conventions()), ("locked", "Locked dimensions", card_locked()), dr("2"), dr("1")]
    if name == "appendix":
        return [("schedule", "Dimension schedule", card_schedule()), ("structure", "Structure & load path", card_structure()), ("revisions", "Revisions", card_revisions())]
    return [dr(n) for n in PAGE_SHEETS[name]]

def nav(here):
    names = [n for n, _ in PAGES]; i = names.index(here); labels = dict(PAGES)
    prv, nxt = (names[i - 1] if i > 0 else None), (names[i + 1] if i + 1 < len(names) else None)
    arrow = lambda t, cls, sym: (f'<a class="arrow {cls}" href="{t}.html" aria-label="{cls[:-1].capitalize()}: {E(labels[t])}" title="{E(labels[t])}">{sym}</a>'
                                 if t else f'<a class="arrow {cls} off" aria-disabled="true">{sym}</a>')
    tabs = "".join(f'<a href="{n}.html"{" class=\"here\" aria-current=\"page\"" if n == here else ""}>{E(l)}</a>' for n, l in PAGES)
    return (f'<nav class="tabs" aria-label="pages" data-prev="{prv or ""}" data-next="{nxt or ""}">{arrow(prv, "prev", "←")}{tabs}<span class="sp"></span>{arrow(nxt, "next", "→")}</nav>')

KEYS_JS = """<script>document.addEventListener('keydown',function(e){if(e.altKey||e.ctrlKey||e.metaKey||e.target.closest('input,textarea'))return;
var n=document.querySelector('nav.tabs');if(!n)return;var t=e.key==='ArrowLeft'?n.dataset.prev:e.key==='ArrowRight'?n.dataset.next:'';if(t){location.href=t+'.html';}});</script>"""

def html_page(title, body, here, today, inline_css=False):
    css = f"<style>{CSS}</style>" if inline_css else '<link rel="stylesheet" href="style.css">'
    return (f'<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{E(title)}</title>\n{css}</head><body><div class="wrap">\n'
            f'<header><h1>Lofted Bed — Working Drawings</h1>\n{meta_line(today)}</header>\n{card_open()}\n{nav(here) if here else ""}'
            f'{body}\n</div>{KEYS_JS if here else ""}</body></html>\n')

def contents_row(parts):
    return '<div class="contents"><span>On this page:</span>' + "".join(f'<a href="#{a}">{E(l)}</a>' for a, l, _ in parts) + '<span class="sp"></span><span><kbd>←</kbd> <kbd>→</kbd> switch pages</span></div>'

def prev_next(here):
    names = [n for n, _ in PAGES]; i = names.index(here); labels = dict(PAGES)
    a = f'<a href="{names[i-1]}.html">← {E(labels[names[i-1]])}</a>' if i > 0 else "<span></span>"
    b = f'<a href="{names[i+1]}.html">{E(labels[names[i+1]])} →</a>' if i + 1 < len(names) else "<span></span>"
    return f'<div class="pn">{a}{b}</div>'

# --------------------------------------------------------------------------- build
def svg_elements(svg):
    return collections.Counter(re.findall(r"<(?!/)(?!svg\b)[^>]*>[^<]*", svg))
def svg_texts(svg):
    return collections.Counter(re.findall(r"<text[^>]*>([^<]*)</text>", svg))
def strip_style(svg):
    return re.sub(r"<style>.*?</style>", "", svg, flags=re.S)
def strip_svgs(h):
    return re.sub(r"<svg.*?</svg>", "", h, flags=re.S)

def diff_figure(old, new):
    """None if identical; otherwise a short human line: element counts and label changes."""
    if old is None: return "new"
    if strip_style(old) == strip_style(new): return None
    eo, en = svg_elements(old), svg_elements(new)
    changed = sum((en - eo).values()) + sum((eo - en).values())
    to, tn = svg_texts(old), svg_texts(new)
    gone, came = list((to - tn).elements()), list((tn - to).elements())
    labels = "; ".join(f"{E(a)!s}→{E(b)!s}" for a, b in zip(gone, came))
    extra = [f"−{E(a)}" for a in gone[len(came):]] + [f"+{E(b)}" for b in came[len(gone):]]
    lab = ", ".join(x for x in [labels] + extra if x)
    return f"{changed} elements" + (f" · labels {lab}" if lab else " · geometry only")

def build(site_dir, single=None, today=None):
    """Write site/, return a report dict: {'changed': {key: why}, 'unchanged': [keys], 'pages_changed': [...]}"""
    today = today or datetime.date.today().isoformat()
    site = pathlib.Path(site_dir); (site / "figs").mkdir(parents=True, exist_ok=True)
    figs = render_figures(); svgs = {k: s for _, k, s in figs}
    report = {"changed": {}, "unchanged": [], "pages_changed": []}
    manifest = {"rev": REV, "yaml": os.path.basename(YAML), "generated": today, "figures": {}, "pages": {}}
    old_manifest = json.load(open(site / "manifest.json")) if (site / "manifest.json").exists() else {}
    for s, k, svg in figs:
        p = site / "figs" / f"{k}.svg"
        old = p.read_text() if p.exists() else None
        why = diff_figure(old, svg)
        (report["changed"].__setitem__(k, why) if why else report["unchanged"].append(k))
        p.write_text(svg.replace(">", f"><style>{CSS_STANDALONE_SVG}</style>", 1))
        page = next(n for n, v in PAGE_SHEETS.items() if s.NUMBER in v)
        manifest["figures"][k] = {"sheet": s.NUMBER, "page": page, "sha": hashlib.sha1(svg.encode()).hexdigest()[:12], "elements": sum(svg_elements(svg).values())}
    (site / "style.css").write_text(CSS)
    for name, label in PAGES:
        parts = page_parts(name, svgs)
        body = contents_row(parts) + "".join(h for _, _, h in parts) + prev_next(name)
        sha = hashlib.sha1(strip_svgs(body).encode()).hexdigest()[:12]; manifest["pages"][name] = sha     # prose only — figures are reported separately
        if old_manifest.get("pages", {}).get(name) not in (None, sha): report["pages_changed"].append(name)
        (site / f"{name}.html").write_text(html_page(f"Lofted Bed · Rev {REV} · {label}", body, name, today))
    for stale in site.glob("*.html"):
        if stale.stem not in dict(PAGES): stale.unlink()
    json.dump(manifest, open(site / "manifest.json", "w"), indent=1)
    if single:
        body = "".join(f'<h2 class="section">{E(label)}</h2>' + "".join(h for _, _, h in page_parts(name, svgs)) for name, label in PAGES)
        pathlib.Path(single).write_text(html_page(f"Lofted Bed — Working Drawings · Rev {REV}", body, None, today, inline_css=True))
    return report

def summary(report, site_dir):
    ch = report["changed"]; n = len(ch) + len(report["unchanged"])
    if not ch and not report["pages_changed"]: return f"{site_dir}/: rev {REV} · {n} figures · nothing changed"
    parts = [f"{k}: {why}" for k, why in ch.items()]
    if report["pages_changed"]: parts.append("prose changed on: " + ", ".join(report["pages_changed"]))
    return f"{site_dir}/: rev {REV} · {len(ch)} of {n} figures changed — " + " | ".join(parts)
