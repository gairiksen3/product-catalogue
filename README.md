# Product Catalogue

A full-stack product catalogue application with session-based authentication and a
PDF import pipeline. Users register/log in, upload a product catalogue PDF, and the
app extracts the products (name, SKU, category, price, stock, description,
ingredients, image) and shows them in a searchable/filterable React catalogue.

- **Backend** — Laravel 12 REST API (PHP), MySQL, session-cookie auth.
- **Frontend** — React 18 + TypeScript SPA built with Vite.
- **PDF import** — a Python script (`pypdf` + `pillow`) invoked by the backend to
  parse the uploaded PDF and extract product data and images.

---

## Architecture

```
product-catalogue/
├── backend/                     # Laravel 12 API
│   ├── app/
│   │   ├── Http/Controllers/    # AuthController, ProductController
│   │   ├── Models/              # Product, User
│   │   └── Services/            # ProductImporter (calls the Python script)
│   ├── database/migrations/     # users, cache, jobs, products
│   ├── routes/web.php           # /api/* routes (session/cookie auth)
│   ├── scripts/
│   │   └── import_products_from_pdf.py   # PDF -> JSON parser
│   ├── composer.json            # PHP dependencies
│   └── .env                     # backend configuration
├── frontend/
│   └── vite-project/            # React + TypeScript SPA  ← the actual UI
│       ├── src/                 # pages, components, api client
│       ├── package.json         # JS dependencies
│       └── vite.config.ts       # dev server + /api & /storage proxy
├── .venv/                       # Python virtual environment (PDF import deps)
├── sample_pdf/                  # sample catalogue PDF for testing imports
└── inspect_*.py                 # helper scripts for inspecting PDFs
```

> **Note:** The real UI lives in `frontend/vite-project/`. The `backend/` folder
> also contains a Vite/Tailwind setup from the default Laravel skeleton, but it is
> **not** used for the SPA — you do not need to run it.

---

## Prerequisites (required software & versions)

Install these on your local machine before setting up the project.

| Tool          | Required version                    | Verified/used here | Notes |
|---------------|-------------------------------------|--------------------|-------|
| **PHP**       | `^8.2` (8.2, 8.3, or 8.4)           | 8.2.12             | Bundled with XAMPP. Laravel 12 requires PHP 8.2+. |
| **Composer**  | 2.x                                 | 2.8.10             | PHP dependency manager. |
| **Laravel**   | 12.x                                | 12.x               | Installed via Composer, not separately. |
| **MySQL / MariaDB** | 5.7+/10.4+ (any XAMPP version) | XAMPP MySQL        | Database `product_catalogue` must be created. |
| **Node.js**   | `^20.19` or `>=22.12`               | v23.6.0            | Required by Vite 7. Node 20 LTS or 22+ recommended. |
| **npm**       | 10+ (ships with Node)               | 11.0.0             | JS package manager. |
| **Python**    | 3.9+ (3.11+ recommended)            | 3.14.5             | Used only for the PDF import script. |

### Required PHP extensions

These ship with XAMPP by default, but confirm they are enabled in `php.ini`:

- `pdo_mysql` (database)
- `mbstring`
- `openssl`
- `fileinfo`
- `ctype`, `json`, `tokenizer`, `xml`, `curl`

### Required Python packages

Installed into the `.venv` virtual environment (see setup below):

- `pypdf` (PDF text/image extraction)
- `pillow` (image handling)

---

## Setup (step by step)

Run everything from the project root: `d:\xampp\htdocs\product-catalogue`
(adjust the path if you cloned it elsewhere).

### 1. Start XAMPP & create the database

1. Open the **XAMPP Control Panel** and start **Apache** and **MySQL**.
2. Open phpMyAdmin (`http://localhost/phpmyadmin`) and create a new database named:
   ```
   product_catalogue
   ```
   (utf8mb4 / utf8mb4_unicode_ci). Credentials used by the app: user `root`, empty
   password — the XAMPP default. Change these in `backend/.env` if yours differ.

### 2. Backend (Laravel API)

```powershell
cd d:\xampp\htdocs\product-catalogue\backend

# Install PHP dependencies
composer install

# Create your .env if it does not exist (one is already present in this repo)
copy .env.example .env

# Generate the application key
php artisan key:generate

# Run database migrations (creates users, cache, jobs, products tables)
php artisan migrate

# Create the storage symlink so uploaded/extracted product images
# are served from /storage
php artisan storage:link
```

**Important — configure the PDF import Python path.** The backend shells out to the
Python interpreter in `.venv`. Add this line to `backend/.env` and point it at the
`.venv` created in step 3 (use forward slashes):

```env
PDF_IMPORT_PYTHON=d:/xampp/htdocs/product-catalogue/.venv/Scripts/python.exe
```

> Without this, the import uses a hardcoded default path that may not match your
> machine and the PDF import will silently return no products.

**Database config in `backend/.env`** (already set for MySQL):

```env
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=product_catalogue
DB_USERNAME=root
DB_PASSWORD=
```

### 3. Python environment (PDF import)

A `.venv` already exists in the repo, but if you need to (re)create it:

```powershell
cd d:\xampp\htdocs\product-catalogue

# Create the virtual environment
python -m venv .venv

# Install the required packages
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Verify it works:

```powershell
.venv\Scripts\python.exe backend\scripts\import_products_from_pdf.py sample_pdf\product_catalog_v2.pdf backend\storage\app\public\products
```

This should print JSON of the extracted products.

### 4. Frontend (React SPA)

```powershell
cd d:\xampp\htdocs\product-catalogue\frontend\vite-project

# Install JS dependencies
npm install
```

The Vite dev server proxies `/api` and `/storage` to the Laravel backend at
`http://127.0.0.1:8000`, so both must be running for the app to work.

---

## Running the project locally

You need **two** terminals running simultaneously.

### Terminal 1 — Backend API (port 8000)

```powershell
cd d:\xampp\htdocs\product-catalogue\backend
php artisan serve
```

Serves the API at **http://127.0.0.1:8000**.

### Terminal 2 — Frontend SPA (port 5173)

```powershell
cd d:\xampp\htdocs\product-catalogue\frontend\vite-project
npm run dev
```

Serves the UI at **http://localhost:5173** — open this in your browser.

> MySQL must be running (XAMPP) for auth and product data. The frontend calls the
> backend through the Vite proxy, so always open the app via the **5173** URL, not 8000.

### Optional — one-command backend dev stack

The backend also defines a combined dev script (server + queue + logs + the
backend's own vite). This is **not** required for the React SPA:

```powershell
cd d:\xampp\htdocs\product-catalogue\backend
composer run dev
```

---

## Using the app

1. Open **http://localhost:5173**.
2. **Register** a new account, then log in.
3. On the catalogue page, click **Import** and upload a PDF (only `.pdf` is
   accepted). Use `sample_pdf/product_catalog_v2.pdf` to try it out.
4. The backend saves the PDF, runs the Python parser, stores the extracted
   products (scoped to your user) and their images, and the catalogue refreshes.
5. Search, filter by category, and browse. Use **Clear** to remove all of your
   imported products.

Products are scoped per user, and a SKU is unique per user (two users can each
import the same SKU without colliding).

---

## API reference

All routes are under `/api` and use session-cookie auth (Laravel `web` middleware).

| Method | Endpoint                   | Auth | Description |
|--------|----------------------------|------|-------------|
| POST   | `/api/register`            | No   | Create an account. |
| POST   | `/api/login`               | No   | Log in (sets session cookie). |
| POST   | `/api/logout`              | Yes  | Log out. |
| GET    | `/api/me`                  | Yes  | Current authenticated user. |
| GET    | `/api/products`            | Yes  | List products (supports search/filter query params). |
| GET    | `/api/products/categories` | Yes  | Category list with counts. |
| POST   | `/api/products/import`     | Yes  | Upload a PDF (`file`) to import products. |
| DELETE | `/api/products`            | Yes  | Delete all of the current user's products. |

---

## Testing

```powershell
cd d:\xampp\htdocs\product-catalogue\backend
php artisan test
# or
composer test
```

---

## Troubleshooting

- **PDF import returns 0 products** — Ensure `PDF_IMPORT_PYTHON` in `backend/.env`
  points at the correct `.venv\Scripts\python.exe`, and that `pypdf` and `pillow`
  are installed in that venv.
- **Product images don't load (404 on /storage/...)** — Run
  `php artisan storage:link` in `backend/`.
- **Login/session fails or CORS-like errors** — Access the app via
  `http://localhost:5173` (the Vite proxy), not the backend port directly.
- **Database connection refused** — Start MySQL in XAMPP and confirm the
  `product_catalogue` database exists and the credentials in `.env` match.
- **`npm run dev` fails on Node version** — Vite 7 needs Node `^20.19` or
  `>=22.12`. Upgrade Node if you're on an older version.
- **`vite` / build errors after pulling** — Re-run `npm install` in
  `frontend/vite-project`.

---

## Tech stack summary

| Layer     | Technology |
|-----------|------------|
| Backend   | Laravel 12, PHP 8.2+ |
| Database  | MySQL (via XAMPP) |
| Auth      | Session-cookie based (Laravel `web` middleware) |
| Frontend  | React 18, TypeScript 5.6, React Router 6, Vite 7 |
| PDF import| Python 3.9+ (`pypdf`, `pillow`) |
| Tooling   | Composer 2, npm 10+ |
