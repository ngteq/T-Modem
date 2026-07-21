# PCB layout policy — safe · stable · performant

**Status:** settled 2026-07-21 · **complete PCB delivered** (v0.25)  
**Baseline:** tag **`v0.25`** · outline **190 × 110 mm** (larger OK for hand soldering)  
**AS-IS** · **standard reference only** · GPLv3

Policy: complete PCB; prefer larger over fiddly; finish DRC before fab.  
**Always:** **Safe · Stable · Performant · KISS**.

---

## Rule

Implement the **complete** T-Modem PCB for **safe**, **stable**, and **performant** operation under **KISS**. Prefer a **somewhat larger** board over a **too small / fiddly** layout.

| Pillar | Requirement |
|--------|-------------|
| **Safe** | Clearances, fuse/OR path, readable polarity silk, serviceable connectors |
| **Stable** | Solid GND pour (B.Cu), short analog/crystal paths, DIP sockets and headers |
| **Performant** | USB Path B discipline; AF/PTT away from USB/digital; adequate power copper |
| **KISS** | One layout path; no parallel mystery boards |
| **Larger > fiddly** | **190 × 110 mm** so hand soldering (TH) stays comfortable |

## Delivered (v0.25)

| Item | Location |
|------|----------|
| KiCad 10 project | `hardware/kicad/t-modem/` |
| Regenerator (no pcbnew) | `hardware/kicad/t-modem/scripts/generate_board.py` |
| Gerber export notes + sample | `hardware/fab/` |
| Outline | `hardware/mechanical/outline-190x110.md` (earlier 160×100 / 100×80 drafts superseded) |

**Routing honesty (2026-07-21):** `generate_board.py` collision-aware manhattan + A* + B.Cu edge fallback; **no `ignore_used` shorts**. GND = **B.Cu pour**; **+5V_OR** = **F.Cu pour** (tracks skipped). **Intentional:** `LCD_VO` = RV2 wiper only (no LCD module pin); **BOOTSEL** = SW1 ↔ TP_BOOTSEL only — **flying lead** to Pico BOOTSEL test pad. Clear remaining DRC before fab.

## vs hardware baseline

Allowed: finish KiCad, enlarge outline for assembly/safety, layout fixes.  
Settled (do not swap for taste): MCU / modem PHY / display **class** and connector **class** (USB-A Path B, optional 12 V barrel, I²C LCD default).

Companion: [PCB-ASSEMBLY.md](PCB-ASSEMBLY.md) · [HARDWARE-BASELINE.md](HARDWARE-BASELINE.md) · [SCHEMATIC.md](SCHEMATIC.md).
