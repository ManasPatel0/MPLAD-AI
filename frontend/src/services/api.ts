/**
 * API client service for MPLAD-AI gateway communication.
 * SIH 2026 | Problem Statement ID: 26102
 */

import {
  AgencyRanking,
  AuthTokenResponse,
  AuthUser,
  BackendExecutiveKpis,
  HealthCheckData,
  ProjectItem,
  ProjectListResponse,
  SectorBreakdown,
} from '../types';

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface HealthCheckResult {
  isOnline: boolean;
  latencyMs: number;
  data: HealthCheckData | null;
  error?: string;
}

/**
 * Perform non-blocking health check probe against the backend gateway.
 */
export async function fetchHealthCheck(): Promise<HealthCheckResult> {
  const startTime = performance.now();
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 4000);

    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    const latencyMs = Math.round(performance.now() - startTime);

    if (!response.ok) {
      return {
        isOnline: false,
        latencyMs,
        data: null,
        error: `HTTP ${response.status}: ${response.statusText}`,
      };
    }

    const data: HealthCheckData = await response.json();
    return {
      isOnline: true,
      latencyMs,
      data,
    };
  } catch (err: unknown) {
    const latencyMs = Math.round(performance.now() - startTime);
    const errorMessage =
      err instanceof Error ? err.message : 'Connection failed or timed out';
    return {
      isOnline: false,
      latencyMs,
      data: null,
      error: errorMessage,
    };
  }
}

/**
 * Fetch paginated developmental projects with optional multi-parametric filters.
 */
export async function fetchProjects(params?: {
  status?: string;
  category?: string;
  priority_quota?: string;
  is_anomaly?: boolean;
  page?: number;
  limit?: number;
}): Promise<ProjectListResponse | null> {
  try {
    const query = new URLSearchParams();
    if (params?.status) query.append('status', params.status);
    if (params?.category) query.append('category', params.category);
    if (params?.priority_quota) query.append('priority_quota', params.priority_quota);
    if (params?.is_anomaly !== undefined) query.append('is_anomaly', String(params.is_anomaly));
    if (params?.page) query.append('page', String(params.page));
    if (params?.limit) query.append('limit', String(params.limit));

    const res = await fetch(`${API_BASE_URL}/projects?${query.toString()}`);
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

/**
 * Fetch Executive Dashboard aggregate KPIs.
 */
export async function fetchExecutiveKpis(): Promise<BackendExecutiveKpis | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/analytics/kpis`);
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

/**
 * Fetch project count and expenditures broken down by developmental sector.
 */
export async function fetchSectorBreakdown(): Promise<SectorBreakdown[] | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/analytics/sectors`);
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

/**
 * Fetch implementing agency efficiency and delay rankings.
 */
export async function fetchAgencyRankings(): Promise<AgencyRanking[] | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/analytics/agencies`);
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

/**
 * Seed realistic sample projects into the active PostgreSQL/Neon database.
 */
export async function seedSampleProjects(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE_URL}/ingest/seed-sample`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    return res.ok;
  } catch {
    return false;
  }
}

/**
 * Authenticate user credentials and receive JWT Bearer token.
 */
export async function loginUser(
  email: string,
  password: string
): Promise<AuthTokenResponse | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

/**
 * Recommend new developmental work proposal (requires MP / Collector auth token).
 */
export async function recommendProject(
  payload: Record<string, unknown>,
  token: string
): Promise<ProjectItem | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/projects`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

/**
 * Transition project status (Sanction, Work Order, Completion).
 */
export async function updateProjectStatus(
  projectId: string,
  statusPayload: {
    to_status: string;
    sanctioned_cost?: number;
    agency_id?: string;
    remarks?: string;
  },
  token: string
): Promise<ProjectItem | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/projects/${projectId}/status`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(statusPayload),
    });
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}
