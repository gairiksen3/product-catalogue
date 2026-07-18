<?php

namespace Database\Seeders;

use App\Models\User;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class DatabaseSeeder extends Seeder
{
    use WithoutModelEvents;

    public function run(): void
    {
        User::updateOrCreate(
            ['email' => 'someone@example.com'],
            [
                'name' => 'Default User',
                'password' => Hash::make('12345678'),
            ]
        );

        $this->call(ProductSeeder::class);
    }
}
