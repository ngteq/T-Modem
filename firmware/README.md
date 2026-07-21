# Firmware — placeholder (v0.25)

**Status:** **no firmware** in this release.

v0.25 is a **hardware-only** standard reference (BOM, schematic netlist, PCB outline/placement). Application firmware (register file, KISS, AFSK 1200/2400, LCD UI, UF2 image) is **out of scope** for tag `v0.25`.

| Later (not v0.25) | Notes |
|-------------------|-------|
| UF2 / USB CDC | RP2040 ROM UF2 already provides field flash path once an image exists |
| KISS + registers | Board owns PHY; host owns AX.25 |
| AFSK | TCM3105 path for 1200; 2400 via MCU DSP |

**AS-IS:** no support, no warranty.
