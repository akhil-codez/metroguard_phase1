import fitz

orig = fitz.open("template/project_report.pdf")
gen = fitz.open("project_report.pdf")

print(f"Original pages: {len(orig)}, Generated pages: {len(gen)}")

print("\n--- ORIGINAL FIRST 10 PAGES SUMMARY ---")
for i in range(min(10, len(orig))):
    p = orig[i]
    first_words = " ".join(p.get_text().split()[:8])
    print(f"Orig Page {i+1}: {first_words.encode('ascii', 'replace').decode('ascii')}")

print("\n--- GENERATED FIRST 15 PAGES SUMMARY ---")
for i in range(min(15, len(gen))):
    p = gen[i]
    first_words = " ".join(p.get_text().split()[:8])
    print(f"Gen Page {i+1}: {first_words.encode('ascii', 'replace').decode('ascii')}")
