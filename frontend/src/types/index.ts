/**
 * Core TypeScript definitions for MPLAD-AI Phase 1.
 * SIH 2026 | Problem Statement ID: 26102
 */

export type ProjectStatus =
  | 'PROPOSED'
  | 'SCRUTINIZED'
  | 'SANCTIONED'
  | 'WORK_ORDERED'
  | 'IN_PROGRESS'
  | 'COMPLETED'
  | 'REJECTED'
  | 'STALLED';

export type WorkCategory =
  | 'DRINKING_WATER'
  | 'EDUCATION'
  | 'PUBLIC_HEALTH'
  | 'SANITATION'
  | 'ROADS_BRIDGES'
  | 'IRRIGATION'
  | 'COMMUNITY_INFRASTRUCTURE'
  | 'OTHER';

export type PriorityQuota = 'GENERAL' | 'SC_MANDATE' | 'ST_MANDATE';

export interface ProjectItem {
  id: string;
  project_code: string;
  title: string;
  category: WorkCategory;
  priority_quota: PriorityQuota;
  estimated_cost: number;
  sanctioned_cost: number;
  actual_expenditure: number;
  status: ProjectStatus;
  progress_percentage: number;
  latitude: number;
  longitude: number;
  location_address: string;
  district_name: string;
  constituency_name: string;
  recommendation_date: string;
  target_completion_date: string;
  delay_risk_score: number; // 0 - 100
  is_anomaly: boolean;
  anomaly_type?: 'DELAY_RISK' | 'DUPLICATE_OVERLAP' | 'COST_OUTLIER' | 'NONE';
  duplicate_similarity?: number;
}

export interface KpiSummary {
  total_entitlement_cr: number;
  sanctioned_amount_cr: number;
  expenditure_amount_cr: number;
  unspent_balance_cr: number;
  total_works: number;
  completed_works: number;
  in_progress_works: number;
  sc_quota_pct: number;
  st_quota_pct: number;
  ai_flagged_count: number;
}

export interface HealthCheckData {
  status: string;
  app_name: string;
  version: string;
  environment: string;
  timestamp: string;
  database: {
    status: 'connected' | 'disconnected' | string;
    dialect?: string;
    driver?: string;
    target?: string;
    message?: string;
    error_detail?: string;
  };
  services: Record<string, string>;
  python_version: string;
}

export interface BackendExecutiveKpis {
  total_projects: number;
  proposed_count: number;
  sanctioned_count: number;
  in_progress_count: number;
  completed_count: number;
  stalled_count: number;
  total_estimated_cost: string | number;
  total_sanctioned_cost: string | number;
  total_actual_expenditure: string | number;
  fund_utilization_percentage: number;
  sc_quota_allocation_pct: number;
  st_quota_allocation_pct: number;
  sc_quota_mandate_met: boolean;
  st_quota_mandate_met: boolean;
  active_anomalies_count: number;
}

export interface SectorBreakdown {
  category: WorkCategory;
  project_count: number;
  sanctioned_amount: string | number;
  expenditure_amount: string | number;
}

export interface AgencyRanking {
  agency_code: string;
  agency_name: string;
  department: string;
  project_count: number;
  efficiency_rating: number;
  avg_delay_days: number;
}

export interface ProjectListResponse {
  total: number;
  page: number;
  limit: number;
  items: ProjectItem[];
}

export interface AuthUser {
  id: string;
  email: string;
  full_name: string;
  role: string;
  constituency_id?: string;
  district_id?: string;
  agency_id?: string;
  is_active: boolean;
  created_at: string;
}

export interface AuthTokenResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}
