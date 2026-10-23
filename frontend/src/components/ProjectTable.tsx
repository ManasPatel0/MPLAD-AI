import React, { useState, useMemo } from 'react';
import {
  Search,
  Filter,
  AlertTriangle,
  CheckCircle2,
  Clock,
  FileQuestion,
  Info,
  Copy,
  TrendingUp,
} from 'lucide-react';
import { MOCK_PROJECTS } from '../data/mockData';
import { ProjectItem, ProjectStatus, WorkCategory } from '../types';

export const ProjectTable: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');

  const filteredProjects = useMemo(() => {
    return MOCK_PROJECTS.filter((proj) => {
      const matchesSearch =
        proj.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        proj.project_code.toLowerCase().includes(searchQuery.toLowerCase()) ||
        proj.location_address.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesStatus =
        selectedStatus === 'ALL' || proj.status === selectedStatus;

      const matchesCategory =
        selectedCategory === 'ALL' || proj.category === selectedCategory;

      return matchesSearch && matchesStatus && matchesCategory;
    });
  }, [searchQuery, selectedStatus, selectedCategory]);

  const renderStatusBadge = (status: ProjectStatus) => {
    switch (status) {
      case 'COMPLETED':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
            <CheckCircle2 className="w-3 h-3 text-emerald-600" />
            Completed
          </span>
        );
      case 'IN_PROGRESS':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-blue-50 text-blue-700 border border-blue-200">
            <Clock className="w-3 h-3 text-blue-600" />
            In Progress
          </span>
        );
      case 'SCRUTINIZED':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-amber-50 text-amber-700 border border-amber-200">
            <FileQuestion className="w-3 h-3 text-amber-600" />
            Scrutinized
          </span>
        );
      case 'PROPOSED':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-purple-50 text-purple-700 border border-purple-200">
            Proposed
          </span>
        );
      case 'STALLED':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-rose-50 text-rose-700 border border-rose-200">
            <AlertTriangle className="w-3 h-3 text-rose-600" />
            Stalled
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium bg-slate-100 text-slate-700">
            {status}
          </span>
        );
    }
  };

  const renderQuotaBadge = (quota: ProjectItem['priority_quota']) => {
    if (quota === 'SC_MANDATE') {
      return (
        <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-amber-100 text-amber-800 border border-amber-200">
          SC (15%)
        </span>
      );
    }
    if (quota === 'ST_MANDATE') {
      return (
        <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 border border-emerald-200">
          ST (7.5%)
        </span>
      );
    }
    return (
      <span className="text-[10px] font-medium px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">
        General
      </span>
    );
  };

  const renderAiBadge = (item: ProjectItem) => {
    if (!item.is_anomaly) {
      return (
        <span className="inline-flex items-center gap-1 text-[11px] text-emerald-700 font-medium bg-emerald-50 px-2 py-0.5 rounded border border-emerald-100">
          <CheckCircle2 className="w-3 h-3 text-emerald-500" />
          Clear
        </span>
      );
    }

    if (item.anomaly_type === 'DUPLICATE_OVERLAP') {
      return (
        <span
          title={`Duplicate overlap detected (${(item.duplicate_similarity! * 100).toFixed(0)}% similarity within 300m)`}
          className="inline-flex items-center gap-1 text-[11px] text-rose-700 font-bold bg-rose-50 px-2 py-0.5 rounded border border-rose-200 animate-pulse-subtle"
        >
          <Copy className="w-3 h-3 text-rose-600" />
          Duplicate {(item.duplicate_similarity! * 100).toFixed(0)}%
        </span>
      );
    }

    if (item.anomaly_type === 'COST_OUTLIER') {
      return (
        <span
          title="SOR Cost Outlier flagged by Isolation Forest"
          className="inline-flex items-center gap-1 text-[11px] text-amber-800 font-bold bg-amber-50 px-2 py-0.5 rounded border border-amber-200"
        >
          <TrendingUp className="w-3 h-3 text-amber-600" />
          SOR Outlier
        </span>
      );
    }

    return (
      <span
        title={`Predicted Delay Risk Score: ${item.delay_risk_score}/100`}
        className="inline-flex items-center gap-1 text-[11px] text-amber-700 font-semibold bg-amber-50 px-2 py-0.5 rounded border border-amber-200"
      >
        <AlertTriangle className="w-3 h-3 text-amber-500" />
        Delay Risk ({item.delay_risk_score})
      </span>
    );
  };

  const formatLakhs = (val: number) => {
    if (val === 0) return '₹ 0';
    return `₹ ${(val / 100000).toFixed(2)} L`;
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
      {/* Table Header & Controls */}
      <div className="p-4 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-bold text-slate-900 tracking-tight">
              Constituency Work Ledger & Status Engine
            </h3>
            <span className="text-[10px] font-bold bg-slate-100 text-slate-700 px-2 py-0.5 rounded-full border border-slate-200 font-mono">
              {filteredProjects.length} items
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Active developmental works with statutory quota verification and AI anomaly alerts.
          </p>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Search */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search by title, code..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="text-xs pl-8 pr-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg focus:outline-hidden focus:ring-1 focus:ring-blue-500 focus:bg-white w-48 sm:w-56"
            />
          </div>

          {/* Status Dropdown */}
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-700 focus:outline-hidden focus:ring-1 focus:ring-blue-500"
          >
            <option value="ALL">All Statuses</option>
            <option value="PROPOSED">Proposed</option>
            <option value="SCRUTINIZED">Scrutinized</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="COMPLETED">Completed</option>
          </select>

          {/* Category Dropdown */}
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-700 focus:outline-hidden focus:ring-1 focus:ring-blue-500"
          >
            <option value="ALL">All Sectors</option>
            <option value="DRINKING_WATER">Drinking Water</option>
            <option value="ROADS_BRIDGES">Roads & Bridges</option>
            <option value="COMMUNITY_INFRASTRUCTURE">Community Infra</option>
            <option value="PUBLIC_HEALTH">Public Health</option>
            <option value="SANITATION">Sanitation</option>
            <option value="EDUCATION">Education</option>
          </select>
        </div>
      </div>

      {/* Notice Banner: Mock Data */}
      <div className="bg-slate-50 px-4 py-2 border-b border-slate-200 flex items-center gap-2 text-xs text-slate-600">
        <Info className="w-3.5 h-3.5 text-blue-600 shrink-0" />
        <span>
          <strong>Phase 1 Preview Mode:</strong> Showing synthetic demonstration works. Relational database migration and automated live ingestion activate in Phase 2.
        </span>
      </div>

      {/* Table Element */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-700">
          <thead className="bg-slate-100/75 text-slate-600 uppercase font-bold text-[10px] tracking-wider border-b border-slate-200">
            <tr>
              <th scope="col" className="px-4 py-3">Work Code & Title</th>
              <th scope="col" className="px-3 py-3">Sector</th>
              <th scope="col" className="px-3 py-3">Quota</th>
              <th scope="col" className="px-3 py-3">Sanctioned Outlay</th>
              <th scope="col" className="px-3 py-3">Physical Progress</th>
              <th scope="col" className="px-3 py-3">Lifecycle Status</th>
              <th scope="col" className="px-4 py-3 text-right">AI Pre-Check</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {filteredProjects.length === 0 ? (
              <tr>
                <td colSpan={7} className="text-center py-8 text-slate-400">
                  No projects match your filter query.
                </td>
              </tr>
            ) : (
              filteredProjects.map((project) => (
                <tr
                  key={project.id}
                  className="hover:bg-slate-50/80 transition-colors"
                >
                  {/* Code & Title */}
                  <td className="px-4 py-3 max-w-xs">
                    <div className="font-mono text-[10px] font-bold text-slate-500">
                      {project.project_code}
                    </div>
                    <div className="font-semibold text-slate-900 line-clamp-1 mt-0.5">
                      {project.title}
                    </div>
                    <div className="text-[11px] text-slate-400 line-clamp-1 mt-0.5">
                      {project.location_address}
                    </div>
                  </td>

                  {/* Sector */}
                  <td className="px-3 py-3 whitespace-nowrap">
                    <span className="font-medium text-slate-700">
                      {project.category.replace(/_/g, ' ')}
                    </span>
                  </td>

                  {/* Quota */}
                  <td className="px-3 py-3 whitespace-nowrap">
                    {renderQuotaBadge(project.priority_quota)}
                  </td>

                  {/* Outlay */}
                  <td className="px-3 py-3 whitespace-nowrap font-mono">
                    <div className="font-bold text-slate-900">
                      {formatLakhs(project.sanctioned_cost || project.estimated_cost)}
                    </div>
                    <div className="text-[10px] text-slate-400">
                      Exp: {formatLakhs(project.actual_expenditure)}
                    </div>
                  </td>

                  {/* Progress */}
                  <td className="px-3 py-3 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <div className="w-20 bg-slate-200 rounded-full h-1.5 overflow-hidden">
                        <div
                          className={`h-1.5 rounded-full ${
                            project.progress_percentage === 100
                              ? 'bg-emerald-500'
                              : 'bg-blue-600'
                          }`}
                          style={{ width: `${project.progress_percentage}%` }}
                        ></div>
                      </div>
                      <span className="text-[11px] font-mono text-slate-600">
                        {project.progress_percentage}%
                      </span>
                    </div>
                  </td>

                  {/* Status */}
                  <td className="px-3 py-3 whitespace-nowrap">
                    {renderStatusBadge(project.status)}
                  </td>

                  {/* AI Pre-Check */}
                  <td className="px-4 py-3 whitespace-nowrap text-right">
                    {renderAiBadge(project)}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
