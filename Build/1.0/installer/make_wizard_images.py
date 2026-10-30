"""Draws the two pictures the setup wizard shows (installer/wizard-large.bmp and wizard-small.bmp).

Run once after changing the app icon or the theme colours; the .bmp files are kept in the repository.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"
PRIMARY = (0x6B, 0x7B, 0x2C)   # theme.PRIMARY
PRIMARY_DARK = (0x56, 0x64, 0x23)  # theme.PRIMARY_HOVER
CREAM = (0xF2, 0xEF, 0xE7)     # theme.BG_CARD


def gradient(width: int, height: int) -> Image.Image:
    image = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(image)
    for y in range(height):
        t = y / (height - 1)
        draw.line([(0, y), (width, y)], fill=tuple(round(PRIMARY[i] + (PRIMARY_DARK[i] - PRIMARY[i]) * t) for i in range(3)))
    return image


def paste_icon(image: Image.Image, size: int, centre: tuple[int, int]) -> None:
    icon = Image.open(ASSETS / "app-icon-512.png").convert("RGBA").resize((size, size), Image.LANCZOS)
    image.paste(icon, (centre[0] - size // 2, centre[1] - size // 2), icon)


def main() -> None:
    scale = 2  # drawn at 200% for sharp text; Inno shrinks it on normal-DPI screens
    large = gradient(164 * scale, 314 * scale)
    paste_icon(large, 96 * scale, (82 * scale, 110 * scale))
    draw = ImageDraw.Draw(large)
    font = ImageFont.truetype(str(ASSETS / "fonts" / "Nunito-Bold.ttf"), 22 * scale)
    small_font = ImageFont.truetype(str(ASSETS / "fonts" / "Nunito-Regular.ttf"), 11 * scale)
    draw.text((82 * scale, 190 * scale), "Daily Fresh", font=font, fill=CREAM, anchor="mm")
    draw.text((82 * scale, 214 * scale), "Daily ledger", font=small_font, fill=CREAM, anchor="mm")
    large.save(HERE / "wizard-large.bmp")

    small = Image.new("RGB", (55 * scale, 55 * scale), CREAM)
    paste_icon(small, 44 * scale, (27 * scale + 1, 27 * scale + 1))
    small.save(HERE / "wizard-small.bmp")


if __name__ == "__main__":
    main()
