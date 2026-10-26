import os
import fitz

comp_dir = r"c:\Users\akhia\Downloads\metroguard_phase1\PROJECT REPORT\pdf_comparison"
doc = fitz.open(r"c:\Users\akhia\Downloads\metroguard_phase1\PROJECT REPORT\project_report.pdf")

# Let's find pages with images and tables
render_pages = [17, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 50, 51]
for p_idx in render_pages:
    if p_idx <= len(doc):
        page = doc[p_idx - 1]
        pix = page.get_pixmap(dpi=120)
        out_path = os.path.join(comp_dir, f"inspect_page_{p_idx}.png")
        pix.save(out_path)
        print(f"Rendered page {p_idx} -> {out_path}")
