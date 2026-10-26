# -*- coding: utf-8 -*-
"""
Generate high-quality KTU-compliant project_report.pdf for MetroGuard AI Phase-1.
Follows the exact fonts, margins, chapter headings, TOC dot leaders, and layout
of the KTU B.Tech LaTeX template (txfonts / Times New Roman, A4, 3.5cm/3.0cm margins).
"""

import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, PageBreak, Flowable
)
from reportlab.pdfgen import canvas

# Global page mapping recorded dynamically during two-pass build
PAGE_MAP = {}

def to_roman(n):
    """Convert integer to lowercase roman numerals."""
    if n <= 0:
        return ""
    val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    syb = ["m", "cm", "d", "cd", "c", "xc", "l", "xl", "x", "ix", "v", "iv", "i"]
    roman_num = ''
    i = 0
    while n > 0:
        for _ in range(n // val[i]):
            roman_num += syb[i]
            n -= val[i]
        i += 1
    return roman_num

class PageRecorder(Flowable):
    """Invisible flowable that records the canvas page number for dynamic TOC/LOF/LOT."""
    def __init__(self, key):
        super().__init__()
        self.key = key
        self.width = 0
        self.height = 0

    def draw(self):
        PAGE_MAP[self.key] = self.canv._pageNumber

class TOCLine(Flowable):
    """Renders a single line of Table of Contents, List of Figures, or List of Tables with dot leaders."""
    def __init__(self, num, title, page_str, is_bold=False, level=0, total_w=411.0, is_front=False):
        super().__init__()
        self.num = num
        self.title = title
        self.page_str = str(page_str)
        self.is_bold = is_bold
        self.level = level
        self.total_w = total_w
        self.is_front = is_front
        self.font = "Times-Bold" if is_bold else "Times-Roman"
        self.size = 12
        self.width = total_w
        # Matching LaTeX vertical spacing: 22pt before chapters, 16pt for sections
        self.height = 22 if (is_bold and level == 0 and not is_front) else 16.5

    def draw(self):
        c = self.canv
        c.saveState()
        c.setFont(self.font, self.size)
        c.setFillColor(colors.black)
        
        # Indentation matching LaTeX template
        if self.level == 0:
            indent = 0
        elif self.level == 1:
            indent = 18
        else:
            indent = 36
            
        x_left = indent
        
        prefix = f"{self.num}   " if self.num else ""
        full_title = f"{prefix}{self.title}"
        
        # Draw page number on right
        w_page = c.stringWidth(self.page_str, self.font, self.size)
        x_page = self.total_w - w_page
        c.drawString(x_page, 3, self.page_str)
        
        # Guard against title colliding with page number
        max_title_w = x_page - 16 - x_left
        w_title = c.stringWidth(full_title, self.font, self.size)
        if w_title > max_title_w:
            while len(full_title) > 3 and c.stringWidth(full_title + "...", self.font, self.size) > max_title_w:
                full_title = full_title[:-1]
            full_title = full_title + "..."
            w_title = c.stringWidth(full_title, self.font, self.size)
            
        # Draw title on left
        c.drawString(x_left, 3, full_title)
        
        # Draw dot leaders for sections, subsections, and lists
        # LaTeX report class: Chapters have NO dot leaders; sections/subsections and lists have dot leaders
        draw_dots = (not self.is_bold) or (self.level > 0)
        if draw_dots:
            x_dots_start = x_left + w_title + 6
            x_dots_end = x_page - 6
            if x_dots_end > x_dots_start:
                dot_w = c.stringWidth(" .", "Times-Roman", self.size)
                num_dots = int((x_dots_end - x_dots_start) / dot_w)
                dots_str = " ." * num_dots
                c.setFont("Times-Roman", self.size)
                c.drawString(x_dots_start, 3, dots_str)
                
        c.restoreState()

class ChapterHeading(Flowable):
    """
    Renders standard LaTeX report class chapter headings:
    'Chapter X' (Times-Bold 24.8pt)
    followed by gap
    'Title' (Times-Bold 24.8pt)
    with exact top margin offset matching LaTeX.
    """
    def __init__(self, number, title, total_w=411.0):
        super().__init__()
        self.number = number # e.g. "Chapter 1" or "" for unnumbered chapters (Abstract, etc.)
        self.title = title
        self.total_w = total_w
        self.width = total_w
        if self.number:
            self.height = 150 # top margin space + num + gap + title
        else:
            self.height = 95  # top margin space + title
            
    def draw(self):
        c = self.canv
        c.saveState()
        c.setFont("Times-Bold", 24.8)
        c.setFillColor(colors.black)
        
        if self.number:
            # Baseline for Chapter X at ~130pt from top of page
            c.drawString(0, self.height - 75, self.number)
            # Baseline for Title at ~190pt from top of page
            c.drawString(0, self.height - 75 - 55, self.title)
        else:
            # Baseline for unnumbered title at ~130pt from top of page
            c.drawString(0, self.height - 75, self.title)
            
        c.restoreState()

class NumberedCanvas(canvas.Canvas):
    """
    Two-stage canvas handling exact KTU LaTeX pagination:
    - Pages 1-4 (Cover, Vision & Mission, Certificate, Declaration): Completely unnumbered
    - Pages 5 to body_start - 1 (Abstract, Acknowledgement, Contents, LOF, LOT, Symbols): Roman numerals (i, ii, iii...)
    - Pages body_start onwards (Chapter 1 to References): Arabic numerals (1, 2, 3...)
    - NO running header line or header text at top (strictly matches template)
    - Page numbers centered at bottom (2.0 cm / 56.7 pt from bottom edge, pure black, Times-Roman 12pt)
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        body_start = PAGE_MAP.get("ch1", 12)
        
        for state in self._saved_page_states:
            self.__dict__.update(state)
            p = self._pageNumber
            
            # Pages 1, 2, 3, 4 are strictly unnumbered
            if p in [1, 2, 3, 4]:
                super().showPage()
                continue
                
            self.saveState()
            self.setFont("Times-Roman", 12)
            self.setFillColor(colors.black)
            
            if p < body_start:
                # Front matter Roman numerals (Abstract on page 5 gets 'i')
                roman_page = to_roman(p - 4)
                self.drawCentredString(A4[0] / 2.0, 2.0 * cm, roman_page)
            else:
                # Body Arabic numerals starting at 1 on Chapter 1
                body_page = p - body_start + 1
                self.drawCentredString(A4[0] / 2.0, 2.0 * cm, str(body_page))
                
            self.restoreState()
            super().showPage()
            
        super().save()

def get_page_str(key, is_front=False):
    """Helper to retrieve formatted page number string for dynamic TOC/LOF/LOT."""
    if key not in PAGE_MAP:
        return "1"
    raw_page = PAGE_MAP[key]
    body_start = PAGE_MAP.get("ch1", 12)
    if is_front or raw_page < body_start:
        return to_roman(max(1, raw_page - 4))
    else:
        return str(max(1, raw_page - body_start + 1))


def build_story(pass_num=1):
    """Constructs the ReportLab story flowables."""
    figures_dir = r"c:\Users\akhia\Downloads\metroguard_phase1\PROJECT REPORT\figures"
    simat_logo_path = os.path.join(figures_dir, "simatlogo.png")
    block_diag_path = os.path.join(figures_dir, "block_diagram.png")
    dash_path = os.path.join(figures_dir, "dashboard_ui.jpg")
    crowd_path = os.path.join(figures_dir, "crowd_result.jpg")
    ann_path = os.path.join(figures_dir, "annotated_frame.png")
    card_path = os.path.join(figures_dir, "benchmark_scorecard.png")
    plan_path = os.path.join(figures_dir, "work_plan.jpeg")
    gantt_path = os.path.join(figures_dir, "gantt_chart.jpeg")
    
    styles = getSampleStyleSheet()
    
    # -------------------------------------------------------------
    # FONT & PARAGRAPH STYLES (Matching LaTeX txfonts / Times-Roman)
    # -------------------------------------------------------------
    body_style = ParagraphStyle(
        'KTU_Body',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=21.6, # LaTeX linespread 1.5 -> 12 * 1.8 = 21.6 pt
        alignment=4,  # Justified
        firstLineIndent=18,
        spaceAfter=10
    )
    
    body_no_indent = ParagraphStyle(
        'KTU_BodyNoIndent',
        parent=body_style,
        firstLineIndent=0,
        spaceAfter=10
    )
    
    section_title_style = ParagraphStyle(
        'KTU_SectionTitle',
        fontName='Times-Bold',
        fontSize=17.2,
        leading=22,
        alignment=0,
        spaceBefore=22,
        spaceAfter=10,
        keepWithNext=True
    )
    
    subsection_title_style = ParagraphStyle(
        'KTU_SubSectionTitle',
        fontName='Times-Bold',
        fontSize=14.3,
        leading=18,
        alignment=0,
        spaceBefore=16,
        spaceAfter=8,
        keepWithNext=True
    )
    
    cover_main_title = ParagraphStyle(
        'KTU_CoverTitle',
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=22,
        alignment=1,
        spaceAfter=30
    )
    
    cover_subtitle = ParagraphStyle(
        'KTU_CoverSubtitle',
        fontName='Times-Italic',
        fontSize=13.5,
        leading=19,
        alignment=1,
        spaceAfter=14
    )
    
    cover_bold_center = ParagraphStyle(
        'KTU_CoverBoldCenter',
        fontName='Times-Bold',
        fontSize=13,
        leading=18,
        alignment=1,
        spaceAfter=6
    )
    
    cover_names = ParagraphStyle(
        'KTU_CoverNames',
        fontName='Times-Bold',
        fontSize=12,
        leading=18,
        alignment=1,
        spaceAfter=4
    )
    
    cover_dept = ParagraphStyle(
        'KTU_CoverDept',
        fontName='Times-Bold',
        fontSize=10,
        leading=14,
        alignment=1,
        spaceAfter=4
    )
    
    fig_caption_style = ParagraphStyle(
        'KTU_FigCaption',
        fontName='Times-Roman',
        fontSize=11,
        leading=15,
        alignment=1,
        spaceBefore=8,
        spaceAfter=14,
        keepWithNext=False
    )
    
    table_caption_style = ParagraphStyle(
        'KTU_TableCaption',
        fontName='Times-Roman',
        fontSize=11,
        leading=15,
        alignment=1,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    
    ref_style = ParagraphStyle(
        'KTU_Reference',
        fontName='Times-Roman',
        fontSize=10,
        leading=14.5,
        alignment=4,
        leftIndent=24,
        firstLineIndent=-24,
        spaceAfter=8
    )

    story = []
    
    # -------------------------------------------------------------
    # 1. COVER PAGE (Page 1 - Strictly Unnumbered)
    # -------------------------------------------------------------
    story.append(Spacer(1, 15))
    story.append(Paragraph("MULTI-EVENT INCIDENT INTELLIGENCE FRAMEWORK FOR SMART METRO SURVEILLANCE", cover_main_title))
    story.append(Spacer(1, 15))
    story.append(Paragraph("A Project Phase-1 Report<br/>Submitted to APJ Abdul Kalam Technological University<br/>in partial fulfillment of requirements for the award of degree", cover_subtitle))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Bachelor of Technology<br/>in<br/>Artificial Intelligence and Data Science", cover_bold_center))
    story.append(Spacer(1, 12))
    story.append(Paragraph("by", ParagraphStyle('By', fontName='Times-Roman', fontSize=12, alignment=1, spaceAfter=8)))
    story.append(Paragraph("ADITHYA CHANDRAN(SPT23AD006)", cover_names))
    story.append(Paragraph("AKHIL P(SPT23AD009)", cover_names))
    story.append(Paragraph("MUHAMMED SHIBIL KP(SPT23AD034)", cover_names))
    story.append(Paragraph("SHEHRUZ MUHAMMED CS(SPT23AD043)", cover_names))
    
    story.append(Spacer(1, 25))
    if os.path.exists(simat_logo_path):
        story.append(RLImage(simat_logo_path, width=2.2*inch, height=1.2*inch))
    
    story.append(Spacer(1, 30))
    story.append(Paragraph("DEPARTMENT OF ARTIFICIAL INTELLIGENCE AND DATA SCIENCE", cover_dept))
    story.append(Paragraph("SREEPATHY INSTITUTE OF MANAGEMENT AND TECHNOLOGY, VAVANOOR", cover_dept))
    story.append(Paragraph("KERALA", cover_dept))
    story.append(Paragraph("OCTOBER 2026", cover_dept))
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # 2. VISION AND MISSION (Page 2 - Strictly Unnumbered)
    # -------------------------------------------------------------
    story.append(Spacer(1, 10))
    if os.path.exists(simat_logo_path):
        story.append(RLImage(simat_logo_path, width=1.8*inch, height=1.0*inch))
    story.append(Spacer(1, 10))
    story.append(Paragraph("SREEPATHY INSTITUTE OF MANAGEMENT AND TECHNOLOGY, VAVANOOR", cover_bold_center))
    story.append(Paragraph("KOOTTANAD 679533", cover_bold_center))
    story.append(Spacer(1, 10))
    story.append(Paragraph("DEPARTMENT OF ARTIFICIAL INTELLIGENCE AND DATA SCIENCE", cover_bold_center))
    story.append(Spacer(1, 28))
    
    story.append(Paragraph("<u><b>Vision of Department</b></u>", cover_bold_center))
    story.append(Spacer(1, 8))
    story.append(Paragraph("To empower future innovators in artificial intelligence and data science, through quality education, transformative research, and to harness it for a positive global impact leading to sustainable advancements in technology and society.", ParagraphStyle('Vis', parent=body_no_indent, alignment=1)))
    story.append(Spacer(1, 22))
    
    story.append(Paragraph("<u><b>Mission of Department</b></u>", cover_bold_center))
    story.append(Spacer(1, 10))
    mission_text = (
        "• To build a skilled workforce for diverse career paths in industries ranging from healthcare and finance to cybersecurity and autonomous systems.<br/><br/>"
        "• To leverage research in AI and data science, to address critical societal challenges, drive economic growth, and improve the quality of life for individuals globally.<br/><br/>"
        "• To foster a culture of continuous learning and adaptation to stay abreast of rapid advancements in AI and data science through industry interaction."
    )
    story.append(Paragraph(mission_text, body_no_indent))
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # 3. CERTIFICATE (Page 3 - Strictly Unnumbered)
    # -------------------------------------------------------------
    story.append(Paragraph("<b>DEPT. OF ARTIFICIAL INTELLIGENCE AND DATA SCIENCE</b><br/><b>SREEPATHY INSTITUTE OF MANAGEMENT AND TECHNOLOGY</b><br/><b>VAVANOOR</b><br/><b>2026 - 2027</b>", cover_bold_center))
    story.append(Spacer(1, 10))
    if os.path.exists(simat_logo_path):
        story.append(RLImage(simat_logo_path, width=1.6*inch, height=0.85*inch))
    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>CERTIFICATE</b>", cover_bold_center))
    story.append(Spacer(1, 10))
    
    cert_body = (
        "This is to certify that the report entitled <b>MULTI-EVENT INCIDENT INTELLIGENCE FRAMEWORK FOR SMART METRO SURVEILLANCE</b> "
        "submitted by <b>ADITHYA CHANDRAN</b>(SPT23AD006), <b>AKHIL P</b>(SPT23AD009), <b>MUHAMMED SHIBIL KP</b>(SPT23AD034) &amp; "
        "<b>SHEHRUZ MUHAMMED CS</b>(SPT23AD043) to APJ Abdul Kalam Technological University in partial fulfillment of the B.Tech. "
        "degree in <b>Artificial Intelligence and Data Science</b> is a bonafide record of the project phase-1 work carried out by them "
        "under our guidance and supervision. This report in any form has not been submitted to any other University or Institute for any purpose."
    )
    story.append(Paragraph(cert_body, body_style))
    story.append(Spacer(1, 30))
    
    sig_data = [
        [Paragraph("<b>Ms. ARYA N S</b><br/>(Project Guide)<br/>Assistant Professor<br/>Dept. of AI &amp; DS<br/>SIMAT, Vavanoor", body_no_indent),
         Paragraph("<b>Ms. Sreeja P</b><br/>(Project Coordinator)<br/>Associate Professor<br/>Dept. of AI &amp; DS<br/>SIMAT, Vavanoor", body_no_indent)]
    ]
    sig_table = Table(sig_data, colWidths=[2.8*inch, 2.8*inch])
    sig_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(sig_table)
    
    story.append(Spacer(1, 24))
    story.append(Paragraph("<b>Ms. Sreeja P</b><br/>Associate Professor and Head<br/>Dept. of AI &amp; DS<br/>SIMAT, Vavanoor", cover_bold_center))
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # 4. DECLARATION (Page 4 - Strictly Unnumbered)
    # -------------------------------------------------------------
    story.append(Spacer(1, 30))
    story.append(Paragraph("<b>DECLARATION</b>", cover_bold_center))
    story.append(Spacer(1, 18))
    
    decl_p1 = (
        "We hereby declare that the project report <b>MULTI-EVENT INCIDENT INTELLIGENCE FRAMEWORK FOR SMART METRO SURVEILLANCE</b>, "
        "submitted for partial fulfillment of the requirements for the award of degree of Bachelor of Technology of APJ Abdul Kalam "
        "Technological University, Kerala is a bonafide work done by us under the supervision of <b>Ms. ARYA N S</b>."
    )
    decl_p2 = (
        "This submission represents our ideas in our own words and where ideas or words of others have been included, we have adequately "
        "and accurately cited and referenced the original sources."
    )
    decl_p3 = (
        "We also declare that we have adhered to ethics of academic honesty and integrity and have not misrepresented or fabricated any data "
        "or idea or fact or source in our submission. We understand that any violation of the above will be a cause for disciplinary action "
        "by the institute and/or the University and can also evoke penal action from the sources which have thus not been properly cited or from "
        "whom proper permission has not been obtained. This report has not previously formed the basis for the award of any degree, diploma "
        "or similar title of any other University."
    )
    story.append(Paragraph(decl_p1, body_style))
    story.append(Paragraph(decl_p2, body_style))
    story.append(Paragraph(decl_p3, body_style))
    story.append(Spacer(1, 35))
    
    decl_table_data = [
        [Paragraph("Vavanoor<br/>26-10-2026", body_no_indent),
         Paragraph("<b>ADITHYA CHANDRAN<br/>AKHIL P<br/>MUHAMMED SHIBIL KP<br/>SHEHRUZ MUHAMMED CS</b>", ParagraphStyle('DeclNames', parent=body_no_indent, alignment=2))]
    ]
    t_decl = Table(decl_table_data, colWidths=[2.8*inch, 2.8*inch])
    t_decl.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(t_decl)
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # 5. ABSTRACT (Page 5 - Roman i, Strictly Single Page)
    # -------------------------------------------------------------
    story.append(PageRecorder("abstract"))
    story.append(ChapterHeading("", "Abstract"))
    abs_1 = (
        "Urban mass transit networks transport millions of commuters daily, necessitating extensive closed-circuit television "
        "(CCTV) surveillance across platform concourses and transfer corridors. However, existing automated video surveillance systems "
        "operate predominantly as isolated, task-specific deep learning detectors that evaluate anomaly classes independently. Consequently, "
        "security control room dispatchers are overwhelmed by disjointed, unprioritized alarms that lack situational context, inducing "
        "operator fatigue and delaying critical emergency interventions."
    )
    abs_2 = (
        "To resolve these operational bottlenecks, this project presents <b>MetroGuard AI</b>: a unified multi-event incident intelligence "
        "framework engineered for real-time surveillance in smart metro environments. The platform transitions surveillance from siloed visual "
        "perception to context-aware spatiotemporal incident correlation and automated priority ranking. In this Project Phase-I implementation, "
        "an edge-capable commuter monitoring pipeline has been engineered. The architecture integrates Ultralytics YOLOv11s object detection with "
        "ByteTrack dual-score Kalman filtering for robust commuter identity persistence across dense crowds. An image-space Region of Interest (ROI) "
        "with ground-contact footpoint filtering derives operational commuter occupancy categorized into LOW, MEDIUM, and HIGH density states. "
        "Furthermore, a Target Tracking Module (TAM) powered by MobileSAM is integrated for prompt-guided silhouette segmentation and trajectory telemetry."
    )
    abs_3 = (
        "The Phase-I prototype was implemented in Python using PyTorch, OpenCV, and Streamlit, and benchmarked on real-world concourse footage "
        "using an NVIDIA GeForce RTX 4050 Laptop GPU (CUDA-enabled). The system achieved an inference throughput of 62.9 FPS at 1280px resolution "
        "(15.91 ms latency), with 79.1% mAP@0.50 on the COCO Person class. Across an empirical benchmark of 20 sampled surveillance frames encompassing "
        "407 ground-truth pedestrians, the model achieved a crowd counting accuracy of 99.51% with a Weighted Absolute Percentage Error (WAPE) "
        "of 0.49% and an MAE of 0.100 pedestrians per frame. These results confirm that the Phase-I perception backbone provides industrial-grade "
        "accuracy and real-time responsiveness, establishing a robust foundation for Phase-II multi-event fusion and risk intelligence."
    )
    abs_style = ParagraphStyle(
        'KTU_Abstract',
        parent=body_style,
        fontSize=11.5,
        leading=17.5,
        spaceAfter=8,
        firstLineIndent=18
    )
    story.append(Paragraph(abs_1, abs_style))
    story.append(Paragraph(abs_2, abs_style))
    story.append(Paragraph(abs_3, abs_style))
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # 6. ACKNOWLEDGEMENT (Page 6 - Roman ii, Strictly Single Page)
    # -------------------------------------------------------------
    story.append(PageRecorder("acknowledgement"))
    story.append(ChapterHeading("", "Acknowledgement"))
    ack_1 = (
        "We take this opportunity to express our deepest sense of gratitude and sincere thanks to everyone who helped us complete this work "
        "successfully. We are extremely thankful to our beloved principal <b>Dr. S P SUBRAMANIAN</b> for giving us his consent for this project. "
        "We express our sincere thanks to <b>Ms. Sreeja P</b>, Head of Department, Department of Artificial Intelligence and Data Science, "
        "Sreepathy Institute of Management and Technology, Vavanoor, for providing us with all necessary compute infrastructure, facilities, and support."
    )
    ack_2 = (
        "We would like to express our sincere gratitude to our Project Coordinator <b>Ms. Sreeja P</b>, Associate Professor, Department of "
        "Artificial Intelligence and Data Science, for her continuous coordination, encouragement, and valuable suggestions throughout the project."
    )
    ack_3 = (
        "We would like to place on record our sincere gratitude to our project guide <b>Ms. ARYA N S</b>, Assistant Professor, Department of "
        "Artificial Intelligence and Data Science, for her invaluable guidance, patient mentoring, constructive critique, and constant encouragement "
        "throughout the progress of this Project Phase-1 work."
    )
    ack_4 = (
        "Finally, we thank our parents, family members, teachers, and peers who contributed their moral support, feedback, and enthusiasm "
        "towards the successful completion of this project phase-1 work."
    )
    ack_style = ParagraphStyle(
        'KTU_Ack',
        parent=body_style,
        fontSize=11.5,
        leading=17.5,
        spaceAfter=8,
        firstLineIndent=18
    )
    story.append(Paragraph(ack_1, ack_style))
    story.append(Paragraph(ack_2, ack_style))
    story.append(Paragraph(ack_3, ack_style))
    story.append(Paragraph(ack_4, ack_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>ADITHYA CHANDRAN<br/>AKHIL P<br/>MUHAMMED SHIBIL KP<br/>SHEHRUZ MUHAMMED CS</b>", ParagraphStyle('AckNames', parent=body_no_indent, alignment=2, leading=16)))
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # 7. CONTENTS (Table of Contents with LaTeX dot leaders)
    # -------------------------------------------------------------
    story.append(PageRecorder("contents"))
    story.append(ChapterHeading("", "Contents"))
    
    # Dynamic page strings from PAGE_MAP
    p_abs = get_page_str("abstract", is_front=True)
    p_ack = get_page_str("acknowledgement", is_front=True)
    p_lof = get_page_str("lof", is_front=True)
    p_lot = get_page_str("lot", is_front=True)
    p_sym = get_page_str("symbols", is_front=True)
    
    p_ch1 = get_page_str("ch1")
    p_s11 = get_page_str("sec1_1")
    p_s12 = get_page_str("sec1_2")
    p_s13 = get_page_str("sec1_3")
    p_s14 = get_page_str("sec1_4")
    p_s15 = get_page_str("sec1_5")
    p_s16 = get_page_str("sec1_6")
    
    p_ch2 = get_page_str("ch2")
    p_s21 = get_page_str("sec2_1")
    p_s22 = get_page_str("sec2_2")
    p_s23 = get_page_str("sec2_3")
    p_s24 = get_page_str("sec2_4")
    p_s25 = get_page_str("sec2_5")
    p_s26 = get_page_str("sec2_6")
    p_s27 = get_page_str("sec2_7")
    p_s28 = get_page_str("sec2_8")
    
    p_ch3 = get_page_str("ch3")
    p_s31 = get_page_str("sec3_1")
    p_s32 = get_page_str("sec3_2")
    p_s33 = get_page_str("sec3_3")
    p_s34 = get_page_str("sec3_4")
    p_s35 = get_page_str("sec3_5")
    p_s36 = get_page_str("sec3_6")
    p_s37 = get_page_str("sec3_7")
    p_s38 = get_page_str("sec3_8")
    
    p_ch4 = get_page_str("ch4")
    p_s41 = get_page_str("sec4_1")
    p_s42 = get_page_str("sec4_2")
    p_s43 = get_page_str("sec4_3")
    p_s44 = get_page_str("sec4_4")
    p_s45 = get_page_str("sec4_5")
    p_s46 = get_page_str("sec4_6")
    
    p_ch5 = get_page_str("ch5")
    p_s51 = get_page_str("sec5_1")
    p_s52 = get_page_str("sec5_2")
    p_s53 = get_page_str("sec5_3")
    p_s54 = get_page_str("sec5_4")
    p_s55 = get_page_str("sec5_5")
    
    p_ch6 = get_page_str("ch6")
    p_s61 = get_page_str("sec6_1")
    p_s62 = get_page_str("sec6_2")
    p_s63 = get_page_str("sec6_3")
    p_ref = get_page_str("references")

    # Front matter in Contents
    story.append(TOCLine("", "Abstract", p_abs, is_bold=True, level=0, is_front=True))
    story.append(TOCLine("", "Acknowledgement", p_ack, is_bold=True, level=0, is_front=True))
    story.append(TOCLine("", "List of Figures", p_lof, is_bold=True, level=0, is_front=True))
    story.append(TOCLine("", "List of Tables", p_lot, is_bold=True, level=0, is_front=True))
    story.append(TOCLine("", "List of Symbols", p_sym, is_bold=True, level=0, is_front=True))
    
    # Chapter 1
    story.append(TOCLine("1", "Introduction", p_ch1, is_bold=True, level=0))
    story.append(TOCLine("1.1", "Background and Context", p_s11, is_bold=False, level=1))
    story.append(TOCLine("1.2", "Problem Identification", p_s12, is_bold=False, level=1))
    story.append(TOCLine("1.3", "Motivation", p_s13, is_bold=False, level=1))
    story.append(TOCLine("1.4", "Objectives of the Project", p_s14, is_bold=False, level=1))
    story.append(TOCLine("1.5", "Scope and Significance", p_s15, is_bold=False, level=1))
    story.append(TOCLine("1.6", "Organization of the Report", p_s16, is_bold=False, level=1))
    
    # Chapter 2
    story.append(TOCLine("2", "Literature Review", p_ch2, is_bold=True, level=0))
    story.append(TOCLine("2.1", "Multi-Source Fusion & Crowd Anomaly Detection", p_s21, is_bold=False, level=1))
    story.append(TOCLine("2.2", "Abandoned Object and Baggage Detection", p_s22, is_bold=False, level=1))
    story.append(TOCLine("2.3", "Passenger Behavior and Action Recognition", p_s23, is_bold=False, level=1))
    story.append(TOCLine("2.4", "Multi-Object Tracking and Edge Vision Systems", p_s24, is_bold=False, level=1))
    story.append(TOCLine("2.5", "Violence Detection and Knowledge-Driven Representation", p_s25, is_bold=False, level=1))
    story.append(TOCLine("2.6", "Context-Aware Video Anomaly Detection", p_s26, is_bold=False, level=1))
    story.append(TOCLine("2.7", "Summary Table of Reviewed Literature (21 Studies)", p_s27, is_bold=False, level=1))
    story.append(TOCLine("2.8", "Identified Research Gaps and Project Positioning", p_s28, is_bold=False, level=1))
    
    # Chapter 3
    story.append(TOCLine("3", "System Architecture and Methodology", p_ch3, is_bold=True, level=0))
    story.append(TOCLine("3.1", "Overall Framework Architecture", p_s31, is_bold=False, level=1))
    story.append(TOCLine("3.2", "System Block Diagram & Layered Pipeline", p_s32, is_bold=False, level=1))
    story.append(TOCLine("3.3", "Commuter Perception Backbone: YOLOv11s", p_s33, is_bold=False, level=1))
    story.append(TOCLine("3.4", "Multi-Object Tracking: ByteTrack", p_s34, is_bold=False, level=1))
    story.append(TOCLine("3.5", "Spatial Calibration and ROI Footpoint Filtering", p_s35, is_bold=False, level=1))
    story.append(TOCLine("3.6", "Operational Crowd Occupancy Estimation", p_s36, is_bold=False, level=1))
    story.append(TOCLine("3.7", "Target Tracking Module (TAM) With MobileSAM", p_s37, is_bold=False, level=1))
    story.append(TOCLine("3.8", "Phase-II Architecture: Context Fusion and Risk Engine", p_s38, is_bold=False, level=1))
    
    # Chapter 4
    story.append(TOCLine("4", "Implementation and Results", p_ch4, is_bold=True, level=0))
    story.append(TOCLine("4.1", "Hardware and Software Environment", p_s41, is_bold=False, level=1))
    story.append(TOCLine("4.2", "Interactive Operator Dashboard", p_s42, is_bold=False, level=1))
    story.append(TOCLine("4.3", "Target Tracking Module (TAM) Demonstration", p_s43, is_bold=False, level=1))
    story.append(TOCLine("4.4", "Concourse Crowd Monitoring Demonstration", p_s44, is_bold=False, level=1))
    story.append(TOCLine("4.5", "Quantitative Benchmarks and Evaluation", p_s45, is_bold=False, level=1))
    story.append(TOCLine("4.6", "Discussion of Phase-I Results", p_s46, is_bold=False, level=1))
    
    # Chapter 5
    story.append(TOCLine("5", "Work Plan, Task Allocation and Future Scope", p_ch5, is_bold=True, level=0))
    story.append(TOCLine("5.1", "Project Work Plan", p_s51, is_bold=False, level=1))
    story.append(TOCLine("5.2", "Gantt Chart and Milestone Timeline", p_s52, is_bold=False, level=1))
    story.append(TOCLine("5.3", "Resource Identification", p_s53, is_bold=False, level=1))
    story.append(TOCLine("5.4", "Task Allocation Among Team Members", p_s54, is_bold=False, level=1))
    story.append(TOCLine("5.5", "Phase-II Development Roadmap", p_s55, is_bold=False, level=1))
    
    # Chapter 6
    story.append(TOCLine("6", "Conclusion", p_ch6, is_bold=True, level=0))
    story.append(TOCLine("6.1", "Summary of Phase-I Work", p_s61, is_bold=False, level=1))
    story.append(TOCLine("6.2", "Key Takeaways and Contributions", p_s62, is_bold=False, level=1))
    story.append(TOCLine("6.3", "Concluding Remarks", p_s63, is_bold=False, level=1))
    
    # References
    story.append(TOCLine("", "References", p_ref, is_bold=True, level=0))
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # 8. LIST OF FIGURES (LaTeX formatted with dot leaders)
    # -------------------------------------------------------------
    story.append(PageRecorder("lof"))
    story.append(ChapterHeading("", "List of Figures"))
    
    p_f31 = get_page_str("fig3_1")
    p_f41 = get_page_str("fig4_1")
    p_f42 = get_page_str("fig4_2")
    p_f43 = get_page_str("fig4_3")
    p_f44 = get_page_str("fig4_4")
    p_f51 = get_page_str("fig5_1")
    p_f52 = get_page_str("fig5_2")
    
    story.append(TOCLine("3.1", "MetroGuard AI System Architecture Block Diagram", p_f31, is_bold=False, level=1))
    story.append(TOCLine("4.1", "MetroGuard AI Phase-I Operator Dashboard Interface", p_f41, is_bold=False, level=1))
    story.append(TOCLine("4.2", "Concourse Crowd Monitoring Frame (39 in ROI)", p_f42, is_bold=False, level=1))
    story.append(TOCLine("4.3", "Footpoint Ground-Contact Verification and ByteTrack Association", p_f43, is_bold=False, level=1))
    story.append(TOCLine("4.4", "MetroGuard AI Model Benchmark Scorecard", p_f44, is_bold=False, level=1))
    story.append(TOCLine("5.1", "MetroGuard AI Project Work Plan and Major Phase Sequences", p_f51, is_bold=False, level=1))
    story.append(TOCLine("5.2", "MetroGuard AI Project Timeline and Milestone Gantt Chart", p_f52, is_bold=False, level=1))
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # 9. LIST OF TABLES (LaTeX formatted with dot leaders)
    # -------------------------------------------------------------
    story.append(PageRecorder("lot"))
    story.append(ChapterHeading("", "List of Tables"))
    
    p_t21 = get_page_str("table2_1")
    p_t41 = get_page_str("table4_1")
    p_t42 = get_page_str("table4_2")
    p_t43 = get_page_str("table4_3")
    p_t44 = get_page_str("table4_4")
    p_t51 = get_page_str("table5_1")
    
    story.append(TOCLine("2.1", "Comprehensive Summary of Reviewed Literature (21 Studies)", p_t21, is_bold=False, level=1))
    story.append(TOCLine("4.1", "Hardware and Deep Learning Model Specifications", p_t41, is_bold=False, level=1))
    story.append(TOCLine("4.2", "Real-Time Inference Speed and Latency Benchmark", p_t42, is_bold=False, level=1))
    story.append(TOCLine("4.3", "Object Detection Accuracy Benchmark (COCO Person Class 0)", p_t43, is_bold=False, level=1))
    story.append(TOCLine("4.4", "Empirical ROI Crowd Counting Accuracy and Error Metrics", p_t44, is_bold=False, level=1))
    story.append(TOCLine("5.1", "Task Allocation Among Project Batch Members", p_t51, is_bold=False, level=1))
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # 10. LIST OF SYMBOLS (Single Page, 2-Column Clean Layout)
    # -------------------------------------------------------------
    story.append(PageRecorder("symbols"))
    story.append(ChapterHeading("", "List of Symbols"))
    
    sym_data = [
        ["AI", "Artificial Intelligence"],
        ["CCTV", "Closed-Circuit Television"],
        ["CNN", "Convolutional Neural Network"],
        ["COCO", "Common Objects in Context (Dataset)"],
        ["CUDA", "Compute Unified Device Architecture"],
        ["FPS", "Frames Per Second"],
        ["GFLOPs", "Giga Floating-Point Operations"],
        ["GPU", "Graphics Processing Unit"],
        ["IoU", "Intersection over Union"],
        ["KTU", "APJ Abdul Kalam Technological University"],
        ["MAE", "Mean Absolute Error"],
        ["mAP", "Mean Average Precision"],
        ["MOT", "Multi-Object Tracking"],
        ["NMS", "Non-Maximum Suppression"],
        ["OpenCV", "Open Source Computer Vision Library"],
        ["RGB", "Red, Green, Blue Color Space"],
        ["RMSE", "Root Mean Squared Error"],
        ["ROI", "Region of Interest"],
        ["SAM", "Segment Anything Model"],
        ["TAM", "Target Tracking Module"],
        ["WAPE", "Weighted Absolute Percentage Error"],
        ["YOLO", "You Only Look Once (Object Detector)"],
        ["rho_img", "Image-space normalized crowd density (people / megapixel)"],
        ["N_ROI", "Instantaneous count of tracked commuters inside ROI"],
        ["A_ROI", "Area of Region of Interest in megapixels"],
        ["F_i", "Ground-contact footpoint coordinate (x_mid, y_bottom) of person i"],
        ["theta_conf", "Detection confidence score threshold (default 0.35)"],
        ["R_incident", "Composite incident risk priority score (scale 0 to 100)"]
    ]
    t_sym = Table([[Paragraph(f"<b>{r[0]}</b>", ParagraphStyle('SymK', fontName='Times-Bold', fontSize=10, leading=13)),
                    Paragraph(r[1], ParagraphStyle('SymV', fontName='Times-Roman', fontSize=10, leading=13))] for r in sym_data],
                  colWidths=[1.3*inch, 4.4*inch])
    t_sym.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 1.2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.2)
    ]))
    story.append(t_sym)
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # 11. CHAPTER 1: INTRODUCTION (Body Page 1)
    # -------------------------------------------------------------
    story.append(PageRecorder("ch1"))
    story.append(ChapterHeading("Chapter 1", "Introduction"))
    story.append(Paragraph(
        "Modern urban mass transit systems constitute the vital arteries of contemporary smart cities, transporting tens of millions "
        "of commuters every day through sprawling underground and elevated metro networks. Ensuring passenger safety, preventing catastrophic "
        "crowd stampedes, curbing physical violence, and detecting unattended baggage across labyrinthine stations requires continuous "
        "surveillance over hundreds of concurrent closed-circuit television (CCTV) feeds. However, the sheer volume of incoming video data "
        "severely outstrips the physiological and cognitive monitoring capacity of human security operators. This introductory chapter outlines "
        "the operational background, formalizes the core transit surveillance challenges, establishes the technical motivations and project "
        "objectives, and outlines the overall organization of this report.", body_style))
    
    story.append(PageRecorder("sec1_1"))
    story.append(Paragraph("1.1   Background and Context", section_title_style))
    story.append(Paragraph(
        "Metro rail networks represent highly complex, safety-critical public transit environments characterized by extreme commuter density "
        "variations, tight headway intervals, and rapid passenger flux across ticketing concourses, turnstiles, transfer corridors, escalators, "
        "and boarding platforms. To maintain situational awareness and deter criminal activity, transit authorities deploy extensive "
        "multi-camera CCTV networks. Large metropolitan transit hubs routinely operate between 150 and 500 fixed and pan-tilt-zoom (PTZ) cameras per station.", body_style))
    story.append(Paragraph(
        "Historically, monitoring these video feeds has relied on human operators seated in centralized security control rooms. Decades of "
        "empirical ergonomics and perceptual psychology research have revealed that human visual vigilance degrades precipitously under "
        "continuous monitoring conditions. In practice, an operator observing multiple split-screen surveillance monitors experiences severe "
        "visual fatigue within twenty minutes, missing as much as 95% of critical visual scene activities. Consequently, the transit industry "
        "has turned towards automated computer vision and deep learning systems to automate visual threat detection.", body_style))
    
    story.append(PageRecorder("sec1_2"))
    story.append(Paragraph("1.2   Problem Identification", section_title_style))
    story.append(Paragraph(
        "Despite rapid advances in deep learning, the state of the art in commercial and academic automated video surveillance exhibits profound "
        "architectural limitations when deployed in dense transit environments:", body_style))
    story.append(Paragraph(
        "<b>1. Isolated, Task-Specific Detection Silos:</b> Existing artificial intelligence surveillance systems operate almost exclusively "
        "as disconnected, single-task detectors. A station might employ an isolated algorithm for fight detection, a separate background-subtraction "
        "model for unattended bag detection, and a distinct crowd density estimation module. Each model processes video frames in isolation with "
        "zero inter-module communication or contextual awareness.", body_style))
    story.append(Paragraph(
        "<b>2. Alert Fatigue and Cognitive Overload:</b> Because isolated algorithms lack mutual awareness, a single complex real-world event "
        "generates an avalanche of uncoordinated, redundant alarms. For instance, a physical altercation erupting on a crowded platform "
        "simultaneously triggers a fight alarm, a crowd anomaly alert, and a rapid-motion warning. Security personnel are forced to manually parse, "
        "de-duplicate, and mentally correlate these disconnected alerts.", body_style))
    story.append(Paragraph(
        "<b>3. Absence of Context-Aware Incident Severity Reasoning:</b> Raw computer vision models cannot contextualize the threats they observe. "
        "An unattended backpack placed next to a stationary commuter resting on a concourse bench possesses a vastly different threat level than "
        "an abandoned backpack situated near a platform edge accompanied by a fleeing commuter and dispersing crowds. Current systems lack the "
        "contextual intelligence required to estimate threat severity and compute operational risk priority.", body_style))
    story.append(Paragraph(
        "<b>4. High False Alarm Rates in Crowded Dynamic Scenes:</b> Standard object detection and background subtraction pipelines suffer "
        "catastrophic performance degradation in crowded metro concourses due to severe inter-object occlusion, dynamic lighting shifts, erratic "
        "commuter trajectories, and reflections.", body_style))
    
    story.append(PageRecorder("sec1_3"))
    story.append(Paragraph("1.3   Motivation", section_title_style))
    story.append(Paragraph(
        "The pressing need for intelligent, automated transit surveillance motivates the paradigm of <i>Multi-Event Incident Intelligence</i>. "
        "Rather than treating video analytics as a collection of independent classification tasks, modern transit security requires a unified, "
        "hierarchical decision-support framework. By integrating high-speed object detection, persistent multi-object tracking, spatial-temporal "
        "event extraction, and multi-source context fusion, automated surveillance can transition from reactive alert generation to proactive, "
        "explainable incident understanding.", body_style))
    story.append(Paragraph(
        "Such a framework provides security dispatchers with consolidated, risk-ranked incident narratives rather than hundreds of disjointed "
        "bounding-box alerts. Developing an edge-efficient perception backbone capable of operating at high frame rates on accessible hardware is "
        "an indispensable prerequisite for this vision, directly motivating the Phase-I research and development presented in this work.", body_style))
    
    story.append(PageRecorder("sec1_4"))
    story.append(Paragraph("1.4   Objectives of the Project", section_title_style))
    story.append(Paragraph("The overarching project objectives are structured across two developmental phases:", body_style))
    story.append(Paragraph(
        "<b>Phase-I Objectives (Accomplished):</b><br/>"
        "1. To design and deploy a high-throughput commuter perception backbone using Ultralytics YOLOv11s, optimized for real-time person detection in dense concourses.<br/>"
        "2. To implement the ByteTrack multi-object tracking algorithm with Kalman filtering, ensuring persistent commuter identities through severe occlusions.<br/>"
        "3. To formulate a calibrated Region of Interest (ROI) with ground-contact footpoint filtering, eliminating perspective errors in crowd estimation.<br/>"
        "4. To construct an interactive operator dashboard in Streamlit providing real-time video streaming, dynamic ROI controls, occupancy alerts, and event logs.<br/>"
        "5. To integrate a Target Tracking Module (TAM) utilizing MobileSAM for prompt-guided silhouette segmentation and trajectory telemetry of designated individuals.<br/>"
        "6. To empirically evaluate the system on real-world transit video feeds, benchmarking inference latency, counting fidelity, and detection precision.", body_no_indent))
    story.append(Paragraph(
        "<b>Phase-II Objectives (Future Scope):</b><br/>"
        "1. To develop and integrate a lightweight physical altercation and violence detection module using human pose dynamics and motion vectors.<br/>"
        "2. To implement a four-state unattended baggage tracking module with owner-luggage distance monitoring.<br/>"
        "3. To engineer a spatiotemporal incident correlation matrix and relational graph engine that unifies simultaneous events into coherent incidents.<br/>"
        "4. To formulate a multi-factor operational risk scoring algorithm (0 to 100) that computes incident priority levels (INFO, MODERATE, HIGH, CRITICAL).<br/>"
        "5. To deploy a lightweight natural language explanation engine synthesizing human-readable incident audit reports for transit dispatchers.", body_no_indent))
    
    story.append(PageRecorder("sec1_5"))
    story.append(Paragraph("1.5   Scope and Significance", section_title_style))
    story.append(Paragraph(
        "<b>Scope:</b> The Phase-I scope focuses on high-speed visual perception, commuter detection, multi-person tracking, spatial ROI calibration, "
        "occupancy classification, and target silhouette telemetry executing on edge-grade hardware. The Phase-II scope encompasses multi-event "
        "fusion, fight detection, baggage tracking, operational risk reasoning, and natural language audit generation.", body_style))
    story.append(Paragraph(
        "<b>Significance:</b> By replacing disjointed alarm streams with unified incident intelligence, MetroGuard AI dramatically reduces operator "
        "cognitive fatigue, mitigates false alarms, and accelerates emergency dispatch response times in metro stations.", body_style))
    
    story.append(PageRecorder("sec1_6"))
    story.append(Paragraph("1.6   Organization of the Report", section_title_style))
    story.append(Paragraph(
        "The remainder of this report is organized as follows: Chapter 2 presents a comprehensive literature review of 21 landmark papers spanning "
        "crowd monitoring, baggage detection, action recognition, multi-object tracking, violence detection, and context-aware anomaly detection. "
        "Chapter 3 details the system architecture, mathematical formulations, and algorithmic pipelines of MetroGuard AI. Chapter 4 provides the "
        "implementation details, operator dashboard demonstration, and empirical quantitative benchmark evaluations. Chapter 5 outlines the project "
        "work plan, Gantt chart timeline, resource requirements, task allocations, and Phase-II roadmap. Chapter 6 concludes the report with key "
        "takeaways and future perspectives.", body_style))
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # 12. CHAPTER 2: LITERATURE REVIEW
    # -------------------------------------------------------------
    story.append(PageRecorder("ch2"))
    story.append(ChapterHeading("Chapter 2", "Literature Review"))
    story.append(Paragraph(
        "This chapter presents an in-depth survey of twenty-one peer-reviewed research papers and IEEE conference publications addressing "
        "automated video surveillance, crowd monitoring, unattended baggage detection, human action recognition, multi-object tracking, and "
        "context-aware incident reasoning. The reviewed literature is critically analyzed across thematic sub-fields, culminating in a comparative "
        "synthesis table that explicitly highlights identified research gaps and establishes the technical positioning of MetroGuard AI.", body_style))
    
    story.append(PageRecorder("sec2_1"))
    story.append(Paragraph("2.1   Multi-Source Fusion and Crowd Anomaly Detection", section_title_style))
    story.append(Paragraph(
        "<b>ABDviaMSIFAT: Abnormal Crowd Behavior Detection Utilizing a Multi-Source Information Fusion Technique [1]:</b> Hamid et al. (2025) proposed "
        "a multi-source information fusion framework for abnormal crowd behavior detection in public spaces. Their architecture extracts dual feature "
        "representations: low-level spatial-temporal visual descriptors (optical flow and texture gradients) and high-level behavioral dynamics "
        "(pedestrian velocity vectors and social force interactions). By employing a weighted score-level fusion mechanism, their method demonstrated "
        "that fusing complementary visual and motion streams achieves significantly higher anomaly detection accuracy than single-modality baselines. "
        "The primary limitation of [1] is its substantial computational complexity, which hinders edge deployment on multi-stream CCTV setups. "
        "MetroGuard AI adopts the multi-source fusion philosophy of [1] but optimizes execution speed by implementing fusion at the decision and "
        "state level rather than deep tensor concatenation.", body_style))
    story.append(Paragraph(
        "<b>Intelligent Anomaly Detection and Localization With Crowd Density Estimation for Improved Public Safety [2]:</b> Chaudhary et al. (2025) "
        "investigated joint anomaly detection and spatial localization in crowded public venues by coupling deep crowd density estimation with "
        "spatiotemporal anomaly maps. Their network generates continuous pixel-level density maps, enabling the localization of localized stampedes "
        "and unnatural crowd dispersals. While effective in open public plazas, their architecture suffers from high false-positive rates during "
        "routine peak-hour commuter rushes in metro stations, where high density is operational normality rather than an anomaly. MetroGuard AI "
        "overcomes this by decoupling raw density counting from anomaly classification, using calibrated operational thresholds and ground-contact "
        "footpoint filtering.", body_style))
    
    story.append(PageRecorder("sec2_2"))
    story.append(Paragraph("2.2   Abandoned Object and Baggage Detection", section_title_style))
    story.append(Paragraph(
        "<b>Abandoned Object Detection and Classification Using Deep Embedded Vision [3]:</b> Qasim et al. (2024) developed an embedded vision framework "
        "for abandoned object detection in transit waiting areas. Their method combines Gaussian mixture background subtraction for stationary candidate "
        "localization with a lightweight CNN classifier for luggage categorization. While demonstrating low computational overhead, their model is "
        "susceptible to illumination shifts and transient pedestrian occlusions. MetroGuard AI replaces background subtraction with the modern YOLOv11s "
        "detector, ensuring invariance to shadows and ambient lighting fluctuations.", body_style))
    story.append(Paragraph(
        "<b>A Two-Stage Spatiotemporal CNN-YOLOv9 Framework for Real-Time Abandoned Object Detection [6]:</b> Shah et al. (2026) introduced a two-stage "
        "spatiotemporal CNN-YOLOv9 pipeline for unattended baggage detection in public surveillance. In the first stage, YOLOv9 detects luggage candidates "
        "(backpacks, suitcases, parcels). In the second stage, a spatiotemporal CNN evaluates owner-baggage proximity over temporal sliding windows to "
        "verify whether an owner has abandoned the luggage. Their results proved that separating detection from temporal ownership tracking yields "
        "outstanding precision. However, YOLOv9 exhibits high latency on multi-camera streams. MetroGuard AI builds upon this two-stage paradigm, "
        "utilizing YOLOv11s in Phase-I and planning a lightweight ownership finite-state machine in Phase-II.", body_style))
    story.append(Paragraph(
        "<b>Abandoned Bag Detection in Public Areas Using Grounding DINO With Fine-Grained Prompts [21]:</b> Soontornnapar (2025) proposed using the "
        "open-vocabulary foundation model Grounding DINO with fine-grained text prompts for abandoned bag detection. Their architecture establishes a "
        "four-stage ownership state machine: <i>carry-place-leave-stationary</i>. While Grounding DINO achieves superior open-vocabulary generalization, "
        "its parameter footprint (~172M parameters) renders real-time edge processing impossible. MetroGuard AI adopts the four-stage ownership state "
        "logic of [21] while implementing it over lightweight YOLOv11s and ByteTrack bounding boxes.", body_style))
    
    story.append(PageRecorder("sec2_3"))
    story.append(Paragraph("2.3   Passenger Behavior and Action Recognition", section_title_style))
    story.append(Paragraph(
        "<b>Abnormal Activity Detection of Bus Passengers With In-Vehicle Image Sensing [4]:</b> Lin and Tseng (2024) investigated passenger anomaly "
        "recognition in public transit vehicles using optical sensing. Their pipeline detects passenger conflicts, sudden falls, and loitering in "
        "restricted spaces. While domain-tailored, their model was trained on constrained bus cabins with fixed viewpoints, limiting generalization to "
        "expansive metro concourses. MetroGuard AI adopts their behavioral categorization taxonomy while adapting spatial geometry to wide-angle "
        "overhead CCTV views.", body_style))
    story.append(Paragraph(
        "<b>Surveillance Video-and-Language Understanding: Datasets and Baselines [5]:</b> Yuan et al. (2024) established a landmark benchmark bridging "
        "video analytics with natural language generation. Their work introduced a surveillance video-and-language dataset and baselines for synthesizing "
        "textual descriptions of multi-agent activities. They demonstrated that automated textual narratives drastically improve dispatcher decision speed "
        "compared to raw bounding boxes. MetroGuard AI leverages this concept in its Layer 7 Explainability Engine for Phase-II.", body_style))
    story.append(Paragraph(
        "<b>Online Action Detection by Long Short-Term Transformer with Query Exemplars [20]:</b> Zhang et al. (2024) introduced an online action "
        "detection framework using a Long Short-Term Transformer with query exemplars. Their system processes video streams continuously, matching "
        "current action queries against historical behavioral exemplars. Their model achieves exceptional temporal localization of violent interactions. "
        "However, transformer attention across prolonged buffers poses edge memory challenges. MetroGuard AI adapts their streaming temporal windowing "
        "philosophy for its Phase-II fight-detection sub-module.", body_style))
    
    story.append(PageRecorder("sec2_4"))
    story.append(Paragraph("2.4   Multi-Object Tracking and Edge Vision Systems", section_title_style))
    story.append(Paragraph(
        "<b>Multi-Object Tracking Based on YOLOv8s and ByteTrack Algorithm [7]:</b> Wang and Mariano (2024) demonstrated that ByteTrack's dual-score "
        "association strategy—retaining low-confidence detection boxes to recover occluded targets—effectively mitigates trajectory fragmentation in "
        "crowded surveillance. Their work proved that pairing an optimized YOLO detector with ByteTrack achieves state-of-the-art MOT accuracy with "
        "minimal overhead. MetroGuard AI adopts and extends this architecture, advancing to Ultralytics YOLOv11s for higher parameter efficiency.", body_style))
    story.append(Paragraph(
        "<b>Real-Time Video Surveillance Analysis at the Edge in Smart Cities [13]:</b> Kannan et al. (2025) designed an edge-computing framework for "
        "surveillance in smart cities, proving that executing detection, tracking, and spatial filtering directly at the edge minimizes network "
        "bandwidth consumption and achieves sub-second alert latency. MetroGuard AI adopts this edge-first architecture, ensuring full local autonomy "
        "during central network disruptions.", body_style))
    story.append(Paragraph(
        "<b>Human Group Detection and Clustering Using Enhanced Multi-Object Tracking [16]:</b> Lee et al. (2024) explored real-time human group "
        "detection in crowded surveillance using an enhanced MOT pipeline. By computing spatial proximity graphs across ByteTrack trajectories, "
        "their system clusters pedestrians into social groups to identify unnatural crowd gatherings. MetroGuard AI integrates proximity metrics "
        "inspired by [16] to analyze converging commuter trajectories during incidents.", body_style))
    story.append(Paragraph(
        "<b>CFTformer: End-to-End Cross-Frame Multi-Object Tracking With Transformer [18]:</b> Amirkhani and Khoshnevis (2025) introduced CFTformer, "
        "utilizing cross-attention across sequential frame embeddings to mitigate identity switches in dense scenes. While accurate, its quadratic "
        "complexity limits real-time frame rates. MetroGuard AI employs ByteTrack for Phase-I edge efficiency, while referencing [18] for future roadmap "
        "refinements.", body_style))
    story.append(Paragraph(
        "<b>SCL-YOLOv11: Lightweight Object Detection for Low-Illumination Environments [19]:</b> Zhuo et al. (2025) developed SCL-YOLOv11 for "
        "low-illumination surveillance, introducing spatial context learning and illumination-adaptive kernels. Their findings proved that YOLOv11 "
        "provides exceptional feature extraction even under poor lighting, validating our choice of YOLOv11s for dimly lit metro concourses and tunnels.", body_style))
    
    story.append(PageRecorder("sec2_5"))
    story.append(Paragraph("2.5   Violence Detection and Knowledge-Driven Representation", section_title_style))
    story.append(Paragraph(
        "<b>Fusion of Human Pose and Motion Dynamics for Violence Detection [8]:</b> Aung et al. (2025) proposed combining skeletal pose keypoints with "
        "optical-flow motion dynamics to identify violent altercations while rejecting benign rapid motions (e.g., running to catch a train). "
        "Their results established that combining structural pose geometry with velocity dynamics drastically reduces false violence alarms. "
        "This serves as the blueprint for MetroGuard AI's planned Phase-II fight-detection sub-module.", body_style))
    story.append(Paragraph(
        "<b>Graph-Based Knowledge-Driven Approach for Violence Detection [11]:</b> Khan et al. (2025) formulated video violence detection using "
        "spatiotemporal knowledge graphs, where nodes represent detected individuals and edges represent spatial proximity, relative velocities, "
        "and contact states. A graph convolutional network (GCN) reasons over these structured interactions. MetroGuard AI adopts this graph "
        "paradigm for its Layer 7 Incident Intelligence Engine.", body_style))
    story.append(Paragraph(
        "<b>Action Knowledge Graph for Violence Detection Using Audiovisual Features [12]:</b> Khan et al. (2024) expanded their graph architecture "
        "to incorporate acoustic cues. While audio is noisy in metro stations, the actor-environment relational modeling methodologies in [12] "
        "directly influence MetroGuard AI's relational database schema and multi-event correlation logic.", body_style))
    story.append(Paragraph(
        "<b>VD-Net: An Edge Vision-Based Surveillance System for Violence Detection [14]:</b> Khan et al. (2024) presented VD-Net, an ultra-lightweight "
        "convolutional network engineered for low-latency violence detection on edge boards. Their design principles prove that violence detection "
        "can execute concurrently alongside YOLOv11s and ByteTrack without exhausting edge compute.", body_style))
    
    story.append(PageRecorder("sec2_6"))
    story.append(Paragraph("2.6   Context-Aware Anomaly Detection in Complex Environments", section_title_style))
    story.append(Paragraph(
        "<b>Context-Aware Video Anomaly Detection in Long-Term Datasets [9]:</b> Yang and Radke (2024) proved that evaluating surveillance frames in "
        "isolation causes high false-positive rates due to cyclical scene shifts. Conditioning anomaly scores on long-term temporal context suppressed "
        "spurious alerts. This principle forms a core tenet of MetroGuard AI: isolated detections only become actionable incidents when evaluated "
        "against spatiotemporal context.", body_style))
    story.append(Paragraph(
        "<b>Spatio-Temporal Semantic Algorithm for Video Anomaly Detection [10]:</b> Zhu et al. (2025) unified pixel trajectories with semantic scene "
        "segmentation to evaluate anomalies based on movement dynamics and spatial zones. MetroGuard AI incorporates this through its calibrated ROI "
        "geometry and footpoint filtering.", body_style))
    story.append(Paragraph(
        "<b>Attention-Based Unsupervised Framework for Anomaly Detection [15]:</b> Habeb et al. (2024) used spatial-temporal attention on normal footage "
        "to detect anomalies as reconstruction errors without exhaustive manual annotations. Their unsupervised concepts guide our future multicamera "
        "calibration.", body_style))
    story.append(Paragraph(
        "<b>Multi-Scale Video Anomaly Detection by Multi-Grained Spatiotemporal Learning [17]:</b> Zhang et al. (2024) captured micro-level individual "
        "behaviors and macro-level scene dynamics in parallel. This mirrors MetroGuard AI's layered design, where individual bounding boxes aggregate "
        "into macro-level crowd states.", body_style))
    
    story.append(PageBreak())
    story.append(PageRecorder("sec2_7"))
    story.append(Paragraph("2.7   Summary Table of Reviewed Literature", section_title_style))
    story.append(Paragraph("Table 2.1 provides a comparative synthesis of all twenty-one reviewed publications across methodology, limitations, and relevance.", body_style))
    
    # Table Caption placed ABOVE the table (Academic / KTU standard)
    story.append(PageRecorder("table2_1"))
    story.append(Paragraph("<b>Table 2.1:</b> Comprehensive Summary of Reviewed Literature (21 Studies)", table_caption_style))
    
    t2_data = [
        ["Ref.", "Authors & Focus", "Key Methodology", "Identified Limitations", "Relevance to MetroGuard AI"],
        ["[1]", "Hamid et al.\n(Crowd Anomaly)", "Dual visual/motion features; weighted score fusion; social forces", "High compute overhead; lacks object relationship modeling", "Theoretical basis for cross-module score fusion"],
        ["[2]", "Chaudhary et al.\n(Crowd Density)", "Crowd density estimation; anomaly localization heatmaps", "High false positives during normal peak-hour rushes", "Informs crowd occupancy and risk weighting"],
        ["[3]", "Qasim et al.\n(Abandoned Bag)", "Deep embedded vision; background subtraction; stationary CNN", "Sensitive to lighting shifts and camera shake", "Shapes baggage classification taxonomy"],
        ["[4]", "Lin & Tseng\n(Transit Sensing)", "In-vehicle optical sensing; fighting, falling, loitering classification", "Constrained to small bus vehicle cabins", "Guides event taxonomy for transit environments"],
        ["[5]", "Yuan et al.\n(Video-Language)", "Surveillance video-language dataset; event captions; baselines", "High resource consumption for caption generation", "Motivates explainable incident summaries"],
        ["[6]", "Shah et al.\n(Abandoned Object)", "Two-stage CNN-YOLOv9; spatiotemporal ownership analysis", "High latency on dense multicamera streams", "Detect-then-analyze ownership design"],
        ["[7]", "Wang & Mariano\n(Tracking MOT)", "YOLOv8s + ByteTrack; persistent IDs; dual-score Kalman matching", "Evaluated primarily on generic street scenes", "Directly adopted as Phase-I tracking backbone"],
        ["[8]", "Aung et al.\n(Violence Detection)", "Human pose and motion dynamics fusion; skeleton keypoints", "Requires high-resolution views of human limbs", "Design template for fight-detection module"],
        ["[9]", "Yang & Radke\n(Context Anomaly)", "Long-term temporal context; context-conditioned anomaly scoring", "Requires extended historical baseline footage", "Proves need for temporal context awareness"],
        ["[10]", "Zhu et al.\n(Semantic Anomaly)", "Spatiotemporal semantic algorithm; monitoring perspective zoning", "Complex semantic segmentation pipeline", "Informs spatial ROI zone calibration"],
        ["[11]", "Khan et al.\n(Graph Violence)", "Spatiotemporal knowledge graphs; graph convolutional reasoning", "Graph construction overhead on edge hardware", "Basis for graph-driven incident engine"],
        ["[12]", "Khan et al.\n(Action Graph)", "Audiovisual action knowledge graphs; multi-modal entity relations", "Audio unavailable or noisy in real concourses", "Informs relational incident data models"],
        ["[13]", "Kannan et al.\n(Edge Surveillance)", "Edge AI surveillance architecture; low-latency smart city streaming", "Focuses on networking rather than incident reasoning", "Edge-first deployment architecture"],
        ["[14]", "Khan et al.\n(VD-Net Edge)", "Lightweight edge network; real-time violence detection on edge boards", "Limited to single-event classification", "Guides lightweight fight detector design"],
        ["[15]", "Habeb et al.\n(Unsupervised VAD)", "Attention-based unsupervised anomaly detection; heterogeneous views", "Lacks explicit multi-agent interaction semantics", "Informs adaptive multicamera calibration"],
        ["[16]", "Lee et al.\n(Group Detection)", "Real-time human group detection; trajectory proximity clustering", "Fails in extreme, uniform stampede densities", "Adds social grouping and crowd context"],
        ["[17]", "Zhang et al.\n(Multi-Scale VAD)", "Multi-grained spatiotemporal learning; local and global representations", "High model complexity and parameter count", "Mirrors layered micro/macro framework"],
        ["[18]", "Amirkhani & Khoshnevis\n(CFTformer MOT)", "CFTformer; cross-frame transformer tracking; attention association", "Quadratic compute overhead; sub-real-time", "Informs future trajectory refinement"],
        ["[19]", "Zhuo et al.\n(SCL-YOLOv11)", "Lightweight YOLOv11 for low-light; spatial context learning", "Evaluated on nighttime vehicle traffic", "Validates YOLOv11 for dark metro stations"],
        ["[20]", "Zhang et al.\n(Online Action)", "Online action detection; Long Short-Term Transformer; query exemplars", "High memory footprint for temporal attention", "Guides streaming temporal windowing"],
        ["[21]", "Soontornnapar\n(DINO Baggage)", "Grounding DINO; fine-grained prompts; 4-stage ownership logic", "Giant foundation model; cannot run on edge", "Provides 4-stage baggage state logic"]
    ]
    # Part 1: Studies 1 to 12 on Page 24
    t2_table1 = Table([[Paragraph(c, ParagraphStyle("TCell", fontName="Times-Roman", fontSize=7.5, leading=10)) for c in row] for row in t2_data[:13]],
                      colWidths=[0.35*inch, 1.25*inch, 1.4*inch, 1.4*inch, 1.3*inch])
    t2_table1.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#EEEEEE")),
        ("FONTNAME", (0,0), (-1,0), "Times-Bold"),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#BBBBBB")),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("TOPPADDING", (0,0), (-1,-1), 2.5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 2.5)
    ]))
    story.append(t2_table1)
    
    story.append(PageBreak())
    story.append(Paragraph("<b>Table 2.1 (Continued):</b> Comprehensive Summary of Reviewed Literature (21 Studies)", table_caption_style))
    
    # Part 2: Studies 13 to 21 with repeated column header on Page 25
    t2_table2 = Table([[Paragraph(c, ParagraphStyle("TCell", fontName="Times-Roman", fontSize=7.5, leading=10)) for c in row] for row in [t2_data[0]] + t2_data[13:]],
                      colWidths=[0.35*inch, 1.25*inch, 1.4*inch, 1.4*inch, 1.3*inch])
    t2_table2.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#EEEEEE")),
        ("FONTNAME", (0,0), (-1,0), "Times-Bold"),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#BBBBBB")),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("TOPPADDING", (0,0), (-1,-1), 2.5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 2.5)
    ]))
    story.append(t2_table2)
    story.append(PageBreak())
    story.append(PageRecorder("sec2_8"))
    story.append(Paragraph("2.8   Identified Research Gaps and Project Positioning", section_title_style))
    story.append(Paragraph(
        "A critical synthesis of the surveyed literature reveals three major unresolved gaps in modern automated surveillance:<br/><br/>"
        "<b>1. The Perception-Reasoning Disconnect:</b> While individual perception models for object detection [7, 19], tracking [7, 18], "
        "violence recognition [8, 14], and baggage detection [6, 21] have reached high accuracy, they operate in absolute isolation. No existing "
        "transit framework unifies these models under a coherent spatiotemporal incident reasoning engine.<br/><br/>"
        "<b>2. Unprioritized Alert Proliferation:</b> Current commercial systems output raw, unranked alarms for every detected threshold violation, "
        "leading directly to operator alert fatigue. Existing research lacks an automated operational risk scoring formula that integrates event type, "
        "crowd context, and spatial urgency into a single priority metric.<br/><br/>"
        "<b>3. Impractical Computational Demands:</b> State-of-the-art vision-language and transformer models [5, 18, 21] achieve impressive results "
        "on benchmarks but require server clusters that cannot be deployed at transit station edges. There is a pressing need for a lightweight, "
        "high-FPS architecture that delivers high precision on station workstations.<br/><br/>"
        "<b>Positioning of MetroGuard AI:</b> MetroGuard AI addresses these gaps directly. In Phase-I, we establish an ultra-fast, edge-capable "
        "perception backbone combining YOLOv11s and ByteTrack with calibrated ROI footpoint filtering and MobileSAM target tracking. This lightweight "
        "foundation achieves &gt;60 FPS on laptop-grade GPUs while setting the architectural stage for Phase-II graph-driven incident fusion and "
        "automated natural-language explainability.", body_style))
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # 13. CHAPTER 3: SYSTEM ARCHITECTURE AND METHODOLOGY
    # -------------------------------------------------------------
    story.append(PageRecorder("ch3"))
    story.append(ChapterHeading("Chapter 3", "System Architecture and Methodology"))
    story.append(Paragraph(
        "MetroGuard AI is designed as a modular, hierarchical video intelligence platform that bridges low-level visual perception and "
        "high-level incident reasoning. This chapter provides a comprehensive exposition of the system architecture, mathematical formulations, "
        "and algorithmic workflows developed for Project Phase-I, alongside the formal design of the planned Phase-II incident intelligence engine.", body_style))
    
    story.append(PageRecorder("sec3_1"))
    story.append(Paragraph("3.1   Overall Framework Architecture", section_title_style))
    story.append(Paragraph(
        "The MetroGuard AI architecture is structured into seven distinct functional layers, ensuring strict separation of concerns, high "
        "computational throughput, and modular extensibility:<br/>"
        "• <b>Layer 1 (Video Ingestion and Preprocessing):</b> Ingests live RTSP camera feeds or high-resolution recorded surveillance footage, "
        "performs frame decoding, color space normalization, and geometric scaling.<br/>"
        "• <b>Layer 2 (Commuter Perception Backbone):</b> Deploys the Ultralytics YOLOv11s convolutional neural network to detect commuters and "
        "objects with high confidence and bounding box precision.<br/>"
        "• <b>Layer 3 (Multi-Object Tracking and Identity Association):</b> Implements the ByteTrack dual-score association algorithm with Kalman "
        "filtering to track detected entities across frames and maintain persistent identities through severe occlusions.<br/>"
        "• <b>Layer 4 (Spatial Calibration and ROI Footpoint Filtering):</b> Translates camera coordinates into calibrated image-space Regions of "
        "Interest (ROI) and applies ground-contact footpoint filtering to count commuters strictly within designated operational zones.<br/>"
        "• <b>Layer 5 (Operational Crowd Occupancy Estimation):</b> Derives real-time occupancy counts, normalizes image-space density indicators, "
        "and triggers operational density state classifications (LOW, MEDIUM, HIGH).<br/>"
        "• <b>Layer 6 (Target Tracking Module - TAM):</b> Leverages MobileSAM (Segment Anything Model) to perform prompt-guided silhouette "
        "segmentation, motion breadcrumb tracking, and dwell time telemetry for targeted individuals.<br/>"
        "• <b>Layer 7 (Spatiotemporal Incident Reasoning and Context Fusion):</b> Formalizes the multi-event correlation engine, relational graph "
        "schema, risk assessment priority scoring, and natural-language incident reporting for Phase-II.", body_no_indent))
    
    story.append(PageBreak())
    story.append(PageRecorder("sec3_2"))
    story.append(Paragraph("3.2   System Block Diagram &amp; Layered Pipeline", section_title_style))
    story.append(Paragraph("Figure 3.1 illustrates the comprehensive end-to-end dataflow and architectural block diagram of the MetroGuard AI framework.", body_style))
    
    if os.path.exists(block_diag_path):
        story.append(RLImage(block_diag_path, width=5.6*inch, height=3.5*inch))
        story.append(PageRecorder("fig3_1"))
        story.append(Paragraph("<b>Figure 3.1:</b> MetroGuard AI System Architecture Block Diagram", fig_caption_style))
    
    story.append(Paragraph(
        "As depicted in Figure 3.1, video frames from CCTV cameras undergo parallel processing through the detection, tracking, and spatial "
        "calibration layers before feeding into operational density indicators and downstream event extraction modules.", body_style))
    
    story.append(PageRecorder("sec3_3"))
    story.append(Paragraph("3.3   Commuter Perception Backbone: YOLOv11s", section_title_style))
    story.append(Paragraph(
        "The core visual detector deployed in MetroGuard AI is the newly released Ultralytics YOLOv11s architecture. YOLOv11 introduces "
        "significant architectural enhancements over previous iterations, including optimized C3k2 cross-stage partial bottleneck blocks, "
        "spatial pyramid pooling fast (SPPF), and an anchor-free decoupled detection head with depthwise separable convolutions.<br/><br/>"
        "Given an input surveillance video frame <i>I_t</i> in R^{H x W x 3} at time <i>t</i>, the backbone extracts multi-scale feature maps "
        "P3, P4, P5 corresponding to downsampling strides of 8, 16, and 32 pixels. The feature pyramid network (FPN) and path aggregation network (PAN) "
        "fuse fine-grained spatial textures with high-level semantic context. For each potential detection anchor, the decoupled head predicts "
        "bounding box coordinates B = [x_c, y_c, w, h] and class probabilities P(C_k). In MetroGuard AI Phase-I, the detector is configured to "
        "isolate COCO class 0 ('person'). Detections satisfying confidence &gt;= theta_conf (default 0.35) are passed to non-maximum suppression "
        "(NMS) with an IoU threshold of 0.70 to eliminate redundant candidate boxes.", body_style))
    
    story.append(PageRecorder("sec3_4"))
    story.append(Paragraph("3.4   Multi-Object Tracking: ByteTrack", section_title_style))
    story.append(Paragraph(
        "Tracking commuters through crowded metro concourses is severely challenged by inter-object occlusion, where people temporarily walk "
        "behind columns, ticket vending machines, or other passengers. Conventional trackers (e.g., SORT) discard low-confidence detection boxes, "
        "resulting in broken trajectories and identity switches. MetroGuard AI resolves this by implementing ByteTrack.<br/><br/>"
        "Each tracked commuter is modeled in an eight-dimensional continuous state space: <b>x</b> = [x_c, y_c, a, h, dx_c, dy_c, da, dh]^T, "
        "where (x_c, y_c) represents the 2D bounding box center, a = w/h is the aspect ratio, h is the box height, and the dotted terms represent "
        "their respective first-order temporal velocities. The Kalman filter predicts the next state and error covariance using standard linear "
        "motion transition models.<br/><br/>"
        "ByteTrack partitions all detections at frame <i>t</i> into two sets: high-confidence detections D_high (conf &gt;= 0.50) and low-confidence "
        "detections D_low (0.10 &lt;= conf &lt; 0.50). In the primary association stage, D_high detections are matched against predicted tracklets "
        "using IoU distance and the Hungarian algorithm. In the secondary association stage, remaining unmatched tracks are matched against D_low. "
        "Because occluded commuters produce lower detection confidence, this secondary step successfully recovers obscured passengers without "
        "introducing false-positive background noise.", body_style))
    
    story.append(PageRecorder("sec3_5"))
    story.append(Paragraph("3.5   Spatial Calibration and ROI Footpoint Filtering", section_title_style))
    story.append(Paragraph(
        "In video surveillance, estimating crowd concentration based purely on full-frame detections produces misleading operational metrics "
        "because cameras capture distant ceilings, background staircases, and off-limits maintenance zones. Furthermore, pedestrians standing "
        "outside a designated platform boundary whose heads visually overlap the region must not be counted.<br/><br/>"
        "MetroGuard AI defines a normalized rectangular Region of Interest: ROI = [L_norm, T_norm, R_norm, B_norm] in [0, 1]^4. For a video frame "
        "of width W and height H, pixel coordinates are computed as L = round(L_norm * W), T = round(T_norm * H), R = round(R_norm * W), and "
        "B = round(B_norm * H).<br/><br/>"
        "To determine whether a commuter is physically located within the ROI, MetroGuard AI evaluates the ground-contact footpoint rather than "
        "the bounding box centroid. For a detected person box [x1, y1, x2, y2], the footpoint F is defined as the bottom-center coordinate: "
        "F = ((x1 + x2)/2, y2). A tracked person <i>k</i> is counted inside the ROI if and only if L &lt;= (x1+x2)/2 &lt;= R and T &lt;= y2 &lt;= B.", body_style))
    
    story.append(PageRecorder("sec3_6"))
    story.append(Paragraph("3.6   Operational Crowd Occupancy Estimation", section_title_style))
    story.append(Paragraph(
        "Let T_t represent the set of active tracks at time <i>t</i>. The instantaneous commuter occupancy count within the ROI is N_ROI(t) = sum(1(F_k in ROI)). "
        "To provide a standardized, camera-invariant density metric, the system computes the normalized image-space occupancy density: "
        "rho_img(t) = N_ROI(t) / A_megapixels, where A_megapixels = (R - L)(B - T) / 10^6.<br/><br/>"
        "Operational occupancy states are categorized using configurable station thresholds tau_med and tau_high (default values tau_med = 8, "
        "tau_high = 16):<br/>"
        "• <b>LOW:</b> N_ROI(t) &lt; 8 (Normal concourse passenger flow; green indicator).<br/>"
        "• <b>MEDIUM:</b> 8 &lt;= N_ROI(t) &lt; 16 (Moderate congestion requiring passenger monitoring; orange indicator).<br/>"
        "• <b>HIGH:</b> N_ROI(t) &gt;= 16 (Severe congestion triggering crowd bottleneck warnings; red indicator).", body_style))
    
    story.append(PageRecorder("sec3_7"))
    story.append(Paragraph("3.7   Target Tracking Module (TAM) With MobileSAM", section_title_style))
    story.append(Paragraph(
        "To support targeted security interventions, MetroGuard AI integrates a specialized Target Tracking Module (TAM) powered by MobileSAM. "
        "MobileSAM distills the massive Vision Transformer (ViT-H) of the original Segment Anything Model into an ultra-lightweight image encoder "
        "(10.1M parameters, 38.8 MB). When a target commuter ID is locked by the operator (or automatically assigned to the first person entering "
        "the ROI), their ByteTrack bounding box [x1, y1, x2, y2] is passed to MobileSAM as a geometric prompt. MobileSAM outputs a pixel-precise "
        "binary silhouette mask M_target in {0, 1}^{H x W}.<br/><br/>"
        "TAM logs the complete trajectory history of the target individual, rendering visual breadcrumbs onto the display. Real-time telemetry "
        "includes cumulative dwell time (T_dwell in seconds), total path distance traversed (D_total in pixels), and real-time ROI containment status.", body_style))
    
    story.append(PageRecorder("sec3_8"))
    story.append(Paragraph("3.8   Phase-II Architecture: Context Fusion and Risk Engine", section_title_style))
    story.append(Paragraph(
        "While Phase-I delivers the operational perception, tracking, occupancy, and TAM modules, the core theoretical contribution of MetroGuard AI "
        "is its unified incident intelligence architecture designed for Phase-II completion.<br/><br/>"
        "All downstream event detectors (fight detection, crowd surge, abandoned baggage) emit events adhering to a standardized schema: "
        "E_i = &lt;event_id, type, track_ids, B_spatial, [t_start, t_end], S_conf, Z_zone&gt;. Two events E_A and E_B are correlated into a single "
        "composite incident if they satisfy temporal overlap (delta_t &lt;= delta_temporal) and spatial Euclidean proximity (dist &lt;= delta_spatial).<br/><br/>"
        "The unified Event Relationship Score is formalized as: S_rel(E_A, E_B) = w_t * exp(-delta_t / sigma_t) + w_s * exp(-dist^2 / (2 * sigma_s^2)) + "
        "w_sem * M(type_A, type_B). For each formed incident, the system computes an operational risk score R in [0, 100]: "
        "R = w_fight * S_fight + w_crowd * S_crowd + w_bag * S_bag + w_context * S_context. Incidents are categorized into operational priority levels: "
        "INFO (R &lt; 30), MODERATE (30 &lt;= R &lt; 60), HIGH (60 &lt;= R &lt; 80), and CRITICAL (R &gt;= 80), providing operators with immediate, "
        "risk-ranked dispatch instructions.", body_style))
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # 14. CHAPTER 4: IMPLEMENTATION AND RESULTS
    # -------------------------------------------------------------
    story.append(PageRecorder("ch4"))
    story.append(ChapterHeading("Chapter 4", "Implementation and Results"))
    story.append(Paragraph(
        "This chapter details the technical implementation of the MetroGuard AI Phase-I system, describes the interactive operator dashboard, "
        "demonstrates concourse crowd monitoring and target tracking, and provides empirical benchmark evaluations on inference latency, "
        "detection accuracy, and crowd counting fidelity.", body_style))
    
    story.append(PageRecorder("sec4_1"))
    story.append(Paragraph("4.1   Hardware and Software Environment", section_title_style))
    story.append(Paragraph(
        "The Phase-I prototype was implemented and benchmarked on a dedicated transit edge workstation environment:<br/>"
        "• <b>Processing Hardware:</b> NVIDIA GeForce RTX 4050 Laptop GPU (6 GB GDDR6 VRAM, CUDA 12.x enabled, 2560 CUDA cores) paired with an "
        "Intel multi-core host CPU and 16 GB DDR5 RAM.<br/>"
        "• <b>Operating System:</b> Microsoft Windows 11 Enterprise (64-bit).<br/>"
        "• <b>Software Stack:</b> Python 3.12, PyTorch 2.9, TorchVision 0.24, Ultralytics YOLOv11s (engine version 8.3.235), OpenCV 4.x, "
        "MobileSAM, Pandas, NumPy, and Streamlit 1.58.", body_no_indent))
    
    story.append(PageBreak())
    story.append(PageRecorder("sec4_2"))
    story.append(Paragraph("4.2   Interactive Operator Dashboard", section_title_style))
    story.append(Paragraph(
        "To provide transit security dispatchers with actionable situational awareness, a full-featured operator dashboard was developed using "
        "Streamlit and OpenCV. Figure 4.1 shows the primary operator interface.", body_style))
    
    if os.path.exists(dash_path):
        story.append(RLImage(dash_path, width=5.6*inch, height=3.1*inch))
        story.append(PageRecorder("fig4_1"))
        story.append(Paragraph("<b>Figure 4.1:</b> MetroGuard AI Phase-I Operator Dashboard Interface", fig_caption_style))
    
    story.append(Paragraph(
        "As shown in Figure 4.1, the dashboard provides video stream selection (local MP4 or live RTSP), dynamic ROI calibration sliders, "
        "occupancy threshold configuration, a live annotated video stream with persistent tracklet IDs, metric telemetry cards (instantaneous count, "
        "image density, occupancy status), and a real-time event audit log.", body_style))
    
    story.append(PageRecorder("sec4_3"))
    story.append(Paragraph("4.3   Target Tracking Module (TAM) Demonstration", section_title_style))
    story.append(Paragraph(
        "When TAM is activated in the dashboard, the operator selects a specific commuter ID (or enables auto-lock). The system prompts MobileSAM "
        "with the target's bounding box, segmenting the commuter's exact silhouette and rendering cyan motion breadcrumbs that chart their exact path "
        "through the concourse. Target telemetry, including dwell time and cumulative distance, is dynamically displayed in the operator sidebar.", body_style))
    
    story.append(PageRecorder("sec4_4"))
    story.append(Paragraph("4.4   Concourse Crowd Monitoring Demonstration", section_title_style))
    story.append(Paragraph(
        "The system was evaluated on high-resolution CCTV footage captured from an active transit concourse. Figure 4.2 displays a demonstration "
        "frame during peak passenger flux.", body_style))
    
    if os.path.exists(crowd_path):
        story.append(RLImage(crowd_path, width=5.6*inch, height=3.1*inch))
        story.append(PageRecorder("fig4_2"))
        story.append(Paragraph("<b>Figure 4.2:</b> Demonstration Frame: 39 Commuters in ROI with HIGH Occupancy Alert", fig_caption_style))
    
    story.append(Paragraph(
        "In this scenario, exactly 39 commuters had ground-contact footpoints within the calibrated ROI, correctly triggering a <b>HIGH</b> occupancy "
        "alert (39 &gt;= 16), while commuters outside the boundary were appropriately excluded from the tally. Figure 4.3 highlights a close-up "
        "annotated frame showing bounding boxes and ground-contact points.", body_style))
    
    if os.path.exists(ann_path):
        story.append(RLImage(ann_path, width=5.5*inch, height=3.0*inch))
        story.append(PageRecorder("fig4_3"))
        story.append(Paragraph("<b>Figure 4.3:</b> Footpoint Ground-Contact Verification and ByteTrack Association", fig_caption_style))
    
    story.append(PageBreak())
    story.append(PageRecorder("sec4_5"))
    story.append(Paragraph("4.5   Quantitative Benchmarks and Evaluation", section_title_style))
    story.append(Paragraph(
        "To rigorously quantify the performance of the Phase-I architecture, an extensive benchmark evaluation was conducted covering deep learning "
        "model complexity, real-time inference latency, COCO object detection accuracy, and empirical crowd counting fidelity. Figure 4.4 presents "
        "the verified terminal evaluation scorecard.", body_style))
    
    if os.path.exists(card_path):
        story.append(RLImage(card_path, width=5.6*inch, height=4.0*inch))
        story.append(PageRecorder("fig4_4"))
        story.append(Paragraph("<b>Figure 4.4:</b> MetroGuard AI Model Evaluation and Accuracy Benchmark Scorecard", fig_caption_style))
    
    # Table 4.1
    story.append(Spacer(1, 10))
    story.append(PageRecorder("table4_1"))
    story.append(Paragraph("<b>Table 4.1:</b> Hardware and Deep Learning Model Specifications", table_caption_style))
    t41_data = [
        ["Component", "Architecture", "Parameters", "FLOPs / Size", "Device / Backend"],
        ["Execution Device", "NVIDIA RTX 4050", "--", "6 GB GDDR6", "CUDA Enabled"],
        ["Detection Backbone", "YOLOv11s", "9,458,752", "21.8 GFLOPs", "PyTorch FP16/FP32"],
        ["TAM Foundation Engine", "MobileSAM", "10,130,092", "38.8 MB", "Lightweight ViT"],
        ["Tracking Engine", "ByteTrack", "--", "Dual Kalman", "C++ / Python Association"]
    ]
    t41 = Table([[Paragraph(c, ParagraphStyle('TC41', fontName='Times-Roman', fontSize=8.5, leading=11)) for c in row] for row in t41_data],
                colWidths=[1.4*inch, 1.3*inch, 1.0*inch, 1.0*inch, 1.0*inch])
    t41.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EEEEEE")),
        ('FONTNAME', (0,0), (-1,0), 'Times-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#BBBBBB")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3)
    ]))
    story.append(t41)
    
    # Table 4.2
    story.append(Spacer(1, 12))
    story.append(PageRecorder("table4_2"))
    story.append(Paragraph("<b>Table 4.2:</b> Real-Time Inference Speed and Latency Benchmark", table_caption_style))
    t42_data = [
        ["Configuration", "Resolution", "Latency (ms)", "Throughput (FPS)", "Operational Status"],
        ["YOLOv11s (CCTV Detail)", "1280 x 1280", "15.91 ms", "62.9 FPS", "PASS (Real-Time Transit)"],
        ["YOLOv11s (Ultra-Fast)", "640 x 640", "16.54 ms", "60.4 FPS", "PASS (High-Speed Edge)"],
        ["MobileSAM (TAM Mask)", "Prompted Box", "69.00 ms", "14.5 FPS", "PASS (Target SOT Tracking)"]
    ]
    t42 = Table([[Paragraph(c, ParagraphStyle('TC42', fontName='Times-Roman', fontSize=8.5, leading=11)) for c in row] for row in t42_data],
                colWidths=[1.6*inch, 1.0*inch, 0.9*inch, 1.0*inch, 1.2*inch])
    t42.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EEEEEE")),
        ('FONTNAME', (0,0), (-1,0), 'Times-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#BBBBBB")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3)
    ]))
    story.append(t42)
    
    # Table 4.3
    story.append(Spacer(1, 12))
    story.append(PageRecorder("table4_3"))
    story.append(Paragraph("<b>Table 4.3:</b> Object Detection Accuracy Benchmark (COCO Person Class 0)", table_caption_style))
    t43_data = [
        ["Metric", "Score / Percentage", "Benchmark Standard"],
        ["mAP @ 0.50 (IoU 50% Threshold)", "79.1%", "COCO Val2017"],
        ["mAP @ 0.50:0.95 (Strict Metric)", "56.4%", "COCO Val2017"],
        ["Detection Precision (P)", "81.2%", "High Confidence Operational"],
        ["Detection Recall (R)", "74.8%", "High Recall Surveillance"]
    ]
    t43 = Table([[Paragraph(c, ParagraphStyle('TC43', fontName='Times-Roman', fontSize=8.5, leading=11)) for c in row] for row in t43_data],
                colWidths=[2.3*inch, 1.4*inch, 2.0*inch])
    t43.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EEEEEE")),
        ('FONTNAME', (0,0), (-1,0), 'Times-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#BBBBBB")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3)
    ]))
    story.append(t43)
    
    # Table 4.4
    story.append(Spacer(1, 12))
    story.append(PageRecorder("table4_4"))
    story.append(Paragraph("<b>Table 4.4:</b> Empirical ROI Crowd Counting Accuracy and Error Metrics", table_caption_style))
    t44_data = [
        ["Metric / Parameter", "Production (conf=0.35)", "High-Recall (conf=0.10)"],
        ["Sampled Frames Analyzed", "20 frames", "20 frames"],
        ["Total Ground-Truth Pedestrians", "407 people", "407 people"],
        ["Total Model Predicted Count", "398 people", "409 people"],
        ["Counting Accuracy (%)", "97.79%", "99.51%"],
        ["Weighted Absolute Percentage Error (WAPE)", "2.21%", "0.49%"],
        ["Mean Absolute Error (MAE)", "0.450 people / frame", "0.100 people / frame"],
        ["Root Mean Squared Error (RMSE)", "0.671 people / frame", "0.316 people / frame"],
        ["Mean Signed Error (Bias)", "-0.450 (Slight undercount)", "+0.100 (Near zero)"]
    ]
    t44 = Table([[Paragraph(c, ParagraphStyle('TC44', fontName='Times-Roman', fontSize=8.5, leading=11)) for c in row] for row in t44_data],
                colWidths=[2.3*inch, 1.7*inch, 1.7*inch])
    t44.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EEEEEE")),
        ('FONTNAME', (0,0), (-1,0), 'Times-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#BBBBBB")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3)
    ]))
    story.append(t44)
    story.append(Spacer(1, 10))
    
    story.append(PageRecorder("sec4_6"))
    story.append(Paragraph("4.6   Discussion of Phase-I Results", section_title_style))
    story.append(Paragraph(
        "The experimental results demonstrate that MetroGuard AI Phase-I achieves exceptional operational fidelity:<br/>"
        "• <b>Industrial-Grade Accuracy:</b> The crowd counting accuracy of 97.79% (production) to 99.51% (high-recall) comfortably surpasses "
        "the transit industry deployment standard of &gt;= 90% counting fidelity.<br/>"
        "• <b>Negligible Counting Error:</b> With an MAE of only 0.10 to 0.45 persons per frame in scenes containing up to 39 simultaneous commuters, "
        "the footpoint filtering algorithm exhibits outstanding resilience against background occlusions.<br/>"
        "• <b>Real-Time Edge Headroom:</b> Operating at 62.9 FPS provides abundant computational headroom to execute Phase-II violence detection "
        "and baggage tracking algorithms concurrently on the same hardware.", body_no_indent))
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # 15. CHAPTER 5: WORK PLAN, TASK ALLOCATION AND FUTURE SCOPE
    # -------------------------------------------------------------
    story.append(PageRecorder("ch5"))
    story.append(ChapterHeading("Chapter 5", "Work Plan, Task Allocation and Future Scope"))
    story.append(Paragraph(
        "Delivering a comprehensive incident intelligence framework requires disciplined project scheduling, milestone tracking, resource "
        "management, and equitable task distribution. This chapter details the project work plan, illustrates the milestone Gantt chart, identifies "
        "necessary compute and data resources, outlines individual member responsibilities, and charts the Phase-II development roadmap.", body_style))
    
    story.append(PageRecorder("sec5_1"))
    story.append(Paragraph("5.1   Project Work Plan", section_title_style))
    story.append(Paragraph(
        "The MetroGuard AI development lifecycle is structured across six major sequential phases spanning the academic year. Figure 5.1 depicts "
        "the major phases and technical task breakdown.", body_style))
    
    if os.path.exists(plan_path):
        story.append(RLImage(plan_path, width=5.6*inch, height=3.1*inch))
        story.append(PageRecorder("fig5_1"))
        story.append(Paragraph("<b>Figure 5.1:</b> MetroGuard AI Project Work Plan and Major Phase Sequences", fig_caption_style))
    
    story.append(Paragraph(
        "The scope of each phase is outlined below:<br/>"
        "• <b>Phase 1 (Literature Study and Requirements):</b> Comprehensive review of state-of-the-art surveillance models, problem definition, "
        "and system requirements analysis.<br/>"
        "• <b>Phase 2 (Dataset Preparation):</b> Curation and annotation of transit video datasets covering normal flows, physical altercations, "
        "crowd surges, and unattended objects.<br/>"
        "• <b>Phase 3 (Detection and Tracking Modules):</b> Implementation and tuning of YOLOv11s object detection, ByteTrack multi-object tracking, "
        "and MobileSAM target tracking (Completed in Phase-I).<br/>"
        "• <b>Phase 4 (Incident Reasoning and Risk Assessment):</b> Engineering the spatiotemporal correlation matrix, event graph schema, and "
        "multi-factor risk priority scoring formula (Phase-II focus).<br/>"
        "• <b>Phase 5 (Dashboard and System Integration):</b> Developing the full multi-camera dispatcher dashboard with natural-language incident "
        "summaries and alert routing.<br/>"
        "• <b>Phase 6 (Testing, Evaluation and Documentation):</b> End-to-end stress testing on multi-hour transit feeds, benchmark evaluations, "
        "final thesis preparation, and defense.", body_no_indent))
    
    story.append(PageBreak())
    story.append(PageRecorder("sec5_2"))
    story.append(Paragraph("5.2   Gantt Chart and Milestone Timeline", section_title_style))
    story.append(Paragraph("Figure 5.2 illustrates the monthly milestone timeline and Gantt chart across the project duration from September 2026 to April 2027.", body_style))
    
    if os.path.exists(gantt_path):
        story.append(RLImage(gantt_path, width=5.6*inch, height=3.1*inch))
        story.append(PageRecorder("fig5_2"))
        story.append(Paragraph("<b>Figure 5.2:</b> MetroGuard AI Project Timeline and Milestone Gantt Chart", fig_caption_style))
    
    story.append(Paragraph(
        "As shown in Figure 5.2, Phase-I milestones (Literature Study, Requirements, Detection Backbone, Tracking, and Initial Crowd Dashboard) "
        "were successfully accomplished on schedule between September and October 2026. Phase-II execution commences in November 2026.", body_style))
    
    story.append(PageRecorder("sec5_3"))
    story.append(Paragraph("5.3   Resource Identification", section_title_style))
    story.append(Paragraph(
        "Successful execution of the project relies on the following identified resources:<br/>"
        "• <b>Compute Hardware:</b> Dedicated workstation equipped with an NVIDIA RTX 4050 GPU (6 GB VRAM) for local edge inference, supported by "
        "high-performance multi-core CPUs for video decoding.<br/>"
        "• <b>Video Data Repositories:</b> Public surveillance benchmark datasets (e.g., UCF-Crime, RWF-2000, PETS 2009, ShanghaiTech Campus) and "
        "recorded 1080p transit concourse footage.<br/>"
        "• <b>Software Frameworks:</b> Python 3.12, PyTorch 2.9, Ultralytics YOLOv11s, ByteTrack C++/Python bindings, MobileSAM, OpenCV, NumPy, and Streamlit.", body_no_indent))
    
    story.append(PageRecorder("sec5_4"))
    story.append(Paragraph("5.4   Task Allocation Among Team Members", section_title_style))
    story.append(Paragraph("Table 5.1 details the formal allocation of responsibilities among the batch members.", body_style))
    
    # Table 5.1
    story.append(PageRecorder("table5_1"))
    story.append(Paragraph("<b>Table 5.1:</b> Task Allocation Among Project Batch Members", table_caption_style))
    t51_data = [
        ["Member Name", "KTU Reg. No.", "Primary Assigned Responsibilities"],
        ["Adithya Chandran", "SPT23AD006", "Overall system architecture design, YOLOv11s perception integration, Streamlit operator dashboard engineering, and edge optimization."],
        ["Akhil P", "SPT23AD009", "Surveillance dataset preparation and curation, abandoned baggage module development, model fine-tuning, and empirical accuracy benchmarking."],
        ["Muhammed Shibil KP", "SPT23AD034", "Comprehensive literature review, ByteTrack multi-object tracking integration, and human pose/motion-based fight detection module development."],
        ["Shehruz Muhammed CS", "SPT23AD043", "Spatiotemporal incident reasoning engine, multi-source context fusion, operational risk assessment formulation, and report documentation."],
        ["All Members", "Joint Team", "System integration testing, end-to-end concourse evaluation, technical documentation, and final defense presentation preparation."]
    ]
    t51 = Table([[Paragraph(c, ParagraphStyle('TC51', fontName='Times-Roman', fontSize=8.5, leading=11)) for c in row] for row in t51_data],
                colWidths=[1.4*inch, 1.0*inch, 3.3*inch])
    t51.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EEEEEE")),
        ('FONTNAME', (0,0), (-1,0), 'Times-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#BBBBBB")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3)
    ]))
    story.append(t51)
    story.append(Spacer(1, 10))
    
    story.append(PageRecorder("sec5_5"))
    story.append(Paragraph("5.5   Phase-II Development Roadmap", section_title_style))
    story.append(Paragraph(
        "Building upon the verified Phase-I perception foundation, the Phase-II roadmap encompasses four major technical frontiers:<br/>"
        "1. <b>Fight Detection Integration:</b> Implement a lightweight pose and optical-flow fusion model (inspired by [8, 14]) to detect "
        "physical violence and aggressive grapples in real time.<br/>"
        "2. <b>Abandoned Baggage Tracking:</b> Deploy the four-state <i>carry-place-leave-stationary</i> finite state machine [21] over tracked luggage "
        "items, measuring owner-bag separation distance and dwell time.<br/>"
        "3. <b>Graph-Driven Incident Intelligence Engine:</b> Construct spatiotemporal interaction graphs [11] that dynamically correlate "
        "simultaneous altercations, baggage drops, and crowd panics into unified incident entities.<br/>"
        "4. <b>Explainable Natural Language Reporting:</b> Integrate lightweight language models [5] to synthesize concise, natural-language "
        "incident audit reports for rapid transit authority review.", body_no_indent))
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # 16. CHAPTER 6: CONCLUSION
    # -------------------------------------------------------------
    story.append(PageRecorder("ch6"))
    story.append(ChapterHeading("Chapter 6", "Conclusion"))
    story.append(Paragraph(
        "This final chapter synthesizes the accomplishments of Project Phase-I, highlights the core technical takeaways, and provides concluding "
        "perspectives on the future evolution of MetroGuard AI.", body_style))
    
    story.append(PageRecorder("sec6_1"))
    story.append(Paragraph("6.1   Summary of Phase-I Work", section_title_style))
    story.append(Paragraph(
        "The primary objective of Project Phase-I was to design, construct, and validate a high-throughput, edge-capable computer vision backbone "
        "capable of serving as the foundation for the MetroGuard AI multi-event incident intelligence platform. All planned Phase-I objectives were "
        "successfully accomplished:<br/>"
        "• <b>High-Speed Commuter Perception:</b> An Ultralytics YOLOv11s detection backbone was deployed, achieving 79.1% mAP@0.50 on the COCO Person "
        "benchmark and maintaining an inference throughput of 62.9 FPS at 1280px resolution on an NVIDIA RTX 4050 GPU.<br/>"
        "• <b>Robust Multi-Object Tracking:</b> The ByteTrack algorithm was integrated, utilizing dual-score Kalman filtering to maintain persistent "
        "commuter identities through severe visual occlusions and crowd intersections.<br/>"
        "• <b>Calibrated Footpoint ROI Filtering:</b> A normalized Region of Interest framework with ground-contact footpoint filtering was formulated, "
        "eliminating perspective distortions and ensuring that only passengers standing within designated operational zones are counted.<br/>"
        "• <b>High-Fidelity Crowd Occupancy Monitoring:</b> Over an empirical benchmark of 20 sampled surveillance frames encompassing 407 ground-truth "
        "pedestrians, the system achieved a remarkable crowd counting accuracy of 99.51% with an MAE of 0.100 pedestrians per frame.<br/>"
        "• <b>Target Tracking Module (TAM):</b> MobileSAM was integrated to provide prompt-guided silhouette segmentation, dwell time analysis, and "
        "kinematic breadcrumb tracking for designated individuals of interest.<br/>"
        "• <b>Interactive Operator Interface:</b> A responsive Streamlit dashboard was built, providing security personnel with live video streaming, "
        "dynamic ROI sliders, occupancy alerts, and an exportable event log.", body_no_indent))
    
    story.append(PageRecorder("sec6_2"))
    story.append(Paragraph("6.2   Key Takeaways and Contributions", section_title_style))
    story.append(Paragraph(
        "The Phase-I research yielded several key technical takeaways:<br/>"
        "• <b>Edge Viability of YOLOv11s:</b> Achieving 62.9 FPS confirms that advanced deep learning surveillance does not require expensive "
        "data center infrastructure; modern lightweight models can run comfortably on local station workstations.<br/>"
        "• <b>Footpoint vs Centroid Filtering:</b> In transit concourses with steep camera angles, evaluating the ground-contact footpoint rather than "
        "the bounding box centroid is critical to eliminating false boundary crossings.<br/>"
        "• <b>Foundation for Multi-Event Fusion:</b> By establishing persistent tracking and robust occupancy estimation, the system possesses the exact "
        "spatial-temporal primitives required to link fights, crowds, and abandoned baggage in Phase-II.", body_no_indent))
    
    story.append(PageRecorder("sec6_3"))
    story.append(Paragraph("6.3   Concluding Remarks", section_title_style))
    story.append(Paragraph(
        "The successful completion of Project Phase-I establishes a validated, industrial-grade perception pipeline for smart metro surveillance. "
        "MetroGuard AI demonstrates that edge computer vision can deliver sub-second processing speeds, exceptional counting fidelity, and real-time "
        "situational awareness. With this robust foundation in place, Project Phase-II will focus on integrating physical altercation detection, unattended "
        "baggage tracking, graph-based context fusion, and explainable incident generation—ultimately delivering a transformative, multi-event "
        "decision-support platform for modern urban transit systems.", body_style))
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # 17. REFERENCES (IEEE Style, Exactly 21 Papers in Order [1]-[21])
    # -------------------------------------------------------------
    story.append(PageRecorder("references"))
    story.append(ChapterHeading("", "References"))
    
    references = [
        "[1] A. A. Hamid, S. A. Monadjemi, and B. Shoushtarian, 'ABDviaMSIFAT: Abnormal Crowd Behavior Detection Utilizing a Multi-Source Information Fusion Technique,' <i>IEEE Access</i>, vol. 13, pp. 75000–75019, 2025, doi: 10.1109/ACCESS.2024.3436007.",
        "[2] D. Chaudhary, S. Kumar, and V. S. Dhaka, 'Intelligent Anomaly Detection and Localization With Crowd Density Estimation for Improved Public Safety,' <i>IEEE Access</i>, vol. 13, pp. 169912–169928, 2025, doi: 10.1109/ACCESS.2025.3614146.",
        "[3] A. M. Qasim, N. Abbas, A. Ali, and B. A. A. Al-Ghamdi, 'Abandoned Object Detection and Classification Using Deep Embedded Vision,' <i>IEEE Access</i>, vol. 12, pp. 35539–35551, 2024, doi: 10.1109/ACCESS.2024.3369233.",
        "[4] H.-Y. Lin and C.-H. Tseng, 'Abnormal Activity Detection and Classification of Bus Passengers With In-Vehicle Image Sensing,' <i>IEEE Access</i>, 2024, doi: 10.1109/ACCESS.2024.3365138.",
        "[5] T. Yuan, X. Zhang, K. Liu, B. Liu, C. Chen, J. Jin, and Z. Jiao, 'Towards Surveillance Video-and-Language Understanding: New Dataset, Baselines, and Challenges,' in <i>Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR)</i>, 2024, pp. 22052–22061, doi: 10.1109/CVPR52733.2024.02082.",
        "[6] S. F. A. Shah, M. Q. Khan, A. A. Alsuwaylimi, and L. A. Alenezi, 'A Two-Stage Spatiotemporal CNN-YOLOv9 Framework for High-Precision Real-Time Abandoned Object Detection in Public Surveillance Videos,' <i>IEEE Access</i>, vol. 14, pp. 35983–35997, 2026, doi: 10.1109/ACCESS.2026.3669588.",
        "[7] Y. Wang and V. Y. Mariano, 'A Multi Object Tracking Framework Based on YOLOv8s and ByteTrack Algorithm,' <i>IEEE Access</i>, 2024, doi: 10.1109/ACCESS.2024.3450370.",
        "[8] S. T. Y. Aung, W. Kusakunniran, and Y. K. Hooi, 'Leveraging Fusion Methods of Human Pose and Motion Dynamics for Accurate Violence Detection in Video Surveillance,' <i>IEEE Access</i>, 2025, doi: 10.1109/ACCESS.2025.3613765.",
        "[9] Z. Yang and R. J. Radke, 'Context-aware Video Anomaly Detection in Long-Term Datasets,' in <i>Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. Workshops (CVPRW)</i>, 2024, pp. 4002–4011, doi: 10.1109/CVPRW63382.2024.00404.",
        "[10] Z. Zhu, H. He, and M. Wang, 'A Spatio-Temporal Semantic Algorithm for Video Anomaly Detection from Monitoring Perspectives,' in <i>Proc. 5th Int. Conf. Artif. Intell., Robot., Commun. (ICAIRC)</i>, 2025, doi: 10.1109/ICAIRC68035.2025.11385035.",
        "[11] M. Khan, W. Gueaieb, A. Elsaddik, G. De Masi, and F. Karray, 'Graph-Based Knowledge Driven Approach for Violence Detection,' <i>IEEE Consum. Electron. Mag.</i>, vol. 14, no. 1, pp. 77–85, 2025, doi: 10.1109/MCE.2024.3446192.",
        "[12] M. Khan, M. Saad, A. Khan, W. Gueaieb, A. E. Saddik, G. De Masi, and F. Karray, 'Action Knowledge Graph for Violence Detection Using Audiovisual Features,' in <i>Proc. IEEE Int. Conf. Consum. Electron. (ICCE)</i>, 2024, doi: 10.1109/ICCE59016.2024.10444158.",
        "[13] A. S. Kannan, Z. A. Alsalami, A. Nihlani, K. Gowthami, M. A. K. Abdukodir Kizi, A. Amudha, and Z. Mamadalieva, 'Real-Time Video Surveillance Analysis at the Edge in Smart Cities,' in <i>Proc. Int. Conf. Innov. Emerg. Technol. AI Commun. Syst. (IETACS)</i>, 2025, doi: 10.1109/IETACS68750.2025.11385417.",
        "[14] M. Khan, A. E. Saddik, W. Gueaieb, G. De Masi, and F. Karray, 'VD-Net: An Edge Vision-Based Surveillance System for Violence Detection,' <i>IEEE Access</i>, vol. 12, pp. 43796–43808, 2024, doi: 10.1109/ACCESS.2024.3380192.",
        "[15] M. H. Habeb, M. Salama, and L. A. Elrefaei, 'An Attention-Based Unsupervised Framework for Video Anomaly Detection in Large Heterogeneous Environments,' in <i>Proc. MIUCC</i>, 2024, doi: 10.1109/MIUCC62295.2024.10783549.",
        "[16] H. Lee, D. Kang, H. Park, S. Park, D. Jeong, and J. Paik, 'Real-Time Human Group Detection and Clustering in Crowded Environments Using Enhanced Multi-Object Tracking,' <i>IEEE Access</i>, vol. 12, pp. 184028–184039, 2024, doi: 10.1109/ACCESS.2024.3503661.",
        "[17] M. Zhang, J. Wang, Q. Qi, H. Sun, Z. Zhuang, P. Ren, R. Ma, and J. Liao, 'Multi-Scale Video Anomaly Detection by Multi-Grained Spatio-Temporal Representation Learning,' in <i>Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR)</i>, 2024, pp. 17385–17394, doi: 10.1109/CVPR52733.2024.01646.",
        "[18] A. Amirkhani and S. A. Khoshnevis, 'CFTformer: End-to-End Cross-Frame Multi-Object Tracking With Transformer,' <i>IEEE Access</i>, 2025, doi: 10.1109/ACCESS.2025.3567349.",
        "[19] S. Zhuo, H. Bai, L. Jiang, X. Zhou, X. Duan, Y. Ma, and Z. Zhou, 'SCL-YOLOv11: A Lightweight Object Detection Network for Low-Illumination Environments,' <i>IEEE Access</i>, vol. 13, pp. 47653–47662, 2025, doi: 10.1109/ACCESS.2025.3550947.",
        "[20] H. Zhang, Y. Guo, and X. Du, 'Online Action Detection by Long Short-Term Transformer with Query Exemplars,' in <i>Proc. IEEE Int. Joint Conf. Neural Netw. (IJCNN)</i>, 2024, doi: 10.1109/IJCNN60899.2024.10651333.",
        "[21] T. Soontornnapar, 'Abandoned Bag Detection in Public Areas Using Grounding DINO With Fine-Grained Prompts,' in <i>Proc. ECTI-CON</i>, 2025, doi: 10.1109/ECTI-CON64996.2025.11100886."
    ]
    
    for r in references:
        story.append(Paragraph(r, ref_style))
        
    return story

def build_pdf():
    pdf_path = r"c:\Users\akhia\Downloads\metroguard_phase1\PROJECT REPORT\project_report.pdf"
    
    # Margin specifications matching KTU LaTeX template:
    # left=3.5cm, top=1.5cm, right=3.0cm, bottom=4.0cm
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=3.5 * cm,
        rightMargin=3.0 * cm,
        topMargin=1.5 * cm,
        bottomMargin=3.5 * cm
    )
    
    print("Pass 1: Discovering exact element page numbers...")
    story_pass1 = build_story(pass_num=1)
    doc.build(story_pass1, canvasmaker=NumberedCanvas)
    
    print(f"Discovered element pages (body start: {PAGE_MAP.get('ch1')}):")
    for k in ["abstract", "acknowledgement", "contents", "lof", "lot", "symbols", "ch1", "ch2", "ch3", "ch4", "ch5", "ch6", "references"]:
        print(f"  {k}: page {PAGE_MAP.get(k)} (TOC string: {get_page_str(k, is_front=(k in ['abstract', 'acknowledgement', 'lof', 'lot', 'symbols']))})")
        
    print("\nPass 2: Building final PDF with verified pagination and dot leaders...")
    story_pass2 = build_story(pass_num=2)
    doc.build(story_pass2, canvasmaker=NumberedCanvas)
    
    print(f"Successfully generated {pdf_path} (size: {os.path.getsize(pdf_path)} bytes)")

if __name__ == "__main__":
    build_pdf()
