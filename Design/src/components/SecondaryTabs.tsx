/**
 * LactaFlow Enterprise SecondaryTabs Component
 * Translucent frosted horizontal sub-tab row for Primary Tab 2 modules.
 */

import React from 'react';
import { SubTabId } from '../types/dairy.ts';
import { SubTabConfig } from '../config/dairyConfig.ts';
import { FlaskConical, Truck } from 'lucide-react';

interface SecondaryTabsProps {
  subTabs: SubTabConfig[];
  activeSubTab: SubTabId;
  onSubTabChange: (subTabId: SubTabId) => void;
  subTabCounts: Record<SubTabId, number>;
}

export const SecondaryTabs: React.FC<SecondaryTabsProps> = ({
  subTabs,
  activeSubTab,
  onSubTabChange,
  subTabCounts,
}) => {
  const getSubTabIcon = (id: SubTabId) => {
    switch (id) {
      case 'quality':
        return <FlaskConical className="w-3.5 h-3.5" />;
      case 'logistics':
        return <Truck className="w-3.5 h-3.5" />;
      default:
        return null;
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
    if (e.key === 'ArrowRight') {
      const nextIndex = (index + 1) % subTabs.length;
      onSubTabChange(subTabs[nextIndex].id);
    } else if (e.key === 'ArrowLeft') {
      const prevIndex = (index - 1 + subTabs.length) % subTabs.length;
      onSubTabChange(subTabs[prevIndex].id);
    }
  };

  return (
    <div
      role="tablist"
      aria-label="Secondary Dairy Sub-tabs"
      className="bg-white/60 backdrop-blur-md border border-sky-100/90 p-1.5 rounded-2xl flex flex-wrap gap-2 shadow-xs"
    >
      {subTabs.map((st, idx) => {
        const isActive = activeSubTab === st.id;
        const count = subTabCounts[st.id] ?? 0;

        return (
          <button
            key={st.id}
            role="tab"
            id={`subtab-${st.id}`}
            aria-selected={isActive}
            aria-controls={`subtab-panel-${st.id}`}
            tabIndex={isActive ? 0 : -1}
            onClick={() => onSubTabChange(st.id)}
            onKeyDown={(e) => handleKeyDown(e, idx)}
            className={`
              flex-1 min-w-[220px] flex items-center justify-between px-4 py-3 rounded-xl text-xs font-bold transition-all cursor-pointer outline-none
              ${
                isActive
                  ? 'bg-white text-slate-900 shadow-sm border border-sky-200/80'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-white/50 border border-transparent'
              }
            `}
          >
            <div className="flex items-center gap-2.5">
              <span
                className={`p-1.5 rounded-lg transition-transform ${
                  isActive
                    ? 'bg-gradient-to-tr from-sky-600 to-cyan-500 text-white shadow-xs'
                    : 'bg-slate-100/80 text-slate-500'
                }`}
              >
                {getSubTabIcon(st.id)}
              </span>

              <div className="text-left">
                <div className="flex items-center gap-1.5">
                  <span
                    className={`text-[10px] font-extrabold uppercase px-1.5 py-0.2 rounded border ${
                      isActive
                        ? 'bg-sky-50 text-sky-800 border-sky-200'
                        : 'bg-slate-100 text-slate-500 border-slate-200'
                    }`}
                  >
                    {st.badgeLabel}
                  </span>
                  <span>{st.label}</span>
                </div>
                <span className="text-[10px] font-normal text-slate-500 block truncate max-w-[220px]">
                  {st.tagline}
                </span>
              </div>
            </div>

            <span
              className={`ml-2 px-2.5 py-0.5 text-[11px] rounded-full font-mono font-bold border transition-colors ${
                isActive
                  ? 'bg-sky-100 text-sky-900 border-sky-300'
                  : 'bg-slate-100 text-slate-600 border-slate-200'
              }`}
            >
              {count}
            </span>
          </button>
        );
      })}
    </div>
  );
};
