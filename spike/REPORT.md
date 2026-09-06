# spike run log

Regenerate with `python3 -m cad.spike` from the repo root.
Full write-up: `audits/V-kernel-spike.md`.

```
cad spike · build123d 0.11.1 · OCP 7.9.3.1.1 · python 3.13.12
dimensions.yaml rev AF · stair: 6 risers @ 8.2500 + 8.5000, run 9.0, throat 5.168

[build] 110 solids in 0.16s (12 derived, not yaml members)
        loft        27 solids     7.47 cu ft
        screen      24 solids     1.27 cu ft
        stair       26 solids     3.67 cu ft
        half_wall   18 solids     3.13 cu ft
        nook        11 solids     1.75 cu ft
        context      4 solids    49.74 cu ft
        ledge_front_rail is ONE notched solid (572.109 cu in, x 0→106.25); yaml rows fused: ledge_front_rail_tongue
        hw_sheath_loft_head is ONE notched solid (835.719 cu in, x 102→102.75); yaml rows fused: hw_sheath_loft_b
        hw_sheath_stair is ONE notched solid (666.000 cu in, x 106.25→107); yaml rows fused: ledge_end_cap, beam_end_cap
        hw_end_cap is ONE notched solid (171.750 cu in, x 102→107); yaml rows fused: hw_end_cap_foot
[clash] 0 real interferences, 3 coincident faces (0.70s) → spike/clash.txt
        underside ray cast vs Stair.underside(): worst Δ 0.00000"
[loft] bearing areas, slat gaps and clearances in 0.45s → spike/loft.txt
       · slat[22]: partly past the end of what carries it — less than the 1.12 sq in the others get
[fasteners] 8 rays in 0.02s → spike/fasteners.txt
[section] cut+HLR in 0.86s → spike/d4-kernel.svg, spike/d8b-kernel.svg
          worst cut-edge deviation vs d4.svg: 0.0048" on stringer_b (1/16" = 0.0625)
[export] model.step 2011 kB, model.stl 75 kB in 0.43s
         re-imported: 106 solids (wrote 106), volume 29878.00 vs 29878.00 cu in, Δ 0.0000

TOTAL 2.82s  (build 0.16 · clash 0.70 · fasteners 0.02 · section 0.86 · export 0.43)
```
