# KiCad project — T-Modem v0.25

Open **`t-modem.kicad_pro`** in **KiCad ≥ 8** (tested with **KiCad 10**).

| File | Role |
|------|------|
| `t-modem.kicad_pro` | Project |
| `t-modem.kicad_sch` | Schematic + embedded symbols |
| `t-modem.kicad_sym` | Custom TCM3105 + Pico subset |
| `t-modem.kicad_pcb` | **190×110 mm** complete TH board (footprints, nets, pours, tracks) |
| `scripts/generate_board.py` | Pure-Python regenerator (**no** `pcbnew`) |
| `sym-lib-table` | Points at `t-modem.kicad_sym` |

## Operator steps

1. Open project → run **DRC** (Board Setup / Inspect).  
2. Finish remaining signal tracks (pad nets are assigned; B.Cu GND zone filled).  
3. Export Gerbers + drill — see [`../../fab/README.md`](../../fab/README.md).

**Regenerate PCB/schematic:**

```bash
python3 scripts/generate_board.py
```

**Authoritative electrical design:** [`../../../docs/SCHEMATIC.md`](../../../docs/SCHEMATIC.md)  
**Assembly:** [`../../../docs/PCB-ASSEMBLY.md`](../../../docs/PCB-ASSEMBLY.md)

**AS-IS:** no support, no warranty · GPLv3 · standard reference only · **not** BayCom/SER12.
