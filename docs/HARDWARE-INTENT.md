# Hardware intent

**Status:** active — aligned with **v0.25** hardware reference  
**AS-IS:** no support, no warranty · **standard reference only**

---

## Form factor

| Item | Intent / v0.25 |
|------|----------------|
| Shape | Classic **rectangle** |
| Outline | **190 × 110 mm** — [PCB-ASSEMBLY.md](PCB-ASSEMBLY.md) |
| PCB | 2-layer FR4; TH / 0805 |
| Front/rear | USB Type A · barrel 12 V · AF/PTT screw · 16×2 green LCD · LEDs |
| Fab | Easy fab; personal small-run OK |

---

## Electrical / host

| Item | Intent / v0.25 |
|------|----------------|
| USB | Type-A **receptacle**, device role |
| Power | **USB-only OK** (`D_OR2` → `+5V_OR`); barrel **12 V** + buck **optional** (on reference, not required); optional active hub or regulated **5 V** into USB/OR path — [SCHEMATIC.md](SCHEMATIC.md) Power rationale |
| MCU | Raspberry Pi Pico (RP2040) |
| Field flash | UF2 via USB (BOOTSEL) |
| Host protocol | Thin KISS + registers (**FW later**) |
| Modulation | AFSK 1200 + 2400 (**FW later**) |
| Display | HD44780 16×2 green preferred |

See [BOM.md](BOM.md) · [SCHEMATIC.md](SCHEMATIC.md).

---

## Radio-equipment support

| Do | Don't |
|----|-------|
| Function labels on screw terminal | Fake “supported radios” list |
| Mark pinouts TBD until verified | Invent connector pinouts |
| Prove RX before live TX when RF exists | Treat untested cables as features |

---

## Explicitly not this product

| Out | Reason |
|-----|--------|
| BayCom/based SER12 | Different product class |
| Albrecht PC-COM / soft-TNC UART clone | Not board modem with registers |
| Framing as BayCom replacement | Separate workstreams |

---

## Sources

| Claim | Rights-granting source | Local copy |
|-------|------------------------|------------|
| GPLv3 | https://www.gnu.org/licenses/gpl-3.0.html | `../LICENSE` |
| Pico | https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf | — |
