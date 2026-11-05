import React from 'react';
import {
  Coins,
  ShieldCheck,
  Hammer,
  AlertOctagon,
  FileSpreadsheet,
  Download,
  Calendar,
  Sparkles,
} from 'lucide-react';
import { KpiCard } from '../components/KpiCard';
import { ExpenditureChart } from '../components/ExpenditureChart';
import { ProjectTable } from '../components/ProjectTable';
import { MOCK_KPI_SUMMARY } from '../data/mockData';

export const DashboardPage: React.FC = () => {
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
          value={`₹ ${MOCK_KPI_SUMMARY.sanctioned_amount_cr} Cr`}
          subValue={`of ₹ ${MOCK_KPI_SUMMARY.total_entitlement_cr} Cr`}
          badgeText="79.4% Sanctioned"
          badgeType="success"
          icon={Coins}
          iconBgColor="bg-blue-50"
          iconColor="text-blue-600"
          footerText={`Spent: ₹ ${MOCK_KPI_SUMMARY.expenditure_amount_cr} Cr`}
        />

        {/* Card 2: Demographic Quotas */}
        <KpiCard
          title="Demographic Quotas"
          value={`SC ${MOCK_KPI_SUMMARY.sc_quota_pct}%`}
          subValue={`ST ${MOCK_KPI_SUMMARY.st_quota_pct}%`}
          badgeText="Statutory Compliant"
          badgeType="success"
          icon={ShieldCheck}
          iconBgColor="bg-emerald-50"
          iconColor="text-emerald-600"
          footerText="Mandate: SC 15% / ST 7.5%"
        />

        {/* Card 3: Execution Progress */}
        <KpiCard
          title="Execution Ledger"
          value={`${MOCK_KPI_SUMMARY.total_works} Works`}
          subValue="Active"
          badgeText={`${MOCK_KPI_SUMMARY.completed_works} Completed`}
          badgeType="info"
          icon={Hammer}
          iconBgColor="bg-amber-50"
          iconColor="text-amber-600"
          footerText={`${MOCK_KPI_SUMMARY.in_progress_works} In Ground Execution`}
        />

        {/* Card 4: AI Anomalies */}
        <KpiCard
          title="AI Anomaly Alerts"
          value={`${MOCK_KPI_SUMMARY.ai_flagged_count} Flags`}
          subValue="Pre-Check"
          badgeText="Active Scrutiny"
          badgeType="danger"
          icon={AlertOctagon}
          iconBgColor="bg-rose-50"
          iconColor="text-rose-600"
          footerText="8 Delay • 4 Dupl • 2 Cost"
        />
      </div>

      {/* Visual Analytics Row */}
      <ExpenditureChart />

      {/* Primary Table Ledger */}
      <ProjectTable />
    </div>
  );
};
