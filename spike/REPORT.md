# spike run log

Regenerate with `python3 -m cad.spike` from the repo root.
Full write-up: `audits/V-kernel-spike.md`.

```
cad spike · build123d 0.11.1 · OCP 7.9.3.1.1 · python 3.13.12
dimensions.yaml rev AB · stair: 6 risers @ 8.2500 + 8.5000, run 9.0, throat 5.168

[build] 114 solids in 0.08s (12 derived, not yaml members)
        loft        29 solids     7.63 cu ft
        screen      24 solids     1.27 cu ft
        stair       24 solids     3.45 cu ft
        half_wall   21 solids     3.22 cu ft
        nook        12 solids     1.93 cu ft
        context      4 solids    49.74 cu ft
        ledge_front_rail is ONE notched solid (572.109 cu in, x 0→106.25); yaml rows fused: ledge_front_rail_tongue
[clash] 0 real interferences, 3 coincident faces (0.61s) → spike/clash.txt
        underside ray cast vs Stair.underside(): worst Δ 0.00000"
[loft] bearing areas, slat gaps and clearances in 0.44s → spike/loft.txt
       · slat[22]: partly past the end of what carries it — less than the 1.12 sq in the others get
[fasteners] 8 rays in 0.02s → spike/fasteners.txt
[section] cut+HLR in 0.83s → spike/d4-kernel.svg, spike/d8b-kernel.svg
          worst cut-edge deviation vs d4.svg: 0.0048" on stringer_b (1/16" = 0.0625)
[export] model.step 2003 kB, model.stl 73 kB in 0.37s
         re-imported: 110 solids (wrote 110), volume 30249.13 vs 30249.13 cu in, Δ 0.0000

TOTAL 2.55s  (build 0.08 · clash 0.61 · fasteners 0.02 · section 0.83 · export 0.37)
```
