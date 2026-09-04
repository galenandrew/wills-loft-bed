# spike run log

Regenerate with `python3 -m cad.spike` from the repo root.
Full write-up: `audits/V-kernel-spike.md`.

```
cad spike · build123d 0.11.1 · OCP 7.9.3.1.1 · python 3.13.12
dimensions.yaml rev W · stair: 7 risers @ 8.2857, run 9.0, throat 5.154

[build] 38 solids in 0.05s (12 derived, not yaml members)
[clash] 0 real interferences, 4 coincident faces (0.28s) → spike/clash.txt
        underside ray cast vs Stair.underside(): worst Δ 0.00000"
[fasteners] 8 rays in 0.01s → spike/fasteners.txt
[section] cut+HLR in 0.34s → spike/d4-kernel.svg, spike/d8b-kernel.svg
          worst cut-edge deviation vs d4.svg: 0.0043" on stringer_b (1/16" = 0.0625)
[export] model.step 773 kB, model.stl 30 kB in 0.09s
         re-imported: 38 solids (wrote 38), volume 10820.74 vs 10820.74 cu in, Δ 0.0000

TOTAL 0.86s  (build 0.05 · clash 0.28 · fasteners 0.01 · section 0.34 · export 0.09)
```
