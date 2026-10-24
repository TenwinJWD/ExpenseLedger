/**
 * LactaFlow Enterprise PrimaryTabs Component
 * Transparent frosted-glass horizontal navigation for Primary Tab 1 and Primary Tab 2.
 */

import React from 'react';
import { PrimaryTabId } from '../types/dairy.ts';
import { TabConfig } from '../config/dairyConfig.ts';
import { Milk, Factory } from 'lucide-react';

interface PrimaryTabsProps {
  tabs: TabConfig[];
  activeTab: PrimaryTabId;
  onTabChange: (tabId: PrimaryTabId) => void;
  tabCounts: Record<PrimaryTabId, number>;
}

export const PrimaryTabs: React.FC<PrimaryTabsProps> = ({
  tabs,
  activeTab,
  onTabChange,
  tabCounts,
}) => {
  const getTabIcon = (id: PrimaryTabId) => {
    switch (id) {
      case 'intake':
        return <Milk className="w-4 h-4" />;
      case 'operations':
        return <Factory className="w-4 h-4" />;
      default:
        return null;
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
    if (e.key === 'ArrowRight') {
      const nextIndex = (index + 1) % tabs.length;
      onTabChange(tabs[nextIndex].id);
    } else if (e.key === 'ArrowLeft') {
      const prevIndex = (index - 1 + tabs.length) % tabs.length;
      onTabChange(tabs[prevIndex].id);
    }
  };

  return (
    <nav
      aria-label="Primary navigation tabs"
      className="frosted-glass-tab sticky top-[97px] z-30 transition-all"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div
          role="tablist"
          aria-label="Primary Dairy Modules"
          className="flex space-x-2 sm:space-x-4 overflow-x-auto no-scrollbar pt-2"
        >
          {tabs.map((tab, idx) => {
            const isActive = activeTab === tab.id;
            const count = tabCounts[tab.id] ?? 0;

            return (
              <button
                key={tab.id}
                role="tab"
                id={`primary-tab-${tab.id}`}
                aria-selected={isActive}
                aria-controls={`primary-panel-${tab.id}`}
                tabIndex={isActive ? 0 : -1}
                onClick={() => onTabChange(tab.id)}
                onKeyDown={(e) => handleKeyDown(e, idx)}
                className={`
                  relative group flex items-center gap-2.5 py-3.5 px-4 text-xs sm:text-sm font-bold border-b-2 transition-all cursor-pointer outline-none whitespace-nowrap rounded-t-xl
                  ${
                    isActive
                      ? 'border-sky-600 text-sky-950 bg-white/90 shadow-2xs'
                      : 'border-transparent text-slate-600 hover:text-slate-900 hover:bg-white/50'
                  }
                `}
              >
                {/* Visual Icon */}
                <span
                  className={`p-1.5 rounded-lg transition-transform ${
                    isActive
                      ? 'bg-gradient-to-tr from-sky-600 to-cyan-500 text-white shadow-xs scale-105'
                      : 'text-slate-400 group-hover:text-slate-700 bg-slate-100/70'
                  }`}
                >
                  {getTabIcon(tab.id)}
                </span>

                {/* Tab Identifiers */}
                <div className="text-left">
                  <div className="flex items-center gap-1.5">
                    <span
                      className={`text-[10px] tracking-wider uppercase font-extrabold px-1.5 py-0.2 rounded border ${
                        isActive
                          ? 'text-sky-800 bg-sky-100 border-sky-200'
                          : 'text-slate-500 bg-slate-100 border-slate-200'
                      }`}
                    >
                      {tab.badgeLabel}
                    </span>
                    <span>{tab.label}</span>
                  </div>
                  <span className="text-[11px] font-normal text-slate-500 block hidden sm:inline">
                    {tab.tagline}
                  </span>
                </div>

                {/* Badge count */}
                <span
                  className={`ml-1.5 px-2 py-0.5 text-xs font-semibold rounded-full font-mono transition-colors border ${
                    isActive
                      ? 'bg-sky-100 text-sky-950 font-bold border-sky-300'
                      : 'bg-slate-100 text-slate-600 border-slate-200'
                  }`}
                >
                  {count}
                </span>

                <span className="sr-only">
                  {isActive ? '(Selected Tab)' : ''}
                </span>
              </button>
            );
          })}
        </div>
      </div>
    </nav>
  );
};
