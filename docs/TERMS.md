# T-Modem — technical terms & acronyms

**Branch:** **`main` only** (glossary index). Product docs live on **`c12s24`**.  
**AS-IS** · GPLv3 · standard reference only · English

Uncommon or project-specific technical terms. Everyday words (USB, PCB, GND) omitted unless used in a special sense here.

| Term | Meaning (this project) |
|------|-------------------------|
| **AF** | Audio frequency — TX/RX audio to/from the radio (not digital data) |
| **AFSK** | Audio Frequency-Shift Keying — tones carry bits over radio AF |
| **AS-IS** | No support and no warranty (project policy + GPLv3) |
| **AX.25** | Amateur packet-radio link layer; owned by the **host**, not this board |
| **Bell 202** | Classic 1200 baud AFSK tone pair (mark/space) used with TCM3105-class PHYs |
| **BOM** | Bill of materials |
| **BOOTSEL** | Pico boot-select: hold at USB plug-in → UF2 mass-storage |
| **buck** | Step-down DC/DC converter (here: optional 12 V → 5 V module) |
| **c12s24** | Product mark: **c12** = chip **1200** AFSK · **s24** = software **2400** |
| **CDC / ACM** | USB serial class profiles (host sees a virtual COM port) — firmware later |
| **CDT / CDL** | Carrier / squelch detect lines on the modem IC (naming varies by datasheet) |
| **courtyard** | Keep-out / assembly outline around a footprint |
| **DIP** | Dual in-line package (modem IC in socket) |
| **DRC** | Design Rule Check (KiCad) — clear before fab order |
| **DSP** | Digital signal processing — here: Pico firmware for 2400 AFSK later |
| **Edge.Cuts** | KiCad board outline layer |
| **Gerber** | Fabrication artwork set (copper, mask, silk, drill) — usually zipped |
| **HD44780** | Common character-LCD controller family (16×2 green preferred) |
| **I²C / I2C** | Two-wire bus (SDA/SCL) — default LCD path via backpack |
| **KISS** | (1) Keep It Simple, Stupid — design law · (2) serial framing for packet TNCs |
| **LCD1602** | Common 16×2 character LCD module size/class |
| **level shifter (U_LVL)** | BSS138-class module: Pico 3.3 V I²C ↔ 5 V LCD backpack |
| **MPN** | Manufacturer part number |
| **NOS** | New old stock — legacy parts (e.g. TCM3105) may only be NOS |
| **NPTH** | Non-plated through-hole |
| **OR (diode-OR)** | Schottky OR of supplies into one rail (`+5V_OR`) without host backfeed |
| **Path B** | USB Type-A on board + short cable to Pico Micro-USB (settled v0.25) |
| **PHY** | Physical layer — here AFSK modem chip / soft-AFSK |
| **Pico / RP2040** | Raspberry Pi Pico module / MCU — UF2 field flash |
| **pour / zone** | Copper fill (GND on B.Cu, `+5V_OR` on F.Cu in the reference) |
| **PTT** | Push-to-talk — open-collector output to radio |
| **PTC / polyfuse** | Resettable over-current device on the optional regulator branch |
| **SCH** / **PCB** | Schematic / printed circuit board |
| **SER12** | BayCom-class serial modem wiring — **out of scope** for T-Modem |
| **silk** | Silkscreen legend on the PCB |
| **soft-AFSK** | MCU-generated AFSK without a second modem IC (s24 path) |
| **standard reference** | One open reference design — not custom commercial SKUs (§0.24) |
| **TBD** | To be decided — not verified yet |
| **TCM3105** | Preferred Bell-202 modem IC class (DIP-16, often NOS) |
| **TH / THT** | Through-hole technology — hobby soldering path |
| **TNC** | Terminal node controller — T-Modem is modem + thin KISS (half-TNC style), host keeps AX.25 |
| **UF2** | USB flash format used by Pico ROM bootloader |
| **VBUS** | USB +5 V wire |
| **VIN_12** | Optional barrel input (~9–14 V class, silk 12 V centre+) |
| **`+5V_OR`** | Board 5 V rail after diode-OR (feeds Pico VSYS, modem, LCD) |
| **v0.25 / v1.0** | Hardware reference tag → built matching unit becomes hardware v1.0 |

## Related

| Where | What |
|-------|------|
| Branch **`c12s24`** | Full docs: `docs/SCHEMATIC.md`, `docs/BOM.md`, … |
| [BRANCHES.md](../BRANCHES.md) | `main` = index · `c12s24` = product |
| Root [README.md](../README.md) | Release / branch portal |

Do not duplicate this glossary onto `c12s24` — link here from product docs instead.
