<?php

use App\Http\Controllers\AuthController;
use App\Http\Controllers\ProductController;
use Illuminate\Support\Facades\Route;

// API routes live in web.php (not api.php) so they get the "web" middleware
// group — cookie/session support is required for session-based SPA auth.
// They are prefixed with /api to avoid colliding with the React client routes.
Route::prefix('api')->group(function () {
    Route::post('/register', [AuthController::class, 'register']);
    Route::post('/login', [AuthController::class, 'login']);
    Route::post('/logout', [AuthController::class, 'logout'])->middleware('auth');
    Route::get('/me', [AuthController::class, 'me'])->middleware('auth');

    Route::middleware('auth')->group(function () {
        Route::get('/products', [ProductController::class, 'index']);
        Route::get('/products/categories', [ProductController::class, 'categories']);
        Route::post('/products/import', [ProductController::class, 'store']);
        Route::delete('/products', [ProductController::class, 'destroyAll']);
    });
});

Route::get('/', function () {
    return response()->json(['message' => 'Catalog API ready.']);
});
