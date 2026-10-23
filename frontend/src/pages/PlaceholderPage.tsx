import React from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowLeft,
  Calendar,
  Layers,
  Sparkles,
  CheckCircle2,
} from 'lucide-react';

interface PlaceholderPageProps {
  title: string;
  moduleRole: string;
  phase: string;
  description: string;
  plannedFeatures: string[];
}

export const PlaceholderPage: React.FC<PlaceholderPageProps> = ({
  title,
  moduleRole,
  phase,
  description,
  plannedFeatures,
}) => {
  return (
    <div className="max-w-3xl mx-auto space-y-6 py-6">
      <Link
        to="/"
        className="inline-flex items-center gap-1.5 text-xs font-semibold text-blue-600 hover:text-blue-800 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Executive Dashboard</span>
      </Link>

      <div className="bg-white rounded-2xl border border-slate-200 p-8 shadow-xs">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200 font-mono">
            {phase}
          </span>
          <span className="text-xs text-slate-500 font-medium">
            Assigned: {moduleRole}
          </span>
        </div>

        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
          {title}
        </h1>
        <p className="text-sm text-slate-600 mt-2 leading-relaxed">
          {description}
        </p>

        <div className="mt-6 pt-6 border-t border-slate-100">
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-amber-500" />
            <span>Planned Sprint Deliverables</span>
          </h2>
          <ul className="space-y-2.5">
            {plannedFeatures.map((feat, idx) => (
              <li
                key={idx}
                className="flex items-start gap-2.5 text-xs text-slate-700"
              >
                <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                <span>{feat}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="mt-8 pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
          <span className="flex items-center gap-1.5 font-medium">
            <Calendar className="w-3.5 h-3.5 text-slate-400" />
            SIH 2026 Problem Statement ID: 26102
          </span>
          <Link
            to="/"
            className="px-4 py-2 rounded-lg bg-gov-navy text-white font-semibold hover:bg-slate-800 transition-colors"
          >
            Return to Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
};
