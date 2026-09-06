#!/usr/bin/env python3
"""
verify.py — recompute the loft bed's derived geometry from dimensions.yaml
and check every declared connection for real three-axis overlap.

    python3 verify.py            # full report, exit 1 on any FAIL
    python3 verify.py --quiet    # failures and warnings only

Nothing in here is remembered from the drawings. Every number is computed
from the member extents in dimensions.yaml. If this disagrees with a drawing,
the drawing is wrong (or the yaml is — fix the yaml, never the script).
"""
import math
import sys
from fractions import Fraction
from itertools import combinations

import yaml

TOL = 0.011          # coincidence tolerance, inches (a 64th)
MIN_OVERLAP = 1.0    # below this a "connection" is marginal


# ----------------------------------------------------------------- formatting
def fr(v):
    """53.75 → '53¾'   8.2857 → '8.29 (8 5/16)'"""
    if v is None:
        return "—"
    f = Fraction(v).limit_denominator(16)
    whole, rem = divmod(abs(f), 1)
    sign = "-" if v < 0 else ""
    uni = {Fraction(1, 2): "½", Fraction(1, 4): "¼", Fraction(3, 4): "¾"}
    if rem == 0:
        s = f"{sign}{int(whole)}"
    elif rem in uni:
        s = f"{sign}{int(whole)}{uni[rem]}" if whole else f"{sign}{uni[rem]}"
    else:
        s = f"{sign}{int(whole)} {rem.numerator}/{rem.denominator}" if whole else f"{sign}{rem.numerator}/{rem.denominator}"
    if abs(float(f) - v) > 0.004:
        return f"{v:.2f} (~{s})"
    return s


class Report:
    def __init__(self, quiet=False):
        self.quiet = quiet
        self.fails = self.warns = 0
        self.lines = []

    def section(self, title):
        self.lines.append(("HDR", f"\n== {title} =="))

    def ok(self, msg):
        self.lines.append(("PASS", msg))

    def warn(self, msg):
        self.warns += 1
        self.lines.append(("WARN", msg))

    def fail(self, msg):
        self.fails += 1
        self.lines.append(("FAIL", msg))

    def info(self, msg):
        self.lines.append(("INFO", msg))

    def dump(self):
        for kind, msg in self.lines:
            if kind == "HDR":
                print(msg)
            elif self.quiet and kind in ("PASS", "INFO"):
                continue
            else:
                print(f"  {kind:4} {msg}")
        print(f"\n{self.fails} FAIL, {self.warns} WARN")


# ----------------------------------------------------------------- model
class Member:
    def __init__(self, d):
        self.id = d["id"]
        self.stock = d.get("stock")
        self.role = d.get("role", "structural")
        self.kind = d.get("kind")
        self.rake = d.get("rake")
        self.part_of = d.get("part_of")
        self.note = d.get("note", "")
        self.x, self.y, self.z = (list(map(float, d[k])) for k in "xyz")

    def ext(self, axis):
        return getattr(self, axis)

    def size(self, axis):
        a = self.ext(axis)
        return a[1] - a[0]

    def __repr__(self):
        return self.id


def expand(members):
    out = {}
    for d in members:
        rep = d.get("repeat")
        if not rep:
            out[d["id"]] = Member(d)
            continue
        ax, n, pitch = rep["axis"], rep["count"], float(rep["pitch"])
        for i in range(n):
            dd = dict(d)
            dd["id"] = f"{d['id']}[{i}]"
            base = list(map(float, d[ax]))
            dd[ax] = [base[0] + i * pitch, base[1] + i * pitch]
            out[dd["id"]] = Member(dd)
    return out


def resolve(pattern, members, exclude=()):
    """'deck_joist[*]' → all repeats; plain id → [that member].

    `exclude` drops named ids from a wildcard, for the one repeat that connects
    somewhere else: slat[0] is past the beam's end and lands on the side ledger,
    so it is excepted from `slat[*] → beam` and given its own rule."""
    if pattern.endswith("[*]"):
        stem = pattern[:-3]
        hits = [m for k, m in members.items()
                if k.startswith(stem + "[") and k not in exclude]
        if not hits:
            raise KeyError(pattern)
        return hits
    return [members[pattern]]


def overlap(a, b):
    lo, hi = max(a[0], b[0]), min(a[1], b[1])
    return hi - lo  # negative = gap, 0 = touch, positive = overlap


# ----------------------------------------------------------------- stair
class Stair:
    def __init__(self, s, deck_top):
        # Rev Y: the riser is stated, not 58/7. The last riser (landing → loft deck) is a
        # separate number because it is not set by the stair at all — it is the fixed
        # framing stack from the landing-ledger bottom up to the deck (9-1/4 header +
        # two 1-1/2 plates + 3-1/2 deck rim + 3/4 ply, less the 8 the ledger takes up
        # below the landing = 8.5), so it holds whatever `riser` is.
        # Archived pre-Rev-Y yaml (Rev T, Rev U) has no `riser` key, only `total_rise` and
        # `risers` — fall back to their uniform division so those snapshots still load.
        self.R = float(s["riser"]) if "riser" in s else float(s["total_rise"]) / s["risers"]
        self.run = float(s["run"])
        self.n_risers = s["risers"]
        self.n_treads = s["treads"]
        self.landing = float(s["landing_depth"])
        self.t = float(s["tread_thickness"])
        self.top_run = float(s.get("top_run", 0))              # stringer extends this far under the landing
        self.deck_t = float(s.get("landing_deck_thickness", 0.75))
        self.stock_depth = float(s.get("_stringer_depth", 11.25))
        self.angle = math.atan2(self.R, self.run)
        self.tan = math.tan(self.angle)
        self.hyp = math.hypot(self.R, self.run)
        self.notch = self.R * self.run / self.hyp          # perpendicular depth of a notch
        self.throat = self.stock_depth - self.notch
        self.R_top = float(s.get("top_riser", self.R))     # landing → deck; need not match
        # z of riser i (1..7) top; tread i occupies y in [72-9i, 81-9i] for a 27" landing
        self.riser_z = {i: i * self.R for i in range(1, self.n_treads + 2)}
        for i in range(self.n_treads + 2, self.n_risers + 1):
            self.riser_z[i] = self.riser_z[i - 1] + self.R_top
        self.total_rise = self.riser_z[self.n_risers]
        self.y_riser_top = self.landing                      # riser n+1 = the landing face
        self.y_top = self.landing - self.top_run             # plumb cut against the rim
        self.y_bottom = self.landing + self.run * self.n_treads

    def tread_y(self, i):
        """tread i (1 = bottom … n_treads = top): [y_start, y_end] of its run."""
        y0 = self.y_bottom - self.run * i
        return [y0, y0 + self.run]

    def underside(self, y):
        """z of the stringer's bottom edge at plan position y (throat below the notch corners)."""
        # inner corner of the top notch = tread cut (riser height − tread thickness); the
        # whole stringer is dropped by t so finished treads land on the riser heights
        z_corner_at_top = self.riser_z[self.n_treads] - self.t
        line = z_corner_at_top - (y - self.y_riser_top) * self.tan
        return line - self.throat / math.cos(self.angle)

    def top_edge(self, y):
        """z of the stringer's top edge at y: the tread cut for the tread whose run contains y."""
        if self.top_run > 0 and self.y_top - TOL <= y <= self.y_riser_top + TOL:
            return self.riser_z[self.n_treads + 1] - self.deck_t    # top run under the landing deck
        for i in range(1, self.n_treads + 1):
            y0, y1 = self.tread_y(i)
            if y0 - TOL <= y <= y1 + TOL:
                return self.riser_z[i] - self.t
        return None

    def plumb_cut(self):
        """z range of the top plumb cut against the landing rim.

        The stringer's wood at y_top runs from the underside up to the TOP TREAD's cut
        (riser n_treads − t). Riser n_treads+1 is the landing face, not stringer material —
        Rev T's '11¼ bearing / stringer 15¼ deep where it lands' assumed otherwise."""
        if self.top_run > 0:
            return [self.underside(self.y_top), self.riser_z[self.n_treads + 1] - self.deck_t]
        return [self.underside(self.y_top), self.riser_z[self.n_treads] - self.t]

    def z_range_over(self, y0, y1):
        """conservative z envelope of the stringer body over plan interval [y0, y1]."""
        lo = self.underside(y1)
        tops = [self.top_edge(y) for y in (y0, y1) if self.top_edge(y) is not None]
        return [lo, max(tops)] if tops else [lo, lo]


# ------------------------------------------------------- raked members
# `kind: raked` generalises `kind: stringer`: a member whose z extents follow a
# profile in y instead of being constant. Its yaml z is the bbox — informational,
# like a stringer's — and the truth comes from `rake`:
#     profile  stringer_underside | soffit | stair_top   the line it is built to
#     offset   inches added to that line     (default 0)
#     side     above | below                 which side of the line it occupies
#     band     inches, measured VERTICALLY   omit to take the far edge from the bbox
#     clip     hard ceiling on z1            e.g. the header bottom
# One place computes it, and drawings/ and cad/ import it from here.
RAKED = ("stringer", "raked")


def rake_profile(name, stair, nook):
    """(z(y), [break points]) for a named profile line. The breaks matter: the soffit
    is flat then raked, and a polygon sampled only at its ends would cut the corner —
    which is exactly the interference the kernel found on the first Rev X run."""
    if name == "stringer_underside":
        return stair.underside, []
    if name == "stair_top":
        # Rev AE: the line the half-wall's stair face (a skirt now) is cut to — the top of
        # everything the stair puts against that wall. 48.75 under the landing box and the
        # stringers' top run, then the tread cuts, 8.25 down at every riser line. It is a
        # STEP function, so each riser line is a break twice over: rake_pts must put two
        # points there or it would draw a diagonal across the step.
        top = stair.riser_z[stair.n_treads + 1] - stair.deck_t
        def z(y):
            # NOT Stair.top_edge(): its TOL slop makes the tread below win at a run
            # boundary, which drags the profile a whole riser down and buries the skirt
            # in the stringer. Here the runs are half-open, so each boundary is exact.
            if y <= stair.y_riser_top:
                return top
            for i in range(stair.n_treads, 0, -1):
                y0, y1 = stair.tread_y(i)
                if y0 <= y < y1:
                    return stair.riser_z[i] - stair.t
            return stair.riser_z[1] - stair.t
        eps = 1e-7
        ys = [stair.y_riser_top] + [stair.tread_y(i)[1] for i in range(1, stair.n_treads + 1)]
        return z, [b for y in ys for b in (y - eps, y + eps)]
    if name == "soffit":
        panel = float(nook["soffit_panel_thickness"])
        face = float(nook["header_bottom"]) - float(nook.get("wrap", 0))
        y_meet = stair.y_riser_top - (face + panel - stair.underside(stair.y_riser_top)) / stair.tan
        return (lambda y: face if y <= y_meet else stair.underside(y) - panel), [y_meet]
    raise KeyError(f"unknown rake profile {name!r}")


def rake_z(m, y, stair, nook):
    """(z0, z1) of a raked member at plan position y."""
    r = m.rake
    base = rake_profile(r["profile"], stair, nook)[0](y) + float(r.get("offset", 0))
    band = r.get("band")
    if r.get("side", "above") == "above":
        z0, z1 = base, (base + float(band) if band else m.z[1])
    else:
        z0, z1 = (base - float(band) if band else m.z[0]), base
    if "clip" in r:
        z1 = min(z1, float(r["clip"]))
    return z0, max(z0, z1)


def rake_range(m, y0, y1, stair, nook):
    """The member's true z envelope over [y0, y1] — the raked answer to a bbox."""
    y0, y1 = max(y0, m.y[0]), min(y1, m.y[1])
    if y1 <= y0:
        return [0.0, 0.0]
    breaks = rake_profile(m.rake["profile"], stair, nook)[1]
    zs = [rake_z(m, y, stair, nook)
          for y in {y0, y1, *(b for b in breaks if y0 < b < y1)}]
    return [min(z[0] for z in zs), max(z[1] for z in zs)]


def rake_pts(m, stair, nook, n=2):
    """The member's y-z profile as a closed polygon (both edges are straight here,
    except where `clip` breaks the top, so the break point is added explicitly)."""
    y0, y1 = m.y
    breaks = rake_profile(m.rake["profile"], stair, nook)[1]
    ys = sorted({y0, y1, *(b for b in breaks if y0 + 1e-6 < b < y1 - 1e-6)})
    if "clip" in (m.rake or {}):
        c = float(m.rake["clip"])
        lo, hi = y0, y1
        for _ in range(48):                     # bisect to the y where the clip releases
            mid = (lo + hi) / 2
            (lo, hi) = (mid, hi) if rake_z(m, mid, stair, nook)[1] >= c - 1e-9 else (lo, mid)
        if y0 + 1e-6 < lo < y1 - 1e-6:
            ys = sorted(set(ys) | {lo})
    top = [(y, rake_z(m, y, stair, nook)[1]) for y in ys]
    bot = [(y, rake_z(m, y, stair, nook)[0]) for y in reversed(ys)]
    return top + bot


# ----------------------------------------------------------------- checks
def check_sections(rep, members, lumber):
    rep.section("MEMBER SECTIONS — do the extents match the stock?")
    for m in members.values():
        if m.role == "existing" or not m.stock:
            continue
        spec = lumber.get(m.stock)
        if spec is None:
            rep.warn(f"{m.id}: unknown stock '{m.stock}'")
            continue
        sizes = sorted([m.size("x"), m.size("y"), m.size("z")])
        if m.kind == "raked" and m.rake and m.rake.get("band"):
            # the thin dimension is the vertical band, not an extent
            sizes = sorted([m.size("x"), float(m.rake["band"])])
        t, d = spec
        if d is None:  # sheet
            if abs(sizes[0] - t) > TOL:
                rep.fail(f"{m.id}: {m.stock} thickness {fr(t)} but thinnest extent is {fr(sizes[0])}")
            continue
        if m.part_of:
            # a notch remnant: the same board as its parent, but one extent is cut
            # back, so it cannot match the full section. Check what is still true —
            # the thickness, and that nothing exceeds the stock it came out of.
            if m.part_of not in members:
                rep.fail(f"{m.id}: part_of '{m.part_of}' is not a member")
            elif members[m.part_of].stock != m.stock:
                rep.fail(f"{m.id}: part of {m.part_of}, which is {members[m.part_of].stock}, "
                         f"not {m.stock}")
            elif abs(sizes[0] - t) > TOL:
                rep.fail(f"{m.id}: part of {m.part_of} but its thickness is {fr(sizes[0])}, not {fr(t)}")
            elif sizes[1] > d + TOL:
                rep.fail(f"{m.id}: part of {m.part_of} but its section is {fr(sizes[1])} deep, "
                         f"more than the {fr(d)} stock it is cut from")
            else:
                rep.ok(f"{m.id}: {fr(sizes[1])} of {m.stock} left after the notch, part of {m.part_of}")
            continue
        if m.kind in RAKED:
            # bbox z follows a profile, not the stock; only check thickness
            if abs(sizes[0] - t) > TOL:
                rep.fail(f"{m.id}: {m.kind} thickness {fr(sizes[0])} ≠ {fr(t)}")
            continue
        # the section is any TWO of the three extents — a stub (a 3" plate off a
        # 2x4) is shorter than its own stock depth, so sorting cannot pick them.
        ext = [m.size("x"), m.size("y"), m.size("z")]
        pairs = [(ext[i], ext[j]) for i in range(3) for j in range(3) if i != j]
        if not any(abs(a - t) <= TOL and abs(b - d) <= TOL for a, b in pairs):
            rep.fail(f"{m.id}: {m.stock} is {fr(t)}×{fr(d)} but no two extents match "
                     f"({fr(ext[0])} × {fr(ext[1])} × {fr(ext[2])})")
    rep.ok("all remaining members match their stock section")


def check_bounds(rep, members, room):
    rep.section("ROOM BOUNDS")
    X, Y, Z = float(room["x"]), float(room["y"]), float(room["ceiling"])
    for m in members.values():
        if m.role == "existing":
            continue
        for ax, hi in (("x", X), ("y", Y), ("z", Z)):
            lo_, hi_ = m.ext(ax)
            if lo_ < -TOL or hi_ > hi + TOL:
                rep.fail(f"{m.id}: {ax} {fr(lo_)}→{fr(hi_)} leaves the room (0→{fr(hi)})")
            if hi_ <= lo_:
                rep.fail(f"{m.id}: {ax} extent is empty or reversed")
    rep.ok("every member lies inside the room")


def wall_plane(name, room):
    return {"bed": ("y", 0.0, 0), "window": ("x", 0.0, 0),
            "right": ("x", float(room["x"]), 1), "closet": ("y", float(room["y"]), 1)}[name]


def check_connection(rep, c, members, stair, room, nook):
    typ = c["type"]
    skip = c.get("except", [])
    a_list = resolve(c["a"], members, skip)
    b_key = c["b"]
    through = [members[t] for t in c.get("through", [])]
    fast = c.get("fastener", "")

    for a in a_list:
        label = f"{a.id} → {b_key}"
        if typ in ("wall", "floor", "ceiling"):
            if typ == "wall":
                ax, plane, side = wall_plane(b_key.split(":")[1], room)
                edge = a.ext(ax)[side]
            elif typ == "floor":
                ax, plane, edge = "z", 0.0, a.z[0]
            else:
                ax, plane, edge = "z", float(room["ceiling"]), a.z[1]
            gap = abs(edge - plane)
            if gap > TOL:
                rep.fail(f"{label}: {ax} edge at {fr(edge)} is {fr(gap)} off the {b_key} plane")
            else:
                rep.ok(f"{label}: touches the {b_key} plane  [{fast}]")
            continue

        b_list = resolve(b_key, members, skip)
        for b in b_list:
            lab = f"{a.id} → {b.id}"
            if typ == "bearing":
                # a sits on b
                if a.kind in RAKED:
                    # a raked member seats on a plan footprint, not a z plane
                    ox, oy = overlap(a.x, b.x), overlap(a.y, b.y)
                    if ox <= 0 or oy <= 0:
                        rep.fail(f"{lab}: no plan overlap (x {fr(ox)}, y {fr(oy)})")
                    else:
                        rep.ok(f"{lab}: seat over {fr(ox)}×{fr(oy)}  [{fast}]")
                    continue
                dz = a.z[0] - b.z[1]
                ox, oy = overlap(a.x, b.x), overlap(a.y, b.y)
                if abs(dz) > TOL:
                    rep.fail(f"{lab}: bottom of a at {fr(a.z[0])} vs top of b at {fr(b.z[1])} — {'gap' if dz > 0 else 'interpenetrates'} {fr(abs(dz))}")
                elif ox <= TOL or oy <= TOL:
                    rep.fail(f"{lab}: same elevation but no plan overlap (x {fr(ox)}, y {fr(oy)})")
                else:
                    rep.ok(f"{lab}: bears on {fr(ox)}×{fr(oy)} at z={fr(b.z[1])}  [{fast}]")
                continue

            # hanger / face-screw: touch on `face`, overlap on the other two
            face = c["face"]
            others = [ax for ax in "xyz" if ax != face]
            af, bf = a.ext(face), b.ext(face)
            touch = min(abs(af[0] - bf[1]), abs(af[1] - bf[0]))
            # fastener path through intermediate members on the face axis
            thru = sum(t.size(face) for t in through)
            if through:
                touch = min(abs(af[0] - bf[1]) - thru, abs(af[1] - bf[0]) - thru, key=abs)
            ovs = {}
            for ax in others:
                if a.kind == "stringer" and ax == "z":
                    # true stringer envelope over the y-interval it shares with b
                    if face == "y":
                        za = stair.plumb_cut()
                    else:
                        oy = [max(a.y[0], b.y[0]), min(a.y[1], b.y[1])]
                        za = stair.z_range_over(*oy) if oy[1] > oy[0] else [0, 0]
                    ovs[ax] = (overlap(za, b.z), za)
                elif a.kind == "raked" and ax == "z":
                    if face == "y":
                        # the joint is a plane: take a's envelope at the end that meets b
                        ya = a.y[1] if abs(a.y[1] - b.y[0]) < abs(a.y[0] - b.y[1]) else a.y[0]
                        za = list(rake_z(a, ya, stair, nook))
                    else:
                        za = rake_range(a, b.y[0], b.y[1], stair, nook)
                    ovs[ax] = (overlap(za, b.z), za)
                else:
                    ovs[ax] = (overlap(a.ext(ax), b.ext(ax)), a.ext(ax))
            msgs = []
            bad = marginal = False
            if abs(touch) > TOL:
                bad = True
                msgs.append(f"{face}-faces {'gap' if touch > 0 else 'overlap'} {fr(abs(touch))}")
            for ax, (ov, ext) in ovs.items():
                if ov <= TOL:
                    bad = True
                    msgs.append(f"{ax} overlap {fr(ov)} (a {fr(ext[0])}→{fr(ext[1])}, b {fr(b.ext(ax)[0])}→{fr(b.ext(ax)[1])})")
                elif ov < MIN_OVERLAP:
                    marginal = True
                    msgs.append(f"{ax} overlap only {fr(ov)}")
                else:
                    msgs.append(f"{ax} {fr(ov)}")
            # a hanger seat / screwed face must be backed across a's full width;
            # engagement along a's depth (z) is graded
            extra = ""
            if typ in ("hanger", "face-screw") and not bad:
                width_ax = [ax for ax in others if ax != "z"][0]
                w_ov, w_ext = ovs[width_ax]
                width = w_ext[1] - w_ext[0]
                # a stringer is fastened locally along its run; its full length need not be backed
                if w_ov < width - TOL and a.kind not in RAKED:
                    bad = True
                    extra += f" · only {fr(w_ov)} of a's {fr(width)} width is backed by b"
                if "z" in ovs and a.kind not in RAKED:
                    eng, z_ext = ovs["z"]
                    depth = z_ext[1] - z_ext[0]
                    if depth > 0 and eng < depth - TOL:
                        pct = eng / depth
                        extra += f" · engages {fr(eng)} of a's {fr(depth)} depth ({pct:.0%})"
                        if pct < 0.5:
                            bad = True
                        else:
                            marginal = True
            if through:
                extra += f" · fasteners pass through {fr(thru)} of {', '.join(t.id for t in through)} first"
            line = f"{lab}: " + ", ".join(msgs) + extra + f"  [{fast}]"
            if bad:
                rep.fail(line)
            elif marginal:
                rep.warn(line)
            else:
                rep.ok(line)


def check_clashes(rep, members, connections):
    rep.section("VOLUME CLASHES — two solid members in the same space")
    declared = set()
    for c in connections:
        try:
            skip = c.get("except", [])
            for a in resolve(c["a"], members, skip):
                if c["b"].startswith(("wall:", "floor", "ceiling")):
                    continue
                for b in resolve(c["b"], members, skip):
                    declared.add(frozenset((a.id, b.id)))
        except KeyError:
            pass
    found = 0
    solids = [m for m in members.values() if m.role != "existing" and m.kind not in RAKED]
    for a, b in combinations(solids, 2):
        ox, oy, oz = overlap(a.x, b.x), overlap(a.y, b.y), overlap(a.z, b.z)
        if ox > TOL and oy > TOL and oz > TOL:
            found += 1
            rep.fail(f"{a.id} ∩ {b.id}: {fr(ox)} × {fr(oy)} × {fr(oz)}  "
                     f"(x {fr(max(a.x[0],b.x[0]))}→{fr(min(a.x[1],b.x[1]))}, "
                     f"y {fr(max(a.y[0],b.y[0]))}→{fr(min(a.y[1],b.y[1]))}, "
                     f"z {fr(max(a.z[0],b.z[0]))}→{fr(min(a.z[1],b.z[1]))})")
    if not found:
        rep.ok("no two solid members occupy the same space")


def compute_derived(d, members, stair, room):
    """The derived quantities, as a dict — shared with drawings.py."""
    return check_derived(Report(quiet=True), d, members, stair, room)


def check_derived(rep, d, members, stair, room):
    rep.section("DERIVED — recomputed from the members, compared with `expected:`")
    M = members
    exp = d["expected"]
    ceiling = float(room["ceiling"])
    mattress_t = float(d["mattress"]["thickness"])
    nook = d["nook"]
    scr = d["screen"]
    got = {}

    got["deck_top"] = M["deck_ply"].z[1]
    got["platform_finished"] = [M["beam_wrap_face"].x[1], M["beam_wrap_face"].y[1]]
    got["clear_below_deck_x"] = M["hw_sheath_loft_a"].x[0]
    got["clear_under_joists"] = M["deck_joist[0]"].z[0]
    got["clear_under_beam"] = M["beam"].z[0]
    got["deck_joist_span"] = M["beam"].y[0] - M["rear_ledger"].y[1]
    got["deck_ply"] = [M["deck_ply"].size("x"), M["deck_ply"].size("y")]
    got["sitting_headroom"] = ceiling - (got["deck_top"] + mattress_t)
    got["riser"] = stair.R
    got["stair_angle_deg"] = math.degrees(stair.angle)
    got["stringer_throat"] = stair.throat
    got["stringer_underside_at_27"] = stair.underside(27)
    got["stringer_underside_at_47"] = stair.underside(47)
    got["landing_top"] = M["lnd_ply"].z[1]
    got["landing_headroom"] = ceiling - M["lnd_ply"].z[1]
    got["deck_headroom"] = ceiling - got["deck_top"]
    oy = nook["opening_y"]
    got["nook_opening"] = [oy[1] - oy[0], float(nook["header_bottom"])]
    got["nook_light_chase"] = M["lnd_joist[0]"].z[0] - float(nook["header_bottom"])
    wrap = float(nook.get("wrap", 0)); panel = float(nook["soffit_panel_thickness"])
    got["nook_far_end_height"] = stair.underside(oy[1]) - panel if wrap else float(nook["header_bottom"]) - (oy[1] - float(nook["flat_ceiling_to_y"])) * stair.tan
    got["rim_header_overlap"] = overlap(M["lnd_rim"].z, M["hw_header"].z)
    got["rim_stringer_bearing"] = overlap(M["lnd_rim"].z, stair.plumb_cut())
    ex = scr["extent_x"]
    got["slat_clear"] = (ex[1] - ex[0] - scr["slat_count"] * scr["slat_size"]) / (scr["slat_count"] - 1)
    got["stair_projection"] = stair.y_bottom
    got["fan_clearance"] = M["fan"].y[0] - got["platform_finished"][1]
    door = room["door"]
    got["room_depth_chain"] = (stair.y_bottom + (M["dresser"].y[0] - stair.y_bottom)
                               + M["dresser"].size("y") + door["width"] + door["to_corner"])
    got["screen_top_plate_band"] = list(M["screen_top_plate"].y)
    # the chain must also close the room: door far edge + corner gap = room depth
    closes = door["y"][1] + door["to_corner"]
    if abs(closes - float(room["y"])) > TOL:
        rep.warn(f"room chain: door ends at {fr(float(door['y'][1]))} + {fr(float(door['to_corner']))} to the corner = "
                 f"{fr(closes)}, but the room is {fr(float(room['y']))} — {fr(float(room['y']) - closes)} is unplaced")

    for k, want in exp.items():
        have = got.get(k)
        if have is None:
            rep.warn(f"{k}: expected but not computed")
            continue
        if isinstance(want, list):
            diff = max(abs(float(w) - h) for w, h in zip(want, have))
            s_have, s_want = " × ".join(fr(h) for h in have), " × ".join(fr(float(w)) for w in want)
        else:
            diff = abs(float(want) - have)
            s_have, s_want = fr(have), fr(float(want))
        if diff <= 1 / 16 + TOL:
            rep.ok(f"{k}: {s_have}" + (f"  (stated {s_want})" if diff > TOL else ""))
        elif diff <= 0.25 + TOL:
            rep.warn(f"{k}: exact {s_have}, stated {s_want} — {fr(diff)} drift; decide which is the layout number")
        else:
            rep.fail(f"{k}: {s_have}   ← expected {s_want}")

    # things worth printing even without an expectation
    rep.info(f"risers: {stair.n_treads + 1} × {fr(stair.R)} to the landing, then {fr(stair.R_top)} "
             f"landing → deck ({stair.n_risers} × {fr(stair.R)} would be {fr(stair.n_risers * stair.R)}, "
             f"{fr(stair.total_rise - stair.n_risers * stair.R)} short of the deck)")
    rep.info(f"riser heights: " + ", ".join(f"{fr(z)}" for z in stair.riser_z.values()))
    rep.info(f"stringer plumb cut z: {fr(stair.plumb_cut()[0])} → {fr(stair.plumb_cut()[1])} (top = landing − tread {fr(stair.t)})")
    rep.info(f"nosing-line length over {stair.n_treads} treads: {fr(stair.hyp * stair.n_treads)} — stringer stock must exceed this plus the plumb and seat cuts")
    for i in range(1, stair.n_treads + 1):
        rep.info(f"headroom over tread {i}: {fr(ceiling - stair.riser_z[i])}")
    rep.info(f"half-wall stud length: {fr(M['hw_king_a'].size('z'))} (kings) / {fr(M['hw_trimmer_a'].size('z'))} (trimmers)")
    rep.info(f"header bearing on trimmers: {fr(overlap(M['hw_header'].y, M['hw_trimmer_a'].y))} / {fr(overlap(M['hw_header'].y, M['hw_trimmer_b'].y))}")
    return got


def check_stair_and_nook(rep, d, members, stair):
    rep.section("STAIR & NOOK GEOMETRY")
    M = members
    nook = d["nook"]
    hb = float(nook["header_bottom"])
    t_panel = float(nook["soffit_panel_thickness"])
    y_break = float(nook["flat_ceiling_to_y"])
    oy = [float(v) for v in nook["opening_y"]]
    wrap = float(nook.get("wrap", 0))
    face = hb - wrap                       # finished flat-ceiling face
    if wrap:
        rep.info(f"nook ply wrap {fr(wrap)} → finished flat ceiling at {fr(face)}, framing plane at {fr(face + t_panel)}")

    # landing top must equal riser 6
    want = stair.riser_z[stair.n_treads + 1]
    have = M["lnd_ply"].z[1]
    (rep.ok if abs(want - have) <= 0.011 else rep.fail)(
        f"landing top {fr(have)} vs riser {stair.n_treads+1} at {fr(want)}")

    # deck must equal riser 7
    (rep.ok if abs(stair.riser_z[stair.n_risers] - M['deck_ply'].z[1]) <= TOL else rep.fail)(
        f"deck top {fr(M['deck_ply'].z[1])} = riser {stair.n_risers} at {fr(stair.riser_z[stair.n_risers])}")

    # throat
    if stair.throat < float(d["stair"]["throat_min"]):
        rep.fail(f"throat {fr(stair.throat)} < minimum {fr(float(d['stair']['throat_min']))}")
    else:
        rep.ok(f"throat {fr(stair.throat)} ≥ {fr(float(d['stair']['throat_min']))}")

    # stringer vs rim: how much hangs below the rim?
    pc = stair.plumb_cut()
    below = M["lnd_rim"].z[0] - pc[0]
    rep.info(f"stringer plumb cut at y={fr(stair.y_top)}: z {fr(pc[0])}→{fr(pc[1])} ({fr(pc[1]-pc[0])} tall); rim bottom {fr(M['lnd_rim'].z[0])} → cut extends {fr(below)} below it")
    if stair.top_run > 0:
        rep.info(f"stringer top run {fr(stair.top_run)} under the landing; plumb cut {fr(stair.top_run)} behind the landing face")

    # flat soffit panel: the finished face is the header bottom (or the head jamb); panel top must clear the framing
    panel_top = face + t_panel
    clear = M["lnd_side_member"].z[0] - panel_top
    if clear < -TOL:
        rep.fail(f"flat soffit: a {fr(t_panel)} panel with its face at {fr(hb)} has its top at {fr(panel_top)}, "
                 f"{fr(-clear)} INTO the side member (bottom {fr(M['lnd_side_member'].z[0])})")
    else:
        rep.ok(f"flat soffit panel clears the side member by {fr(clear)}")

    # raked soffit = one panel under the stringer undersides; it meets the flat ceiling where underside − panel = face
    def rake(y):
        return stair.underside(y) - t_panel
    y_meet = stair.y_riser_top - (face + t_panel - stair.underside(stair.y_riser_top)) / stair.tan
    def soffit(y):
        return face if y <= y_meet else rake(y)
    if abs(y_meet - y_break) > 0.1:
        rep.warn(f"flat/rake break: the stringer-underside soffit reaches the {fr(face)} ceiling at y={fr(y_meet)}, but nook.flat_ceiling_to_y says {fr(y_break)}")
    else:
        rep.ok(f"flat ceiling {fr(face)} to y={fr(y_meet)}, then the panel rides the stringer undersides to {fr(rake(oy[1]))} at y={fr(oy[1])}")
    if stair.top_run > 0 and stair.y_top > y_meet + TOL:
        rep.fail(f"stringers stop at y={fr(stair.y_top)} but the raked panel needs them from y={fr(y_meet)}")

    # every landing member must clear the soffit along its whole y extent
    for m in members.values():
        # Rev AE: the landing box moved out to the half-wall framing at 106.25, so the
        # cut-off that keeps the half wall itself out of this loop moved with it.
        if m.role == "existing" or m.kind in RAKED or m.x[0] < members["hw_sheath_stair"].x[0] - TOL: continue
        if overlap(m.y, oy) <= TOL or m.z[0] > face + 8: continue
        worst = min(m.z[0] - (soffit(y) + (t_panel if y <= y_meet else 0)) for y in (m.y[0], m.y[1]))
        (rep.ok if worst > -TOL else rep.fail)(f"{m.id} bottom {fr(m.z[0])} clears the soffit by {fr(worst)} over y {fr(m.y[0])}→{fr(m.y[1])}")


    # screen
    scr = d["screen"]
    # Rev AG: the slats stand on the beam's poplar cap, not on the LVL itself, and
    # screw down through it into the beam — so the finished top is the datum.
    top = M["beam_wrap_top"].z[1]
    if any(M[f"slat[{i}]"].z[0] != top for i in range(scr["slat_count"])):
        rep.fail("slat bottoms are not at the beam's finished top")
    elif abs(M["beam_wrap_top"].z[0] - M["beam"].z[1]) > TOL:
        rep.fail("beam_wrap_top does not sit on the beam")
    else:
        rep.ok(f"slats sit on the beam's finished top at {fr(top)} "
               f"({fr(M['beam'].z[1])} framing + {fr(M['beam_wrap_top'].size('z'))} cap)")
    last = M[f"slat[{scr['slat_count']-1}]"]
    (rep.ok if abs(last.x[1] - scr["extent_x"][1]) <= TOL else rep.fail)(
        f"last slat ends at {fr(last.x[1])} (screen extent {fr(float(scr['extent_x'][1]))})")


# ----------------------------------------------------------------- main
def main():
    quiet = "--quiet" in sys.argv
    paths = [a for a in sys.argv[1:] if not a.startswith("--")]
    with open(paths[0] if paths else "dimensions.yaml") as f:
        d = yaml.safe_load(f)
    rep = Report(quiet)
    members = expand(d["members"])
    lumber = {k: (v[0], v[1]) for k, v in d["lumber"].items()}
    d["stair"]["_stringer_depth"] = lumber[d["stair"]["stringer_stock"]][1]
    stair = Stair(d["stair"], float(d["expected"]["deck_top"]))

    print(f"loft bed · dimensions.yaml rev {d.get('rev')} · {len(members)} members · {len(d['connections'])} connection rules")
    check_sections(rep, members, lumber)
    check_bounds(rep, members, d["room"])
    check_derived(rep, d, members, stair, d["room"])
    check_stair_and_nook(rep, d, members, stair)

    rep.section("CONNECTIONS — does each claimed connection exist in all three axes?")
    for c in d["connections"]:
        try:
            check_connection(rep, c, members, stair, d["room"], d["nook"])
        except KeyError as e:
            rep.fail(f"connection {c}: unknown member {e}")

    check_clashes(rep, members, d["connections"])
    rep.dump()
    sys.exit(1 if rep.fails else 0)


if __name__ == "__main__":
    main()
