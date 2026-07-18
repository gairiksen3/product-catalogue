<?php

namespace Database\Seeders;

use App\Models\User;
use App\Services\ProductImporter;
use Illuminate\Database\Seeder;

class ProductSeeder extends Seeder
{
    public function run(): void
    {
        // Attach the seeded catalogue to the default user created in DatabaseSeeder.
        $user = User::query()->firstWhere('email', 'someone@example.com');

        if (!$user) {
            $this->command->warn('Default user not found — skipping product seed.');
            return;
        }

        // Seed the catalogue from the bundled sample PDF using the same importer
        // the /api/products/import endpoint uses. Override the path with the
        // SEED_PRODUCT_PDF env var if needed.
        $pdfPath = env('SEED_PRODUCT_PDF', base_path('../sample_pdf/product_catalog_v2.pdf'));

        if (!is_file($pdfPath)) {
            $this->command->warn("Sample PDF not found at {$pdfPath} — skipping product seed.");
            return;
        }

        $products = app(ProductImporter::class)->importFromPdf($pdfPath, $user->id);

        $this->command->info('Seeded ' . count($products) . ' products from the sample catalogue.');
    }
}
