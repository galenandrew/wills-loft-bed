# spike run log

Regenerate with `python3 -m cad.spike` from the repo root.
Full write-up: `audits/V-kernel-spike.md`.

```
cad spike · build123d 0.11.1 · OCP 7.9.3.1.1 · python 3.13.12
dimensions.yaml rev Y · stair: 6 risers @ 8.2500 + 8.5000, run 9.0, throat 5.168

[build] 55 solids in 0.05s (11 derived, not yaml members)
[clash] 0 real interferences, 3 coincident faces (0.36s) → spike/clash.txt
        underside ray cast vs Stair.underside(): worst Δ 0.00000"
[fasteners] 8 rays in 0.02s → spike/fasteners.txt
[section] cut+HLR in 0.45s → spike/d4-kernel.svg, spike/d8b-kernel.svg
          worst cut-edge deviation vs d4.svg: 0.0048" on stringer_b (1/16" = 0.0625)
[export] model.step 1067 kB, model.stl 41 kB in 0.17s
         re-imported: 55 solids (wrote 55), volume 14486.07 vs 14486.07 cu in, Δ 0.0000

TOTAL 1.15s  (build 0.05 · clash 0.36 · fasteners 0.02 · section 0.45 · export 0.17)
```
