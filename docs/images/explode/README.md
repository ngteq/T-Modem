# Exploded assembly drawings (from KiCad PCB)

Teaching sequence for builders — **2D top view** exported from gold
`hardware/kicad/t-modem/t-modem.kicad_pcb` (not mechanical CAD / not 3D).

Front edge (USB / DC / BOOTSEL) is at the **bottom** of each image.

Regenerate explode only: `python3 hardware/kicad/t-modem/scripts/render_docs_images.py --explode`  
Repo-root complete (assembled 3D): default `python3 …/render_docs_images.py` (does not rewrite this set).

| # | File | Topic |
|---|------|-------|
| 1 | [t-modem-explode-01-board-outline.png](t-modem-explode-01-board-outline.png) | Board outline · M3 |
| 2 | [t-modem-explode-02-pico.png](t-modem-explode-02-pico.png) | Raspberry Pi Pico |
| 3 | [t-modem-explode-03-modem-socket.png](t-modem-explode-03-modem-socket.png) | DIP-16 socket · TCM3105 |
| 4 | [t-modem-explode-04-crystal.png](t-modem-explode-04-crystal.png) | Crystal · load caps |
| 5 | [t-modem-explode-05-radio-af.png](t-modem-explode-05-radio-af.png) | J_AF radio AF/PTT |
| 6 | [t-modem-explode-06-lcd-i2c.png](t-modem-explode-06-lcd-i2c.png) | LCD I²C · level shift |
| 7 | [t-modem-explode-07-usb.png](t-modem-explode-07-usb.png) | USB Path B |
| 8 | [t-modem-explode-08-straps-leds.png](t-modem-explode-08-straps-leds.png) | Straps · LEDs · trimmers |
| 9 | [t-modem-explode-09-power-dc.png](t-modem-explode-09-power-dc.png) | 12 V · buck · OR-ing |
| 10 | [t-modem-explode-10-complete-stack.png](t-modem-explode-10-complete-stack.png) | Complete stack |

PNG · 1536×1024 · branch **`c12s24`** · companion (assembled 3D with Pico): repo-root [`t-modem-c12s24-complete.png`](../../../t-modem-c12s24-complete.png).
