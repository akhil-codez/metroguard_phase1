from reportlab.platypus import SimpleDocTemplate, Flowable, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class ChapterHeading(Flowable):
    def __init__(self, number, title, total_w=411.0):
        super().__init__()
        self.number = number # e.g. "Chapter 1" or "" for Abstract
        self.title = title   # e.g. "Introduction"
        self.total_w = total_w
        self.width = total_w
        if self.number:
            self.height = 115
        else:
            self.height = 65
            
    def draw(self):
        c = self.canv
        c.saveState()
        c.setFont("Times-Bold", 24.8)
        c.setFillColor(colors.black)
        
        if self.number:
            # Baseline for Chapter X
            c.drawString(0, self.height - 40, self.number)
            # Baseline for Title
            c.drawString(0, self.height - 40 - 45, self.title)
        else:
            # Baseline for Title
            c.drawString(0, self.height - 40, self.title)
            
        c.restoreState()

styles = getSampleStyleSheet()
body_style = ParagraphStyle(
    'KTU_Body',
    parent=styles['Normal'],
    fontName='Times-Roman',
    fontSize=12,
    leading=21.6,
    alignment=4,
    firstLineIndent=18
)

doc = SimpleDocTemplate("scratch/test_ch_heading.pdf", pagesize=A4, leftMargin=3.5*cm, rightMargin=3.0*cm, topMargin=1.5*cm, bottomMargin=3.5*cm)
story = [
    ChapterHeading("Chapter 1", "Introduction"),
    Spacer(1, 15),
    Paragraph("Modern urban mass transit systems constitute the vital arteries of contemporary smart cities, transporting tens of millions of commuters every day through sprawling underground and elevated metro networks.", body_style)
]
doc.build(story)
print("Built scratch/test_ch_heading.pdf")
