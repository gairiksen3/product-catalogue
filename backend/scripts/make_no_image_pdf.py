"""Generate a text-only catalogue PDF (no embedded images) for testing the
"No image" placeholder in the product listing.

Dependency-free: writes a minimal but valid PDF by hand. The layout follows the
"Block" style the importer's generic parser understands:

    CATEGORY / Name / $price / SKU: XXX / DESCRIPTION / <text> /
    INGREDIENTS / <text> / In Stock (N)

Because no image XObjects are added, page.images is empty and every product is
imported with image_path = null.
"""

import sys
from pathlib import Path

PRODUCTS = [
    {
        "category": "BEVERAGES",
        "name": "Cold Brew Coffee",
        "price": "4.50",
        "sku": "BEV-1001",
        "description": "Slow-steeped cold brew with a smooth, low-acid finish.",
        "ingredients": "Water, Arabica coffee.",
        "stock": "In Stock (42)",
    },
    {
        "category": "BAKERY",
        "name": "Sourdough Loaf",
        "price": "6.00",
        "sku": "BAK-2002",
        "description": "Naturally leavened sourdough with a crisp crust.",
        "ingredients": "Flour, water, salt, starter.",
        "stock": "In Stock (18)",
    },
    {
        "category": "SNACKS",
        "name": "Sea Salt Almonds",
        "price": "3.25",
        "sku": "SNK-3003",
        "description": "Dry-roasted almonds finished with flaky sea salt.",
        "ingredients": "Almonds, sea salt.",
        "stock": "Out of Stock (0)",
    },
    {
        "category": "DAIRY",
        "name": "Greek Yogurt",
        "price": "2.75",
        "sku": "DRY-4004",
        "description": "Thick, protein-rich plain Greek yogurt.",
        "ingredients": "Cultured milk.",
        "stock": "In Stock (60)",
    },
]


def esc(text: str) -> str:
    """Escape a string for a PDF literal ()."""
    return text.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


def build_lines():
    lines = ["PRODUCT CATALOG (NO IMAGES)"]
    for p in PRODUCTS:
        lines += [
            "",
            p["category"],
            p["name"],
            f"${p['price']}",
            f"SKU: {p['sku']}",
            "DESCRIPTION",
            p["description"],
            "INGREDIENTS",
            p["ingredients"],
            p["stock"],
        ]
    return lines


def content_stream(lines):
    leading = 16
    parts = ["BT", "/F1 11 Tf", f"{leading} TL", "50 780 Td"]
    for i, line in enumerate(lines):
        if i > 0:
            parts.append("T*")
        parts.append(f"({esc(line)}) Tj")
    parts.append("ET")
    return "\n".join(parts).encode("latin-1")


def build_pdf(lines) -> bytes:
    stream = content_stream(lines)
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, body in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf += b"%d 0 obj\n" % i + body + b"\nendobj\n"

    xref_pos = len(pdf)
    pdf += b"xref\n"
    pdf += b"0 %d\n" % (len(objects) + 1)
    pdf += b"0000000000 65535 f \n"
    for off in offsets:
        pdf += b"%010d 00000 n \n" % off
    pdf += b"trailer\n<< /Size %d /Root 1 0 R >>\n" % (len(objects) + 1)
    pdf += b"startxref\n%d\n%%%%EOF\n" % xref_pos
    return bytes(pdf)


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else (
        Path(__file__).resolve().parents[2] / "sample_pdf" / "no_image_products.pdf"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(build_pdf(build_lines()))
    print(f"Wrote {out}")
