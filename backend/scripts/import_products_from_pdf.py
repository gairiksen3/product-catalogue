"""Extract products from a catalogue PDF.

Supports several common catalogue layouts:

  * "Gourmet" style  - CATEGORY / $price SKU: XXX / DESCRIPTION / INGREDIENTS /
                       In Stock (N), with product names grouped after a page header.
  * "Block" style    - CATEGORY / Name / $price / SKU: XXX / DESCRIPTION / ... /
                       INGREDIENTS / ... / In Stock (N)   (e.g. bakery catalogue).
  * "Table" style    - Image / Name / SKU-1001 / $price / In Stock / Description
                       repeating per product.

The parser normalises whitespace (tabs, unicode junk), auto-detects the layout,
and falls back to a generic SKU-anchored scan so unknown layouts still work when
they contain recognisable price / SKU / stock markers.
"""

import json
import os
import re
import sys
from pathlib import Path

from pypdf import PdfReader

PRICE_RE = re.compile(r'\$\s*(\d+(?:\.\d{1,2})?)')
STOCK_RE = re.compile(r'\b(In\s*Stock|Out\s*of\s*Stock)\b(?:\s*\((\d+)\))?', re.I)
SKU_LABEL_RE = re.compile(r'\bSKU\b\s*[:#]\s*([A-Za-z0-9][A-Za-z0-9\-_/]*)', re.I)
SKU_CODE_RE = re.compile(r'^(SKU[-\s][A-Za-z0-9\-]+|[A-Z]{2,}-\d{2,}[A-Za-z0-9\-]*)$')

SECTION_WORDS = {
    'DESCRIPTION', 'INGREDIENTS', 'IMAGE', 'IMAGES', 'NAME', 'SKU',
    'PRICE', 'STOCK', 'CATEGORY', 'PHOTO',
}


def slugify(value: str) -> str:
    value = re.sub(r'[^a-zA-Z0-9]+', '-', value).strip('-').lower()
    return value or 'product'


def norm_lines(text: str):
    """Normalise a page's text into clean, non-empty lines."""
    lines = []
    for raw in (text or '').splitlines():
        s = raw.replace('\t', ' ').replace('�', ' ')
        s = re.sub(r'\s+', ' ', s).strip()
        if s:
            lines.append(s)
    return lines


def get_sku(line: str):
    m = SKU_CODE_RE.match(line)
    if m:
        return re.sub(r'^SKU[-\s]', '', m.group(1)).strip() or m.group(1).strip()
    m = SKU_LABEL_RE.search(line)
    if m:
        return m.group(1).strip()
    return None


def is_price(line: str) -> bool:
    return bool(PRICE_RE.search(line))


def is_stock(line: str) -> bool:
    return bool(STOCK_RE.search(line))


def is_category(line: str) -> bool:
    if line.upper() in SECTION_WORDS:
        return False
    if len(line) > 28 or '$' in line:
        return False
    if any(ch.isdigit() for ch in line):
        return False
    letters = [c for c in line if c.isalpha()]
    if len(letters) < 2:
        return False
    return line == line.upper()


def is_header(line: str) -> bool:
    up = line.upper()
    return 'CATALOG' in up or 'CATALOGUE' in up or up.startswith('PAGE ')


def looks_like_name(line: str) -> bool:
    if not line or line.upper() in SECTION_WORDS:
        return False
    if line.lower() in ('image', 'images', 'photo'):
        return False
    if is_price(line) or is_stock(line) or get_sku(line):
        return False
    if is_category(line) or is_header(line):
        return False
    return any(c.isalpha() for c in line)


def parse_price(line: str):
    m = PRICE_RE.search(line)
    return float(m.group(1)) if m else None


def parse_stock(line: str):
    m = STOCK_RE.search(line)
    if not m:
        return None, None
    status = 'Out of Stock' if 'out' in m.group(1).lower() else 'In Stock'
    qty = int(m.group(2)) if m.group(2) else None
    return status, qty


def extract_page_images(page, output_dir, base_name, page_num, count):
    """Return up to `count` image paths saved from the page, in order."""
    paths = []
    try:
        images = list(page.images)
    except Exception:
        images = []
    for idx in range(count):
        if idx >= len(images):
            paths.append(None)
            continue
        try:
            image_obj = images[idx]
            data = image_obj.data
            if not data:
                paths.append(None)
                continue
            ext = 'jpg' if image_obj.name.lower().endswith(('.jpg', '.jpeg')) else 'png'
            filename = f'{slugify(base_name)}-{page_num}-{idx + 1}.{ext}'
            path = Path(output_dir) / filename
            path.write_bytes(data)
            paths.append(str(path).replace('\\', '/'))
        except Exception:
            paths.append(None)
    return paths


def parse_page_generic(lines, page_num):
    """SKU-anchored parser that handles block and table layouts on one page."""
    anchors = [i for i, ln in enumerate(lines) if get_sku(ln)]
    products = []

    for a, idx in enumerate(anchors):
        lo = anchors[a - 1] + 1 if a > 0 else 0
        hi = anchors[a + 1] if a + 1 < len(anchors) else len(lines)
        sku = get_sku(lines[idx])

        # --- price: nearest price line either side of the SKU ---
        price = None
        for off in range(1, max(hi - idx, idx - lo) + 1):
            for j in (idx + off, idx - off):
                if lo <= j < hi and j != idx and is_price(lines[j]):
                    price = parse_price(lines[j])
                    break
            if price is not None:
                break
        # price may also sit on the SKU line itself (e.g. "$5 SKU: X")
        if price is None and is_price(lines[idx]):
            price = parse_price(lines[idx])

        # --- name: nearest sensible title line before the SKU ---
        name = None
        for j in range(idx - 1, lo - 1, -1):
            if looks_like_name(lines[j]):
                name = lines[j].strip(' -–—:').strip()
                break
        # fall back to a title line just after the SKU
        if not name:
            for j in range(idx + 1, hi):
                if looks_like_name(lines[j]):
                    name = lines[j].strip(' -–—:').strip()
                    break

        # --- category: last ALL-CAPS category line at/before the SKU ---
        category = None
        for j in range(idx, lo - 1, -1):
            if is_category(lines[j]):
                category = lines[j].title()
                break

        # --- stock: first stock marker after the SKU (then before) ---
        stock_status, stock_qty = None, None
        for j in list(range(idx + 1, hi)) + list(range(idx - 1, lo - 1, -1)):
            if is_stock(lines[j]):
                stock_status, stock_qty = parse_stock(lines[j])
                break

        # --- description & ingredients ---
        description, ingredients = None, None
        window = list(range(idx + 1, hi))
        desc_marker = next((j for j in window if lines[j].upper() == 'DESCRIPTION'), None)
        ing_marker = next((j for j in window if lines[j].upper() == 'INGREDIENTS'), None)

        def collect(start, stops):
            out = []
            for j in range(start + 1, hi):
                if j in stops or lines[j].upper() in SECTION_WORDS:
                    break
                if is_stock(lines[j]) or get_sku(lines[j]) or is_category(lines[j]):
                    break
                if is_price(lines[j]) or is_header(lines[j]):
                    continue
                out.append(lines[j])
            return ' '.join(out).strip() or None

        if desc_marker is not None:
            description = collect(desc_marker, {ing_marker} if ing_marker is not None else set())
        if ing_marker is not None:
            ingredients = collect(ing_marker, set())

        # table layout: no DESCRIPTION marker — take the longest sentence after SKU
        if description is None:
            candidates = [
                lines[j] for j in window
                if not is_price(lines[j]) and not is_stock(lines[j])
                and not get_sku(lines[j]) and not is_category(lines[j])
                and lines[j].upper() not in SECTION_WORDS and not is_header(lines[j])
                and lines[j].lower() not in ('image', 'images', 'photo')
                and lines[j] != name
            ]
            if candidates:
                description = max(candidates, key=len)

        products.append({
            'name': name,
            'sku': sku,
            'category': category or 'General',
            'price': round(price, 2) if price is not None else 0,
            'stock_status': stock_status or 'In Stock',
            'stock_quantity': stock_qty if stock_qty is not None else 0,
            'description': description or 'Imported from PDF',
            'ingredients': ingredients,
            'page_num': page_num,
        })

    return products


def parse_gourmet(reader):
    """Original layout: names grouped after 'GOURMET RESTAURANT CATALOG' header."""
    results = []
    for page_num, page in enumerate(reader.pages, start=1):
        lines = norm_lines(page.extract_text() or '')
        header_index = next((i for i, l in enumerate(lines)
                             if l.startswith('GOURMET RESTAURANT CATALOG')), None)

        page_title_lines = []
        if header_index is not None:
            for line in lines[header_index + 1:]:
                if line in {'DESCRIPTION', 'INGREDIENTS'}:
                    continue
                if line.startswith('$') or 'SKU:' in line or line.startswith('In Stock') or line.startswith('Out of Stock'):
                    continue
                if line.isupper() and len(line) < 40:
                    continue
                if line.lower().startswith('gourmet restaurant catalog'):
                    continue
                if len(line) > 80:
                    continue
                if re.match(r'^[A-Z][A-Za-z0-9\s\-]+$', line) and not line.isupper():
                    page_title_lines.append(line)
                    if len(page_title_lines) == 2:
                        break

        blocks = []
        current = {}
        for line in lines:
            price_match = re.match(r'^\$(\d+(?:\.\d+)?) SKU: ([A-Z0-9-]+)$', line)
            if price_match:
                current['price'] = float(price_match.group(1))
                current['sku'] = price_match.group(2)
                continue
            stock_match = re.match(r'^(In Stock|Out of Stock)\s*\((\d+)\)$', line)
            if stock_match:
                current['stock_status'] = stock_match.group(1)
                current['stock_quantity'] = int(stock_match.group(2))
                blocks.append(current)
                current = {}
                continue
            if re.match(r'^[A-Z][A-Z0-9\s\-]+$', line) and len(line) <= 20 and line not in {'DESCRIPTION', 'INGREDIENTS'} and line != 'GOURMET RESTAURANT CATALOG':
                if 'category' not in current:
                    current['category'] = line

        for idx, block in enumerate(blocks):
            name = page_title_lines[idx] if idx < len(page_title_lines) else f'Imported Product {page_num}-{idx + 1}'
            results.append({
                'name': name,
                'sku': block.get('sku') or f'PDF-{page_num}-{idx + 1}',
                'category': block.get('category', 'General'),
                'price': round(block.get('price', 0), 2),
                'stock_status': block.get('stock_status', 'In Stock'),
                'stock_quantity': block.get('stock_quantity', 0),
                'description': 'Imported from PDF',
                'ingredients': None,
                'page_num': page_num,
            })

    return results


def extract_products(pdf_path: str, output_dir: str):
    reader = PdfReader(pdf_path)
    joined = '\n'.join((p.extract_text() or '') for p in reader.pages)

    if 'GOURMET RESTAURANT CATALOG' in joined:
        products = parse_gourmet(reader)
    else:
        products = []
        for page_num, page in enumerate(reader.pages, start=1):
            products.extend(parse_page_generic(norm_lines(page.extract_text() or ''), page_num))

    # keep only products with both a name and an SKU
    products = [p for p in products if p.get('sku') and p.get('name')]

    # assign images per page, in product order
    by_page = {}
    for p in products:
        by_page.setdefault(p['page_num'], []).append(p)
    for page_num, page_products in by_page.items():
        page = reader.pages[page_num - 1]
        base = page_products[0]['name'] if page_products else 'product'
        image_paths = extract_page_images(page, output_dir, base, page_num, len(page_products))
        for p, img in zip(page_products, image_paths):
            p['image_path'] = img

    for p in products:
        p.pop('page_num', None)
        p.setdefault('image_path', None)

    return products


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(json.dumps([]))
        sys.exit(0)

    pdf_path = sys.argv[1]
    output_dir = sys.argv[2]
    os.makedirs(output_dir, exist_ok=True)
    try:
        products = extract_products(pdf_path, output_dir)
    except Exception as exc:  # never crash silently — surface the reason on stderr
        print(f'PDF import error: {exc}', file=sys.stderr)
        products = []
    print(json.dumps(products))
