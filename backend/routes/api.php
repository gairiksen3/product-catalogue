<?php

use App\Http\Controllers\AuthController;
use App\Http\Controllers\ProductController;
use Illuminate\Support\Facades\Route;

// These routes are automatically prefixed with /api (see bootstrap/app.php).
// Session/cookie middleware is added to the "api" group in bootstrap/app.php so
// the session-based SPA auth (web guard) keeps working here.
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
