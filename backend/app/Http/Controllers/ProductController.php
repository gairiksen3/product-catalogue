<?php

namespace App\Http\Controllers;

use App\Models\Product;
use App\Services\ProductImporter;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Symfony\Component\HttpFoundation\Response;

class ProductController extends Controller
{
    public function index(Request $request)
    {
        // Only ever return the authenticated user's own products.
        $query = Product::query()->where('user_id', $request->user()->id);

        if ($request->filled('search')) {
            $search = trim($request->string('search'));
            $query->where(function ($q) use ($search) {
                $q->where('name', 'like', "%{$search}%")
                    ->orWhere('sku', 'like', "%{$search}%")
                    ->orWhere('category', 'like', "%{$search}%");
            });
        }

        if ($request->filled('category')) {
            $query->where('category', $request->input('category'));
        }

        if ($request->filled('stock_status')) {
            $query->where('stock_status', $request->input('stock_status'));
        }

        $sort = $request->input('sort', 'default');
        if ($sort === 'price_asc') {
            $query->orderBy('price', 'asc');
        } elseif ($sort === 'price_desc') {
            $query->orderBy('price', 'desc');
        } else {
            $query->orderBy('id', 'desc');
        }

        $perPage = min((int) $request->input('per_page', 12), 50);

        $products = $query->paginate($perPage)->appends($request->query());

        return response()->json([
            'data' => $products->items(),
            'meta' => [
                'current_page' => $products->currentPage(),
                'per_page' => $products->perPage(),
                'total' => $products->total(),
                'last_page' => $products->lastPage(),
            ],
        ]);
    }

    public function store(Request $request, ProductImporter $importer): Response
    {
        $validated = $request->validate([
            'file' => ['required', 'file', 'mimes:pdf'],
        ]);

        $storedPath = $validated['file']->storeAs('imports', $validated['file']->getClientOriginalName(), 'local');
        // Resolve the absolute path via the disk itself — the "local" disk root
        // is storage/app/private in Laravel 11+, so hardcoding storage/app/ breaks.
        $importedProducts = $importer->importFromPdf(
            Storage::disk('local')->path($storedPath),
            $request->user()->id,
        );

        $count = count($importedProducts);

        return response()->json([
            'message' => $count > 0
                ? 'Imported successfully.'
                : 'No products could be recognised in this PDF. Please check that it is a product catalogue.',
            'count' => $count,
            'products' => $importedProducts,
        ], $count > 0 ? 201 : 200);
    }

    public function categories(Request $request): Response
    {
        $categories = Product::query()
            ->where('user_id', $request->user()->id)
            ->selectRaw('category, COUNT(*) as count')
            ->groupBy('category')
            ->orderBy('category')
            ->get();

        return response()->json(['data' => $categories]);
    }

    public function destroyAll(Request $request): Response
    {
        // Remove only this user's products. Image files are left on disk because
        // imports of the same PDF can share filenames across users.
        $deleted = Product::query()
            ->where('user_id', $request->user()->id)
            ->delete();

        return response()->json([
            'message' => 'Catalogue cleared.',
            'deleted' => $deleted,
        ]);
    }
}
