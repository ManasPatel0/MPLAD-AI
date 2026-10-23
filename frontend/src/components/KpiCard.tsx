import React from 'react';
import { LucideIcon } from 'lucide-react';

interface KpiCardProps {
  title: string;
  value: string;
  subValue?: string;
  badgeText?: string;
  badgeType?: 'success' | 'warning' | 'danger' | 'info';
  icon: LucideIcon;
  iconBgColor?: string;
  iconColor?: string;
  footerText?: string;
}

export const KpiCard: React.FC<KpiCardProps> = ({
  title,
  value,
  subValue,
  badgeText,
  badgeType = 'info',
  icon: Icon,
  iconBgColor = 'bg-blue-50',
  iconColor = 'text-blue-600',
  footerText,
}) => {
  const badgeStyles = {
    success: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    warning: 'bg-amber-50 text-amber-700 border-amber-200',
    danger: 'bg-rose-50 text-rose-700 border-rose-200',
    info: 'bg-blue-50 text-blue-700 border-blue-200',
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            {title}
          </p>
          <div className="mt-2 flex items-baseline gap-2">
            <h3 className="text-2xl font-extrabold text-slate-900 tracking-tight">
              {value}
            </h3>
            {subValue && (
              <span className="text-xs font-medium text-slate-500">
                {subValue}
              </span>
            )}
          </div>
        </div>
        <div
          className={`h-11 w-11 rounded-xl ${iconBgColor} flex items-center justify-center shrink-0 border border-slate-100`}
        >
          <Icon className={`w-5 h-5 ${iconColor}`} />
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
        {badgeText && (
          <span
            className={`font-semibold px-2 py-0.5 rounded text-[11px] border ${badgeStyles[badgeType]}`}
          >
            {badgeText}
          </span>
        )}
        {footerText && (
          <span className="text-slate-500 font-medium ml-auto">
            {footerText}
          </span>
        )}
      </div>
    </div>
  );
};
