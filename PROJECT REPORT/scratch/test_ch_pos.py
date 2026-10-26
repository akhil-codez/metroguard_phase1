from reportlab.platypus import SimpleDocTemplate, Flowable, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import fitz

class ChapterHeading(Flowable):
    def __init__(self, number, title, total_w=411.0):
        super().__init__()
        self.number = number
        self.title = title
        self.total_w = total_w
        self.width = total_w
        if self.number:
            self.height = 160
        else:
            self.height = 110
            
    def draw(self):
        c = self.canv
        c.saveState()
        c.setFont("Times-Bold", 24.8)
        c.setFillColor(colors.black)
        
        if self.number:
            c.drawString(0, self.height - 90, self.number)
            c.drawString(0, self.height - 90 - 55, self.title)
        else:
            c.drawString(0, self.height - 90, self.title)
            
        c.restoreState()

doc = SimpleDocTemplate("scratch/test_exact_ch.pdf", pagesize=A4, leftMargin=3.5*cm, rightMargin=3.0*cm, topMargin=1.5*cm, bottomMargin=3.5*cm)
story = [ChapterHeading("Chapter 1", "Introduction")]
doc.build(story)

doc_fitz = fitz.open("scratch/test_exact_ch.pdf")
p = doc_fitz[0]
blocks = p.get_text("dict")["blocks"]
for b in blocks:
    if "lines" in b:
        for l in b["lines"]:
            text = "".join(s["text"] for s in l["spans"]).strip()
            bbox = l["bbox"]
            print(f"'{text}': bbox=({bbox[0]:.1f}, {bbox[1]:.1f}, {bbox[2]:.1f}, {bbox[3]:.1f})")
