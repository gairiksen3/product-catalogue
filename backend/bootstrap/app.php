<?php

use Illuminate\Foundation\Application;
use Illuminate\Foundation\Configuration\Exceptions;
use Illuminate\Foundation\Configuration\Middleware;

return Application::configure(basePath: dirname(__DIR__))
    ->withRouting(
        web: __DIR__.'/../routes/web.php',
        api: __DIR__.'/../routes/api.php',
        commands: __DIR__.'/../routes/console.php',
        health: '/up',
    )
    ->withMiddleware(function (Middleware $middleware): void {
        // The API routes use the session-based "web" guard for auth (the React
        // frontend is same-origin via the Vite dev proxy). The stateless "api"
        // group has no session/cookie middleware by default, so add it here.
        $middleware->api(prepend: [
            \Illuminate\Cookie\Middleware\EncryptCookies::class,
            \Illuminate\Cookie\Middleware\AddQueuedCookiesToResponse::class,
            \Illuminate\Session\Middleware\StartSession::class,
        ]);

        // The api group does not run CSRF verification, so these JSON endpoints
        // remain exempt without needing an explicit token — no config required.
    })
    ->withExceptions(function (Exceptions $exceptions): void {
        //
    })->create();
