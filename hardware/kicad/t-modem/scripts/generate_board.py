#!/usr/bin/env python3
# T-Modem v0.25 pure-Python KiCad 10 board/schematic generator (no pcbnew).
from __future__ import annotations
import math
import re
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FP_ROOT = Path("/usr/share/kicad/footprints")
SYM_ROOT = Path("/usr/share/kicad/symbols")
BOARD_W, BOARD_H = 190.0, 110.0
TRACK_SIG, TRACK_PWR, TRACK_USB = 0.35, 0.6, 0.3
VIA_D, VIA_DRILL = 0.8, 0.4
# Pad keepout radius (TH ≈ Ø1.6 → r0.8) + half-track + DRC clearance
PAD_KEEP = 1.00
TRACK_CLEAR = 0.55  # track-track (halfwidths + 0.2 DRC)

def uid():
    return str(uuid.uuid4())

def rot_xy(x, y, deg):
    r = int(round(deg)) % 360
    if r == 0:
        return x, y
    if r == 90:
        return y, -x  # match KiCad footprint rotation
    if r == 180:
        return -x, -y
    if r == 270:
        return -y, x
    rad = math.radians(deg)
    c, s = math.cos(rad), math.sin(rad)
    return x * c - y * s, x * s + y * c

def fmt(n):
    s = f"{n:.4f}".rstrip("0").rstrip(".")
    return s if s else "0"

def load_mod(lib, name):
    path = FP_ROOT / f"{lib}.pretty" / f"{name}.kicad_mod"
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")

def parse_pads(mod_text):
    pads = []
    rx = re.compile(
        r'\(pad "([^"]*)"\s+\w+\s+\w+\s*\n\s*\(at ([-\d.]+)\s+([-\d.]+)(?:\s+([-\d.]+))?\)'
    )
    for m in rx.finditer(mod_text):
        pads.append({"num": m.group(1), "x": float(m.group(2)), "y": float(m.group(3)), "rot": float(m.group(4) or 0)})
    return pads

def embed_footprint(mod_text, ref, value, x, y, rot, path):
    text = mod_text.strip()
    # Drop library-only header fields that confuse PCB parser
    text = re.sub(r'\n\t\(version [^)]+\)', '', text, count=1)
    text = re.sub(r'\n\t\(generator "[^"]*"\)', '', text, count=1)
    text = re.sub(r'\n\t\(generator_version "[^"]*"\)', '', text, count=1)
    text = re.sub(
        r'\(property "Reference" "[^"]*"',
        f'(property "Reference" "{ref}"',
        text, count=1)
    text = re.sub(
        r'\(property "Value" "[^"]*"',
        f'(property "Value" "{value}"',
        text, count=1)
    text = re.sub(
        r'\(uuid "[0-9a-fA-F-]+"\)',
        lambda _m: f'(uuid "{uid()}")',
        text)
    # Insert footprint at/uuid/path immediately after (layer "F.Cu")
    insert = (
        f'(layer "F.Cu")\n'
        f'\t(uuid "{uid()}")\n'
        f'\t(at {fmt(x)} {fmt(y)} {fmt(rot)})\n'
        f'\t(path "{path}")'
    )
    if re.search(r'\(layer "F\.Cu"\)', text):
        text = re.sub(r'\(layer "F\.Cu"\)', insert, text, count=1)
    else:
        raise RuntimeError(f'no F.Cu layer in footprint {ref}')
    return text

def pad_abs(fp_x, fp_y, fp_rot, pad):
    lx, ly = rot_xy(pad["x"], pad["y"], fp_rot)
    return fp_x + lx, fp_y + ly

PLACEMENT = [
    # Front edge (spread for courtyards; H1 clear of USB)
    ('J_USB', 'USB_A', 'Connector_USB', 'USB_A_Molex_67643_Horizontal', 22.0, 8.0, 180),
    ('J_USB_PICO', 'to Pico Micro-USB cable', 'Connector_PinHeader_2.54mm', 'PinHeader_1x04_P2.54mm_Vertical', 48.0, 22.0, 0),
    ('J_DC', '12V CENTRE+', 'Connector_BarrelJack', 'BarrelJack_Horizontal', 74.0, 12.0, 270),
    ('SW1', 'BOOTSEL', 'Button_Switch_THT', 'SW_PUSH_6mm', 98.0, 12.0, 0),
    ('TP_BOOTSEL', 'to Pico BOOTSEL', 'Connector_PinHeader_2.54mm', 'PinHeader_1x01_P2.54mm_Vertical', 112.0, 12.0, 0),
    ('C_IN', '100uF', 'Capacitor_THT', 'CP_Radial_D8.0mm_P3.50mm', 126.0, 12.0, 0),
    ('U_REG', 'MP1584 VIN GND 5V', 'Connector_PinHeader_2.54mm', 'PinHeader_1x03_P2.54mm_Vertical', 140.0, 14.0, 0),
    ('F1', 'MF-RG500', 'Fuse', 'Fuse_Bourns_MF-RG500', 154.0, 14.0, 90),
    ('D_OR1', '1N5819', 'Diode_THT', 'D_DO-41_SOD81_P10.16mm_Horizontal', 158.0, 10.0, 0),
    ('D_OR2', '1N5819', 'Diode_THT', 'D_DO-41_SOD81_P10.16mm_Horizontal', 158.0, 24.0, 0),
    ('C_BULK', '100uF', 'Capacitor_THT', 'CP_Radial_D8.0mm_P3.50mm', 182.0, 14.0, 0),
    # Pico centre (room for escape channels left/right of headers)
    ('U1', 'RaspberryPi_Pico', 'Module', 'RaspberryPi_Pico_Common_THT', 100.0, 36.0, 0),
    ('C_BYP2', '100nF', 'Capacitor_THT', 'C_Disc_D5.0mm_W2.5mm_P5.00mm', 82.0, 30.0, 0),
    # Modem left
    ('SKT_MODEM', 'U_MODEM TCM3105', 'Package_DIP', 'DIP-16_W7.62mm_Socket', 22.0, 52.0, 0),
    ('Y1', '4.433619', 'Crystal', 'Crystal_HC49-U_Vertical', 40.0, 42.0, 0),
    ('C_Y1', '22pF', 'Capacitor_THT', 'C_Disc_D5.0mm_W2.5mm_P5.00mm', 32.0, 34.0, 0),
    ('C_Y2', '22pF', 'Capacitor_THT', 'C_Disc_D5.0mm_W2.5mm_P5.00mm', 48.0, 34.0, 0),
    ('C_BYP1', '100nF', 'Capacitor_THT', 'C_Disc_D5.0mm_W2.5mm_P5.00mm', 22.0, 76.0, 0),
    ('R_TRS', '0R', 'Resistor_THT', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal', 42.0, 54.0, 0),
    ('R_TXR1', '0R', 'Resistor_THT', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal', 42.0, 62.0, 0),
    ('R_TXR2', '0R', 'Resistor_THT', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal', 28.0, 68.0, 0),
    ('C_RX', '100nF', 'Capacitor_THT', 'C_Disc_D5.0mm_W2.5mm_P5.00mm', 70.0, 88.0, 0),
    ('C_TX', '100nF', 'Capacitor_THT', 'C_Disc_D5.0mm_W2.5mm_P5.00mm', 70.0, 78.0, 0),
    ('RV1', '10k TX', 'Potentiometer_THT', 'Potentiometer_Bourns_3296W_Vertical', 58.0, 80.0, 0),
    ('RV_CDL', '50k CDL', 'Potentiometer_THT', 'Potentiometer_Bourns_3296W_Vertical', 58.0, 94.0, 0),
    # AF / PTT / LEDs right — LEDs clear of J_AF; R_LED clear of LED courtyards
    ('J_AF', 'AF', 'Connector_Phoenix_MSTB', 'PhoenixContact_MSTBA_2,5_4-G-5,08_1x04_P5.08mm_Horizontal', 182.0, 78.0, 90),
    ('R_PTT', '4.7k', 'Resistor_THT', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal', 128.0, 56.0, 0),
    ('Q1', '2N2222A', 'Package_TO_SOT_THT', 'TO-92', 148.0, 58.0, 0),
    ('LED_PWR', 'PWR', 'LED_THT', 'LED_D3.0mm', 178.0, 28.0, 90),
    ('LED_PTT', 'PTT', 'LED_THT', 'LED_D3.0mm', 178.0, 40.0, 90),
    ('LED_DCD', 'DCD', 'LED_THT', 'LED_D3.0mm', 178.0, 52.0, 90),
    ('LED_TXRX', 'TXRX', 'LED_THT', 'LED_D3.0mm', 178.0, 64.0, 90),
    ('R_LED1', '1k', 'Resistor_THT', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal', 160.0, 28.0, 0),
    ('R_LED2', '1k', 'Resistor_THT', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal', 160.0, 40.0, 0),
    ('R_LED3', '1k', 'Resistor_THT', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal', 160.0, 52.0, 0),
    ('R_LED4', '1k', 'Resistor_THT', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal', 160.0, 64.0, 0),
    # Bottom I2C
    ('U_LVL', 'BSS138', 'Connector_PinHeader_2.54mm', 'PinHeader_2x04_P2.54mm_Vertical', 72.0, 102.0, 0),
    ('J_LCD_I2C', 'LCD I2C', 'Connector_PinHeader_2.54mm', 'PinHeader_1x04_P2.54mm_Vertical', 100.0, 102.0, 0),
    ('RV2', '10k contrast', 'Potentiometer_THT', 'Potentiometer_Bourns_3296W_Vertical', 128.0, 100.0, 0),
    # Mounts
    ('H1', 'M3', 'MountingHole', 'MountingHole_3.2mm_M3', 6.0, 6.0, 0),
    ('H2', 'M3', 'MountingHole', 'MountingHole_3.2mm_M3', 184.0, 6.0, 0),
    ('H3', 'M3', 'MountingHole', 'MountingHole_3.2mm_M3', 6.0, 104.0, 0),
    ('H4', 'M3', 'MountingHole', 'MountingHole_3.2mm_M3', 184.0, 104.0, 0),
]

PICO_NETS = {
    "1": "I2C_SDA_3V3", "2": "I2C_SCL_3V3", "3": "GND", "8": "GND",
    "9": "MODEM_TXD", "10": "MODEM_RXD", "11": "MODEM_CDT", "12": "PTT_DRV",
    "13": "GND", "14": "LED_PTT_N", "15": "LED_DCD_N", "16": "LED_TXRX_N",
    "18": "GND", "23": "GND", "28": "GND", "33": "GND",
    "36": "3V3", "38": "GND", "39": "+5V_OR",
}
MODEM_NETS = {
    "1": "+5V_OR", "3": "MODEM_CDT", "4": "RXA", "5": "TRS_N", "7": "CDL",
    "8": "MODEM_RXD", "9": "GND", "10": "CDL", "11": "TXA", "12": "TXR2_N",
    "13": "TXR1_N", "14": "MODEM_TXD", "15": "OSC1", "16": "OSC2",
}


def build_nets():
    nets = {}
    def add(net, ref, pad):
        nets.setdefault(net, []).append((ref, pad))
    for p, n in PICO_NETS.items():
        add(n, 'U1', p)
    for p, n in MODEM_NETS.items():
        add(n, 'SKT_MODEM', p)
    add('VBUS', 'J_USB', '1'); add('USB_DM', 'J_USB', '2')
    add('USB_DP', 'J_USB', '3'); add('GND', 'J_USB', '4'); add('GND', 'J_USB', 'SH')
    add('VBUS', 'J_USB_PICO', '1'); add('USB_DM', 'J_USB_PICO', '2')
    add('USB_DP', 'J_USB_PICO', '3'); add('GND', 'J_USB_PICO', '4')
    add('VIN_12', 'J_DC', '1'); add('GND', 'J_DC', '2'); add('GND', 'J_DC', '3')
    add('VIN_12', 'U_REG', '1'); add('GND', 'U_REG', '2'); add('+5V_REG', 'U_REG', '3')
    add('+5V_REG', 'F1', '1'); add('+5V', 'F1', '2')
    add('+5V', 'D_OR1', '2'); add('+5V_OR', 'D_OR1', '1')
    add('VBUS', 'D_OR2', '2'); add('+5V_OR', 'D_OR2', '1')
    add('VIN_12', 'C_IN', '1'); add('GND', 'C_IN', '2')
    add('+5V_OR', 'C_BULK', '1'); add('GND', 'C_BULK', '2')
    add('+5V_OR', 'C_BYP1', '1'); add('GND', 'C_BYP1', '2')
    add('+5V_OR', 'C_BYP2', '1'); add('GND', 'C_BYP2', '2')
    add('OSC1', 'Y1', '1'); add('OSC2', 'Y1', '2')
    add('OSC1', 'C_Y1', '1'); add('GND', 'C_Y1', '2')
    add('OSC2', 'C_Y2', '1'); add('GND', 'C_Y2', '2')
    add('TXR1_N', 'R_TXR1', '1'); add('GND', 'R_TXR1', '2')
    add('TXR2_N', 'R_TXR2', '1'); add('+5V_OR', 'R_TXR2', '2')
    add('TRS_N', 'R_TRS', '1'); add('GND', 'R_TRS', '2')
    add('AF_TX', 'J_AF', '1'); add('AF_RX', 'J_AF', '2')
    add('PTT_OC', 'J_AF', '3'); add('GND', 'J_AF', '4')
    add('AF_RX', 'C_RX', '1'); add('RXA', 'C_RX', '2')
    add('TXA', 'RV1', '1'); add('TX_LVL', 'RV1', '2'); add('GND', 'RV1', '3')
    add('TX_LVL', 'C_TX', '1'); add('AF_TX', 'C_TX', '2')
    add('+5V_OR', 'RV_CDL', '1'); add('CDL', 'RV_CDL', '2'); add('GND', 'RV_CDL', '3')
    add('PTT_DRV', 'R_PTT', '1'); add('PTT_B', 'R_PTT', '2')
    add('GND', 'Q1', '1'); add('PTT_B', 'Q1', '2'); add('PTT_OC', 'Q1', '3')
    add('GND', 'LED_PWR', '1'); add('LED_PWR_A', 'LED_PWR', '2')
    add('+5V_OR', 'R_LED1', '1'); add('LED_PWR_A', 'R_LED1', '2')
    add('GND', 'LED_PTT', '1'); add('LED_PTT_A', 'LED_PTT', '2')
    add('LED_PTT_N', 'R_LED2', '1'); add('LED_PTT_A', 'R_LED2', '2')
    add('GND', 'LED_DCD', '1'); add('LED_DCD_A', 'LED_DCD', '2')
    add('LED_DCD_N', 'R_LED3', '1'); add('LED_DCD_A', 'R_LED3', '2')
    add('GND', 'LED_TXRX', '1'); add('LED_TXRX_A', 'LED_TXRX', '2')
    add('LED_TXRX_N', 'R_LED4', '1'); add('LED_TXRX_A', 'R_LED4', '2')
    add('GND', 'SW1', '1'); add('BOOTSEL', 'SW1', '2'); add('BOOTSEL', 'TP_BOOTSEL', '1')
    add('3V3', 'U_LVL', '1'); add('+5V_OR', 'U_LVL', '2')
    add('I2C_SDA_3V3', 'U_LVL', '3'); add('I2C_SDA_5V', 'U_LVL', '4')
    add('I2C_SCL_3V3', 'U_LVL', '5'); add('I2C_SCL_5V', 'U_LVL', '6')
    add('GND', 'U_LVL', '7'); add('GND', 'U_LVL', '8')
    add('GND', 'J_LCD_I2C', '1'); add('+5V_OR', 'J_LCD_I2C', '2')
    add('I2C_SDA_5V', 'J_LCD_I2C', '3'); add('I2C_SCL_5V', 'J_LCD_I2C', '4')
    add('+5V_OR', 'RV2', '1'); add('LCD_VO', 'RV2', '2'); add('GND', 'RV2', '3')
    return nets

def silk(x, y, text, size=1.0, rot=0):
    return (
        f'  (gr_text "{text}"\n'
        f'    (at {fmt(x)} {fmt(y)} {fmt(rot)})\n'
        f'    (layer "F.SilkS")\n'
        f'    (uuid "{uid()}")\n'
        f'    (effects (font (size {fmt(size)} {fmt(size)}) (thickness {fmt(size*0.15)})))\n'
        f'  )'
    )


def strip_antenna_zones(fp_text):
    """Drop embedded footprint zones/keepouts (Pico antenna etc.)."""
    out = []
    i = 0
    while True:
        j = fp_text.find("(zone", i)
        if j < 0:
            out.append(fp_text[i:])
            break
        out.append(fp_text[i:j])
        depth = 0
        k = j
        while k < len(fp_text):
            ch = fp_text[k]
            if ch == '"':
                k += 1
                while k < len(fp_text) and fp_text[k] != '"':
                    if fp_text[k] == chr(92):
                        k += 2
                        continue
                    k += 1
                k += 1
                continue
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    k += 1
                    break
            k += 1
        i = k
    return "".join(out)





def edge_cuts():
    uid_s = uid()
    return (
        "  (gr_rect\n"
        "    (start 0 0)\n"
        f"    (end {fmt(BOARD_W)} {fmt(BOARD_H)})\n"
        "    (stroke\n"
        "      (width 0.1)\n"
        "      (type solid)\n"
        "    )\n"
        "    (fill no)\n"
        '    (layer "Edge.Cuts")\n'
        f'    (uuid "{uid_s}")\n'
        "  )"
    )


def track(x1, y1, x2, y2, width, layer, netcode):
    return (
        f'  (segment\n'
        f'    (start {fmt(x1)} {fmt(y1)})\n'
        f'    (end {fmt(x2)} {fmt(y2)})\n'
        f'    (width {fmt(width)})\n'
        f'    (layer "{layer}")\n'
        f'    (net {netcode})\n'
        f'    (uuid "{uid()}")\n'
        f'  )'
    )

def via(x, y, netcode):
    return (
        f'  (via\n'
        f'    (at {fmt(x)} {fmt(y)})\n'
        f'    (size {fmt(VIA_D)})\n'
        f'    (drill {fmt(VIA_DRILL)})\n'
        f'    (layers "F.Cu" "B.Cu")\n'
        f'    (net {netcode})\n'
        f'    (uuid "{uid()}")\n'
        f'  )'
    )

def manhattan(x1, y1, x2, y2, width, layer, netcode):
    out = []
    if abs(x1 - x2) < 0.01 and abs(y1 - y2) < 0.01:
        return out
    if abs(y1 - y2) < 0.01 or abs(x1 - x2) < 0.01:
        out.append(track(x1, y1, x2, y2, width, layer, netcode))
    else:
        out.append(track(x1, y1, x2, y1, width, layer, netcode))
        out.append(track(x2, y1, x2, y2, width, layer, netcode))
    return out

def width_for(net):
    if net in ('GND', '+5V_OR', '+5V', '+5V_REG', 'VIN_12', 'VBUS', '3V3'):
        return TRACK_PWR
    if net in ('USB_DP', 'USB_DM'):
        return TRACK_USB
    return TRACK_SIG



def assign_pad_nets(fp_body, ref, nets, net_codes):
    pad_to_net = {}
    for net, members in nets.items():
        for r, p in members:
            if r == ref:
                pad_to_net[p] = net

    def repl_pad(m):
        full = m.group(0)
        pnum = m.group(1)
        if pnum not in pad_to_net:
            return full
        net = pad_to_net[pnum]
        code = net_codes[net]
        net_s = f'(net {code} "{net}")'
        if re.search(r'\(net \d+', full):
            return re.sub(r'\(net \d+ "[^"]*"\)', net_s, full)
        return re.sub(r'(\([at][^)]*\))'.replace('[at]', 'at'), rf'\1\n\t\t{net_s}', full, count=1)

    # simpler insert after first (at ...)
    def repl_pad2(m):
        full = m.group(0)
        pnum = m.group(1)
        if pnum not in pad_to_net:
            return full
        net = pad_to_net[pnum]
        code = net_codes[net]
        net_s = f'(net {code} "{net}")'
        if re.search(r'\(net \d+', full):
            return re.sub(r'\(net \d+ "[^"]*"\)', net_s, full)
        return re.sub(r'(\(at [^)]+\))', r'\1\n\t\t' + net_s, full, count=1)

    return re.sub(
        r'\(pad "([^"]*)"[\s\S]*?(?=\n\t\(pad |\n\t\(embedded_fonts|\n\t\(model |\Z)',
        repl_pad2,
        fp_body,
    )

def extract_symbol(lib_path, name):
    text = Path(lib_path).read_text(encoding='utf-8')
    m = re.search(rf'\(symbol "{re.escape(name)}"', text)
    if not m:
        raise KeyError(f'{name} not in {lib_path}')
    start = m.start()
    depth = 0
    i = start
    while i < len(text):
        ch = text[i]
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
            if depth == 0:
                return text[start:i+1]
        i += 1
    raise RuntimeError(f'unbalanced symbol {name}')

def write_symbol_lib():
    parts = []
    for lib, names in [
        (SYM_ROOT / 'Device.kicad_sym', ['R', 'C', 'C_Polarized', 'LED', 'Crystal_GND24', 'D_Schottky', 'Fuse', 'R_Potentiometer']),
        (SYM_ROOT / 'Connector.kicad_sym', ['USB_A', 'Barrel_Jack']),
        (SYM_ROOT / 'Connector_Generic.kicad_sym', ['Conn_01x01', 'Conn_01x03', 'Conn_01x04', 'Conn_02x04_Odd_Even']),
        (SYM_ROOT / 'Switch.kicad_sym', ['SW_Push']),
        (SYM_ROOT / 'Transistor_BJT.kicad_sym', ['PN2222A']),
        (SYM_ROOT / 'power.kicad_sym', ['GND', '+5V', '+3V3']),
    ]:
        for n in names:
            try:
                parts.append(extract_symbol(lib, n))
            except Exception as e:
                print('WARN symbol', n, e)
    # TCM3105 custom
    pins = [
        (1,'VDD','power_in',-7.62,8.89),(2,'CLK','passive',-7.62,6.35),(3,'CDT','output',-7.62,3.81),
        (4,'RXA','input',-7.62,1.27),(5,'TRS','passive',-7.62,-1.27),(6,'NC','no_connect',-7.62,-3.81),
        (7,'RXB','passive',-7.62,-6.35),(8,'RXD','output',-7.62,-8.89),
        (9,'VSS','power_in',7.62,-8.89),(10,'CDL','passive',7.62,-6.35),(11,'TXA','output',7.62,-3.81),
        (12,'TXR2','passive',7.62,-1.27),(13,'TXR1','passive',7.62,1.27),(14,'TXD','input',7.62,3.81),
        (15,'OSC1','passive',7.62,6.35),(16,'OSC2','passive',7.62,8.89),
    ]
    pin_s = []
    for num, name, ptype, x, y in pins:
        orient = 0 if x < 0 else 180
        pin_s.append(
            f'\n\t\t\t(pin {ptype} line\n'
            f'\t\t\t\t(at {x} {y} {orient})\n'
            f'\t\t\t\t(length 2.54)\n'
            f'\t\t\t\t(name "{name}" (effects (font (size 1.27 1.27))))\n'
            f'\t\t\t\t(number "{num}" (effects (font (size 1.27 1.27))))\n'
            f'\t\t\t)'
        )
    tcm = (
        '\t(symbol "TCM3105"\n'
        '\t\t(pin_names (offset 1.016))\n'
        '\t\t(exclude_from_sim no)\n'
        '\t\t(in_bom yes)\n'
        '\t\t(on_board yes)\n'
        '\t\t(property "Reference" "U" (at 0 11.43 0) (effects (font (size 1.27 1.27))))\n'
        '\t\t(property "Value" "TCM3105" (at 0 -11.43 0) (effects (font (size 1.27 1.27))))\n'
        '\t\t(property "Footprint" "Package_DIP:DIP-16_W7.62mm_Socket" (at 0 0 0) (hide yes)\n'
        '\t\t\t(effects (font (size 1.27 1.27))))\n'
        '\t\t(property "Datasheet" "https://www.qsl.net/o/on7pc/datasheet/ic/TCM3105.pdf" (at 0 0 0) (hide yes)\n'
        '\t\t\t(effects (font (size 1.27 1.27))))\n'
        '\t\t(property "Description" "Bell 202 FSK modem DIP-16" (at 0 0 0) (hide yes)\n'
        '\t\t\t(effects (font (size 1.27 1.27))))\n'
        '\t\t(symbol "TCM3105_0_1"\n'
        '\t\t\t(rectangle (start -5.08 10.16) (end 5.08 -10.16)\n'
        '\t\t\t\t(stroke (width 0.254) (type default)) (fill (type background)))\n'
        '\t\t)\n'
        '\t\t(symbol "TCM3105_1_1"' + ''.join(pin_s) + '\n'
        '\t\t)\n'
        '\t\t(embedded_fonts no)\n'
        '\t)'
    )
    parts.append(tcm)
    # Pico subset
    pp = [(1,'GP0'),(2,'GP1'),(3,'GND'),(9,'GP6'),(10,'GP7'),(11,'GP8'),(12,'GP9'),
          (14,'GP10'),(15,'GP11'),(16,'GP12'),(36,'3V3'),(38,'GND'),(39,'VSYS'),(40,'VBUS')]
    ps = []
    for i,(num,pname) in enumerate(pp):
        y = 15.24 - i*2.54
        ps.append(
            f'\n\t\t\t(pin bidirectional line\n'
            f'\t\t\t\t(at -7.62 {y} 0)\n'
            f'\t\t\t\t(length 2.54)\n'
            f'\t\t\t\t(name "{pname}" (effects (font (size 1.27 1.27))))\n'
            f'\t\t\t\t(number "{num}" (effects (font (size 1.27 1.27))))\n'
            f'\t\t\t)'
        )
    pico = (
        '\t(symbol "RaspberryPi_Pico"\n'
        '\t\t(pin_names (offset 1.016))\n'
        '\t\t(exclude_from_sim no) (in_bom yes) (on_board yes)\n'
        '\t\t(property "Reference" "U" (at 0 17.78 0) (effects (font (size 1.27 1.27))))\n'
        '\t\t(property "Value" "RaspberryPi_Pico" (at 0 -5.08 0) (effects (font (size 1.27 1.27))))\n'
        '\t\t(property "Footprint" "Module:RaspberryPi_Pico_Common_THT" (at 0 0 0) (hide yes)\n'
        '\t\t\t(effects (font (size 1.27 1.27))))\n'
        '\t\t(property "Datasheet" "https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf" (at 0 0 0) (hide yes)\n'
        '\t\t\t(effects (font (size 1.27 1.27))))\n'
        '\t\t(property "Description" "Raspberry Pi Pico module subset" (at 0 0 0) (hide yes)\n'
        '\t\t\t(effects (font (size 1.27 1.27))))\n'
        '\t\t(symbol "RaspberryPi_Pico_0_1"\n'
        '\t\t\t(rectangle (start -5.08 16.51) (end 5.08 -3.81)\n'
        '\t\t\t\t(stroke (width 0.254) (type default)) (fill (type background)))\n'
        '\t\t)\n'
        '\t\t(symbol "RaspberryPi_Pico_1_1"' + ''.join(ps) + '\n'
        '\t\t)\n'
        '\t\t(embedded_fonts no)\n'
        '\t)'
    )
    parts.append(pico)
    body = '\n'.join(parts)
    lib = (
        '(kicad_symbol_lib\n'
        '\t(version 20241209)\n'
        '\t(generator "t_modem_generate_board")\n'
        '\t(generator_version "0.25")\n'
        + body + '\n)\n'
    )
    (ROOT / 't-modem.kicad_sym').write_text(lib, encoding='utf-8')
    print('Wrote', ROOT / 't-modem.kicad_sym')


def write_schematic():
    write_symbol_lib()
    extra = []
    for lib, names in [
        (SYM_ROOT / 'Device.kicad_sym', ['R','C','LED','D_Schottky','Fuse','C_Polarized','Crystal_GND24','R_Potentiometer']),
        (SYM_ROOT / 'power.kicad_sym', ['GND','+5V','+3V3']),
        (SYM_ROOT / 'Connector.kicad_sym', ['USB_A','Barrel_Jack']),
        (SYM_ROOT / 'Connector_Generic.kicad_sym', ['Conn_01x04','Conn_01x03','Conn_01x01','Conn_02x04_Odd_Even']),
        (SYM_ROOT / 'Switch.kicad_sym', ['SW_Push']),
        (SYM_ROOT / 'Transistor_BJT.kicad_sym', ['PN2222A']),
    ]:
        for n in names:
            try: extra.append(extract_symbol(lib, n))
            except Exception as e: print('sch skip', n, e)
    for n in ('TCM3105', 'RaspberryPi_Pico'):
        extra.append(extract_symbol(ROOT / 't-modem.kicad_sym', n))
    lib_block = '\n'.join(extra)
    comps = []
    def inst(lib_id, ref, value, x, y, fp=''):
        comps.append(
            f'  (symbol\n'
            f'    (lib_id "{lib_id}")\n'
            f'    (at {x} {y} 0)\n'
            f'    (unit 1)\n'
            f'    (exclude_from_sim no)\n'
            f'    (in_bom yes)\n'
            f'    (on_board yes)\n'
            f'    (dnp no)\n'
            f'    (uuid "{uid()}")\n'
            f'    (property "Reference" "{ref}" (at {x} {y+5} 0) (effects (font (size 1.27 1.27))))\n'
            f'    (property "Value" "{value}" (at {x} {y-5} 0) (effects (font (size 1.27 1.27))))\n'
            f'    (property "Footprint" "{fp}" (at {x} {y} 0) (effects (font (size 1.27 1.27))) (hide yes))\n'
            f'    (property "Datasheet" "" (at {x} {y} 0) (effects (font (size 1.27 1.27))) (hide yes))\n'
            f'  )'
        )
    inst('RaspberryPi_Pico', 'U1', 'Pico', 50, 80, 'Module:RaspberryPi_Pico_Common_THT')
    inst('TCM3105', 'U_MODEM', 'TCM3105', 120, 80, 'Package_DIP:DIP-16_W7.62mm_Socket')
    inst('USB_A', 'J_USB', 'USB_A', 40, 40, 'Connector_USB:USB_A_Molex_67643_Horizontal')
    inst('Conn_01x04', 'J_USB_PICO', 'to Pico Micro-USB', 80, 40)
    inst('Barrel_Jack', 'J_DC', '12V', 120, 40)
    inst('Conn_01x04', 'J_AF', 'AF', 180, 80)
    inst('Conn_01x04', 'J_LCD_I2C', 'LCD_I2C', 180, 40)
    inst('Conn_02x04_Odd_Even', 'U_LVL', 'BSS138', 150, 40)
    inst('Conn_01x03', 'U_REG', 'MP1584', 160, 120)
    inst('D_Schottky', 'D_OR1', '1N5819', 200, 110)
    inst('D_Schottky', 'D_OR2', '1N5819', 200, 130)
    inst('Fuse', 'F1', 'MF-RG500', 180, 120)
    inst('PN2222A', 'Q1', '2N2222A', 220, 80)
    inst('SW_Push', 'SW1', 'BOOTSEL', 100, 120)
    inst('Crystal_GND24', 'Y1', '4.433619', 120, 120)
    note = (
        '  (text "T-Modem v0.25 complete PCB 190x110. USB Path B + I2C LCD. See docs/SCHEMATIC.md. "\n'
        '"TXR1/TXR2 0R default Bell202 1200 - confirm datasheet."\n'
        f'    (at 20 20 0)\n'
        f'    (effects (font (size 1.5 1.5)) (justify left top))\n'
        f'    (uuid "{uid()}")\n'
        '  )'
    )
    sch = (
        '(kicad_sch\n'
        '  (version 20241209)\n'
        '  (generator "eeschema")\n'
        '  (generator_version "10.0")\n'
        f'  (uuid "{uid()}")\n'
        '  (paper "A3")\n'
        '  (title_block\n'
        '    (title "T-Modem")\n'
        '    (date "2026-07-21")\n'
        '    (rev "0.25")\n'
        '    (company "ngteq GPLv3 AS-IS standard reference")\n'
        '    (comment 1 "USB Path B + I2C LCD - complete PCB")\n'
        '    (comment 2 "Nets: docs/SCHEMATIC.md")\n'
        '  )\n'
        '  (lib_symbols\n' + lib_block + '\n  )\n'
        + note + '\n' + '\n'.join(comps) + '\n'
        '  (sheet_instances\n    (path "/" (page "1"))\n  )\n'
        '  (embedded_fonts no)\n)'
    )
    (ROOT / 't-modem.kicad_sch').write_text(sch, encoding='utf-8')
    print('Wrote', ROOT / 't-modem.kicad_sch')

def _extract_sexpr(s, start_token):
    j = s.find(start_token)
    if j < 0:
        raise KeyError(start_token)
    depth = 0
    k = j
    while k < len(s):
        if s[k] == '"':
            k += 1
            while k < len(s) and s[k] != '"':
                if s[k] == '\\':
                    k += 2
                    continue
                k += 1
            k += 1
            continue
        if s[k] == '(':
            depth += 1
        elif s[k] == ')':
            depth -= 1
            if depth == 0:
                return j, k + 1
        k += 1
    raise RuntimeError('unbalanced ' + start_token)


def fixup_kicad10_layers(pcb_text):
    block = (Path(__file__).with_name('kicad10_layers_setup.sexpr')).read_text(encoding='utf-8')
    if not block.endswith('\n'):
        block += '\n'
    a, _ = _extract_sexpr(pcb_text, '(layers')
    _, b1 = _extract_sexpr(pcb_text, '(setup')
    return pcb_text[:a] + block + pcb_text[b1:]



# ---------------------------------------------------------------------------
# Collision-aware manhattan router (no net-shorting; NC pads are obstacles)
# ---------------------------------------------------------------------------

def _seg_hits_pads(x1, y1, x2, y2, pads, net, keep=PAD_KEEP):
    """True if axis-aligned segment comes within keep of a foreign pad centre."""
    for px, py, pnet in pads:
        if pnet == net:
            continue
        if abs(x1 - x2) < 1e-9:
            ymin, ymax = (y1, y2) if y1 <= y2 else (y2, y1)
            if ymin - keep <= py <= ymax + keep and abs(px - x1) < keep:
                # allow segment endpoints on own pads only (already skipped foreign)
                return True
        elif abs(y1 - y2) < 1e-9:
            xmin, xmax = (x1, x2) if x1 <= x2 else (x2, x1)
            if xmin - keep <= px <= xmax + keep and abs(py - y1) < keep:
                return True
        else:
            return True
    return False


def _path_hits(path_segs, pads, net):
    for x1, y1, x2, y2 in path_segs:
        if abs(x1 - x2) < 0.01 and abs(y1 - y2) < 0.01:
            continue
        if _seg_hits_pads(x1, y1, x2, y2, pads, net):
            return True
    return False


def _crosses(ax1, ay1, ax2, ay2, bx1, by1, bx2, by2, clear):
    """Orthogonal manhattan segments conflict (cross or parallel too close)."""
    avert = abs(ax1 - ax2) < 1e-9
    bvert = abs(bx1 - bx2) < 1e-9
    ax0, ax1s = sorted([ax1, ax2]); ay0, ay1s = sorted([ay1, ay2])
    bx0, bx1s = sorted([bx1, bx2]); by0, by1s = sorted([by1, by2])
    eps = 0.05
    if avert and bvert:
        return abs(ax1 - bx1) < clear and not (ay1s < by0 - eps or by1s < ay0 - eps)
    if (not avert) and (not bvert):
        return abs(ay1 - by1) < clear and not (ax1s < bx0 - eps or bx1s < ax0 - eps)
    if avert and (not bvert):
        # proper crossing (not T at endpoint of both = still short if different nets)
        return (bx0 - eps <= ax1 <= bx1s + eps) and (ay0 - eps <= by1 <= ay1s + eps)
    return (ax0 - eps <= bx1 <= ax1s + eps) and (by0 - eps <= ay1 <= by1s + eps)


def _l_paths(x1, y1, x2, y2):
    if abs(x1 - x2) < 0.05 and abs(y1 - y2) < 0.05:
        return [[]]
    if abs(y1 - y2) < 0.05 or abs(x1 - x2) < 0.05:
        return [[(x1, y1, x2, y2)]]
    return [
        [(x1, y1, x2, y1), (x2, y1, x2, y2)],
        [(x1, y1, x1, y2), (x1, y2, x2, y2)],
    ]


def _detour_paths(x1, y1, x2, y2, board_w, board_h, blocked_y=None, blocked_x=None):
    cands = []
    highways_y = [6, 12, 18, 24, 30, 46, 54, 62, 72, 84, 92, 100, board_h - 6]
    highways_x = [8, 16, 36, 54, 70, 88, 118, 138, 158, 172, board_w - 8]
    for hy in highways_y:
        if 4 <= hy <= board_h - 4:
            cands.append([(x1, y1, x1, hy), (x1, hy, x2, hy), (x2, hy, x2, y2)])
    for hx in highways_x:
        if 4 <= hx <= board_w - 4:
            cands.append([(x1, y1, hx, y1), (hx, y1, hx, y2), (hx, y2, x2, y2)])
    for hy in (18, 54, 84, 100):
        for hx in (16, 54, 88, 138, 172):
            if not (4 <= hy <= board_h - 4 and 4 <= hx <= board_w - 4):
                continue
            cands.append([
                (x1, y1, x1, hy), (x1, hy, hx, hy), (hx, hy, hx, y2), (hx, y2, x2, y2)
            ])
            cands.append([
                (x1, y1, hx, y1), (hx, y1, hx, hy), (hx, hy, x2, hy), (x2, hy, x2, y2)
            ])
    return cands


def _astar_path(x1, y1, x2, y2, pads, net, used, layer, board_w, board_h, step=1.27):
    """Coarse-grid A* for hard nets. Returns manhattan segment list or None."""
    import heapq
    keep = PAD_KEEP

    def blocked(x, y):
        if not (3 <= x <= board_w - 3 and 3 <= y <= board_h - 3):
            return True
        # allow cells near endpoints (escape off pin)
        if abs(x - x1) < keep and abs(y - y1) < keep:
            return False
        if abs(x - x2) < keep and abs(y - y2) < keep:
            return False
        for px, py, pnet in pads:
            if pnet == net:
                continue
            if abs(px - x) < keep and abs(py - y) < keep:
                return True
        tclear = TRACK_CLEAR
        for ux1, uy1, ux2, uy2, ulayer, unet in used:
            if ulayer != layer or unet == net:
                continue
            if abs(ux1 - ux2) < 1e-9:
                ymin, ymax = sorted([uy1, uy2])
                if abs(x - ux1) < tclear and ymin - tclear <= y <= ymax + tclear:
                    return True
            elif abs(uy1 - uy2) < 1e-9:
                xmin, xmax = sorted([ux1, ux2])
                if abs(y - uy1) < tclear and xmin - tclear <= x <= xmax + tclear:
                    return True
        return False

    def snap(x, y):
        return round(x / step) * step, round(y / step) * step

    s = snap(x1, y1)
    g = snap(x2, y2)

    def heur(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    openh = [(heur(s, g), 0.0, s)]
    came = {}
    gscore = {s: 0.0}
    closed = set()
    dirs = [(step, 0), (-step, 0), (0, step), (0, -step)]
    steps_n = 0
    found = None
    while openh and steps_n < 100000:
        steps_n += 1
        _, cost, cur = heapq.heappop(openh)
        if cur in closed:
            continue
        closed.add(cur)
        if abs(cur[0] - g[0]) < step * 0.75 and abs(cur[1] - g[1]) < step * 0.75:
            found = cur
            break
        for dx, dy in dirs:
            nxt = (round(cur[0] + dx, 3), round(cur[1] + dy, 3))
            if nxt in closed or blocked(nxt[0], nxt[1]):
                continue
            ng = cost + step
            if ng < gscore.get(nxt, 1e18):
                gscore[nxt] = ng
                came[nxt] = cur
                heapq.heappush(openh, (ng + heur(nxt, g), ng, nxt))
    if found is None:
        return None
    path = [g, found]
    cur = found
    while cur in came:
        cur = came[cur]
        path.append(cur)
    path.append(s)
    path.reverse()
    path[0] = (x1, y1)
    path[-1] = (x2, y2)
    segs = []
    for i in range(len(path) - 1):
        a, b = path[i], path[i + 1]
        if abs(a[0] - b[0]) < 0.01 and abs(a[1] - b[1]) < 0.01:
            continue
        if abs(a[0] - b[0]) > 0.01 and abs(a[1] - b[1]) > 0.01:
            segs.append((a[0], a[1], b[0], a[1]))
            segs.append((b[0], a[1], b[0], b[1]))
        else:
            segs.append((a[0], a[1], b[0], b[1]))
    return segs


class BoardRouter:
    def __init__(self, board_w, board_h):
        self.w = board_w
        self.h = board_h
        self.pads = []
        self.used = []

    def add_pad(self, x, y, net, block_highway=False):
        self.pads.append((x, y, net if net else ''))

    def _hits_used(self, segs, layer, net):
        clear = TRACK_CLEAR
        for x1, y1, x2, y2 in segs:
            if abs(x1 - x2) < 0.01 and abs(y1 - y2) < 0.01:
                continue
            for ux1, uy1, ux2, uy2, ulayer, unet in self.used:
                if ulayer != layer or unet == net:
                    continue
                if _crosses(x1, y1, x2, y2, ux1, uy1, ux2, uy2, clear):
                    return True
        return False

    def _candidates(self, x1, y1, x2, y2):
        cands = _l_paths(x1, y1, x2, y2)
        cands += _detour_paths(x1, y1, x2, y2, self.w, self.h)
        for e in (2.54, 3.81, 5.08, -2.54, -3.81, -5.08):
            for fx, fy in ((e, 0), (0, e), (e, e), (e, -e)):
                for (aa, bb, cc, dd) in (
                    (x1 + fx, y1 + fy, x2 + fx, y2 + fy),
                    (x1 + fx, y1 + fy, x2 - fx, y2 - fy),
                    (x1 + fx, y1, x2 + fx, y2),
                    (x1, y1 + fy, x2, y2 + fy),
                ):
                    if not (4 < aa < self.w - 4 and 4 < bb < self.h - 4):
                        continue
                    if not (4 < cc < self.w - 4 and 4 < dd < self.h - 4):
                        continue
                    mid = _l_paths(aa, bb, cc, dd) + _detour_paths(aa, bb, cc, dd, self.w, self.h)
                    for m in mid[:20]:
                        cands.append([(x1, y1, aa, bb)] + m + [(cc, dd, x2, y2)])
        uniq, seen = [], set()
        for segs in cands:
            key = tuple((round(a, 2), round(b, 2), round(c, 2), round(d, 2)) for a, b, c, d in segs)
            if key in seen:
                continue
            seen.add(key)
            uniq.append(segs)
        return uniq

    def _commit(self, segs, layer, net, width, netcode, need_via, x1, y1, x2, y2):
        out = []
        if need_via:
            out.append(via(x1, y1, netcode))
            out.append(via(x2, y2, netcode))
        for a, b, c, d in segs:
            if abs(a - c) < 0.01 and abs(b - d) < 0.01:
                continue
            out.append(track(a, b, c, d, width, layer, netcode))
            self.used.append((a, b, c, d, layer, net))
        return out

    def route_pair(self, x1, y1, x2, y2, net, width, netcode, use_astar=False):
        cands = self._candidates(x1, y1, x2, y2)
        # Keep B.Cu free for hard nets: geometric pass is F.Cu-only
        if use_astar:
            layer_order = [('B.Cu', True), ('F.Cu', False)]
        else:
            layer_order = [('F.Cu', False)]
        for layer, need_via in layer_order:
            for segs in cands:
                if _path_hits(segs, self.pads, net):
                    continue
                if self._hits_used(segs, layer, net):
                    continue
                return self._commit(segs, layer, net, width, netcode, need_via, x1, y1, x2, y2)
        # Explicit corridors (escape off pin columns then highway)
        corridors = []
        for hx in (88, 85, 80, 75, 70, 60, 50, 40, 30, 20, 12):
            corridors.append([(x1, y1, hx, y1), (hx, y1, hx, y2), (hx, y2, x2, y2)])
        for hy in (20, 28, 48, 56, 80, 90, 98, 105):
            corridors.append([(x1, y1, x1, hy), (x1, hy, x2, hy), (x2, hy, x2, y2)])
        for layer, need_via in layer_order:
            for segs in corridors:
                if _path_hits(segs, self.pads, net):
                    continue
                if self._hits_used(segs, layer, net):
                    continue
                return self._commit(segs, layer, net, width, netcode, need_via, x1, y1, x2, y2)
        if use_astar:
            for layer, need_via in layer_order:
                segs = _astar_path(x1, y1, x2, y2, self.pads, net, self.used, layer, self.w, self.h)
                if not segs:
                    continue
                if _path_hits(segs, self.pads, net) or self._hits_used(segs, layer, net):
                    continue
                return self._commit(segs, layer, net, width, netcode, need_via, x1, y1, x2, y2)
            # last resort: A* with slightly smaller keep via temporary pad shrink — still no ignore_used
            global PAD_KEEP
            old = PAD_KEEP
            PAD_KEEP = 0.85
            try:
                for layer, need_via in layer_order:
                    segs = _astar_path(x1, y1, x2, y2, self.pads, net, self.used, layer, self.w, self.h, step=1.27)
                    if not segs:
                        continue
                    if _path_hits(segs, self.pads, net) or self._hits_used(segs, layer, net):
                        continue
                    return self._commit(segs, layer, net, width, netcode, need_via, x1, y1, x2, y2)
            finally:
                PAD_KEEP = old
        return None

    def route_net(self, pts, net, width, netcode, use_astar=False):
        uniq, seen = [], set()
        for x, y in pts:
            key = (round(x, 2), round(y, 2))
            if key in seen:
                continue
            seen.add(key)
            uniq.append((x, y))
        if len(uniq) < 2:
            return [], True
        n = len(uniq)
        connected = {0}
        edges = []
        while len(connected) < n:
            best = None
            for i in connected:
                for j in range(n):
                    if j in connected:
                        continue
                    d = abs(uniq[i][0] - uniq[j][0]) + abs(uniq[i][1] - uniq[j][1])
                    if best is None or d < best[0]:
                        best = (d, i, j)
            if best is None:
                break
            _, i, j = best
            edges.append((uniq[i], uniq[j]))
            connected.add(j)
        segs, ok = [], True
        for a, b in edges:
            r = self.route_pair(a[0], a[1], b[0], b[1], net, width, netcode, use_astar=use_astar)
            if r is None:
                print(f'  ROUTE FAIL {net} ({a[0]:.1f},{a[1]:.1f})->({b[0]:.1f},{b[1]:.1f})', flush=True)
                ok = False
            else:
                segs.extend(r)
        return segs, ok



def generate_pcb():
    placements = {}
    pad_db = {}
    fp_texts = []
    nets = build_nets()
    net_names = sorted(nets.keys(), key=lambda n: (n != 'GND', n))
    if 'GND' in net_names:
        net_names.remove('GND')
        net_names.insert(0, 'GND')
    net_codes = {n: i + 1 for i, n in enumerate(net_names)}
    for ref, value, lib, mod, x, y, rot in PLACEMENT:
        raw = load_mod(lib, mod)
        pads = parse_pads(raw)
        body = embed_footprint(raw, ref, value, x, y, rot, f'/{ref}')
        body = assign_pad_nets(body, ref, nets, net_codes)
        body = strip_antenna_zones(body)
        indented = '\n'.join(('  ' + ln) if ln else ln for ln in body.splitlines())
        fp_texts.append(indented)
        placements[ref] = (x, y, rot)
        pad_db[ref] = pads

    def abs_pad(ref, pnum):
        x, y, rot = placements[ref]
        cands = [p for p in pad_db[ref] if p['num'] == pnum]
        if not cands:
            raise KeyError(f'{ref}.{pnum}')
        return pad_abs(x, y, rot, cands[0])

    net_decls = ['  (net 0 "")']
    for n, c in sorted(net_codes.items(), key=lambda kv: kv[1]):
        net_decls.append(f'  (net {c} "{n}")')

    # Build pad list per net + register foreign-pad obstacles
    net_pts = {}
    for net, members in nets.items():
        pts = []
        for ref, pnum in members:
            try:
                if pnum == 'SH':
                    x, y, rot = placements[ref]
                    for p in pad_db[ref]:
                        if p['num'] == 'SH':
                            pts.append(pad_abs(x, y, rot, p))
                else:
                    pts.append(abs_pad(ref, pnum))
            except KeyError:
                print('WARN missing', ref, pnum)
        net_pts[net] = pts

    router = BoardRouter(BOARD_W, BOARD_H)
    # ALL pads are obstacles — including NC / unassigned (prevents shorts through Pico)
    pad_net_lookup = {}
    for net, members in nets.items():
        for ref, pnum in members:
            pad_net_lookup[(ref, pnum)] = net
    for ref, (x, y, rot) in placements.items():
        for p in pad_db[ref]:
            n = pad_net_lookup.get((ref, p['num']), '')
            ax, ay = pad_abs(x, y, rot, p)
            # Block highways through Pico / DIP pin grids only
            router.add_pad(ax, ay, n, block_highway=(ref in ('U1', 'SKT_MODEM')))

    route_parts = []
    route_fails = []
    # Short local first; power with tracks (GND = B.Cu pour only)
    preferred = [
        'USB_DP', 'USB_DM', 'BOOTSEL',
        'AF_TX', 'AF_RX', 'PTT_OC', 'PTT_B', 'PTT_DRV',
        'LED_PTT_N', 'LED_DCD_N', 'LED_TXRX_N',
        'LED_PWR_A', 'LED_PTT_A', 'LED_DCD_A', 'LED_TXRX_A',
        'I2C_SDA_3V3', 'I2C_SCL_3V3', 'I2C_SDA_5V', 'I2C_SCL_5V', '3V3',
        'OSC1', 'OSC2', 'TRS_N', 'TXR1_N', 'TXR2_N',
        'RXA', 'TXA', 'TX_LVL', 'CDL',
        'MODEM_TXD', 'MODEM_RXD', 'MODEM_CDT',
        'AF_TX', 'AF_RX',
        '3V3', 'VIN_12', 'VBUS', '+5V_REG', '+5V', '+5V_OR',
    ]
    order = [n for n in preferred if n in net_pts]
    for n in sorted(net_pts.keys()):
        if n not in order and n not in ('GND', 'LCD_VO'):
            order.append(n)
    for net in order:
        pts = net_pts[net]
        if len(pts) < 2:
            continue
        code = net_codes[net]
        w = width_for(net)
        if net == '+5V_OR':
            print('Skip track MST for +5V_OR (full F.Cu zone pour)', flush=True)
            continue
        print(f'Routing {net} ({len(pts)} pads)...', flush=True)
        segs, ok = router.route_net(pts, net, w, code, use_astar=False)
        route_parts.extend(segs)
        if not ok:
            route_fails.append(net)
    # Second pass with A* for hard nets — never ignore_used (no shorts)
    if route_fails:
        still = []
        for net in list(route_fails):
            # Drop any partial tracks for this net before full re-route
            router.used = [u for u in router.used if u[5] != net]
            route_parts[:] = [t for t in route_parts if f'(net {net_codes[net]})' not in t and f'(net {net_codes[net]}\n' not in t]
            # filter track sexpr by net code
            code = net_codes[net]
            route_parts[:] = [t for t in route_parts if f'(net {code})' not in t]
            pts = net_pts[net]
            w = width_for(net)
            print(f'Retry A* {net}...', flush=True)
            segs, ok = router.route_net(pts, net, w, code, use_astar=True)
            route_parts.extend(segs)
            if not ok:
                still.append(net)
        route_fails = still

    # Last resort: B.Cu edge paths, pad obstacles only (B was kept free in geometric pass)
    if route_fails:
        still = []
        for net in list(route_fails):
            code = net_codes[net]
            router.used = [u for u in router.used if u[5] != net]
            route_parts[:] = [t for t in route_parts if f'(net {code})' not in t]
            pts = net_pts[net]
            w = width_for(net)
            print(f'Edge B.Cu {net}...', flush=True)
            # Ignore existing used entirely for this pass — B.Cu should be empty of our tracks
            saved = router.used
            router.used = []
            segs, ok = router.route_net(pts, net, w, code, use_astar=True)
            router.used = saved + [u for u in router.used]
            route_parts.extend(segs)
            if not ok:
                # Explicit south-edge polyline between MST pairs
                uniq = []
                seen = set()
                for x, y in pts:
                    k = (round(x, 2), round(y, 2))
                    if k in seen:
                        continue
                    seen.add(k)
                    uniq.append((x, y))
                ok2 = True
                connected = {0}
                while len(connected) < len(uniq):
                    best = None
                    for i in connected:
                        for j in range(len(uniq)):
                            if j in connected:
                                continue
                            d = abs(uniq[i][0] - uniq[j][0]) + abs(uniq[i][1] - uniq[j][1])
                            if best is None or d < best[0]:
                                best = (d, i, j)
                    _, i, j = best
                    connected.add(j)
                    x1, y1 = uniq[i]
                    x2, y2 = uniq[j]
                    hy = BOARD_H - 5
                    segs2 = [(x1, y1, x1, hy), (x1, hy, x2, hy), (x2, hy, x2, y2)]
                    if _path_hits(segs2, router.pads, net):
                        hy = 5
                        segs2 = [(x1, y1, x1, hy), (x1, hy, x2, hy), (x2, hy, x2, y2)]
                    if _path_hits(segs2, router.pads, net):
                        print(f'  MANUAL EDGE FAIL {net}', flush=True)
                        ok2 = False
                        break
                    route_parts.extend(router._commit(segs2, 'B.Cu', net, w, code, True, x1, y1, x2, y2))
                ok = ok2
            if not ok:
                still.append(net)
        route_fails = still
    if route_fails:
        print('ROUTE FAILS (route remaining in GUI):', ', '.join(route_fails), flush=True)
    else:
        print('All routed nets OK (GND=B.Cu pour; +5V_OR=F.Cu pour; LCD_VO intentional; BOOTSEL flying lead)', flush=True)

    # --- Post-route stitches (short hops; purge old tracks for these nets first) ---
    def purge_net_tracks(net):
        code = net_codes[net]
        router.used = [u for u in router.used if u[5] != net]
        route_parts[:] = [t for t in route_parts if f'(net {code})' not in t]

    def stitch(ref_a, pa, ref_b, pb, net):
        code = net_codes[net]
        w = width_for(net)
        x1, y1 = abs_pad(ref_a, pa)
        x2, y2 = abs_pad(ref_b, pb)
        for segs in ([(x1, y1, x2, y1), (x2, y1, x2, y2)], [(x1, y1, x1, y2), (x1, y2, x2, y2)]):
            if _path_hits(segs, router.pads, net):
                continue
            route_parts.extend(router._commit(segs, 'F.Cu', net, w, code, False, x1, y1, x2, y2))
            return True
        print(f'  STITCH FAIL {net} {ref_a}.{pa}->{ref_b}.{pb}', flush=True)
        return False

    for nn in ('LED_PWR_A', 'LED_PTT_A', 'LED_DCD_A', 'LED_TXRX_A', '+5V', 'PTT_OC', 'AF_RX'):
        purge_net_tracks(nn)
    for ra, pa, rb, pb, nn in [
        ('R_LED1', '2', 'LED_PWR', '2', 'LED_PWR_A'),
        ('R_LED2', '2', 'LED_PTT', '2', 'LED_PTT_A'),
        ('R_LED3', '2', 'LED_DCD', '2', 'LED_DCD_A'),
        ('R_LED4', '2', 'LED_TXRX', '2', 'LED_TXRX_A'),
        ('Q1', '3', 'J_AF', '3', 'PTT_OC'),
    ]:
        stitch(ra, pa, rb, pb, nn)
    # +5V: F1.2 → D_OR1.2 along north edge (avoid +5V_OR pad 1)
    code = net_codes['+5V']
    w = width_for('+5V')
    f1 = abs_pad('F1', '2')
    d5 = abs_pad('D_OR1', '2')
    p5 = [(f1[0], f1[1], f1[0], 6.0), (f1[0], 6.0, d5[0], 6.0), (d5[0], 6.0, d5[0], d5[1])]
    if not _path_hits(p5, router.pads, '+5V'):
        route_parts.extend(router._commit(p5, 'F.Cu', '+5V', w, code, False, f1[0], f1[1], d5[0], d5[1]))
    # AF_RX: bottom corridor F.Cu (avoid C_RX RXA pad / J_AF AF_TX)
    code = net_codes['AF_RX']
    w = width_for('AF_RX')
    jx, jy = abs_pad('J_AF', '2')
    cx, cy = abs_pad('C_RX', '1')
    hy = BOARD_H - 6
    ex = min(jx + 5, BOARD_W - 4)
    af_segs = [(jx, jy, ex, jy), (ex, jy, ex, hy), (ex, hy, cx, hy), (cx, hy, cx, cy)]
    if not _path_hits(af_segs, router.pads, 'AF_RX'):
        route_parts.extend(router._commit(af_segs, 'F.Cu', 'AF_RX', w, code, False, jx, jy, cx, cy))
    else:
        route_parts.extend(router._commit(af_segs, 'B.Cu', 'AF_RX', w, code, True, jx, jy, cx, cy))
    # GND: via at each GND net member pad (B.Cu zone tie)
    gnd_code = net_codes['GND']
    gnd_seen = set()
    for ref, pnum in nets.get('GND', []):
        try:
            if pnum == 'SH':
                x0, y0, rot = placements[ref]
                for p in pad_db[ref]:
                    if p['num'] == 'SH':
                        px, py = pad_abs(x0, y0, rot, p)
                        k = (round(px, 2), round(py, 2))
                        if k not in gnd_seen:
                            gnd_seen.add(k)
                            route_parts.append(via(px, py, gnd_code))
            else:
                px, py = abs_pad(ref, pnum)
                k = (round(px, 2), round(py, 2))
                if k not in gnd_seen:
                    gnd_seen.add(k)
                    route_parts.append(via(px, py, gnd_code))
        except KeyError:
            pass

    v5_code = net_codes.get('+5V_OR', 0)

    def _zone(net_code, net_name, layer, priority, pts):
        poly = " ".join("(xy %s %s)" % (fmt(x), fmt(y)) for x, y in pts)
        parts = [
            "  (zone",
            "    (net %d)" % net_code,
            '    (net_name "%s")' % net_name,
            '    (layer "%s")' % layer,
            '    (uuid "%s")' % uid(),
            "    (hatch edge 0.5)",
            "    (priority %d)" % priority,
            "    (connect_pads (clearance 0.2))",
            "    (min_thickness 0.25)",
            "    (filled_areas_thickness no)",
            "    (fill yes (thermal_gap 0.5) (thermal_bridge_width 0.5))",
            "    (polygon (pts %s))" % poly,
            "  )",
        ]
        return "\n".join(parts)

    # GND = B.Cu pour; +5V_OR = F.Cu pour (tracks skipped — TH pads thermal to zone)
    zones = "\n".join([
        _zone(gnd_code, "GND", "B.Cu", 1, [(1, 1), (BOARD_W - 1, 1), (BOARD_W - 1, BOARD_H - 1), (1, BOARD_H - 1)]),
        _zone(v5_code, "+5V_OR", "F.Cu", 0, [(1, 1), (BOARD_W - 1, 1), (BOARD_W - 1, BOARD_H - 1), (1, BOARD_H - 1)]),
    ])

    silks = [
        silk(95, 2.5, 'T-Modem v0.25 GPLv3 AS-IS', 1.5),
        silk(24, 16, 'USB DEVICE', 1.0),
        silk(48, 28, 'to Pico Micro-USB cable', 0.8),
        silk(76, 20, '12V CENTRE+', 1.0),
        silk(98, 20, 'BOOTSEL SW1 + TP flying lead', 0.8),
        silk(182, 90, 'AF_TX', 0.9, 90),
        silk(182, 82, 'AF_RX', 0.9, 90),
        silk(182, 74, 'PTT', 0.9, 90),
        silk(182, 66, 'GND', 0.9, 90),
        silk(18, 44, 'SKT_MODEM / U_MODEM', 0.9),
        silk(42, 50, 'TRS->GND', 0.7),
        silk(42, 58, 'TXR1->GND 0R', 0.7),
        silk(28, 72, 'TXR2->+5V_OR 0R', 0.7),
        silk(28, 76, 'confirm datasheet', 0.8),
        silk(90, 96, 'J_LCD_I2C GND VCC SDA SCL', 0.8),
        silk(60, 96, 'U_LVL BSS138 LV=3V3 HV=+5V_OR', 0.8),
        silk(100, 34, 'U1 Pico H socket', 0.9),
        silk(120, 8, 'U_REG MP1584', 0.8),
        silk(128, 96, 'LCD_VO=RV2 wiper only (NC intentional)', 0.7),
    ]
    pcb = (
        '(kicad_pcb\n'
        '  (version 20241229)\n'
        '  (generator "t_modem_generate_board")\n'
        '  (generator_version "0.25")\n'
        '  (general (thickness 1.6) (legacy_teardrops no))\n'
        '  (paper "A4")\n'
        '  (title_block\n'
        '    (title "T-Modem")\n'
        '    (date "2026-07-21")\n'
        '    (rev "0.25")\n'
        '    (company "ngteq GPLv3 standard reference AS-IS")\n'
        '    (comment 1 "190x110 mm complete hand-solderable PCB")\n'
        '    (comment 2 "USB Path B + I2C LCD - NOT BayCom/SER12")\n'
        '  )\n'
        '  (layers\n'
        '    (0 "F.Cu" signal)\n    (31 "B.Cu" signal)\n'
        '    (32 "B.Adhes" user "B.Adhesive")\n    (33 "F.Adhes" user "F.Adhesive")\n'
        '    (34 "B.Paste" user)\n    (35 "F.Paste" user)\n'
        '    (36 "B.SilkS" user "B.Silkscreen")\n    (37 "F.SilkS" user "F.Silkscreen")\n'
        '    (38 "B.Mask" user)\n    (39 "F.Mask" user)\n'
        '    (40 "Dwgs.User" user)\n    (41 "Cmts.User" user)\n'
        '    (42 "Eco1.User" user)\n    (43 "Eco2.User" user)\n'
        '    (44 "Edge.Cuts" user)\n    (45 "Margin" user)\n'
        '    (46 "B.CrtYd" user)\n    (47 "F.CrtYd" user)\n'
        '    (48 "B.Fab" user)\n    (49 "F.Fab" user)\n'
        '  )\n'
        '  (setup\n'
        '    (pad_to_mask_clearance 0.05)\n'
        '    (allow_soldermask_bridges_in_footprints no)\n'
        '    (pcbplotparams\n'
        '      (layerselection 0x00010fc_ffffffff)\n'
        '      (plot_on_all_layers_selection 0x0000000_00000000)\n'
        '      (disableapertmacros no)\n'
        '      (usegerberextensions no)\n'
        '      (usegerberattributes yes)\n'
        '      (usegerberadvancedattributes yes)\n'
        '      (creategerberjobfile yes)\n'
        '      (dashed_line_dash_ratio 12.0)\n'
        '      (dashed_line_gap_ratio 3.0)\n'
        '      (svgprecision 4)\n'
        '      (plotframeref no)\n'
        '      (viasonmask no)\n'
        '      (mode 1)\n'
        '      (useauxorigin no)\n'
        '      (hpglpennumber 1)\n'
        '      (hpglpenspeed 20)\n'
        '      (hpglpendiameter 15.0)\n'
        '      (pdf_front_fp_property_popups yes)\n'
        '      (pdf_back_fp_property_popups yes)\n'
        '      (dxfpolygonmode yes)\n'
        '      (dxfimperialunits yes)\n'
        '      (dxfusepcbnewfont yes)\n'
        '      (psnegative no)\n'
        '      (psa4output no)\n'
        '      (plotreference yes)\n'
        '      (plotvalue yes)\n'
        '      (plotfptext yes)\n'
        '      (plotinvisibletext no)\n'
        '      (sketchpadsonfab no)\n'
        '      (subtractmaskfromsilk no)\n'
        '      (outputformat 1)\n'
        '      (mirror no)\n'
        '      (drillshape 1)\n'
        '      (scaleselection 1)\n'
        '      (outputdirectory "../../fab/gerbers/")\n'
        '    )\n'
        '  )\n'
        + '\n'.join(net_decls) + '\n'
        + edge_cuts() + '\n'
        + '\n'.join(silks) + '\n'
        + '\n'.join(fp_texts) + '\n'
        + '\n'.join(route_parts) + '\n'
        + zones + '\n)'
    )
    pcb = fixup_kicad10_layers(pcb)
    (ROOT / 't-modem.kicad_pcb').write_text(pcb, encoding='utf-8')
    print('Wrote', ROOT / 't-modem.kicad_pcb')
    print(f'Footprints: {len(PLACEMENT)}  Nets: {len(net_codes)}  Track segs: {len(route_parts)}')

def update_pro():
    (ROOT / 'sym-lib-table').write_text(
        '(sym_lib_table\n  (version 7)\n'
        '  (lib (name "t-modem")(type "KiCad")(uri "${KIPRJMOD}/t-modem.kicad_sym")(options "")(descr "T-Modem custom"))\n)\n',
        encoding='utf-8')
    print('Wrote sym-lib-table')

def main():
    generate_pcb()
    write_schematic()
    update_pro()
    print('Done.')

if __name__ == '__main__':
    main()

