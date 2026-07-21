# Fabrication export — T-Modem v0.25

**AS-IS** · GPLv3 · standard reference only

Gerbers in this tree are produced with `kicad-cli` (KiCad 10). Re-export after any PCB edit.

## CLI (headless)

```bash
export HOME=/tmp/kicad-home   # or a writable KiCad config home
mkdir -p "$HOME/.config/kicad/10.0"

PCB=hardware/kicad/t-modem/t-modem.kicad_pcb
OUT=hardware/fab/gerbers
mkdir -p "$OUT"

kicad-cli pcb drc --refill-zones --save-board --format report \
  --output hardware/fab/drc-report.txt --units mm "$PCB"

kicad-cli pcb export gerbers -o "$OUT/" \
  --layers "F.Cu,B.Cu,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts" "$PCB"

kicad-cli pcb export drill -o "$OUT/" "$PCB"
```

## GUI

File → Fabrication Outputs → Gerbers (+ Drill Files). Match layer set above. Zip `gerbers/` for the fab house.

## Board

| Item | Value |
|------|-------|
| Size | **190 × 110 mm** (grown from 160×100 for courtyard/spacing §0.26) |
| Thickness | 1.6 mm |
| Layers | 2 |
| Finish | operator choice (HASL/ENIG) |

Review DRC before ordering. **2026-07-21:** auto-router + stitches — **6 unconnected** (mostly GND pour islands), **4 shorts** (B.Cu 3V3/I2C, AF_RX vs I2C, LED_TXRX_N vs PTT_OC). **Route remaining in pcbnew** (~15 min) before fab.
