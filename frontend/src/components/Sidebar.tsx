import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  CheckSquare,
  MapPin,
  PieChart,
  Users,
  Activity,
  Layers,
  ChevronRight,
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const navItems = [
    {
      to: '/',
      label: 'Executive Overview',
      icon: LayoutDashboard,
      badge: 'Live',
    },
    {
      to: '/recommendations',
      label: 'MP Recommendations',
      icon: FileText,
      badge: 'Phase 2',
    },
    {
      to: '/scrutiny',
      label: 'Collector Scrutiny',
      icon: CheckSquare,
      badge: 'Phase 2',
    },
    {
      to: '/gis-map',
      label: 'GIS Map & Anti-Spoof',
      icon: MapPin,
      badge: 'Phase 2',
    },
    {
      to: '/funds',
      label: 'Fund & Quota Tracker',
      icon: PieChart,
      badge: 'Phase 2',
    },
    {
      to: '/citizen',
      label: 'Citizen Transparency',
      icon: Users,
      badge: 'Phase 2',
    },
    {
      to: '/diagnostics',
      label: 'System Diagnostics',
      icon: Activity,
      badge: null,
    },
  ];

  return (
    <aside className="w-64 bg-slate-900 text-slate-200 min-h-screen flex flex-col shrink-0 border-r border-slate-800">
      {/* Brand Header */}
      <div className="p-4 border-b border-slate-800 flex items-center gap-3">
        <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-amber-600 via-blue-600 to-emerald-600 p-[2px] flex items-center justify-center shadow-lg">
          <div className="h-full w-full bg-slate-900 rounded-[10px] flex items-center justify-center">
            <Layers className="w-5 h-5 text-amber-500" />
          </div>
        </div>
        <div>
          <div className="flex items-center gap-1.5">
            <h1 className="font-extrabold text-base tracking-tight text-white">
              MPLAD-AI
            </h1>
            <span className="text-[10px] font-bold bg-amber-500/20 text-amber-400 px-1.5 py-0.2 rounded border border-amber-500/30">
              v1.0
            </span>
          </div>
          <p className="text-[11px] text-slate-400 font-medium leading-none mt-0.5">
            MoSPI Monitoring & Intelligence
          </p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <div className="px-3 pb-2 text-[10px] font-bold tracking-wider text-slate-400 uppercase">
          Core Modules
        </div>

        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-md shadow-blue-600/20'
                    : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                }`
              }
            >
              <div className="flex items-center gap-2.5">
                <Icon className="w-4 h-4 shrink-0" />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800/80 text-slate-400 border border-slate-700 font-mono">
                  {item.badge}
                </span>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Footer Info Box */}
      <div className="p-3 m-3 bg-slate-800/60 rounded-xl border border-slate-800 text-xs">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="font-medium">SIH 2026</span>
          <span className="text-[10px] bg-slate-700 text-slate-300 px-1.5 py-0.5 rounded font-mono">
            PS 26102
          </span>
        </div>
        <p className="text-[11px] text-slate-400 leading-snug">
          Phase 1 Foundation: React + FastAPI Full-Stack Engine.
        </p>
        <div className="mt-2 pt-2 border-t border-slate-700/60 flex items-center justify-between text-[11px] text-slate-400">
          <span>Engine Status</span>
          <span className="text-emerald-400 font-semibold flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            Operational
          </span>
        </div>
      </div>
    </aside>
  );
};
