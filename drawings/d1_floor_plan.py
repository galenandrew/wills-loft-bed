"""Drawing 1 — Floor plan. Figure code is a verbatim projection of the model; edit labels here, geometry in the yaml."""
from .model import *

NUMBER, TITLE = "1", "Floor plan"

def d1():
    v = View(-6, RX + 6, -9, RY + 6, 3.3, ml=70, mr=80, mt=30, mb=54, vdown=True)
    v.rect(0, RX, 0, RY, "room")
    # loft
    v.rect(0, m("beam_wrap_face").x[1], 0, m("beam_wrap_face").y[1], "deck")
    v.rect(0, m("beam_wrap_face").x[1], 0, 8, "ledge")
    v.rect(MAT["size"][1] and 2, 2 + MAT["size"][1], 8, 8 + MAT["size"][0], "matt")
    for k in ("beam", "beam_tongue"): R(v, m(k), "x", "y", "beamplan"); R(v, m("beam_wrap_face"), "x", "y", "fin")
    v.rect(m("hw_sheath_loft_a").x[0], SKIRT.x[1], 0, m("hw_end_cap").y[1], "hid")
    # landing + stair
    v.rect(*m("lnd_ply").x, 0, m("lnd_ply").y[1], "landing")  # finished deck, incl. its 1/8 nose
    for i in range(1, ST.n_treads + 1):
        for bx0, bx1, by0, by1 in board_rects(*tread_y_board(i)):
            v.rect(bx0, bx1, by0, by1, "tread")               # the boards, not the stringer runs
    R(v, m("stringer_a_skin"), "x", "y", "fin")               # drawn last — it is the finished edge
    # existing
    dk = m("desk"); v.rect(*dk.x, *dk.y, "dashfill")
    dr = m("dresser"); v.rect(*dr.x, *dr.y, "exist")
    door = room["door"]; hy = float(door["y"][1]); w = float(door["width"])
    pts = [(RX - w * math.sin(a * math.pi / 2 / 24), hy - w * math.cos(a * math.pi / 2 / 24)) for a in range(25)]
    v.path(pts, "ghostl"); v.line(RX, hy, RX - w, hy, "door")
    fan = m("fan"); cx, cy, r = (fan.x[0] + fan.x[1]) / 2, (fan.y[0] + fan.y[1]) / 2, (fan.x[1] - fan.x[0]) / 2
    v.out.append(f'<circle class="ghostl" cx="{v.X(cx):.1f}" cy="{v.Y(cy):.1f}" r="{r*v.s:.1f}" fill="none"/>')
    win = room["window"]; v.line(-1.2, float(win["y"][0]), -1.2, float(win["y"][1]), "window")
    # labels
    v.text(50, 4, f"8w × {fr(m('ledge_lid').z[1]-DECK)}h BOXED LEDGE — lid runs the full 107, over the stair face at the deck end", "labs", "middle", dy=4)
    v.text(39.5, 27, f"Twin mattress {MAT['size'][0]} × {MAT['size'][1]}", "lab", "middle", dy=4)
    v.text(39.5, 31.5, f"in a {fr(BAY)} bay — {fr(BAY-MAT['size'][0])}\" slack", "labs", "middle", dy=4)
    v.text(92, 27, "landing area", "lab", "middle", dy=4); v.text(92, 31.5, f"30 × {fr(BAY)}", "labs", "middle", dy=4)
    v.text(50, 54.5, f"{BEAMSTOCK} upstand beam + ¾ poplar wrap — {fr(m('beam').x[1])} long, no posts", "labs", "middle", dy=4)
    v.text(104.6, 30, "half-wall below", "labs", "middle", rot=-90)
    v.text(119, 12, "LANDING", "lab", "middle", dy=4); v.text(119, 17, f"24 × {fr(m('lnd_ply').y[1])} finished @ {fr(LAND)}", "labs", "middle", dy=4)
    v.text(119, 50, f"{ST.n_treads} treads @ {fr(ST.run)}", "labs", "middle", dy=4)
    v.text(RX, 78, "¾ ply skin on stringer A closes the understair cavity", "labs", "end", dy=4)
    v.text(RX, 82, f"boards lap it {fr(STAIR_X[1] - SKIN_X0)} — board 3 notched {fr(STAIR_X[0]-SKIN_X0)} × {fr(STEP_Y - tread_y_board(3)[0])}", "labs", "end", dy=4)
    v.text(12, 60.5, "desk 24 × 55", "labs", "middle", dy=4)
    v.text(123, 126, "dresser 16 × 48", "labs", "middle", rot=-90)
    v.text(cx, cy, f"ceiling fan — blades {fr(fan.z[0])}", "labs", "middle", dy=4)
    v.text(2.2, (float(win["y"][0]) + float(win["y"][1])) / 2, "window", "labs", "middle", rot=-90)
    v.text(RX / 2, RY + 3, "closet wall", "labs", "middle", dy=4)
    v.text(2.2, 75, "window wall", "labs", "middle", rot=-90); v.text(RX - 2.2, 88, "right wall", "labs", "middle", rot=-90)
    # dims
    v.dim_h(0, RX, -5.6, fr(RX)); v.dim_h(0, 107, -2.4, "107 deck"); v.dim_h(107, RX, -2.4, "24")
    v.dim_v(-4.5, 0, m("beam_wrap_face").y[1], fr(m("beam_wrap_face").y[1]))
    yb = Y_FIN; dg = m("dresser").y                           # finished extent — this is a clearance
    v.dim_v(RX + 2.6, 0, yb, f"{fr(yb)} stair", left=False); v.dim_v(RX + 2.6, yb, dg[0], f"{fr(dg[0]-yb)} gap", left=False)
    v.dim_v(RX + 2.6, dg[0], dg[1], f"{fr(dg[1]-dg[0])} dresser", left=False); v.dim_v(RX + 2.6, float(door["y"][0]), hy, f"{fr(w)} door", left=False)
    v.dim_v(RX + 2.6, hy, RY, fr(RY - hy), left=False); v.dim_v(-6.2, 0, RY, fr(RY))
    chain = DER["room_depth_chain"]
    # the chain closes only because door.to_corner is ASSUMED 4 — still a field measurement
    close = f"closes on room {fr(RY)} — to_corner {fr(float(door['to_corner']))} assumed (field)" if abs(RY - chain) < 1e-6 else f"room {fr(RY)} — {fr(RY-chain)} unplaced (field)"
    v.text(RX / 2, RY + 4.8, f"{fr(yb)} + {fr(dg[0]-yb)} + {fr(dg[1]-dg[0])} + {fr(w)} + {fr(float(door['to_corner']))} = {fr(chain)}  ·  {close}", "labs", "middle", dy=13)
    return v.svg("Room floor plan, bed wall at the top, window wall to the left")

FIGURES = [("d1", d1)]
CAPTION = "Facing the bed wall, the window and desk are on your left; the stairs, dresser and entry door on your right. Door swing never reaches below the 150 line. The room-depth chain closes on 186, but only because the door's 4 to the corner is assumed rather than measured — still a field item."
