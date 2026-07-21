# Release v0.25 — hardware-only standard reference

**Version:** 0.25  
**Git tag:** `v0.25`  
**Date:** 2026-07-20 · **docs refresh:** 2026-07-21  
**License:** GNU GPLv3 · **AS-IS** — no support, no warranty  
**Scope:** **standard reference only**

**Verification:** [v0.25-VERIFICATION.md](v0.25-VERIFICATION.md) · **Baseline:** [HARDWARE-BASELINE.md](HARDWARE-BASELINE.md)

**Operator path:** build this hardware **as-is** toward **v1.0**; firmware/software **after** the build. No redesign for preference.

---

## What this release is

A **hardware reference** package (solderable / finish-in-KiCad):

- Preferred commodity parts (BOM) with honest **TBD** where MPN not yet picked from stock
- Electrical intent: **USB and/or 12 V** · USB Type-A device · green LCD · Pico UF2 · TCM3105-class AFSK IF
- Rectangle PCB outline **190 × 110 mm** + connector placement + assembly notes
- KiCad project with complete TH board (DRC cleanup before fab order)

## What this release is not

| Not included | Note |
|--------------|------|
| Firmware | [../firmware/README.md](../firmware/README.md) placeholder |
| Host software / MAX25 plugin | [../software/README.md](../software/README.md) placeholder |
| Radio mic pinouts | Never invented — screw terminals labeled by function only |
| BayCom / SER12 / PC-COM | Out of product scope |
| Custom / commercial SKU lines | Not T-Modem |
| Verified fab Gerbers | Operator clears DRC before order |

---

## Deliverable map

| Artifact | Path |
|----------|------|
| VERSION | [`../VERSION`](../VERSION) → `0.25` |
| Verification | [v0.25-VERIFICATION.md](v0.25-VERIFICATION.md) |
| Baseline | [HARDWARE-BASELINE.md](HARDWARE-BASELINE.md) |
| BOM (human) | [BOM.md](BOM.md) |
| BOM (CSV) | [`../hardware/bom/BOM.csv`](../hardware/bom/BOM.csv) |
| Schematic / netlist | [SCHEMATIC.md](SCHEMATIC.md) |
| PCB / assembly | [PCB-ASSEMBLY.md](PCB-ASSEMBLY.md) · [PCB-LAYOUT.md](PCB-LAYOUT.md) |
| KiCad project | [`../hardware/kicad/t-modem/`](../hardware/kicad/t-modem/) |
| Mechanical outline | [`../hardware/mechanical/outline-190x110.md`](../hardware/mechanical/outline-190x110.md) |
| Fab notes | [`../hardware/fab/`](../hardware/fab/) |

---

## Electrical readiness (HW now / FW later)

| Subsystem | v0.25 hardware | Firmware later |
|-----------|----------------|----------------|
| USB → `+5V_OR` (USB-only OK) | Designed | — |
| Optional 12 V barrel → buck → `+5V_OR` | On reference, not required | — |
| USB Type-A receptacle (device) | Path B to Pico | CDC/ACM + KISS |
| UF2 / BOOTSEL field flash | BOOTSEL + USB path | Application image |
| 16×2 green LCD (HD44780) | I²C default (+ U_LVL) | UI / status |
| TCM3105-class AFSK 1200 + AF/PTT | In netlist | Drive TXD/RXD/CDT/PTT |
| AFSK 2400 | MCU pins reserved | Soft-AFSK / DSP |
| Radio connector map | Function labels only | — |

---

## Sources

| Claim | Rights-granting source | Local copy |
|-------|------------------------|------------|
| GPLv3 | https://www.gnu.org/licenses/gpl-3.0.html | `../LICENSE` |
| RP2040 / Pico | https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf · https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf | — |
| TCM3105 | https://www.qsl.net/o/on7pc/datasheet/ic/TCM3105.pdf | — |
| HD44780U | https://cdn.sparkfun.com/assets/9/5/f/7/b/HD44780.pdf | — |
