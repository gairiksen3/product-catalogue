import type {
  CategoryCount,
  Product,
  ProductQuery,
  ProductsResponse,
  User,
} from './types';

export class ApiError extends Error {
  status: number;
  errors?: Record<string, string[]>;

  constructor(message: string, status: number, errors?: Record<string, string[]>) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.errors = errors;
  }
}

const BASE_URL = '/api';

interface RequestOptions {
  method?: string;
  body?: unknown;
  isFormData?: boolean;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, isFormData = false } = options;
  const url = `${BASE_URL}${path}`;

  const headers: Record<string, string> = { Accept: 'application/json' };
  let payload: BodyInit | undefined;

  if (body !== undefined) {
    if (isFormData) {
      payload = body as FormData;
    } else {
      headers['Content-Type'] = 'application/json';
      payload = JSON.stringify(body);
    }
  }

  const response = await fetch(url, {
    method,
    headers,
    body: payload,
    credentials: 'same-origin',
    cache: 'no-store',
  });

  if (response.status === 204) {
    return undefined as T;
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new ApiError(
      (data as { message?: string }).message || 'Request failed.',
      response.status,
      (data as { errors?: Record<string, string[]> }).errors,
    );
  }

  return data as T;
}

export const api = {
  register(input: {
    name: string;
    email: string;
    password: string;
    password_confirmation: string;
  }) {
    return request<{ message: string; user: User }>('/register', {
      method: 'POST',
      body: input,
    });
  },

  login(input: { email: string; password: string }) {
    return request<{ message: string; user: User }>('/login', {
      method: 'POST',
      body: input,
    });
  },

  logout() {
    return request<{ message: string }>('/logout', { method: 'POST' });
  },

  me() {
    return request<{ user: User }>('/me');
  },

  products(query: ProductQuery = {}) {
    const params = new URLSearchParams();
    Object.entries(query).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, String(value));
      }
    });
    const qs = params.toString();
    return request<ProductsResponse>(`/products${qs ? `?${qs}` : ''}`);
  },

  importProducts(file: File) {
    const form = new FormData();
    form.append('file', file);
    return request<{ message: string; count: number; products: Product[] }>(
      '/products/import',
      { method: 'POST', body: form, isFormData: true },
    );
  },

  categories() {
    return request<{ data: CategoryCount[] }>('/products/categories');
  },

  clearProducts() {
    return request<{ message: string; deleted: number }>('/products', {
      method: 'DELETE',
    });
  },
};
