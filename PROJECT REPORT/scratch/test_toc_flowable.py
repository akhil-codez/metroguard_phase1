from reportlab.platypus import SimpleDocTemplate, Flowable, Spacer, PageBreak
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors

class TOCLine(Flowable):
    def __init__(self, num, title, page_str, is_bold=False, level=0, total_w=411.0):
        super().__init__()
        self.num = num
        self.title = title
        self.page_str = str(page_str)
        self.is_bold = is_bold
        self.level = level
        self.total_w = total_w
        self.font = "Times-Bold" if is_bold else "Times-Roman"
        self.size = 12
        self.width = total_w
        self.height = 22 if is_bold and level == 0 else 16

    def draw(self):
        c = self.canv
        c.saveState()
        c.setFont(self.font, self.size)
        c.setFillColor(colors.black)
        
        indent = 0 if self.level == 0 else (18 if self.level == 1 else 36)
        x_left = indent
        
        prefix = f"{self.num}   " if self.num else ""
        full_title = f"{prefix}{self.title}"
        c.drawString(x_left, 3, full_title)
        
        w_page = c.stringWidth(self.page_str, self.font, self.size)
        x_page = self.total_w - w_page
        c.drawString(x_page, 3, self.page_str)
        
        if not self.is_bold or self.level > 0:
            w_title = c.stringWidth(full_title, self.font, self.size)
            x_dots_start = x_left + w_title + 6
            x_dots_end = x_page - 6
            if x_dots_end > x_dots_start:
                dot_w = c.stringWidth(" .", "Times-Roman", self.size)
                num_dots = int((x_dots_end - x_dots_start) / dot_w)
                dots_str = " ." * num_dots
                c.setFont("Times-Roman", self.size)
                c.drawString(x_dots_start, 3, dots_str)
                
        c.restoreState()

doc = SimpleDocTemplate("scratch/test_toc.pdf", pagesize=A4, leftMargin=3.5*cm, rightMargin=3.0*cm, topMargin=1.5*cm, bottomMargin=3.5*cm)
story = [
    TOCLine("", "Abstract", "i", is_bold=True, level=0),
    TOCLine("", "Acknowledgement", "ii", is_bold=True, level=0),
    TOCLine("", "List of Figures", "iv", is_bold=True, level=0),
    TOCLine("", "List of Tables", "v", is_bold=True, level=0),
    TOCLine("", "List of Symbols", "vi", is_bold=True, level=0),
    Spacer(1, 10),
    TOCLine("1", "Introduction", "1", is_bold=True, level=0),
    TOCLine("1.1", "Background and Context", "1", is_bold=False, level=1),
    TOCLine("1.2", "Problem Identification", "2", is_bold=False, level=1),
    TOCLine("1.3", "Motivation", "3", is_bold=False, level=1),
    TOCLine("1.4", "Objectives of the Project", "4", is_bold=False, level=1),
    Spacer(1, 10),
    TOCLine("2", "Literature Review", "6", is_bold=True, level=0),
    TOCLine("2.1", "Multi-Source Information Fusion", "6", is_bold=False, level=1),
    TOCLine("2.2", "Abandoned Object and Baggage Detection", "8", is_bold=False, level=1),
]
doc.build(story)
print("Built scratch/test_toc.pdf successfully")
