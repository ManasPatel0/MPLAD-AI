import React, { useState, useEffect, useCallback } from 'react';
import {
  Coins,
  ShieldCheck,
  Hammer,
  AlertOctagon,
  FileSpreadsheet,
  Download,
  RefreshCw,
  Sparkles,
} from 'lucide-react';
import { KpiCard } from '../components/KpiCard';
import { ExpenditureChart } from '../components/ExpenditureChart';
import { ProjectTable } from '../components/ProjectTable';
import { MOCK_KPI_SUMMARY } from '../data/mockData';
import { fetchExecutiveKpis, seedSampleProjects } from '../services/api';
import { BackendExecutiveKpis } from '../types';

export const DashboardPage: React.FC = () => {
  const [liveKpis, setLiveKpis] = useState<BackendExecutiveKpis | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isSeeding, setIsSeeding] = useState<boolean>(false);

  const loadKpis = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await fetchExecutiveKpis();
      if (data && data.total_projects > 0) {
        setLiveKpis(data);
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadKpis();
  }, [loadKpis]);

  const handleSeedData = async () => {
    setIsSeeding(true);
    try {
      const success = await seedSampleProjects();
      if (success) {
        await loadKpis();
      }
    } finally {
      setIsSeeding(false);
    }
  };

  // Convert numbers or fallback to mock
  const sanctionedCr = liveKpis
    ? (Number(liveKpis.total_sanctioned_cost) / 10000000).toFixed(2)
    : MOCK_KPI_SUMMARY.sanctioned_amount_cr;

  const spentCr = liveKpis
    ? (Number(liveKpis.total_actual_expenditure) / 10000000).toFixed(2)
    : MOCK_KPI_SUMMARY.expenditure_amount_cr;

  const scPct = liveKpis
    ? liveKpis.sc_quota_allocation_pct
    : MOCK_KPI_SUMMARY.sc_quota_pct;

  const stPct = liveKpis
    ? liveKpis.st_quota_allocation_pct
    : MOCK_KPI_SUMMARY.st_quota_pct;

  const totalWorks = liveKpis
    ? liveKpis.total_projects
    : MOCK_KPI_SUMMARY.total_works;

  const completedWorks = liveKpis
    ? liveKpis.completed_count
    : MOCK_KPI_SUMMARY.completed_works;

  const inProgressWorks = liveKpis
    ? liveKpis.in_progress_count
    : MOCK_KPI_SUMMARY.in_progress_works;

  const anomaliesCount = liveKpis
    ? liveKpis.active_anomalies_count
    : MOCK_KPI_SUMMARY.ai_flagged_count;

  return (
    <div className="space-y-6">
      {/* Top Banner & Context Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 mb-1">
            <span>MoSPI Analytics</span>
            <span>/</span>
            <span>Constituency Command</span>
            <span>/</span>
            <span className="text-blue-600 font-bold">Varanasi (UP-77)</span>
            {liveKpis && (
              <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                ● Live REST API
              </span>
            )}
          </div>
          <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900 tracking-tight">
            Executive Monitoring & Anomaly Center
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Real-time MPLADS developmental work tracking, statutory demographic quota auditing, and AI anomaly safeguards.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={handleSeedData}
            disabled={isSeeding}
            title="Pre-populate database with multi-state MPLADS projects"
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-indigo-50 border border-indigo-200 text-indigo-700 text-xs font-semibold hover:bg-indigo-100 shadow-2xs transition-colors disabled:opacity-50"
          >
            <Sparkles className={`w-3.5 h-3.5 ${isSeeding ? 'animate-spin' : ''}`} />
            <span>{isSeeding ? 'Seeding...' : 'Seed Sample DB'}</span>
          </button>
          <button
            onClick={loadKpis}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-white border border-slate-200 text-slate-700 text-xs font-semibold hover:bg-slate-50 shadow-2xs transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
          <button
            onClick={() => alert('Phase 1 Notice: Report generation export pipeline activates in Phase 2.')}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-white border border-slate-200 text-slate-700 text-xs font-semibold hover:bg-slate-50 shadow-2xs transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export Brief</span>
          </button>
          <button
            onClick={() => alert('Phase 1 Notice: MoSPI audit log sync activates in Phase 2.')}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-gov-navy text-white text-xs font-semibold hover:bg-gov-navy-light shadow-2xs transition-colors"
          >
            <FileSpreadsheet className="w-3.5 h-3.5" />
            <span>Audit Trail</span>
          </button>
        </div>
      </div>

      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Fund Allocation */}
        <KpiCard
          title="Sanctioned Outlay"
          value={`₹ ${sanctionedCr} Cr`}
          subValue="Allocated"
          badgeText={liveKpis ? `${liveKpis.fund_utilization_percentage}% Utilized` : "79.4% Sanctioned"}
          badgeType="success"
          icon={Coins}
          iconBgColor="bg-blue-50"
          iconColor="text-blue-600"
          footerText={`Spent: ₹ ${spentCr} Cr`}
        />

        {/* Card 2: Demographic Quotas */}
        <KpiCard
          title="Demographic Quotas"
          value={`SC ${scPct}%`}
          subValue={`ST ${stPct}%`}
          badgeText={
            liveKpis
              ? liveKpis.sc_quota_mandate_met && liveKpis.st_quota_mandate_met
                ? "Statutory Compliant"
                : "Quota Attention Required"
              : "Statutory Compliant"
          }
          badgeType={
            liveKpis && (!liveKpis.sc_quota_mandate_met || !liveKpis.st_quota_mandate_met)
              ? "danger"
              : "success"
          }
          icon={ShieldCheck}
          iconBgColor="bg-emerald-50"
          iconColor="text-emerald-600"
          footerText="Mandate: SC 15% / ST 7.5%"
        />

        {/* Card 3: Execution Progress */}
        <KpiCard
          title="Execution Ledger"
          value={`${totalWorks} Works`}
          subValue="Active"
          badgeText={`${completedWorks} Completed`}
          badgeType="info"
          icon={Hammer}
          iconBgColor="bg-amber-50"
          iconColor="text-amber-600"
          footerText={`${inProgressWorks} In Ground Execution`}
        />

        {/* Card 4: AI Anomalies */}
        <KpiCard
          title="AI Anomaly Alerts"
          value={`${anomaliesCount} Flags`}
          subValue="Active Flags"
          badgeText="Active Scrutiny"
          badgeType={anomaliesCount > 0 ? "danger" : "success"}
          icon={AlertOctagon}
          iconBgColor="bg-rose-50"
          iconColor="text-rose-600"
          footerText={liveKpis ? "Real-time AI Inspection Flags" : "8 Delay • 4 Dupl • 2 Cost"}
        />
      </div>

      {/* Visual Analytics Row */}
      <ExpenditureChart />

      {/* Primary Table Ledger */}
      <ProjectTable />
    </div>
  );
};
