/**
 * API client service for MPLAD-AI gateway communication.
 */

import { HealthCheckData } from '../types';

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface HealthCheckResult {
  isOnline: boolean;
  latencyMs: number;
  data: HealthCheckData | null;
  error?: string;
}

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
