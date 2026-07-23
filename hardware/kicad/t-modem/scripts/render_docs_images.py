#!/usr/bin/env python3
"""Render T-Modem docs images from the gold KiCad PCB (2D top/bottom + teaching explode).

Requires: kicad-cli, PyGObject (Rsvg), cairo, Pillow.

Outputs:
  <repo>/t-modem-c12s24-complete.png
  <repo>/docs/images/explode/t-modem-explode-0N-*.png  (10 panels)
"""

from __future__ import annotations

import math
import subprocess
import tempfile
from pathlib import Path

import cairo
import gi
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

gi.require_version("Rsvg", "2.0")
from gi.repository import Rsvg  # noqa: E402

REPO = Path(__file__).resolve().parents[4]
PCB = REPO / "hardware/kicad/t-modem/t-modem.kicad_pcb"
OUT_COMPLETE = REPO / "t-modem-c12s24-complete.png"
OUT_EXPLODE = REPO / "docs/images/explode"

BOARD_W_MM = 190.0
BOARD_H_MM = 110.0
# Builder-facing: front (USB/DC, KiCad Y≈0) at bottom of image — matches docs ASCII.
FLIP_Y = True

# Footprint centres from gold PCB (mm, KiCad coords).
POS = {
    "U1": (100.0, 36.0),
    "SKT_MODEM": (22.0, 52.0),
    "Y1": (40.0, 42.0),
    "J_AF": (182.0, 78.0),
    "J_USB": (22.0, 8.0),
    "J_DC": (74.0, 12.0),
    "J_LCD_I2C": (100.0, 101.45),
    "U_LVL": (72.0, 101.45),
    "U_REG": (140.0, 14.0),
    "SW1": (98.0, 12.0),
    "LED_PWR": (178.0, 28.0),
    "LED_PTT": (178.0, 40.0),
    "LED_DCD": (178.0, 52.0),
    "LED_TXRX": (178.0, 64.0),
    "RV1": (58.0, 80.0),
    "RV2": (128.0, 100.0),
    "RV_CDL": (58.0, 94.0),
    "Q1": (148.0, 58.0),
    "R_TRS": (42.0, 54.0),
    "R_TXR1": (42.0, 62.0),
    "R_TXR2": (27.9, 68.0),
    "J_USB_PICO": (48.0, 22.0),
    "TP_BOOTSEL": (112.0, 12.0),
    "F1": (154.0, 14.0),
    "H1": (6.0, 6.0),
    "H2": (184.0, 6.0),
    "H3": (6.0, 104.0),
    "H4": (184.0, 104.0),
}

# Highlight boxes (cx, cy, w, h) in KiCad mm.
BOX = {
    "outline": (95.0, 55.0, 188.0, 108.0),
    "pico": (100.0, 36.0, 28.0, 58.0),
    "modem": (22.0, 52.0, 22.0, 28.0),
    "crystal": (40.0, 42.0, 18.0, 20.0),
    "radio": (175.0, 70.0, 28.0, 40.0),
    "lcd": (90.0, 100.0, 70.0, 18.0),
    "usb": (35.0, 14.0, 55.0, 24.0),
    "straps_leds": (110.0, 55.0, 140.0, 70.0),
    "power": (125.0, 16.0, 90.0, 28.0),
}


def find_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ):
        p = Path(path)
        if p.is_file():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def mm_to_xy(x_mm: float, y_mm: float, ox: float, oy: float, scale: float) -> tuple[float, float]:
    y = (BOARD_H_MM - y_mm) if FLIP_Y else y_mm
    return ox + x_mm * scale, oy + y * scale


def export_svgs(tmp: Path) -> tuple[Path, Path]:
    top = tmp / "top.svg"
    bot = tmp / "bottom.svg"
    layers_top = "F.Cu,F.SilkS,F.Mask,F.Fab,Edge.Cuts,User.Drawings,User.Comments"
    layers_bot = "B.Cu,B.SilkS,B.Mask,B.Fab,Edge.Cuts"
    common = [
        "kicad-cli",
        "pcb",
        "export",
        "svg",
        "--mode-single",
        "--page-size-mode",
        "2",
        "--exclude-drawing-sheet",
        "--fit-page-to-board",
        "--drill-shape-opt",
        "2",
        "--subtract-soldermask",
    ]
    subprocess.run(
        common + ["-o", str(top), "--layers", layers_top, str(PCB)],
        check=True,
    )
    subprocess.run(
        common + ["-o", str(bot), "--layers", layers_bot, "--mirror", str(PCB)],
        check=True,
    )
    return top, bot


def svg_to_png(svg: Path, scale_px_per_mm: float) -> Image.Image:
    handle = Rsvg.Handle.new_from_file(str(svg))
    w = int(math.ceil(BOARD_W_MM * scale_px_per_mm))
    h = int(math.ceil(BOARD_H_MM * scale_px_per_mm))
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = cairo.Context(surf)
    ctx.set_source_rgb(1, 1, 1)
    ctx.paint()
    ctx.scale(scale_px_per_mm, scale_px_per_mm)
    vp = Rsvg.Rectangle()
    vp.x = 0
    vp.y = 0
    vp.width = BOARD_W_MM
    vp.height = BOARD_H_MM
    handle.render_document(ctx, vp)
    buf = surf.get_data()
    # Cairo ARGB32 little-endian → BGRA
    im = Image.frombuffer("RGBA", (w, h), bytes(buf), "raw", "BGRA", 0, 1).convert("RGB")
    if FLIP_Y:
        im = im.transpose(Image.FLIP_TOP_BOTTOM)
    return im


def board_canvas(
    board: Image.Image,
    canvas_w: int,
    canvas_h: int,
    margin: int = 48,
    title_h: int = 72,
) -> tuple[Image.Image, float, float, float]:
    """Place board on canvas; return image, origin_x, origin_y, scale_px_per_mm."""
    avail_w = canvas_w - 2 * margin
    avail_h = canvas_h - title_h - margin - 36
    scale = min(avail_w / BOARD_W_MM, avail_h / BOARD_H_MM)
    bw = int(BOARD_W_MM * scale)
    bh = int(BOARD_H_MM * scale)
    board_r = board.resize((bw, bh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (canvas_w, canvas_h), (248, 248, 246))
    ox = (canvas_w - bw) // 2
    oy = title_h + (avail_h - bh) // 2
    canvas.paste(board_r, (ox, oy))
    return canvas, float(ox), float(oy), scale


def draw_title(draw: ImageDraw.ImageDraw, text: str, sub: str, w: int) -> None:
    font_t = find_font(28)
    font_s = find_font(16)
    draw.text((24, 16), text, fill=(20, 20, 20), font=font_t)
    draw.text((24, 48), sub, fill=(70, 70, 70), font=font_s)
    draw.line((24, 68, w - 24, 68), fill=(180, 180, 180), width=1)


def draw_box(
    draw: ImageDraw.ImageDraw,
    ox: float,
    oy: float,
    scale: float,
    cx: float,
    cy: float,
    bw: float,
    bh: float,
    color: tuple[int, int, int] = (220, 40, 40),
    width: int = 3,
) -> None:
    x0, y0 = mm_to_xy(cx - bw / 2, cy + bh / 2, ox, oy, scale)
    x1, y1 = mm_to_xy(cx + bw / 2, cy - bh / 2, ox, oy, scale)
    draw.rectangle([x0, y0, x1, y1], outline=color, width=width)


def draw_callout(
    draw: ImageDraw.ImageDraw,
    ox: float,
    oy: float,
    scale: float,
    x_mm: float,
    y_mm: float,
    label: str,
    side: str = "right",
    color: tuple[int, int, int] = (30, 30, 30),
) -> None:
    font = find_font(15)
    px, py = mm_to_xy(x_mm, y_mm, ox, oy, scale)
    if side == "right":
        tx, ty = px + 28, py - 8
        draw.line([(px, py), (px + 18, py), (tx - 4, ty + 8)], fill=color, width=2)
    elif side == "left":
        tx, ty = px - 160, py - 8
        draw.line([(px, py), (px - 18, py), (tx + 140, ty + 8)], fill=color, width=2)
    elif side == "up":
        tx, ty = px + 8, py - 36
        draw.line([(px, py), (px, py - 18), (tx, ty + 14)], fill=color, width=2)
    else:
        tx, ty = px + 8, py + 18
        draw.line([(px, py), (px, py + 14), (tx, ty)], fill=color, width=2)
    # background pill
    bbox = draw.textbbox((tx, ty), label, font=font)
    pad = 4
    draw.rectangle(
        [bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad],
        fill=(255, 255, 255),
        outline=color,
    )
    draw.text((tx, ty), label, fill=color, font=font)


def dim_except_boxes(
    base: Image.Image,
    ox: float,
    oy: float,
    scale: float,
    boxes: list[tuple[float, float, float, float]],
    dim: float = 0.38,
) -> Image.Image:
    """Dim whole image then restore rectangular highlight regions."""
    faded = ImageEnhance.Brightness(base).enhance(dim)
    faded = ImageEnhance.Color(faded).enhance(0.55)
    out = faded.copy()
    for cx, cy, bw, bh in boxes:
        x0, y0 = mm_to_xy(cx - bw / 2, cy + bh / 2, ox, oy, scale)
        x1, y1 = mm_to_xy(cx + bw / 2, cy - bh / 2, ox, oy, scale)
        box = (int(min(x0, x1)), int(min(y0, y1)), int(max(x0, x1)), int(max(y0, y1)))
        region = base.crop(box)
        out.paste(region, box)
    return out


def make_complete(top_board: Image.Image, bottom_board: Image.Image) -> Image.Image:
    W, H = 1600, 1180
    canvas = Image.new("RGB", (W, H), (248, 248, 246))
    draw = ImageDraw.Draw(canvas)
    draw_title(
        draw,
        "T-Modem-c12s24 — complete board (from KiCad PCB)",
        "chip 1200 · software 2400 · v0.25 · GPLv3 · AS-IS · standard reference",
        W,
    )

    # Top view (large)
    top_area_h = 720
    scale = min((W - 80) / BOARD_W_MM, (top_area_h - 40) / BOARD_H_MM)
    tw, th = int(BOARD_W_MM * scale), int(BOARD_H_MM * scale)
    top_r = top_board.resize((tw, th), Image.Resampling.LANCZOS)
    ox = (W - tw) // 2
    oy = 88
    canvas.paste(top_r, (ox, oy))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([ox - 1, oy - 1, ox + tw + 1, oy + th + 1], outline=(60, 60, 60), width=2)

    callouts = [
        ("U1", "U1 Pico H (socket)", "right"),
        ("SKT_MODEM", "SKT_MODEM / TCM3105", "left"),
        ("Y1", "Y1 4.433619 MHz", "up"),
        ("J_AF", "J_AF radio AF/PTT", "left"),
        ("J_USB", "J_USB USB-A Path B", "down"),
        ("J_DC", "J_DC 12 V CENTRE+", "down"),
        ("J_LCD_I2C", "J_LCD_I2C + U_LVL", "up"),
        ("U_REG", "U_REG MP1584 + F1", "up"),
        ("LED_PWR", "LEDs PWR/PTT/DCD/TXRX", "left"),
        ("RV1", "RV1 TX · RV_CDL", "right"),
    ]
    for ref, label, side in callouts:
        x, y = POS[ref]
        draw_callout(draw, ox, oy, scale, x, y, label, side=side)

    # Bottom strip
    bot_scale = min(520 / BOARD_W_MM, 220 / BOARD_H_MM)
    bw, bh = int(BOARD_W_MM * bot_scale), int(BOARD_H_MM * bot_scale)
    bot_r = bottom_board.resize((bw, bh), Image.Resampling.LANCZOS)
    bx, by = 40, H - bh - 48
    canvas.paste(bot_r, (bx, by))
    draw.rectangle([bx - 1, by - 1, bx + bw + 1, by + bh + 1], outline=(60, 60, 60), width=1)
    font = find_font(14)
    draw.text((bx, by - 22), "Bottom (B.Cu / silk, mirrored)", fill=(40, 40, 40), font=font)

    note = (
        "Top view: front edge (USB / DC / BOOTSEL) at bottom of image · "
        "190×110 mm · gold: hardware/kicad/t-modem/t-modem.kicad_pcb"
    )
    draw.text((40, H - 28), note, fill=(90, 90, 90), font=find_font(13))
    draw.text((W - 280, H - 28), "https://github.com/ngteq/T-Modem", fill=(90, 90, 90), font=find_font(13))
    return canvas


def make_panel(
    board: Image.Image,
    step: int,
    title: str,
    subtitle: str,
    highlight: list[str],
    callouts: list[tuple[str, str, str]],
    footer: str,
) -> Image.Image:
    W, H = 1536, 1024
    base, ox, oy, scale = board_canvas(board, W, H, margin=56, title_h=78)
    boxes = [BOX[k] for k in highlight if k in BOX]
    if boxes:
        base = dim_except_boxes(base, ox, oy, scale, boxes, dim=0.42)
    draw = ImageDraw.Draw(base)
    draw_title(draw, f"{step:02d} · {title}", subtitle, W)
    for key in highlight:
        if key in BOX:
            cx, cy, bw, bh = BOX[key]
            draw_box(draw, ox, oy, scale, cx, cy, bw, bh, color=(200, 30, 30), width=3)
    for ref, label, side in callouts:
        if ref not in POS:
            continue
        x, y = POS[ref]
        draw_callout(draw, ox, oy, scale, x, y, label, side=side, color=(25, 25, 25))
    draw.text((24, H - 28), footer, fill=(90, 90, 90), font=find_font(13))
    draw.text((W - 200, H - 28), f"Panel {step}/10", fill=(90, 90, 90), font=find_font(13))
    return base


def main() -> None:
    if not PCB.is_file():
        raise SystemExit(f"missing PCB: {PCB}")
    OUT_EXPLODE.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="tmodem-render-") as td:
        tmp = Path(td)
        top_svg, bot_svg = export_svgs(tmp)
        top = svg_to_png(top_svg, scale_px_per_mm=14.0)
        bot = svg_to_png(bot_svg, scale_px_per_mm=14.0)
        # keep raw exports for debugging (optional copy)
        (tmp / "keep").mkdir(exist_ok=True)

    complete = make_complete(top, bot)
    complete.save(OUT_COMPLETE, "PNG", optimize=True)
    print(f"wrote {OUT_COMPLETE}")

    panels: list[tuple[str, str, str, list[str], list[tuple[str, str, str]], str]] = [
        (
            "t-modem-explode-01-board-outline.png",
            "Board outline",
            "190 × 110 mm · M3 holes · Edge.Cuts — empty teaching frame from gold PCB",
            ["outline"],
            [
                ("H1", "H1 M3", "down"),
                ("H2", "H2 M3", "down"),
                ("H3", "H3 M3", "up"),
                ("H4", "H4 M3", "up"),
            ],
            "Step 1 — know the board size and mounting before stuffing parts",
        ),
        (
            "t-modem-explode-02-pico.png",
            "Raspberry Pi Pico",
            "U1 · RaspberryPi_Pico_Common_THT · Pico H plugs into female headers",
            ["pico"],
            [
                ("U1", "U1 Pico H", "right"),
                ("SW1", "SW1 BOOTSEL", "down"),
                ("TP_BOOTSEL", "TP_BOOTSEL flying lead", "down"),
            ],
            "Step 2 — MCU centre · USB end of Pico toward front edge",
        ),
        (
            "t-modem-explode-03-modem-socket.png",
            "Modem socket · TCM3105",
            "SKT_MODEM DIP-16 · do not solder the IC directly — socket first",
            ["modem"],
            [
                ("SKT_MODEM", "SKT_MODEM DIP-16", "right"),
            ],
            "Step 3 — PHY chip class: TCM3105 (c12) · socketed for service",
        ),
        (
            "t-modem-explode-04-crystal.png",
            "Crystal · load caps",
            "Y1 HC-49-U 4.433619 MHz · C_Y1 / C_Y2 22 pF beside modem",
            ["crystal"],
            [
                ("Y1", "Y1 4.433619", "right"),
            ],
            "Step 4 — short analog path: crystal next to TCM3105",
        ),
        (
            "t-modem-explode-05-radio-af.png",
            "Radio AF · PTT",
            "J_AF Phoenix 1×4 · AF_TX AF_RX PTT GND · Q1 2N2222A driver",
            ["radio"],
            [
                ("J_AF", "J_AF screw terminal", "left"),
                ("Q1", "Q1 2N2222A PTT", "left"),
            ],
            "Step 5 — radio interconnect on the right edge",
        ),
        (
            "t-modem-explode-06-lcd-i2c.png",
            "LCD · I²C · level shift",
            "J_LCD_I2C GND VCC SDA SCL · U_LVL BSS138 · RV2 contrast optional",
            ["lcd"],
            [
                ("J_LCD_I2C", "J_LCD_I2C", "down"),
                ("U_LVL", "U_LVL BSS138", "down"),
                ("RV2", "RV2 contrast", "left"),
            ],
            "Step 6 — default display path: I²C backpack via level shifter",
        ),
        (
            "t-modem-explode-07-usb.png",
            "USB Path B",
            "J_USB Type-A device · J_USB_PICO cable to Pico Micro-USB · D+/D− + VBUS",
            ["usb"],
            [
                ("J_USB", "J_USB USB-A", "up"),
                ("J_USB_PICO", "J_USB_PICO → Pico", "right"),
            ],
            "Step 7 — USB DEVICE on board; Path B data cable to Pico",
        ),
        (
            "t-modem-explode-08-straps-leds.png",
            "Straps · LEDs · trimmers",
            "0 Ω straps R_TRS / R_TXR* · LEDs PWR PTT DCD TXRX · RV1 TX · RV_CDL",
            ["straps_leds"],
            [
                ("R_TRS", "0 Ω straps", "right"),
                ("LED_PWR", "LED row", "left"),
                ("RV1", "RV1 / RV_CDL", "right"),
            ],
            "Step 8 — confirm strap silk vs TCM3105 datasheet before power",
        ),
        (
            "t-modem-explode-09-power-dc.png",
            "12 V · buck · OR-ing",
            "J_DC 12 V CENTRE+ · U_REG MP1584 · F1 · Schottky OR into +5V_OR",
            ["power"],
            [
                ("J_DC", "J_DC 12 V", "down"),
                ("U_REG", "U_REG MP1584", "up"),
                ("F1", "F1 fuse", "up"),
            ],
            "Step 9 — bring up 12 V alone → measure +5V_OR ≈ 5 V before USB-only path",
        ),
        (
            "t-modem-explode-10-complete-stack.png",
            "Complete stack",
            "All subsystems on one board — insert IC · Pico · LCD after soldering sockets",
            ["outline", "pico", "modem", "crystal", "radio", "lcd", "usb", "power"],
            [
                ("U1", "Pico", "right"),
                ("SKT_MODEM", "TCM3105", "left"),
                ("J_AF", "Radio", "left"),
                ("J_USB", "USB", "down"),
                ("J_LCD_I2C", "LCD I²C", "up"),
                ("J_DC", "12 V", "down"),
            ],
            "Step 10 — RX before TX when RF is attached · AS-IS standard reference",
        ),
    ]

    # Remove old German/sketch explode names if still present
    for old in OUT_EXPLODE.glob("t-modem-explode-*.png"):
        old.unlink()

    for i, (fname, title, sub, hl, calls, foot) in enumerate(panels, start=1):
        img = make_panel(top, i, title, sub, hl, calls, foot)
        path = OUT_EXPLODE / fname
        img.save(path, "PNG", optimize=True)
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
