from reportlab.platypus import Flowable, SimpleDocTemplate, Paragraph, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

page_records = {}

class PageRecorder(Flowable):
    def __init__(self, key):
        super().__init__()
        self.key = key
        self.width = 0
        self.height = 0

    def draw(self):
        page_records[self.key] = self.canv._pageNumber

styles = getSampleStyleSheet()
doc = SimpleDocTemplate("scratch/test_recorder.pdf")
story = [
    PageRecorder("start"),
    Paragraph("Page 1", styles["Normal"]),
    PageBreak(),
    PageRecorder("chap1"),
    Paragraph("Page 2", styles["Normal"]),
]
doc.build(story)
print("Recorded pages:", page_records)
