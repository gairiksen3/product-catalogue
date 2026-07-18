<?php

namespace App\Services;

use App\Models\Product;
use Illuminate\Support\Facades\Storage;

class ProductImporter
{
    /**
     * Parse a catalogue PDF and upsert the products it contains for a given user.
     * Duplicate detection is scoped to that user (by user_id + sku).
     *
     * @return Product[]
     */
    public function importFromPdf(string $pdfPath, int $userId): array
    {
        $python = env('PDF_IMPORT_PYTHON', 'd:/xampp/htdocs/product_catalogue/.venv/Scripts/python.exe');
        $script = base_path('scripts/import_products_from_pdf.py');
        $outputDir = Storage::disk('public')->path('products');

        if (!is_dir($outputDir)) {
            Storage::disk('public')->makeDirectory('products');
        }

        $command = sprintf(
            '%s %s %s %s',
            escapeshellarg($python),
            escapeshellarg($script),
            escapeshellarg($pdfPath),
            escapeshellarg($outputDir),
        );

        $output = shell_exec($command);
        $entries = json_decode((string) $output, true) ?: [];

        $products = [];
        foreach ($entries as $entry) {
            if (empty($entry['sku']) || empty($entry['name'])) {
                continue;
            }

            // Python writes every image into the products/ directory and returns
            // an absolute path (with OS-specific separators). Store only the disk
            // -relative path so Storage::url() builds a correct /storage/... URL.
            $imagePath = null;
            if (!empty($entry['image_path'])) {
                $imagePath = 'products/' . basename(str_replace('\\', '/', $entry['image_path']));
            }

            $products[] = Product::updateOrCreate(
                ['user_id' => $userId, 'sku' => $entry['sku']],
                [
                    'name' => $entry['name'],
                    'category' => $entry['category'] ?? 'General',
                    'price' => (float) ($entry['price'] ?? 0),
                    'stock_status' => $entry['stock_status'] ?? 'In Stock',
                    'stock_quantity' => (int) ($entry['stock_quantity'] ?? 0),
                    'description' => $entry['description'] ?? 'Imported from PDF',
                    'ingredients' => $entry['ingredients'] ?? null,
                    'image_path' => $imagePath,
                ]
            );
        }

        return $products;
    }
}
