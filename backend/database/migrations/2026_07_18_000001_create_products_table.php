<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('products', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('name');
            $table->string('sku');
            $table->string('category');
            $table->decimal('price', 10, 2);
            $table->string('stock_status');
            $table->integer('stock_quantity')->default(0);
            $table->text('description')->nullable();
            $table->text('ingredients')->nullable();
            $table->string('image_path')->nullable();
            $table->timestamps();

            // SKU is unique per user, not globally — two users may each import
            // a product with the same SKU without colliding.
            $table->unique(['user_id', 'sku']);

            // Indexes to speed up lookups/searches by name and SKU.
            $table->index('name');
            $table->index('sku');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('products');
    }
};
