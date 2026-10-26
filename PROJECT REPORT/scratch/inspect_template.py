import fitz

doc = fitz.open("template/project_report.pdf")
print("Total pages:", len(doc))
for p in range(min(12, len(doc))):
    print(f"\n=================== PAGE {p+1} ===================")
    page = doc[p]
    blocks = page.get_text("dict")["blocks"]
    for b in blocks:
        if "lines" in b:
            for l in b["lines"]:
                line_str = "".join(s["text"] for s in l["spans"]).strip()
                if not line_str:
                    continue
                first_span = l["spans"][0]
                fonts = set(s["font"] for s in l["spans"])
                sizes = set(round(s["size"], 1) for s in l["spans"])
                bbox = l["bbox"]
                out = f"y={bbox[1]:5.1f} | x={bbox[0]:5.1f}..{bbox[2]:5.1f} | font={list(fonts)} size={list(sizes)} | {line_str[:70]}"
                print(out.encode('ascii', 'replace').decode('ascii'))
