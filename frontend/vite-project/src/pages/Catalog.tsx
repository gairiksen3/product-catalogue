import { useCallback, useEffect, useRef, useState } from 'react';
import { api, ApiError } from '../api';
import { useAuth } from '../auth-context';
import type { CategoryCount, PaginationMeta, Product } from '../types';
import ProductCard from '../components/ProductCard';
import ImportModal from '../components/ImportModal';

const SORT_OPTIONS = [
  { value: 'default', label: 'Newest' },
  { value: 'price_asc', label: 'Price: Low to High' },
  { value: 'price_desc', label: 'Price: High to Low' },
];

const STOCK_OPTIONS = [
  { value: '', label: 'All stock' },
  { value: 'In Stock', label: 'In Stock' },
  { value: 'Out of Stock', label: 'Out of Stock' },
];

export default function Catalog() {
  const { user, logout } = useAuth();

  const [products, setProducts] = useState<Product[]>([]);
  const [meta, setMeta] = useState<PaginationMeta | null>(null);
  const [categories, setCategories] = useState<CategoryCount[]>([]);

  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [category, setCategory] = useState('');
  const [stockStatus, setStockStatus] = useState('');
  const [sort, setSort] = useState('default');
  const [page, setPage] = useState(1);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showImport, setShowImport] = useState(false);
  const [clearing, setClearing] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  const hasFilters = Boolean(debouncedSearch || category || stockStatus);
  // Whether the user owns any products at all (categories are never filtered),
  // used only to decide if the "Clear catalogue" button should appear.
  const hasAnyProducts = categories.length > 0;

  // Debounce the search box.
  useEffect(() => {
    const id = setTimeout(() => setDebouncedSearch(search), 350);
    return () => clearTimeout(id);
  }, [search]);

  // Reset to page 1 whenever a filter changes.
  useEffect(() => {
    setPage(1);
  }, [debouncedSearch, category, stockStatus, sort]);

  const loadCategories = useCallback(async () => {
    try {
      const res = await api.categories();
      setCategories(res.data);
    } catch {
      // Non-fatal — the filter just stays empty.
    }
  }, []);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.products({
        search: debouncedSearch,
        category,
        stock_status: stockStatus,
        sort,
        page,
        per_page: 12,
      });
      setProducts(res.data);
      setMeta(res.meta);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to load products.');
    } finally {
      setLoading(false);
    }
  }, [debouncedSearch, category, stockStatus, sort, page]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    loadCategories();
  }, [loadCategories]);

  const toastTimer = useRef<number | undefined>(undefined);
  const flashToast = (message: string) => {
    setToast(message);
    window.clearTimeout(toastTimer.current);
    toastTimer.current = window.setTimeout(() => setToast(null), 3500);
  };

  const refresh = async () => {
    await Promise.all([load(), loadCategories()]);
  };

  const handleImported = async (count: number) => {
    setShowImport(false);
    flashToast(`Imported ${count} product${count === 1 ? '' : 's'}.`);
    await refresh();
  };

  const handleClear = async () => {
    if (
      !window.confirm(
        'Clear your entire catalogue? This permanently deletes all of your products.',
      )
    ) {
      return;
    }
    setClearing(true);
    setError(null);
    try {
      const res = await api.clearProducts();
      // Reset filters so we don't sit on a now-empty page.
      setSearch('');
      setCategory('');
      setStockStatus('');
      setPage(1);
      flashToast(`Cleared ${res.deleted} product${res.deleted === 1 ? '' : 's'}.`);
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to clear catalogue.');
    } finally {
      setClearing(false);
    }
  };

  return (
    <div className="app">
      <header className="navbar">
        <div className="navbar-brand">🛒 Product Catalogue</div>
        <div className="navbar-right">
          <span className="navbar-user">Hi, {user?.name}</span>
          <button className="btn btn-primary" onClick={() => setShowImport(true)}>
            Import PDF
          </button>
          {hasAnyProducts && (
            <button
              className="btn btn-danger"
              onClick={handleClear}
              disabled={clearing}
            >
              {clearing ? 'Clearing…' : 'Clear catalogue'}
            </button>
          )}
          <button className="btn btn-ghost" onClick={logout}>
            Sign out
          </button>
        </div>
      </header>

      <main className="content">
        <div className="content-head">
          <h1 className="page-title">Your products</h1>
          {meta && (
            <span className="count-pill">
              {meta.total} {meta.total === 1 ? 'product' : 'products'}
            </span>
          )}
        </div>

        <section className="toolbar">
          <input
            className="search"
            type="search"
            placeholder="Search by name, SKU or category…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <select value={category} onChange={(e) => setCategory(e.target.value)}>
            <option value="">All categories</option>
            {categories.map((c) => (
              <option key={c.category} value={c.category}>
                {c.category} ({c.count})
              </option>
            ))}
          </select>
          <select value={stockStatus} onChange={(e) => setStockStatus(e.target.value)}>
            {STOCK_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
          <select value={sort} onChange={(e) => setSort(e.target.value)}>
            {SORT_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </section>

        {error && <div className="alert alert-error">{error}</div>}

        {loading ? (
          <div className="state">Loading products…</div>
        ) : products.length > 0 ? (
          <>
            <div className="grid">
              {products.map((p) => (
                <ProductCard key={p.id} product={p} />
              ))}
            </div>

            {meta && meta.last_page > 1 && (
              <nav className="pagination">
                <button
                  className="btn btn-ghost"
                  disabled={meta.current_page <= 1}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                >
                  Previous
                </button>
                <span className="pagination-info">
                  Page {meta.current_page} of {meta.last_page} · {meta.total} items
                </span>
                <button
                  className="btn btn-ghost"
                  disabled={meta.current_page >= meta.last_page}
                  onClick={() => setPage((p) => Math.min(meta.last_page, p + 1))}
                >
                  Next
                </button>
              </nav>
            )}
          </>
        ) : hasFilters ? (
          <div className="state">
            No products match your filters. Try adjusting your search or filters.
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-emoji">📦</div>
            <h2>Your catalogue is empty</h2>
            <p>Import a catalogue PDF to add your products.</p>
            <button className="btn btn-primary" onClick={() => setShowImport(true)}>
              Import PDF
            </button>
          </div>
        )}
      </main>

      {showImport && (
        <ImportModal
          onClose={() => setShowImport(false)}
          onImported={handleImported}
        />
      )}

      {toast && <div className="toast">{toast}</div>}
    </div>
  );
}
