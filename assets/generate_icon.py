"""Script to generate modern NovaCalc application icons (.png and .ico) using Pillow.
"""

from PIL import Image, ImageDraw, ImageFont
import math


def create_novacalc_icon():
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Draw rounded squircle background with gradient
    margin = 12
    corner_radius = 52

    # Create background mask with rounded rectangle
    base = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    base_draw = ImageDraw.Draw(base)
    base_draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=corner_radius,
        fill=(24, 20, 36, 255)
    )

    # Gradient overlay: Deep indigo to vibrant violet
    grad = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    for y in range(size):
        ratio = y / size
        # From #1e1b4b (30, 27, 75) to #7c3aed (124, 58, 237)
        r = int(24 + ratio * (110 - 24))
        g = int(20 + ratio * (45 - 20))
        b = int(40 + ratio * (210 - 40))
        for x in range(size):
            grad.putpixel((x, y), (r, g, b, 255))

    # Composite gradient with base mask
    bg = Image.composite(grad, Image.new("RGBA", (size, size), (0, 0, 0, 0)), base.split()[3])

    # Add subtle border highlight
    border_draw = ImageDraw.Draw(bg)
    border_draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=corner_radius,
        outline=(167, 139, 250, 160),
        width=3
    )

    # Inner decorative calculator display panel
    disp_x1, disp_y1 = margin + 28, margin + 28
    disp_x2, disp_y2 = size - margin - 28, margin + 76
    border_draw.rounded_rectangle(
        [disp_x1, disp_y1, disp_x2, disp_y2],
        radius=14,
        fill=(15, 12, 25, 230),
        outline=(139, 92, 246, 120),
        width=2
    )

    # Display indicator light / mini math text
    border_draw.ellipse([disp_x1 + 12, disp_y1 + 14, disp_x1 + 22, disp_y1 + 24], fill=(168, 85, 247, 255))
    # Display accent line
    border_draw.line([disp_x1 + 34, disp_y1 + 19, disp_x1 + 70, disp_y1 + 19], fill=(196, 181, 253, 180), width=3)
    # Right-aligned fake numbers line
    border_draw.line([disp_x2 - 50, disp_y1 + 19, disp_x2 - 14, disp_y1 + 19], fill=(245, 243, 255, 240), width=4)

    # Keypad grid matrix (4 columns, 3 rows)
    grid_y_start = margin + 94
    btn_w = 40
    btn_h = 32
    gap_x = 10
    gap_y = 10
    start_x = (size - (4 * btn_w + 3 * gap_x)) // 2

    key_colors = [
        # row 0 (sci functions)
        [(55, 48, 85), (55, 48, 85), (55, 48, 85), (109, 40, 217)],
        # row 1 (numbers)
        [(38, 35, 52), (38, 35, 52), (38, 35, 52), (124, 58, 237)],
        # row 2 (bottom row)
        [(38, 35, 52), (38, 35, 52), (139, 92, 246), (168, 85, 247)],
    ]

    for row in range(3):
        y_top = grid_y_start + row * (btn_h + gap_y)
        for col in range(4):
            x_left = start_x + col * (btn_w + gap_x)
            col_color = key_colors[row][col]
            border_draw.rounded_rectangle(
                [x_left, y_top, x_left + btn_w, y_top + btn_h],
                radius=8,
                fill=(*col_color, 255),
                outline=(196, 181, 253, 60),
                width=1
            )

    # Center floating mathematical symbol: elegant glowing square root or integral or sigma
    # Draw large stylized '=' or '√' symbol overlay
    # Let's draw an elegant radical and pi glyph or shiny accent
    border_draw.line([start_x + 10, grid_y_start + 16, start_x + 18, grid_y_start + 16], fill=(216, 180, 254, 255), width=2)
    border_draw.line([start_x + 14, grid_y_start + 12, start_x + 14, grid_y_start + 20], fill=(216, 180, 254, 255), width=2)

    # Save PNG
    bg.save("d:/Personal projects/Calculator/assets/icon.png", format="PNG")

    # Save ICO with multiple sizes
    icon_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    bg.save("d:/Personal projects/Calculator/assets/icon.ico", format="ICO", sizes=icon_sizes)
    print("Icon generated successfully!")


if __name__ == "__main__":
    create_novacalc_icon()
