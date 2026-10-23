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
