from pypdf import PdfReader
from pathlib import Path
pdf_path = Path('sample_pdf/product_catalog_v2.pdf')
reader = PdfReader(str(pdf_path))
print('pages', len(reader.pages))
for i, p in enumerate(reader.pages[:3]):
    text = p.extract_text() or ''
    print('--- PAGE', i + 1, '---')
    print(text[:4000])
    print()
