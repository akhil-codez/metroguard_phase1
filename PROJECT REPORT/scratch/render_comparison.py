import os
import fitz

comp_dir = r"c:\Users\akhia\Downloads\metroguard_phase1\PROJECT REPORT\pdf_comparison"
os.makedirs(comp_dir, exist_ok=True)

doc = fitz.open(r"c:\Users\akhia\Downloads\metroguard_phase1\PROJECT REPORT\project_report.pdf")
print("Total pages in generated PDF:", len(doc))

# Render first 14 pages
for p in range(min(14, len(doc))):
    page = doc[p]
    pix = page.get_pixmap(dpi=150)
    out_path = os.path.join(comp_dir, f"new_gen_page_{p+1}.png")
    pix.save(out_path)
    print(f"Saved {out_path}")
