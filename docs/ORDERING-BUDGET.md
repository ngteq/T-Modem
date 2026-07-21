# Ordering — budget / hobby value (v0.25)

**Goal:** **best value for money** — socketed, through-hole, hand-solderable by anyone who can solder reasonably well.  
**AS-IS:** no support, no warranty · **standard reference only**  
**Not a price quote:** check live shop prices; prefer in-stock commodity.

Companion: [BOM.md](BOM.md) · [`../hardware/bom/BOM.csv`](../hardware/bom/BOM.csv)

---

## Sourcing rules (cheap but sane)

| Do | Don't |
|----|-------|
| Generic **16-pin DIP socket** + insert modem IC | Solder TCM3105/MX614 pins straight into the board |
| **Pico H** or bare Pico + cheap male pins into **female** 2.54 mm sockets | Hand-solder RP2040 BGA/QFN |
| Commodity **16×2 green HD44780** LCD module (many €-range clones with pin header) | Expensive industrial TFT as default |
| **BSS138-class 4-ch I²C level shifter** when using a **5 V** LCD1602 I²C backpack on Pico **3.3 V** | Direct 5 V I²C to Pico GPIO; TFT-specific shifter kits |
| Pre-made **12 V→5 V buck module** (MP1584 / LM2596 class) on pin headers | Designing a discrete SOIC buck from scratch for first build |
| TH resistor/LED/diode assortments | Fine-pitch 0402 as hobby default |
| USB-A **through-hole** receptacle + 5.5×2.1 barrel from hobby catalogues | Exotic connectors |

Shops (examples, not exclusive): Reichelt, Conrad, DigiKey/Mouser value lines, reputable Pico distributors. Verify counterfeit risk on NOS modem ICs (TCM3105).

---

## Suggested buy list (classes)

| # | Item | Qty | Cheap class | Socket / note |
|---|------|-----|-------------|---------------|
| 1 | Raspberry Pi Pico **H** (or Pico + pin headers) | 1 | Official / clone with headers | Plugs into female 1×20×2 |
| 2 | Female header 2.54 mm 1×20 | 2 | Generic | Pico socket |
| 3 | 16×2 LCD **green backlight** HD44780 | 1 | Module with pin row | Female 1×16 header |
| 4 | Female header 1×16 2.54 mm | 1 | Generic | LCD socket |
| 5 | **4-ch bidirectional level converter** BSS138 / I²C IIC | **5** | Hobby module ~15×13 mm, pin headers | **OK / preferred** — LCD1602 **5 V I²C backpack** ↔ Pico **3.3 V**; **LV=3.3 V** · **HV=5 V** · **GND** common — **not** for TFT |
| 6 | 16-pin DIP socket 0.3″ | 1 | Generic / turned-pin if budget allows | Modem IC |
| 7 | TCM3105 DIP **or** MX614P-class | 1 | Verify stock / NOS carefully | Insert in socket only |
| 8 | Crystal 4.433619 MHz HC-49 | 1 | Commodity | Confirm vs modem datasheet |
| 9 | Buck module 12→5 V ≥0.5 A | 1 | MP1584 / LM2596 module | Header pins |
| 10 | USB Type-A receptacle TH | 1 | Commodity | — |
| 11 | Barrel jack 5.5×2.1 centre+ | 1 | Commodity | — |
| 12 | Screw terminal 4-pin 5.08 mm | 1 | Commodity | AF/PTT labels |
| 13 | 1N5819 Schottky | 2 | TH | OR diodes |
| 14 | 1N4148 | 2 | TH | Clamp |
| 15 | 2N2222A or BC547 | 1 | TO-92 | PTT |
| 16 | Resistors 0.25 W (330R, 1k, 4.7k, 10k, …) | pack | Assortment OK | TH |
| 17 | Caps 100 nF + 100 µF electrolytic | pack | Commodity | TH / radial |
| 18 | Trimmer 10 kΩ TH | 2–3 | Carbon / cermet | Contrast + TX level |
| 19 | LED 3 mm + tactile switch | 4+1 | Commodity | — |
| 20 | 12 V wall wart 5.5×2.1 ≥0.5 A | 1 | Commodity centre+ | Off-board |
| 21 | USB-A cable (PC → T-Modem) | 1 | Commodity | Device port |

Exact DigiKey/Reichelt order codes = **TBD at cart time** (stock moves). Prefer parts that stay in catalogues for years.

---

## Cost realism (order of magnitude, not a quote)

Excluding PCB fab and NOS modem premium: a careful hobby cart for sockets + Pico + LCD + buck + connectors + passives is typically in the **low tens of €** region at EU hobby shops; TCM3105/MX614 availability can dominate cost if only broker stock exists. Soft-AFSK-only (no modem IC) is a later cost escape hatch (firmware) — not the v0.25 preferred PHY.

---

## Sources

| Claim | Rights-granting source | Local copy |
|-------|------------------------|------------|
| Pico / RP2040 | https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf | — |
| TCM3105 mirror | https://www.qsl.net/o/on7pc/datasheet/ic/TCM3105.pdf | — |
| GPLv3 | https://www.gnu.org/licenses/gpl-3.0.html | `../LICENSE` |
