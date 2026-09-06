"""Schedule tables A–E and the 'locked dimensions' cards. Every number here is computed from the model."""
from .model import *

def tbl(rows, head, num=(1, 2)):
    """num = column indexes that hold numbers (tabular figures, no wrapping). Prose columns must wrap."""
    out = ["<table><tr>" + "".join(f"<th>{E(h)}</th>" for h in head) + "</tr>"]
    for r in rows:
        out.append("<tr>" + "".join(f'<td class="{"n" if i in num else ""}">{c}</td>' for i, c in enumerate(r)) + "</tr>")
    return "\n".join(out) + "</table>"

def z_row(name, k, note=""):
    mm = m(k); return (name, fr(mm.z[0]), fr(mm.z[1]), note)

def schedule():
    A = [z_row(f"Half-wall bottom plates (y {fr(m('hw_bottom_plate_a').y[0])}→{fr(m('hw_bottom_plate_a').y[1])}, {fr(m('hw_bottom_plate_b').y[0])}→{fr(m('hw_bottom_plate_b').y[1])})", "hw_bottom_plate_a", "split at the opening — the nook is open to the floor"), z_row("Half-wall studs (kings)", "hw_king_a", f"{fr(m('hw_king_a').size('z'))} long · trimmers to {fr(m('hw_trimmer_a').z[1])} · ½ ply flitch between king and trimmer makes each pack {fr(m('hw_trimmer_a').y[1] - m('hw_king_a').y[0])}"),
         z_row("Nook header (3½ sandwich)", "hw_header", f"2×10 + ½ ply + 2×10, full {fr(m('hw_header').size('z'))} stock · bottom = the landing-ledger bottom"),
         ("Nook finished ceiling (flat run)", "—", fr(CEIL), f"header/ledger bottom {fr(HB)} less the ¾ panel; framing plane {fr(CEIL+PANEL)}"),
         z_row("Landing box — rim, side member, ledgers, all 2×8", "lnd_rim", f"clears the {fr(CEIL+PANEL)} panel top by {fr(m('lnd_rim').z[0]-CEIL-PANEL)}"),
         z_row("Landing joists, 2×4", "lnd_joist[0]"), z_row("Stringer plumb cut (at y 18)", "lnd_rim", f"{fr(ST.plumb_cut()[1]-ST.plumb_cut()[0])} tall against a {fr(m('lnd_rim').size('z'))} rim"),
         ("Landing finished top", "—", fr(LAND), f"{fr(DECK)} − the {fr(ST.R_top)} top riser — <b>not</b> a {fr(ST.R)} stair riser"),
         z_row("Half-wall double top plate", "hw_top_plate_1", "deck bears here"), z_row("Beam wrap, underside", "beam_wrap_underside", "¾ poplar"),
         z_row("Deck joists, 2×4", "deck_joist[0]"), z_row("Beam, doubled 2×10", "beam", f"{fr(m('beam').z[1]-DECK)} proud of the deck"),
         z_row("Side ledger, 2×10", "side_ledger", "top = beam top"), z_row("Rear ledger, 2×6", "rear_ledger", "top inside the ledge box"),
         z_row("Deck plywood", "deck_ply", f"<b>deck top = {fr(DECK)}</b>"), ("Mattress", fr(DECK), fr(DECK + MAT["thickness"]), f"{fr(MAT['thickness'])} ASSUMED"),
         ("Boxed ledge", fr(DECK), fr(m("ledge_lid").z[1]), f"{fr(m('ledge_lid').z[1]-DECK-MAT['thickness'])} proud of the mattress"),
         z_row("Screen slats", "slat[0]", f"{fr(m('slat[0]').size('z'))} long"), z_row("Screen top plate, 2×4 flat", "screen_top_plate"), ("Ceiling", "—", fr(CEILING), "")]
    A[6] = ("Stringer plumb cut (at y 18)", fr(ST.plumb_cut()[0]), fr(ST.plumb_cut()[1]), "= the rim, full depth")
    B = "<table><tr><th>Riser</th>" + "".join(f"<th>{i}{' (landing)' if i == ST.n_treads+1 else ' (deck)' if i == ST.n_risers else ''}</th>" for i in range(1, ST.n_risers + 1)) + "</tr><tr><td>Height</td>" + "".join(f'<td class="n">{ST.riser_z[i]:.2f}</td>' for i in range(1, ST.n_risers + 1)) + "</tr></table>"
    def x_row(name, k, note=""):
        mm = m(k); return (name, fr(mm.x[0]), fr(mm.x[1]), note)
    C = [x_row("Desk (existing)", "desk"), ("Mattress", "2", fr(2 + MAT["size"][1]), "2 tuck gap at the window wall"), ("Deck landing area", fr(2 + MAT["size"][1]), "107", ""),
         ("Half-wall", fr(m("hw_sheath_loft_a").x[0]), fr(m("hw_sheath_stair_a").x[1]), f"studs {fr(m('hw_king_a').x[0])}–{fr(m('hw_king_a').x[1])}"),
         x_row("Deck structural rim", "deck_rim", "stair-side panel runs to the deck top"), ("<b>Deck, overall</b>", "0", "107", ""),
         x_row("Landing side member", "lnd_side_member", "on the header's flush face"), ("Stringers A / B / C", " · ".join(f"{fr(m(k).x[0])}–{fr(m(k).x[1])}" for k in ("stringer_a", "stringer_b", "stringer_c")), "", f"{fr(float(d['stair']['stringer_pitch']))} centres"),
         ("Landing joists", " · ".join(f"{fr(m(k).x[0])}–{fr(m(k).x[1])}" for k in ids("lnd_joist")), "", "run with the stringers"),
         x_row("Stringer A skin, ¾ ply", "stringer_a_skin", f"y {fr(m('stringer_a_skin').y[0])}→{fr(m('stringer_a_skin').y[1])} — continues the half-wall's stair-side sheathing band, ¾ inboard of its visible face; boards lap it, so they are {fr(STAIR_X[1] - SKIN_X0)} there"),
         x_row("Right-wall ledger", "lnd_ledger_rightwall"), ("<b>Stair &amp; landing</b>", "107", fr(RX), "24")]
    def y_row(name, k, note=""):
        mm = m(k); return (name, fr(mm.y[0]), fr(mm.y[1]), note)
    D = [y_row("Rear ledger", "rear_ledger"), ("Boxed ledge", "0", "8", f"well {fr(m('ledge_front_rail').y[0]-m('rear_ledger').y[1])} wide"),
         ("Nook opening — rough", fr(NOOK_Y[0]), fr(NOOK_Y[1]), fr(NOOK_Y[1]-NOOK_Y[0])), ("Nook opening — finished", fr(JAMB_Y[0]), fr(JAMB_Y[1]), f"{fr(JAMB_Y[1]-JAMB_Y[0])} between ¾ ply wraps"),
         y_row(f"Header (kings {fr(m('hw_king_a').y[0])}–{fr(m('hw_king_a').y[1])}, {fr(m('hw_king_b').y[0])}–{fr(m('hw_king_b').y[1])})", "hw_header", f"{fr(m('hw_header').size('y'))} long, {fr(m('hw_trimmer_a').y[1] - m('hw_header').y[0])} bearing each end (trimmer + ½ ply flitch)"),
         ("Nook flat ceiling", fr(NOOK_Y[0]), fr(Y_MEET), "rake begins where the stringer undersides reach the panel"),
         ("Mattress bay", "8", fr(m("beam").y[0]), f"{fr(m('beam').y[0]-8)} for a {MAT['size'][0]} mattress"),
         y_row("Landing side member", "lnd_side_member"), y_row("Landing rim", "lnd_rim", "2×8"), ("Stringer top runs", fr(ST.y_top), fr(ST.y_riser_top), "under the landing deck"),
         y_row("Stringer A skin", "stringer_a_skin", "half-wall end cap → riser 1's plumb cut · 2×2 floor cleat behind it to 61⅞"),
         y_row("Blocking between stringers", "lnd_blocking[0]", "flush with riser 6"), y_row("Right-wall ledger", "lnd_ledger_rightwall", "stringer C bears on its end"),
         ("Landing", "0", fr(ST.landing), ""), y_row("Beam structure", "beam", "over the end stud pack"), y_row("Beam wrap", "beam_wrap_face"),
         ("<b>Platform, finished</b>", "0", fr(m("beam_wrap_face").y[1]), f"8 + {fr(m('beam').y[0]-8)} + 3 + ¾"), y_row("Desk (existing)", "desk", f"projects {fr(m('desk').y[1]-m('beam_wrap_face').y[1])} past the beam"),
         ("Fan blade edge", "—", fr(m("fan").y[0]), f"blades at {fr(m('fan').z[0])}"), ("Stair, to the bottom nosing", fr(ST.y_riser_top), fr(Y_FIN), f"{ST.n_treads} treads @ {fr(ST.run)} · framing line {fr(ST.y_bottom)}"),
         y_row("Dresser (48 × 16)", "dresser", f"{fr(m('dresser').y[0]-Y_FIN)} gap to the stair"), ("Entry door (32)", fr(float(room["door"]["y"][0])), fr(float(room["door"]["y"][1])), f"{fr(float(room['door']['to_corner']))} to the corner")]
    Ed = [("Clear span below the deck", fr(DER["clear_below_deck_x"]), "107 deck − 5 half-wall"), ("Clear height under joists", fr(DER["clear_under_joists"]), "58 − ¾ ply − 3½ joist"),
          ("Clear height under the beam", fr(DER["clear_under_beam"]), "less the ¾ wrap — not uniform with the joists"), ("Deck joist span", fr(DER["deck_joist_span"]), "ledger face → beam face"),
          ("Deck plywood", " × ".join(fr(a) for a in DER["deck_ply"]), "1½→106¼ by 1½→47"), ("Sitting headroom", fr(DER["sitting_headroom"]), f"{fr(CEILING)} − mattress top"),
          ("Riser", fr(ST.R), f"{ST.n_treads+1} of them, floor → landing"), ("Top riser (landing → deck)", fr(ST.R_top), "set by the framing stack over the header, not by the stair"), ("Stair angle", f"{math.degrees(ST.angle):.2f}°", "atan(rise/run)"), ("Stringer throat", fr(ST.throat), "11¼ − notch depth · 3½ min"),
          ("Stringer plumb cut (y 18)", f"{fr(ST.plumb_cut()[0])} → {fr(ST.plumb_cut()[1])}", "≈7 tall = the 2×8 rim"), ("Stringer underside at y 27 / 47", f"{fr(U(27))} / {fr(U(47))}", f"notch corners − throat, dropped {fr(T)} for the treads"),
          ("Landing headroom", fr(DER["landing_headroom"]), f"{fr(CEILING)} − {fr(LAND)}"), ("Nook finished opening", f"{fr(JAMB_Y[1]-JAMB_Y[0])} × {fr(CEIL)}", f"rough less ¾ ply wrap; head raked past y {fr(Y_MEET)}"),
          ("Nook flat ceiling depth", fr(Y_MEET - JAMB_Y[0]), f"wrap face to y {fr(Y_MEET)}"), ("Nook far end height", fr(DER["nook_far_end_height"]), f"stringer underside at {fr(NOOK_Y[1])} − ¾ panel"),
          ("Light chase over the flat", fr(DER["nook_light_chase"]), "joist bottom − header bottom — wafer LED only"), ("Rim ↔ header engagement", fr(DER["rim_header_overlap"]), "full 2×8"),
          ("Rim ↔ stringer bearing", fr(DER["rim_stringer_bearing"]), "≈ full 2×8"), ("Slat clear opening", fr(DER["slat_clear"]), f"(107 − {SCR['slat_count']} × 1½) ÷ {SCR['slat_count']-1} · 3½ max"),
          ("Stair projection", f"{fr(DER['stair_projection'])} framing · {fr(Y_FIN)} finished", f"{fr(ST.landing)} landing + {fr(ST.y_bottom-ST.y_riser_top)} run + {fr(RISER_T)} riser + {fr(NOSE)} nose"), ("Fan clearance", fr(DER["fan_clearance"]), f"{fr(m('fan').y[0])} − {fr(m('beam_wrap_face').y[1])}"),
          ("Room depth chain", fr(DER["room_depth_chain"]), (f"closes on {fr(RY)} — but only because the door's {fr(float(room['door']['to_corner']))} to the corner is ASSUMED, not measured (field)" if abs(RY - DER["room_depth_chain"]) < 1e-6 else f"{fr(RY - DER['room_depth_chain'])} unplaced in {fr(RY)} — field"))]
    return (f'<h2 style="margin-top:4px">A · Vertical datums</h2>{tbl(A, ["Member", "Bottom", "Top", "Note"])}'
            f'<h2 style="margin-top:18px">B · Stair heights</h2>{B}'
            f'<div class="note" style="border-left-color:#b07d1a;background:#fdf7ec"><b style="color:#b07d1a">The risers are not all equal.</b> The {ST.n_treads+1} risers from the floor to the landing are {fr(ST.R)} — set the square to {fr(ST.R)} / {fr(ST.run)} and step it off. The {ST.n_risers}th, the sideways step from the landing onto the deck, is {fr(ST.R_top)}: it is the framing stack over the nook header, not a stair riser. Stepping {fr(ST.R)} off {ST.n_risers} times lands at {fr(ST.n_risers * ST.R)}, {fr(DECK - ST.n_risers * ST.R)} short of the deck. Drop each stringer {fr(T)} for the tread thickness.</div>'
            f'<h2 style="margin-top:18px">C · Plan — x, from the window wall</h2>{tbl(C, ["Element", "From", "To", "Note"])}'
            f'<h2 style="margin-top:18px">D · Plan — y, out from the bed wall</h2>{tbl(D, ["Element", "From", "To", "Note"])}'
            f'<h2 style="margin-top:18px">E · Derived — do not measure these independently</h2>{tbl([(a, b, c) for a, b, c in Ed], ["Quantity", "Value", "Falls out of"], num=(1,))}')


def cards():
    rows = [("Deck height", fr(DECK), "top of plywood, AFF"), ("Platform", f"107 × {fr(m('beam_wrap_face').y[1])}", "finished, incl. ¾ wrap"),
            ("Clear underneath", fr(DER["clear_under_joists"]), f"at joists; {fr(DER['clear_under_beam'])} under the wrapped beam"), ("Sitting headroom", fr(DER["sitting_headroom"]), "mattress top to ceiling"),
            ("Boxed ledge", "8w × 8h", f"well {fr(m('ledge_front_rail').y[0]-1.5)} × {fr(m('ledge_front_rail').z[1]-DECK)}"), ("Mattress bay", f"{fr(m('beam').y[0]-8)} × {fr(107-2-24)}", "1 slack + 2 tuck at the window wall"),
            ("Stair", f"{ST.n_treads+1} @ {fr(ST.R)} + {fr(ST.R_top)}", f"{fr(ST.run)} run · {math.degrees(ST.angle):.1f}° · 24 wide · ¾ ply treads"), ("Stair landing", f"24 × {fr(ST.landing)}", f"at {fr(LAND)} — {fr(ST.R_top)} below the deck"),
            ("Half-wall", "5 thick", "¾ ply + 3½ studs + ¾ ply"), ("Clear below deck", fr(DER["clear_below_deck_x"]), "107 deck less the 5 wall"),
            ("Under-stair nook", f"{fr(JAMB_Y[1]-JAMB_Y[0])} × {fr(CEIL)}", f"finished, ply-wrapped · {fr(DER['nook_far_end_height'])} at the far end")]
    return "".join(f'<div class="spec"><dt>{E(a)}</dt><dd>{E(b)}<span>{E(c)}</span></dd></div>' for a, b, c in rows)
