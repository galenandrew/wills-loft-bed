# spike run log

Regenerate with `python3 -m cad.spike` from the repo root.
Full write-up: `audits/V-kernel-spike.md`.

```
cad spike · build123d 0.11.1 · OCP 7.9.3.1.1 · python 3.13.12
dimensions.yaml rev AM · stair: 6 risers @ 8.2500 + 8.5000, run 9.0, throat 5.168

[build] 116 solids in 0.14s (12 derived, not yaml members)
        loft        33 solids     8.62 cu ft
        screen      24 solids     1.10 cu ft
        stair       26 solids     3.67 cu ft
        half_wall   18 solids     3.14 cu ft
        nook        11 solids     1.75 cu ft
        context      4 solids    53.03 cu ft
        beam is ONE notched solid (2584.750 cu in, x 0→106.25); yaml rows fused: beam_tongue
        deck_joist[0] is ONE notched solid (254.625 cu in, x 1.5→3); yaml rows fused: deck_joist_tail
        hw_sheath_loft_head is ONE notched solid (835.719 cu in, x 102→102.75); yaml rows fused: hw_sheath_loft_b
        hw_sheath_stair is ONE notched solid (686.531 cu in, x 106.25→107); yaml rows fused: ledge_end_cap, beam_end_cap
        hw_end_cap is ONE notched solid (171.750 cu in, x 102→107); yaml rows fused: hw_end_cap_foot
[clash] 0 real interferences, 3 coincident faces (0.74s) → spike/clash.txt
        underside ray cast vs Stair.underside(): worst Δ 0.00000"
[loft] bearing areas, slat gaps and clearances in 0.42s → spike/loft.txt
       · slat[22]: only 0.75 of its 1.50 width is over the LVL (it overhangs the beam's end onto the stair face) — offset its screw inboard
[fasteners] 8 rays in 0.03s → spike/fasteners.txt
[section] cut+HLR in 0.92s → spike/d4-kernel.svg, spike/d8b-kernel.svg
          worst cut-edge deviation vs d4.svg: 0.0048" on stringer_b (1/16" = 0.0625)
[export] model.step 2113 kB, model.stl 78 kB in 0.47s
         re-imported: 112 solids (wrote 112), volume 31590.03 vs 31590.03 cu in, Δ 0.0000

TOTAL 2.95s  (build 0.14 · clash 0.74 · fasteners 0.03 · section 0.92 · export 0.47)
```
