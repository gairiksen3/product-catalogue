from pypdf import PdfReader
reader = PdfReader('sample_pdf/product_catalog_v2.pdf')
for page_num in range(1, 6):
    text = reader.pages[page_num-1].extract_text() or ''
    print('=== PAGE', page_num, '===')
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines:
        print(line)
    print()
