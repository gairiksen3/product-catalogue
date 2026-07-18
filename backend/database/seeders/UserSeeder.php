<?php

namespace Database\Seeders;

use App\Models\User;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class UserSeeder extends Seeder
{
    public function run(): void
    {
        User::updateOrCreate(
            ['email' => 'someone@example.com'],
            [
                'name' => 'Default User',
                'password' => Hash::make('12345678'),
            ]
        );
    }
}
