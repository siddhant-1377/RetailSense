export type TabKey = 'dashboard' | 'dataset' | 'preprocess' | 'analytics' | 'insights' | 'dwm';

export interface Profile {
  rows: number;
  columns: number;
  column_names: string[];
  numeric_columns: string[];
  categorical_columns: string[];
  date_columns: string[];
  missing_values: number;
  missing_by_column: Record<string, number>;
  duplicate_records: number;
  negative_quantities: number;
  negative_prices: number;
  invalid_dates: number;
  status: string;
  preview: Record<string, unknown>[];
}

export interface SummaryResponse {
  session_id: string;
  demo: boolean;
  metrics: {
    total_customers: number;
    total_transactions: number;
    total_revenue: number;
    avg_transaction_value: number;
    total_products: number;
    total_records: number;
  };
  charts: {
    monthly_sales?: { month: string; revenue: number }[];
    category_sales?: { category: string; revenue: number }[];
    top_products?: { product: string; revenue: number }[];
    customer_type?: { type: string; count: number }[];
    payment_method?: { method: string; count: number }[];
    city_sales?: { city: string; revenue: number }[];
  };
  profile: Profile;
}

export interface ClassificationModelResult {
  algorithm: string;
  label: string;
  target: string;
  features: string[];
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
  labels: string[];
  confusion_matrix: number[][];
  tree_rules?: string | null;
  test_samples: number;
}

export interface AssociationResult {
  transaction_count: number;
  rules: Rule[];
  rule_count: number;
  top_rules: Rule[];
  scatter: { support: number; confidence: number; lift: number; label: string }[];
  message: string;
}

export interface Rule {
  antecedent: string;
  consequent: string;
  support: number;
  confidence: number;
  lift: number;
}

export interface RegressionResult {
  target: string;
  features: string[];
  r2: number;
  mae: number;
  rmse: number;
  samples: { actual: number; predicted: number }[];
  coefficients: number[];
  test_samples: number;
}

export interface ClusterSummary {
  cluster: number;
  customers: number;
  description: string;
  [key: string]: string | number;
}

export interface ComparisonRow {
  algorithm: string;
  task: string;
  metric: string;
  value: number | null;
  score: number | null;
  runtime_ms: number;
  status: string;
  detail: string;
  rank_within_task?: number;
}

export interface ComparisonResponse {
  session_id: string;
  rows: ComparisonRow[];
  ready_count: number;
  algorithm_count: number;
  classification_winner: string | null;
  notes: string[];
  methodology: {
    classification: string;
    regression: string;
    clustering: string;
    association: string;
    cross_task: string;
  };
}

export interface ClusteringResult {
  features: string[];
  k: number;
  customer_count: number;
  silhouette_score: number;
  summary: ClusterSummary[];
  points: { x: number; y: number; cluster: number }[];
  axes: { x: string; y: string };
}
