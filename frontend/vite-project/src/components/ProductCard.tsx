import type { Product } from '../types';

const currency = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
});

export default function ProductCard({ product }: { product: Product }) {
  const inStock = product.stock_status.toLowerCase().includes('in stock');
  const price = Number(product.price);

  return (
    <article className="card">
      <div className="card-media">
        {product.image_url ? (
          <img src={product.image_url} alt={product.name} loading="lazy" />
        ) : (
          <div className="card-media-placeholder">
            <svg
              className="card-media-placeholder-icon"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
              <circle cx="8.5" cy="8.5" r="1.5" />
              <path d="M21 15l-5-5L5 21" />
            </svg>
            <span>No image</span>
          </div>
        )}
        <span className={`badge ${inStock ? 'badge-in' : 'badge-out'}`}>
          {product.stock_status}
        </span>
      </div>

      <div className="card-body">
        <span className="card-category">{product.category}</span>
        <h3 className="card-title">{product.name}</h3>
        <p className="card-sku">SKU: {product.sku}</p>
        {product.description && (
          <p className="card-description">{product.description}</p>
        )}
        <div className="card-footer">
          <span className="card-price">
            {Number.isFinite(price) ? currency.format(price) : product.price}
          </span>
          <span className="card-qty">{product.stock_quantity} in stock</span>
        </div>
      </div>
    </article>
  );
}
