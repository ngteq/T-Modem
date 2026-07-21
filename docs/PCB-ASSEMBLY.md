# PCB outline and assembly — v0.25

**Status:** complete hand-solderable **reference PCB** (TH + sockets)  
**Board size:** **190 × 110 mm** · 2-layer FR4 · 1.6 mm  
**AS-IS:** no support, no warranty · first fab = operator responsibility

Companion: [SCHEMATIC.md](SCHEMATIC.md) · [BOM.md](BOM.md) · [PCB-LAYOUT.md](PCB-LAYOUT.md) · KiCad [`../hardware/kicad/t-modem/`](../hardware/kicad/t-modem/) · mechanical [`../hardware/mechanical/outline-190x110.md`](../hardware/mechanical/outline-190x110.md) · fab [`../hardware/fab/README.md`](../hardware/fab/README.md)

---

## Outline

| Item | Value |
|------|-------|
| Outer | Rectangle **190.0 × 110.0 mm** (X × Y) |
| Origin | Lower-left corner of board |
| Mounting | M3 holes ≈ inset **6 mm** → (6,6), (184,6), (6,104), (184,104) |
| Keep-out | 2 mm from edge for overhanging connectors |

Larger than the early 100×80 draft per safe · stable · performant layout (§0.26).

---

## Placement (top view, silk facing up)

| Ref | Region | Notes |
|-----|--------|-------|
| J_USB | Front / left | Type-A receptacle — **USB DEVICE** |
| J_USB_PICO | Near J_USB | 1×4 — silk **to Pico Micro-USB cable** (Path B) |
| J_DC | Front | Barrel — **12 V CENTRE +** |
| SW1 + TP_BOOTSEL | Front | BOOTSEL tactile + wire pad to Pico BOOTSEL TP |
| U_REG / F1 / D_OR* / C_* | Front-right | Power island + Schottky OR |
| U1 Pico | Centre | `RaspberryPi_Pico_Common_THT` female headers; Pico H plugs in |
| SKT_MODEM | Left | DIP-16 socket for TCM3105 (`U_MODEM`) |
| Y1 + C_Y* | Near modem | 4.433619 HC-49-U Vertical + load caps |
| R_TRS / R_TXR1 / R_TXR2 | Left of modem | 0 Ω straps — silk **confirm datasheet** |
| J_AF | Right | Phoenix MSTBA 1×4 5.08 — **AF_TX AF_RX PTT GND** |
| Q1 + R_PTT | Mid-right | 2N2222A TO-92 + 4.7 kΩ |
| LED* + R_LED* | Right | 3 mm ×4 |
| U_LVL | Top | BSS138 module headers — LV=`3V3`, HV=`+5V_OR` |
| J_LCD_I2C | Top | 1×4 **GND VCC SDA SCL** (default I²C LCD) |
| RV1 / RV_CDL / RV2 | Upper mid | Bourns 3296W — TX level, CDL, contrast (RV2 optional if backpack has own) |

```text
Y=110 ┌──────────────────────────────────────────────────────────────┐
      │  U_LVL          J_LCD_I2C (I2C)                               │
      │  SKT_MODEM          U1 Pico H                  J_AF          │
      │  TCM3105            (USB end→front)            screw         │
      │                                                               │
Y=0   │  J_USB  J_USB_PICO  J_DC  SW1   power / LEDs                 │
      └──────────────────────────────────────────────────────────────┘
       X=0                                                        X=190
```

---

## USB Path B (settled)

Type-A receptacle on board. **VBUS** → Schottky OR into `+5V_OR`. **D+/D−/GND** (+ VBUS) also to `J_USB_PICO` for a short cable into the Pico Micro-USB. Silk: **to Pico Micro-USB cable**.

---

## LCD default — I²C

`J_LCD_I2C` via `U_LVL` (BSS138-class). Pico **GP0/GP1** = SDA/SCL (3.3 V side).

---

## Hobby-friendly soldering

| Rule | Detail |
|------|--------|
| **Sockets** | SKT_MODEM DIP-16 before IC; female 2.54 mm for Pico |
| **Through-hole** | Prefer TH resistors, diodes, LEDs, trimmers, USB-A / barrel / screw |
| **Modules** | Pico H; MP1584-class buck on 1×3 header |

---

## Assembly order

1. Passives and diodes (D_OR*, R*, C*) — TH  
2. F1, crystal + load caps, U_REG headers  
3. **SKT_MODEM** — do not solder the IC directly  
4. Female headers for Pico  
5. J_USB, J_USB_PICO, J_DC, J_AF, SW1, LEDs, trimmers, U_LVL, J_LCD_I2C  
6. Insert modem IC · Pico · LCD backpack cable  
7. 12 V alone → measure `+5V_OR` ≈ 5 V; then USB-only OR path  

**RX before TX** when RF attached later.

---

## Sources

| Claim | Rights-granting source | Local copy |
|-------|------------------------|------------|
| Product / GPLv3 | https://github.com/ngteq/T-Modem · https://www.gnu.org/licenses/gpl-3.0.html | `../LICENSE` |
| Electrical nets | [SCHEMATIC.md](SCHEMATIC.md) | — |
