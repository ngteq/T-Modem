# Bill of materials — v0.25 (hardware reference)

**Status:** assemble-ready **candidates** — prefer in-production commodity; mark **TBD** where MPN not yet picked from stock  
**AS-IS:** no support, no warranty · **standard reference only**  
**Hobby-friendly:** **sockets + through-hole** — hand soldering for anyone who can solder reasonably well  
**Budget:** prefer **cheap commodity** modules/sockets (see [ORDERING-BUDGET.md](ORDERING-BUDGET.md)) — best value, not boutique parts  
**CSV:** [`../hardware/bom/BOM.csv`](../hardware/bom/BOM.csv)

Do **not** invent radio mic pinouts. BayCom/SER12 parts are forbidden.

---

## Hobby-friendly mounting (required for reference)

| Ref | Qty | Description | Preferred candidate | Role | Status |
|-----|-----|-------------|---------------------|------|--------|
| SKT_MODEM | 1 | **16-pin DIP socket** 0.3″ (7.62 mm) | **Cheap generic** DIP socket OK (turned-pin nicer but not required) | Holds U_MODEM — **do not solder IC pins directly** | **Preferred** |
| HDR_PICO_F | 2 | **Female** 1×20 header 2.54 mm | Generic strip / break-to-length | Socket for Pico H | **Preferred** |
| HDR_LCD_F | 1 | **Female** 1×16 (or dual-row per module) 2.54 mm | Generic | Socket / header for LCD | **Preferred** |
| HDR_REG | 1 | Header for buck module | 2.54 mm male pins on module | Plug-in **cheap** 12 V→5 V module | Candidate |

Default passives: **0.25 W through-hole**. SMD 0805 only as optional alternate, not the hobby default.

---

## Preferred MCU path (settled for v0.25 reference)

| Ref | Qty | Description | Preferred candidate | Role | Status |
|-----|-----|-------------|---------------------|------|--------|
| U1 | 1 | MCU module, native USB device, UF2 field flash | **Raspberry Pi Pico H** (RP2040, **headers fitted**) — plug into HDR_PICO_F | Firmware host · USB KISS later · 2400 DSP later | **Preferred** — [Pico datasheet](https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf) · [RP2040](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf) |
| SW1 | 1 | Momentary N.O. **TH** | DigiKey-class 6×6 mm tactile (Omron B3F / TE — **MPN TBD** in-stock) | BOOTSEL → GND | Candidate |
| — | — | Alt MCU (not default) | ESP32-S3 module native USB on headers | Only if Pico unavailable | Optional alt |

**Field flash:** hold BOOTSEL, plug USB into PC → UF2 mass-storage (ROM). No separate programmer for normal updates.

---

## Modem PHY (required for “modem” milestone)

| Ref | Qty | Description | Preferred candidate | Role | Status |
|-----|-----|-------------|---------------------|------|--------|
| U_MODEM | 1 | Bell-202 FSK modem IC **DIP-16** | **TCM3105** DIP-16 (or MX614P-class) — insert into **SKT_MODEM** | AFSK **1200** TXA/RXA · RXD/TXD/CDT to Pico | **Preferred class** — [datasheet mirror](https://www.qsl.net/o/on7pc/datasheet/ic/TCM3105.pdf) · longevity: often NOS — verify stock |
| Y1 | 1 | Crystal | **4.4336 MHz** class (confirm vs datasheet) | TCM3105 OSC | Candidate |
| — | 0/1 | Alt if TCM3105 unobtainable | **MX614**-class Bell-202 modem | Same net roles | Optional |
| — | — | 2400 baud | Pico DSP / soft-AFSK (firmware later) | Not TCM3105 headline | TBD FW |

**Longevity (honest):** TCM3105 is **legacy / often NOS**. Prefer active DigiKey/Mouser qty when picking MPN; if none, use MX614-class or document soft-AFSK-only revision. **Not** BayCom SER12 charge-pump.

Netlist: [SCHEMATIC.md](SCHEMATIC.md).

---

## Display (preferred)

| Ref | Qty | Description | Preferred candidate | Status |
|-----|-----|-------------|---------------------|--------|
| DSP1 | 1 | 16×2 HD44780-compatible character LCD, **green LED backlight** | Commodity **16×2 green** (Newhaven / Displaytech / Adafruit-class). Prefer named OEM on DigiKey/Mouser — exact glass MPN = **TBD** after stock pick | **Preferred class** |
| U2 | 0/1 | Optional PCF8574 I²C backpack (often **5 V**) | Common backpack modules | Optional |
| U_LVL | 0/1 | 4-ch bidirectional BSS138 / I²C level shifter (~15×13 mm, headers) | **Operator-approved OK** — **LV=3.3 V** (Pico) · **HV=5 V** (LCD I²C) · **GND** common; required with 5 V backpack; **not** TFT | **Preferred** (I²C path) |
| RV2 | 1 | 10 kΩ trimmer | Bourns 3296 / carbon 10k TH — **MPN TBD** | Contrast |

Controller: Hitachi **HD44780U** — [PDF](https://cdn.sparkfun.com/assets/9/5/f/7/b/HD44780.pdf).

TFT (ST7735/ILI9341) = optional alt only; longevity weaker — not default.

---

## USB and power

| Ref | Qty | Description | Preferred candidate | Status |
|-----|-----|-------------|---------------------|--------|
| J_USB | 1 | USB **Type-A receptacle**, through-hole, USB 2.0 FS | DigiKey [USB connectors](https://www.digikey.com/en/products/filter/usb-dvi-hdmi-connectors/308) — Amphenol / TE / Molex Type-A TH — **pick one in-stock MPN at order** | Class settled · MPN **TBD** at order |
| J_DC | 1 | DC barrel **5.5×2.1 mm**, centre-**positive** (optional path) | DigiKey [barrel](https://www.digikey.com/en/products/filter/barrel-power-connectors/439) — CUI **PJ-002A** class | Size settled; not required for USB-only |
| U_REG | 1 | **12 V → 5 V**, ≥500 mA | Prefer **buck** (MP1584EN class) or AMS1117-5.0 (watch heat) | Candidate |
| D_OR1, D_OR2 | 2 | Schottky ≥1 A | **1N5819** / SS14 | OR USB ↔ 5 V; no host backfeed |
| C_BULK / C_IN | 1+1 | 100 µF electrolytics | Commodity | Bulk |
| C_BYP* | 8+ | 100 nF | 0805 or TH | Decoupling |
| F1 | 1 | PTC ~500 mA hold | DigiKey PTC class | Fault limit |
| — | 1 | Wall wart **12 V** centre-positive 5.5×2.1 ≥0.5 A | Commodity | Not on PCB |

Silk: **12 V CENTRE +** · **USB DEVICE**.

---

## Analog IF / indicators

| Ref | Qty | Description | Preferred candidate | Status |
|-----|-----|-------------|---------------------|--------|
| J_AF | 1 | 4-pin screw 5.08 mm | Phoenix / Wurth / generic — **MPN TBD** | `AF_TX` · `AF_RX` · `PTT` · `GND` only |
| Q1 | 1 | NPN OC PTT | **2N2222A** / **BC547** | Open-collector |
| R_PTT | 1 | 4.7 kΩ | Commodity | Base drive |
| RV1 | 1 | 10 kΩ trimmer | Commodity | TX AF level |
| C_AC* | 2 | 100 nF | Commodity | AF AC couple |
| R_PAD* | 2–4 | 100 Ω … 10 kΩ | Commodity | TX pad / bias |
| D_PROT | 2 | 1N4148 | Commodity | Clamp |
| LED1–4 | 4 | 3 mm LED | Green preferred for PWR | PWR, PTT, DCD, TX/RX |
| R_LED* | 4 | 330 Ω–1 kΩ | Commodity | LED series |

---

## Explicitly out of BOM

| Forbidden | Reason |
|-----------|--------|
| SER12 DTR/RTS/TXD charge-pump as PHY | BayCom/PC-COM — out of scope |
| Programmer-only flash as sole update | Violates USB field-flash Eckpunkt |
| Invented radio mic adapters as “supported” | No verified pinouts |

---

## Sources

| Claim | Rights-granting source | Local copy |
|-------|------------------------|------------|
| Pico / RP2040 | https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf · https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf | — |
| TCM3105 | https://www.qsl.net/o/on7pc/datasheet/ic/TCM3105.pdf | — |
| HD44780U | https://cdn.sparkfun.com/assets/9/5/f/7/b/HD44780.pdf | — |
| DigiKey USB / barrel classes | https://www.digikey.com/en/products/filter/usb-dvi-hdmi-connectors/308 · https://www.digikey.com/en/products/filter/barrel-power-connectors/439 | — |
| GPLv3 | https://www.gnu.org/licenses/gpl-3.0.html | `../LICENSE` |
