import fitz

doc = fitz.open("project_report.pdf")
found = 0
for p in range(len(doc)):
    page = doc[p]
    blocks = page.get_text("dict")["blocks"]
    for b in blocks:
        if "lines" in b:
            for l in b["lines"]:
                for s in l["spans"]:
                    if "Helvetica" in s["font"]:
                        print(f"Page {p+1}: font={s['font']} text={s['text'][:50]}")
                        found += 1
if found == 0:
    print("No text spans use Helvetica!")
else:
    print(f"Total Helvetica spans: {found}")
