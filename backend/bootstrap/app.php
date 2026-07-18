<?php

use Illuminate\Foundation\Application;
use Illuminate\Foundation\Configuration\Exceptions;
use Illuminate\Foundation\Configuration\Middleware;

return Application::configure(basePath: dirname(__DIR__))
    ->withRouting(
        web: __DIR__.'/../routes/web.php',
        commands: __DIR__.'/../routes/console.php',
        health: '/up',
    )
    ->withMiddleware(function (Middleware $middleware): void {
        // Session-based SPA auth: these JSON endpoints are consumed by the
        // React frontend (same-origin via the Vite dev proxy) and are exempt
        // from CSRF token verification.
        $middleware->validateCsrfTokens(except: [
            'api/register',
            'api/login',
            'api/logout',
            'api/products',
            'api/products/*',
        ]);
    })
    ->withExceptions(function (Exceptions $exceptions): void {
        //
    })->create();
