from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

c = canvas.Canvas("scratch/test_dots.pdf")
font = "Times-Roman"
size = 12

def make_toc_line(num, title, page_str, level=1, total_w=411.0):
    indent = 0 if level == 0 else (18 if level == 1 else 36)
    prefix = f"{num}   " if num else ""
    full_title = f"{prefix}{title} "
    w_title = c.stringWidth(full_title, font, size)
    w_page = c.stringWidth(f" {page_str}", font, size)
    gap = total_w - indent - w_title - w_page
    dot_w = c.stringWidth(" .", font, size)
    num_dots = max(0, int(gap / dot_w))
    dots = " ." * num_dots
    return indent, full_title, dots, page_str

lines = [
    ("", "Abstract", "i", 0),
    ("", "Acknowledgement", "ii", 0),
    ("", "List of Figures", "iv", 0),
    ("", "List of Tables", "v", 0),
    ("", "List of Symbols", "vi", 0),
    ("1", "Introduction", "1", 0),
    ("1.1", "Background and Context", "1", 1),
    ("1.2", "Problem Identification", "2", 1),
    ("1.3", "Motivation", "3", 1),
]

for l in lines:
    ind, t, d, p = make_toc_line(l[0], l[1], l[2], l[3])
    print(f"indent={ind:2d} | title='{t}' | dots='{d[:10]}...' ({len(d)} chars) | page={p}")
