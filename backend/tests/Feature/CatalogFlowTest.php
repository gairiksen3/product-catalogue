<?php

namespace Tests\Feature;

use App\Models\Product;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class CatalogFlowTest extends TestCase
{
    use RefreshDatabase;

    public function test_user_can_register_with_valid_credentials(): void
    {
        $response = $this->postJson('/api/register', [
            'name' => 'Jane Doe',
            'email' => 'jane@example.com',
            'password' => '12345678',
            'password_confirmation' => '12345678',
        ]);

        $response->assertStatus(201)
            ->assertJsonPath('user.email', 'jane@example.com');

        $this->assertAuthenticated();
    }

    public function test_products_can_be_filtered_and_paginated(): void
    {
        $user = User::factory()->create();

        Product::create([
            'user_id' => $user->id,
            'name' => 'Tangy Salad',
            'sku' => 'SAL-1001',
            'category' => 'Salad',
            'price' => 12.50,
            'stock_status' => 'In Stock',
            'stock_quantity' => 10,
            'image_path' => 'products/demo.jpg',
        ]);

        Product::create([
            'user_id' => $user->id,
            'name' => 'Vegan Risotto',
            'sku' => 'VEG-2002',
            'category' => 'Appetizer',
            'price' => 25.00,
            'stock_status' => 'Out of Stock',
            'stock_quantity' => 0,
            'image_path' => 'products/demo.jpg',
        ]);

        $this->actingAs($user);

        $response = $this->getJson('/api/products?search=sal&category=Salad&stock_status=In%20Stock&sort=price_desc&page=1');

        $response->assertStatus(200)
            ->assertJsonPath('meta.per_page', 12)
            ->assertJsonCount(1, 'data');
    }
}
