# Hardware baseline — path to v1.0

**Status:** settled 2026-07-20 · wording update 2026-07-21  
**Baseline:** git tag **`v0.25`**

| Phase | Fact |
|-------|------|
| **Hardware** | Design **settled** as v0.25 (BOM/sockets/TH, netlist, outline **190 × 110 mm**). No redesign for preference. |
| **Operator** | **Build** the reference → prove rails / assembly → hardware **v1.0** when the built unit matches. |
| **Software** | Firmware, host tools, MAX25 plugin — **after** the hardware build path. Placeholders until then. |
| **Allowed HW edits** | Only **blocking** fab/assembly errors proven on the bench; outline/spacing growth OK ([PCB-LAYOUT.md](PCB-LAYOUT.md)). |
| **PCB finish** | Complete place/route/Gerbers; prefer **larger** over fiddly — [PCB-LAYOUT.md](PCB-LAYOUT.md) |
| **Power** | USB-only is enough; 12 V barrel + buck **optional** but on the reference — [SCHEMATIC.md](SCHEMATIC.md) |

**AS-IS** · **standard reference only**. PCB policy: [PCB-LAYOUT.md](PCB-LAYOUT.md).

Former filename `HARDWARE-FREEZE.md` redirects here (same policy, clearer wording).
