import fitz

doc = fitz.open("template/project_report.pdf")
print("Page count:", len(doc))
print("Page 1 rect:", doc[0].rect)
print("Page 1 margins estimation:")
# Let's inspect where text starts on page 10 (Chapter 1)
p10 = doc[9] # 0-indexed page 10
blocks = p10.get_text("dict")["blocks"]
for b in blocks:
    if "lines" in b:
        for l in b["lines"]:
            text = "".join(s["text"] for s in l["spans"]).strip()
            if text in ["Chapter 1", "Introduction"]:
                print(f"'{text}': bbox={l['bbox']}, font={l['spans'][0]['font']}, size={l['spans'][0]['size']}")
