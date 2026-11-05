import React from 'react';
import {
  X,
  Activity,
  Server,
  Database,
  Terminal,
  RotateCw,
  CheckCircle2,
  AlertTriangle,
} from 'lucide-react';
import { HealthCheckResult } from '../services/api';

interface ApiStatusModalProps {
  isOpen: boolean;
  onClose: () => void;
  health: HealthCheckResult | null;
  isLoading: boolean;
  onRefresh: () => void;
}

export const ApiStatusModal: React.FC<ApiStatusModalProps> = ({
  isOpen,
  onClose,
  health,
  isLoading,
  onRefresh,
}) => {
  if (!isOpen) return null;

  const isOnline = health?.isOnline ?? false;
  const data = health?.data;
  const db = data?.database;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4 animate-in fade-in duration-150">
      <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl max-w-lg w-full overflow-hidden">
        {/* Modal Header */}
        <div className="bg-slate-900 text-white px-5 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <Activity className="w-5 h-5 text-blue-400" />
            <div>
              <h3 className="font-bold text-sm text-white">
                FastAPI Gateway & Database Diagnostics
              </h3>
              <p className="text-[11px] text-slate-400">
                Phase 1 Full-Stack Health & Connectivity Check
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Content */}
        <div className="p-5 space-y-4 text-xs">
          {/* Main Status Pill */}
          <div
            className={`p-4 rounded-xl border flex items-center justify-between ${
              isOnline
                ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
                : 'bg-amber-50 border-amber-200 text-amber-900'
            }`}
          >
            <div className="flex items-center gap-3">
              {isOnline ? (
                <CheckCircle2 className="w-6 h-6 text-emerald-600 shrink-0" />
              ) : (
                <AlertTriangle className="w-6 h-6 text-amber-600 shrink-0" />
              )}
              <div>
                <p className="font-bold text-sm">
                  {isOnline
                    ? 'FastAPI Backend Online & Responding'
                    : 'Backend Gateway Offline / Standby'}
                </p>
                <p className="text-xs opacity-90 mt-0.5">
                  {isOnline
                    ? `GET /api/v1/health responded in ${health?.latencyMs}ms.`
                    : 'Frontend is running in Phase 1 standalone mock mode.'}
                </p>
              </div>
            </div>
            <button
              onClick={onRefresh}
              disabled={isLoading}
              className="px-3 py-1.5 rounded-lg bg-white border border-slate-200 shadow-2xs font-semibold text-slate-700 hover:bg-slate-50 flex items-center gap-1.5 shrink-0"
            >
              <RotateCw
                className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-blue-600' : ''}`}
              />
              Re-check
            </button>
          </div>

          {/* Diagnostic Details Grid */}
          <div className="grid grid-cols-2 gap-3">
            {/* FastAPI Service */}
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
              <div className="flex items-center gap-2 text-slate-600 font-bold mb-1.5">
                <Server className="w-4 h-4 text-blue-600" />
                <span>API Gateway</span>
              </div>
              <div className="space-y-1 text-[11px] text-slate-600">
                <p>
                  <span className="text-slate-400">Endpoint:</span>{' '}
                  <code className="font-mono text-slate-800">/api/v1/health</code>
                </p>
                <p>
                  <span className="text-slate-400">App Name:</span>{' '}
                  {data?.app_name || 'MPLAD-AI API Gateway'}
                </p>
                <p>
                  <span className="text-slate-400">Version:</span>{' '}
                  {data?.version || '1.0.0 (Phase 1)'}
                </p>
                <p>
                  <span className="text-slate-400">Environment:</span>{' '}
                  {data?.environment || 'development'}
                </p>
              </div>
            </div>

            {/* PostgreSQL Database */}
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
              <div className="flex items-center gap-2 text-slate-600 font-bold mb-1.5">
                <Database className="w-4 h-4 text-emerald-600" />
                <span>PostgreSQL 15+ Store</span>
              </div>
              <div className="space-y-1 text-[11px] text-slate-600">
                <p>
                  <span className="text-slate-400">Status:</span>{' '}
                  <span
                    className={`font-semibold ${
                      db?.status === 'connected'
                        ? 'text-emerald-700'
                        : 'text-amber-700'
                    }`}
                  >
                    {db?.status || 'Standby'}
                  </span>
                </p>
                <p>
                  <span className="text-slate-400">Dialect:</span>{' '}
                  {db?.dialect || 'postgresql'}
                </p>
                <p>
                  <span className="text-slate-400">Driver:</span>{' '}
                  {db?.driver || 'asyncpg'}
                </p>
                <p className="truncate" title={db?.target || 'localhost:5432'}>
                  <span className="text-slate-400">Host:</span>{' '}
                  <code className="font-mono text-slate-800">
                    {db?.target || 'localhost:5432'}
                  </code>
                </p>
              </div>
            </div>
          </div>

          {/* PowerShell Quickstart Instructions */}
          {!isOnline && (
            <div className="p-3 bg-slate-900 rounded-xl text-slate-200 font-mono text-[11px] space-y-1.5">
              <div className="flex items-center gap-2 text-amber-400 font-sans font-bold text-xs">
                <Terminal className="w-3.5 h-3.5" />
                <span>To Start Local FastAPI Server (PowerShell):</span>
              </div>
              <div className="bg-slate-950 p-2 rounded border border-slate-800 text-slate-300">
                cd backend<br />
                uvicorn app.main:app --reload --port 8000
              </div>
              <p className="text-[10px] text-slate-400 font-sans">
                Interactive OpenAPI Swagger docs will launch at{' '}
                <a
                  href="http://localhost:8000/docs"
                  target="_blank"
                  rel="noreferrer"
                  className="text-blue-400 underline"
                >
                  http://localhost:8000/docs
                </a>
              </p>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="bg-slate-50 px-5 py-3 border-t border-slate-200 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-slate-900 text-white rounded-lg text-xs font-semibold hover:bg-slate-800 transition-colors"
          >
            Close Diagnostics
          </button>
        </div>
      </div>
    </div>
  );
};
