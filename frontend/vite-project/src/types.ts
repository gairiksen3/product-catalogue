export interface User {
  id: number;
  name: string;
  email: string;
}

export interface Product {
  id: number;
  name: string;
  sku: string;
  category: string;
  price: string;
  stock_status: string;
  stock_quantity: number;
  description: string | null;
  ingredients: string | null;
  image_path: string | null;
  image_url: string | null;
}

export interface PaginationMeta {
  current_page: number;
  per_page: number;
  total: number;
  last_page: number;
}

export interface ProductsResponse {
  data: Product[];
  meta: PaginationMeta;
}

export interface CategoryCount {
  category: string;
  count: number;
}

export interface ProductQuery {
  search?: string;
  category?: string;
  stock_status?: string;
  sort?: string;
  page?: number;
  per_page?: number;
}
