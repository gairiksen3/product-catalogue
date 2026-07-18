<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Product extends Model
{
    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    protected $fillable = [
        'user_id',
        'name',
        'sku',
        'category',
        'price',
        'stock_status',
        'stock_quantity',
        'description',
        'ingredients',
        'image_path',
    ];

    protected $casts = [
        'price' => 'decimal:2',
        'stock_quantity' => 'integer',
    ];

    protected $appends = ['image_url'];

    public function getImageUrlAttribute(): ?string
    {
        // Root-relative URL so it resolves through the Vite dev proxy in
        // development and against the same origin in production.
        return $this->image_path ? '/storage/' . ltrim($this->image_path, '/') : null;
    }
}
