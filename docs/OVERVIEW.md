# T-Modem overview

**Status:** active — settled facts  
**Version:** **0.25** (hardware-only milestone)  
**Name:** **T-Modem** = **Terminal-Modem**  
**PHY mark:** **T-Modem-c12s24** — chip **1200** + software **2400**  
**License:** GNU GPLv3 (repo root `LICENSE`)  
**Project intent:** non-profit / non-commercial community hardware under GPLv3

**AS-IS:** provided **as-is** — **no support**, **no warranty** of any kind.

**Scope:** **standard reference only** — derivatives / custom lines = separate projects, not T-Modem.

| PHY | Owner |
|-----|-------|
| **1200** AFSK Bell-202 | **Chip** — TCM3105-class (`U_MODEM`) |
| **2400** AFSK | **Software** — Pico RP2040 firmware (**after** HW prototype) |

---

## What it is

T-Modem is a **real board modem** with **registers and firmware** on the device (**firmware not in v0.25**). The host (for example MAX25-Stack) owns AX.25 and higher services. The board provides AFSK PHY, a modem register file, and a thin KISS bridge — a transparent half-TNC / modem+TNC mix.

| Settled | Fact |
|---------|------|
| Product home | This repository = **standard reference** |
| v0.25 | Hardware package (BOM / schematic intent / PCB notes / KiCad skeleton) |
| Beyond reference | Custom / commercial SKU variants → **separate projects** |
| MAX25 role | **Thin plugin only** later |
| Modulation | **c12s24:** AFSK **1200** (chip) + **2400** (Pico FW later) — one unit |
| Host interface | USB 2.0 **Type A receptacle**; no active hub required |
| Power | **USB-only OK**; optional barrel **12 V** + buck on reference; optional active hub / **5 V** into USB/OR — [SCHEMATIC.md](SCHEMATIC.md) |
| Display | 16×2 HD44780 **green** preferred |
| MCU | Raspberry Pi Pico (RP2040), UF2 USB flash — host + **s24** DSP later |
| Form | Rectangle **190 × 110 mm** (v0.25) |
| Not this product | BayCom/based · SER12 · PC-COM soft-TNC · host UART bitbang modem |

---

## Layer split

| Layer | Owner |
|-------|-------|
| AX.25, digipeat, BBX/UI / services | Host (e.g. MAX25 / HyBBX) |
| KISS framing / thin cmds | Board firmware (**later**) |
| Modem registers | Board firmware (**later**) |
| AFSK 1200 / 2400 PHY | On-board (**FW later**) |
| AF TX/RX + PTT | Analog IF on board (**HW in v0.25**) |
| USB 2.0 device | Board (**HW in v0.25**; CDC profile **TBD**) |

---

## Radio equipment

**Operator lock:** radio equipment **must be supported** and remain **expandable**.

| Settled intent | Not claimed |
|----------------|-------------|
| Screw terminals: AF_TX, AF_RX, PTT, GND | Named radio model list |
| Expand after verification | Invented mic pinouts |

---

## TBD (explicit)

| Item | Status |
|------|--------|
| Exact connector MPNs at order | TBD — pick in-stock DigiKey/Mouser |
| Register map bytes | TBD (FW) |
| USB VID/PID / CDC details | TBD (FW) |
| Gerbers / DRC | TBD — clear DRC before fab order |
| Per-radio cable pinouts | TBD |

---

## Sources

| Claim | Rights-granting source | Local copy |
|-------|------------------------|------------|
| License GPLv3 | https://www.gnu.org/licenses/gpl-3.0.html | `LICENSE` |
| Pico / RP2040 | https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf | — |
