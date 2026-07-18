from pypdf import PdfReader
reader = PdfReader('sample_pdf/product_catalog_v2.pdf')
for i in range(min(5, len(reader.pages))):
    page = reader.pages[i]
    print(i + 1, len(page.images), [img.name for img in page.images[:5]])
