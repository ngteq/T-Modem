# Schematic / netlist — v0.25

**Status:** complete **electrical + PCB** for first fab — Gerbers generatable from KiCad project  
**KiCad:** [`../hardware/kicad/t-modem/`](../hardware/kicad/t-modem/) · fab [`../hardware/fab/`](../hardware/fab/) (open in KiCad ≥8 / 10)  
**Board:** **190 × 110 mm** · Path B USB + I²C LCD **settled** for v0.25 complete PCB  
**AS-IS:** no support, no warranty · **standard reference only**

This document is the **authoritative netlist** for v0.25. Gerbers are exportable; operator must clear remaining DRC (signal finish) before fab order. No measured radio performance claimed.

---

## Block diagram

```text
  12 V barrel ──► buck/LDO ──► +5V ──┬── Pico VSYS (+ Schottky OR with VBUS)
  USB-A (device) ── D+/D−/GND/VBUS ──┤── Pico USB · UF2 BOOTSEL
                                    ├── TCM3105 VDD (5 V)
                                    └── LCD backlight / logic (5 V or 3.3 V module)

  J_AF AF_RX ── AC ──► TCM3105 RXA ── RXD/CDT ──► Pico GPIO
  Pico GPIO TXD ──► TCM3105 TXD ── TXA ── pot ── AC ──► J_AF AF_TX
  Pico GPIO PTT ──► NPN OC ──► J_AF PTT
  Pico ── parallel ──► 16×2 green LCD
  Pico I²C (3.3 V) ── U_LVL (LV/HV) ──► 5 V I²C backpack ──► LCD1602
```

**Not BayCom/SER12:** no DTR bitclock, no RTS-as-PHY, no TXD charge-pump modem. Host USB is CDC/KISS later; air path is TCM3105-class FSK + MCU.

---

## Rails

| Net | Source | Notes |
|-----|--------|-------|
| `VIN_12` | J_DC tip (centre +) | 9–14 V class; silk **12 V CENTRE +** — **optional** path (see Power rationale) |
| `GND` | J_DC sleeve · USB GND · analog GND star near U_MODEM | Single ground plane preferred |
| `+5V` | U_REG out | After polyfuse F1 — only when barrel+buck fitted |
| `VBUS` | J_USB VBUS | Through D_OR2 into `+5V_OR`; USB-only supply uses this leg |
| `+5V_OR` | cathode junction D_OR1 (from U_REG) + D_OR2 (from VBUS) | Feeds Pico `VSYS`, TCM3105 `VDD`, LCD — **either** OR leg sufficient |
| `3V3` | Pico on-board 3.3 V | GPIO logic; with 5 V LCD I²C backpack use **U_LVL** — **LV=`3V3`** · **HV=`+5V_OR`** · **GND** common (BSS138-class; not for TFT) |

---

## Connectors

### J_DC — barrel 5.5×2.1 mm centre-positive

| Pin | Net |
|-----|-----|
| Tip | `VIN_12` |
| Sleeve | `GND` |

### J_USB — USB Type-A receptacle (device toward PC)

| Pin | Net | Pico (U1) |
|-----|-----|-----------|
| VBUS | `VBUS` | — (OR diodes only) |
| D− | `USB_DM` | Pico pin **USB_DM** (board USB pads / GP) |
| D+ | `USB_DP` | Pico pin **USB_DP** |
| GND | `GND` | GND |
| Shield | `GND` | via 0 Ω or direct |

**Path B (settled for v0.25 complete PCB):** Type-A receptacle on board. VBUS → Schottky OR (`D_OR2`) into `+5V_OR`. D+/D−/GND (+ VBUS) also to 4-pin header `J_USB_PICO` — silk **to Pico Micro-USB cable**. Short cable from header to Pico Micro-USB for data + UF2.

PC sees one USB device on the Type-A receptacle; UF2 works when BOOTSEL held at plug-in (board SW1 → `TP_BOOTSEL` flying lead to Pico BOOTSEL pad if needed).

### J_AF — 4-pin screw 5.08 mm (function labels only)

| Pin silk | Net | Role |
|----------|-----|------|
| `AF_TX` | `AF_TX` | Audio to radio mic / TX AF |
| `AF_RX` | `AF_RX` | Audio from radio speaker / RX AF |
| `PTT` | `PTT_OC` | Open-collector to radio PTT |
| `GND` | `GND` | Common |

No mic pinout map claimed.

---

## Power rationale

| Path | Role | Required to run? |
|------|------|------------------|
| **USB → `D_OR2` → `+5V_OR`** | Full board supply from VBUS | **No** barrel needed — **USB-only is a complete alternative** |
| **`J_DC` + `U_REG` → `D_OR1` → `+5V_OR`** | 12 V barrel + buck → 5 V | **Not required** for operation; **planned and on the reference** for radio/station wall-warts and future mods that want PSU headroom |
| USB host / **active hub** / stronger USB 5 V | Same `VBUS` → `D_OR2` leg | Hub **optional** (budget ≪ host port limit; use hub when preferred) |
| Optional **5 V** regulated PSU | Into the **USB / OR 5 V domain** | **Planned option** — feed regulated 5 V at the `VBUS` node (before `D_OR2`) or an auxiliary wire to the `+5V_OR` side of the OR; **no second barrel class** on the v0.25 BOM (only `J_DC` 12 V + `J_USB`) |

**KISS:** one OR rail (`+5V_OR`). Either diode leg can power the board. Do **not** put 12 V on Pico / modem / LCD rails.

---

## Power path

| Ref | Connection |
|-----|------------|
| J_DC tip | `VIN_12` (optional inlet) |
| C_IN 100 µF/25 V | `VIN_12`–`GND` |
| U_REG IN | `VIN_12`; U_REG GND → `GND`; U_REG OUT → `+5V_REG` |
| F1 PTC | `+5V_REG` → `+5V` |
| D_OR1 Schottky | anode `+5V` → cathode `+5V_OR` |
| D_OR2 Schottky | anode `VBUS` → cathode `+5V_OR` |
| C_BULK 100 µF | `+5V_OR`–`GND` |
| C_BYP×N 100 nF | each IC VDD–GND |

Pico: `VSYS` ← `+5V_OR`; `GND` ← `GND`. Do **not** feed 12 V into Pico. USB-only: leave `J_DC` / `U_REG` unpowered; `D_OR2` alone supplies `+5V_OR`.

---

## MCU — U1 Raspberry Pi Pico (RP2040)

| Pico net / pin (board edge) | Net | Role |
|-----------------------------|-----|------|
| VSYS | `+5V_OR` | Power |
| GND | `GND` | Ground |
| 3V3 | `3V3` | Sense / LCD if 3.3 V module |
| BOOTSEL | SW1 → `GND` | UF2 entry |
| GP0 | `I2C_SDA_3V3` | → U_LVL LV → LCD backpack SDA |
| GP1 | `I2C_SCL_3V3` | → U_LVL LV → LCD backpack SCL |
| GP6 | `MODEM_TXD` | → TCM3105 TXD |
| GP7 | `MODEM_RXD` | ← TCM3105 RXD |
| GP8 | `MODEM_CDT` | ← TCM3105 CDT (DCD LED / FW) |
| GP9 | `PTT_DRV` | → R_PTT → Q1 base |
| GP10 | `LED_PTT` | |
| GP11 | `LED_DCD` | |
| GP12 | `LED_TXRX` | |
| VSYS | `+5V_OR` | Power |
| BOOTSEL | SW1 / TP_BOOTSEL | UF2 entry |
| USB (Path B) | via `J_USB_PICO` cable | Type-A → Pico Micro-USB |

LED_PWR: hardwire anode to `+5V_OR` via R_LED, cathode to GND (always-on when powered).

---

## Modem IC — U_MODEM TCM3105 (16-pin DIP/SO class)

Bell 202 **1200** AFSK PHY. **2400** = firmware DSP on Pico (later) — not TCM3105 headline rate.

| Pin | Name | Net / strap |
|-----|------|-------------|
| 1 | VDD | `+5V_OR` |
| 2 | CLK | NC or test pad |
| 3 | CDT | `MODEM_CDT` |
| 4 | RXA | `RXA` (from AF_RX path) |
| 5 | TRS | `GND` (Bell 202 class — confirm per datasheet mode table at fab) |
| 6 | NC | NC |
| 7 | RXB | RV_RXB wiper (bias pot) or datasheet recommended R network |
| 8 | RXD | `MODEM_RXD` |
| 9 | VSS | `GND` |
| 10 | CDL | RV_CDL / R network (carrier detect level) |
| 11 | TXA | `TXA` |
| 12 | TXR2 | `R_TXR2` 0 Ω → `+5V_OR` default (Bell 202 1200) — silk **confirm datasheet** |
| 13 | TXR1 | `R_TXR1` 0 Ω → `GND` default (Bell 202 1200) — silk **confirm datasheet** |
| 14 | TXD | `MODEM_TXD` |
| 15 | OSC1 | Y1 4.4336 MHz crystal (or datasheet Xtal) |
| 16 | OSC2 | Y1 other leg + load caps |

**Longevity:** TCM3105 is a **legacy** TI/MX-COM-era part — often **NOS / broker**. Prefer in-stock DIP/SO when ordering; if unavailable, substitute **MX614**-class Bell-202 modem IC (same role nets) or document MCU soft-AFSK only — mark substitute in BOM.

Sources: TCM3105 datasheet (TI historical) — e.g. https://www.qsl.net/o/on7pc/datasheet/ic/TCM3105.pdf

### Analog IF around U_MODEM

| From | Via | To |
|------|-----|-----|
| `AF_RX` | C_RX 100 nF · optional R pad | `RXA` |
| `TXA` | RV1 10 kΩ (TX level) · C_TX 100 nF · R_PAD | `AF_TX` |
| Clamp | D_PROT 1N4148 to rails | `AF_RX` / `AF_TX` as needed |

---

## PTT

| From | Via | To |
|------|-----|-----|
| `PTT_DRV` | R_PTT 4.7 kΩ | Q1 base (2N2222A) |
| Q1 emitter | — | `GND` |
| Q1 collector | — | `PTT_OC` → J_AF `PTT` |
| Optional | LED_PTT driven from `PTT_DRV` | |

---

## Display — DSP1 16×2 HD44780 green

| LCD pin (typical) | Net |
|-------------------|-----|
| VSS | `GND` |
| VDD | `+5V_OR` (or `3V3` if module rated) |
| V0 | RV2 contrast wiper |
| RS, E, D4–D7 | as MCU table (or backpack I²C on GP0/GP1 via **U_LVL**) |
| A / K backlight | `+5V_OR` via R_BL · `GND` — **green** LED backlight |

### U_LVL — I²C level shifter (when using 5 V backpack)

| Side | Net | Note |
|------|-----|------|
| LV | `3V3` | Pico side |
| HV | `+5V_OR` | LCD1602 green I²C backpack (5 V) |
| GND | `GND` | Common |
| SDA/SCL | GP0/GP1 ↔ backpack | Bidirectional BSS138-class module |

**Not** for TFT. Parallel 4-bit LCD on 5 V with series resistors or 3.3 V–tolerant module may omit U_LVL.

TFT alt: not default — see [HARDWARE-INTENT.md](HARDWARE-INTENT.md) (optional; longevity weaker than character LCD).

---

## Fabrication contract

| Deliverable | v0.25 |
|-------------|-------|
| Netlist + BOM + **190×110** PCB (KiCad) | **Yes** — complete TH reference |
| USB Path B + I²C LCD | **Settled** |
| Gerbers generatable (`kicad-cli` / GUI) | **Yes** — see `hardware/fab/` |
| DRC zero / production-verified | **Not claimed** — finish signal tracks; clear DRC before order |
| Firmware | Placeholder — nets reserved |

---

## Sources

| Claim | Rights-granting source | Local copy |
|-------|------------------------|------------|
| TCM3105 FSK modem (historical TI datasheet mirrors) | https://www.qsl.net/o/on7pc/datasheet/ic/TCM3105.pdf | — |
| RP2040 / Pico | https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf · https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf | — |
| HD44780U | https://cdn.sparkfun.com/assets/9/5/f/7/b/HD44780.pdf | — |
| GPLv3 | https://www.gnu.org/licenses/gpl-3.0.html | `../LICENSE` |
