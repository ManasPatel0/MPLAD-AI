import React from 'react';
import {
  Bell,
  CheckCircle2,
  AlertTriangle,
  RotateCw,
  Building2,
  ShieldAlert,
} from 'lucide-react';
import { HealthCheckResult } from '../services/api';

interface HeaderProps {
  health: HealthCheckResult | null;
  isLoadingHealth: boolean;
  onRefreshHealth: () => void;
  onOpenHealthModal: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  health,
  isLoadingHealth,
  onRefreshHealth,
  onOpenHealthModal,
}) => {
  const isOnline = health?.isOnline ?? false;

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-xs">
      {/* Top Gov Banner Strip */}
      <div className="bg-gov-navy px-4 sm:px-6 py-1 text-xs text-slate-300 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-white tracking-wide">
            GOVERNMENT OF INDIA
          </span>
          <span className="text-slate-500">|</span>
          <span className="text-slate-300">
            Ministry of Statistics and Programme Implementation (MoSPI)
          </span>
        </div>
        <div className="hidden md:flex items-center gap-3 text-xs">
          <span className="bg-gov-saffron text-slate-900 font-bold px-2 py-0.5 rounded text-[10px] tracking-wide uppercase">
            SIH 2026
          </span>
          <span className="text-slate-300 font-medium">
            Problem Statement ID: <strong className="text-white">26102</strong>
          </span>
        </div>
      </div>

      {/* Main Header Bar */}
      <div className="px-4 sm:px-6 py-3 flex items-center justify-between">
        {/* Left: Constituency / Context */}
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex h-10 w-10 rounded-lg bg-slate-100 border border-slate-200 items-center justify-center text-gov-navy">
            <Building2 className="w-5 h-5 text-slate-700" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold text-slate-900">
                Varanasi (UP-77)
              </h2>
              <span className="bg-blue-50 text-blue-700 text-[11px] font-semibold px-2 py-0.5 rounded border border-blue-200">
                Lok Sabha
              </span>
            </div>
            <p className="text-xs text-slate-500">
              Nodal District Authority: District Magistrate & Collector, Varanasi
            </p>
          </div>
        </div>

        {/* Right: Actions, Health Indicator, User Badge */}
        <div className="flex items-center gap-3">
          {/* Live API Health Status Badge */}
          <button
            onClick={onOpenHealthModal}
            title="Click for Gateway & Database Diagnostics"
            className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium border transition-colors shadow-2xs ${
              isOnline
                ? 'bg-emerald-50 text-emerald-800 border-emerald-300 hover:bg-emerald-100'
                : 'bg-amber-50 text-amber-900 border-amber-300 hover:bg-amber-100'
            }`}
          >
            {isOnline ? (
              <>
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                <span className="font-semibold">API Live</span>
                <span className="text-[10px] text-emerald-700 font-mono">
                  ({health?.latencyMs}ms)
                </span>
              </>
            ) : (
              <>
                <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                <span className="font-semibold">Mock Mode</span>
                <span className="text-[10px] text-amber-700 hidden sm:inline">
                  (API Offline)
                </span>
              </>
            )}
            <RotateCw
              onClick={(e) => {
                e.stopPropagation();
                onRefreshHealth();
              }}
              className={`w-3 h-3 text-slate-400 hover:text-slate-700 ${
                isLoadingHealth ? 'animate-spin text-blue-600' : ''
              }`}
            />
          </button>

          {/* Fiscal Year Filter */}
          <div className="hidden lg:flex items-center text-xs bg-slate-100 border border-slate-200 rounded-lg px-2.5 py-1.5 font-medium text-slate-700">
            <span className="text-slate-400 mr-1.5">FY:</span>
            <span className="font-semibold text-slate-900">2026-2027</span>
          </div>

          {/* AI Alerts Indicator */}
          <button
            title="14 Active AI Anomaly Flags in Varanasi"
            className="relative p-2 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-amber-500 rounded-full ring-2 ring-white"></span>
          </button>

          {/* User Role Badge */}
          <div className="flex items-center gap-2 pl-2 border-l border-slate-200">
            <div className="w-8 h-8 rounded-full bg-gov-navy text-white flex items-center justify-center font-bold text-xs ring-2 ring-slate-100">
              DM
            </div>
            <div className="hidden sm:block text-left text-xs">
              <p className="font-semibold text-slate-800 leading-none">
                District Magistrate
              </p>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Collector Scrutiny Portal
              </p>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
