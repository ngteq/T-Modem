# KiCad project — T-Modem v0.25

Open **`t-modem.kicad_pro`** in **KiCad ≥ 8** (tested with **KiCad 10**).

| File | Role |
|------|------|
| `t-modem.kicad_pro` | Project |
| `t-modem.kicad_sch` | Schematic + embedded symbols |
| `t-modem.kicad_sym` | Custom TCM3105 + Pico subset |
| `t-modem.kicad_pcb` | **190×110 mm** board — copper DRC short/unconn/cross **0/0/0** (prototype-ready) |
| `sym-lib-table` | Points at `t-modem.kicad_sym` |

## Operator steps

1. Open **`t-modem.kicad_pro`** → run **DRC**.  
2. Silk cosmetic warnings may remain (`silk_over_copper` / overlap) — OK for prototype.  
3. Export Gerbers + drill — see [`../../fab/README.md`](../../fab/README.md).

**Authoritative electrical design:** [`../../../docs/SCHEMATIC.md`](../../../docs/SCHEMATIC.md)  
**Assembly:** [`../../../docs/PCB-ASSEMBLY.md`](../../../docs/PCB-ASSEMBLY.md)

**AS-IS:** no support, no warranty · GPLv3 · standard reference only · **not** BayCom/SER12.
