# cad-out run log

Regenerate with `python3 -m cad` from the repo root.
Timings are printed, not recorded — this file changes only when the model does.
Full write-up: `audits/V-kernel-spike.md`.

```
cad kernel · build123d 0.11.1 · OCP 7.9.3.1.1 · python 3.13.12
dimensions.yaml rev AR · stair: 6 risers @ 8.2500 + 8.5000, run 9.0, throat 5.168

[build] 108 solids (12 derived, not yaml members)
        loft        25 solids    10.26 cu ft
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
[clash] 0 real interferences, 3 coincident faces → cad-out/clash.txt
        underside ray cast vs Stair.underside(): worst Δ 0.00000"
[loft] bearing areas, slat gaps and clearances → cad-out/loft.txt
       · slat[22]: only 0.75 of its 1.50 width is over the LVL (it overhangs the beam's end onto the stair face) — offset its screw inboard
       · fan → nearest slat: kernel 16.1250", yaml expects 15.25
[fasteners] 8 rays → cad-out/fasteners.txt
[section] cut+HLR → cad-out/d4-kernel.svg, cad-out/d8b-kernel.svg
          worst cut-edge deviation vs d4.svg: 0.0048" on stringer_b (1/16" = 0.0625)
[export] model.step 1978 kB, model.stl 74 kB
         re-imported: 104 solids (wrote 104), volume 34430.38 vs 34430.38 cu in, Δ 0.0000
```
