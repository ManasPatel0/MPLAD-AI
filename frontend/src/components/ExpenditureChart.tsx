import React from 'react';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { MOCK_EXPENDITURE_TRENDS, MOCK_SECTOR_BREAKDOWN } from '../data/mockData';

export const ExpenditureChart: React.FC = () => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* 2-Column: Financial Pacing Trajectory */}
      <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 p-5 shadow-xs">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-bold text-slate-900 tracking-tight">
              Constituency Fund Utilization & Pacing Trajectory
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Sanctioned Outlay vs. Cumulative Ground Expenditure vs. MoSPI Target Pacing (₹ Crores)
            </p>
          </div>
          <span className="text-[11px] font-semibold bg-emerald-50 text-emerald-700 px-2.5 py-1 rounded-md border border-emerald-200">
            FY 2026-27 Active Pacing
          </span>
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              data={MOCK_EXPENDITURE_TRENDS}
              margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
            >
              <defs>
                <linearGradient id="sanctionedGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#2563EB" stopOpacity={0.25} />
                  <stop offset="95%" stopColor="#2563EB" stopOpacity={0.0} />
                </linearGradient>
                <linearGradient id="expenditureGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#059669" stopOpacity={0.35} />
                  <stop offset="95%" stopColor="#059669" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
              <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#64748b' }} stroke="#cbd5e1" />
              <YAxis tick={{ fontSize: 11, fill: '#64748b' }} stroke="#cbd5e1" unit=" Cr" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  borderColor: '#334155',
                  borderRadius: '8px',
                  color: '#fff',
                  fontSize: '12px',
                }}
              />
              <Legend
                verticalAlign="top"
                height={32}
                iconType="circle"
                wrapperStyle={{ fontSize: '11px', color: '#475569' }}
              />
              <Area
                type="monotone"
                dataKey="sanctioned"
                name="Sanctioned Outlay (₹ Cr)"
                stroke="#2563EB"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#sanctionedGrad)"
              />
              <Area
                type="monotone"
                dataKey="expenditure"
                name="Actual Ground Expenditure (₹ Cr)"
                stroke="#059669"
                strokeWidth={2.5}
                fillOpacity={1}
                fill="url(#expenditureGrad)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 1-Column: Sectoral Outlay Breakdown */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-bold text-slate-900 tracking-tight">
              Sectoral Allocation
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Outlay by Priority Work Category (₹ Cr)
            </p>
          </div>
          <span className="text-[10px] font-mono text-slate-400">
            142 Works
          </span>
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={MOCK_SECTOR_BREAKDOWN}
              layout="vertical"
              margin={{ top: 5, right: 10, left: 20, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
              <XAxis type="number" tick={{ fontSize: 10, fill: '#64748b' }} stroke="#cbd5e1" unit=" Cr" />
              <YAxis
                type="category"
                dataKey="name"
                tick={{ fontSize: 10, fill: '#334155' }}
                stroke="#cbd5e1"
                width={85}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  borderColor: '#334155',
                  borderRadius: '8px',
                  color: '#fff',
                  fontSize: '11px',
                }}
              />
              <Bar dataKey="value" name="Allocation (₹ Cr)" fill="#D97706" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
