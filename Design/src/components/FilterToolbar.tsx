/**
 * LactaFlow Enterprise FilterToolbar Component
 * Positioned between tab navigation and data table.
 * Supports multi-field search, dropdown filtering, date ranges, and clear actions.
 */

import React, { useState } from 'react';
import { FilterState } from '../types/dairy.ts';
import { Search, Filter, X, Calendar, RotateCcw, ChevronDown } from 'lucide-react';

interface FilterToolbarProps {
  filters: FilterState;
  onFilterChange: (filters: FilterState) => void;
  categories: string[];
  statuses: string[];
  locations?: string[];
  totalResults: number;
  unfilteredCount: number;
}

export const FilterToolbar: React.FC<FilterToolbarProps> = ({
  filters,
  onFilterChange,
  categories,
  statuses,
  locations = [],
  totalResults,
  unfilteredCount,
}) => {
  const [localFilters, setLocalFilters] = useState<FilterState>(filters);
  const [isExpanded, setIsExpanded] = useState<boolean>(true);

  // Sync if external filters change
  React.useEffect(() => {
    setLocalFilters(filters);
  }, [filters]);

  const handleInputChange = (field: keyof FilterState, value: string) => {
    const updated = { ...localFilters, [field]: value };
    setLocalFilters(updated);
    // Instant search for text and dropdowns
    onFilterChange(updated);
  };

  const handleApply = () => {
    onFilterChange(localFilters);
  };

  const handleClear = () => {
    const cleared: FilterState = {
      search: '',
      category: 'ALL',
      status: 'ALL',
      location: 'ALL',
      dateFrom: '',
      dateTo: '',
    };
    setLocalFilters(cleared);
    onFilterChange(cleared);
  };

  // Count active non-empty filters
  const activeCount = [
    localFilters.search.trim() !== '',
    localFilters.category !== 'ALL' && localFilters.category !== '',
    localFilters.status !== 'ALL' && localFilters.status !== '',
    localFilters.location !== 'ALL' && localFilters.location !== '',
    localFilters.dateFrom !== '',
    localFilters.dateTo !== '',
  ].filter(Boolean).length;

  return (
    <div className="frosted-glass-card rounded-2xl overflow-hidden transition-all">
      {/* Top Bar with Search & Quick Filter Stats */}
      <div className="p-4 flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 bg-gradient-to-r from-slate-50/50 to-white">
        <div className="flex items-center gap-3 flex-1 min-w-[280px]">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input
              type="text"
              value={localFilters.search}
              onChange={(e) => handleInputChange('search', e.target.value)}
              placeholder="Search by ID, name, email, phone, location..."
              className="w-full pl-9 pr-8 py-2 text-xs sm:text-sm bg-white border border-slate-300 rounded-lg focus:outline-none focus:border-sky-500 focus:ring-2 focus:ring-sky-100 text-slate-800 placeholder-slate-400 transition"
            />
            {localFilters.search && (
              <button
                type="button"
                onClick={() => handleInputChange('search', '')}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 p-1 text-slate-400 hover:text-slate-600 rounded cursor-pointer"
                aria-label="Clear search text"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          <button
            type="button"
            onClick={() => setIsExpanded(!isExpanded)}
            className="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition"
          >
            <Filter className="w-3.5 h-3.5 text-sky-600" />
            <span>Filters</span>
            {activeCount > 0 && (
              <span className="px-1.5 py-0.2 text-[10px] font-bold bg-sky-600 text-white rounded-full">
                {activeCount}
              </span>
            )}
            <ChevronDown
              className={`w-3.5 h-3.5 text-slate-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
            />
          </button>
        </div>

        {/* Status / Count indicator */}
        <div className="flex items-center gap-3">
          <div className="text-xs text-slate-500">
            Matching Records:{' '}
            <span className="font-bold text-slate-800 font-mono">{totalResults}</span>
            {totalResults !== unfilteredCount && (
              <span className="text-slate-400"> of {unfilteredCount}</span>
            )}
          </div>

          {activeCount > 0 && (
            <button
              type="button"
              onClick={handleClear}
              className="inline-flex items-center gap-1 text-xs font-medium text-rose-600 hover:text-rose-700 cursor-pointer hover:underline"
            >
              <RotateCcw className="w-3 h-3" />
              Clear Filters
            </button>
          )}
        </div>
      </div>

      {/* Expanded Multi-Filter Controls */}
      {isExpanded && (
        <div className="p-4 bg-slate-50/60 border-t border-slate-100">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
            {/* Category Filter */}
            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-600 mb-1">
                Category / Product Line
              </label>
              <select
                value={localFilters.category}
                onChange={(e) => handleInputChange('category', e.target.value)}
                className="w-full px-3 py-2 text-xs bg-white border border-slate-300 rounded-lg focus:outline-none focus:border-sky-500 focus:ring-2 focus:ring-sky-100 text-slate-800 cursor-pointer"
              >
                <option value="ALL">All Categories</option>
                {categories.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
            </div>

            {/* Status Filter */}
            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-600 mb-1">
                Operating Status
              </label>
              <select
                value={localFilters.status}
                onChange={(e) => handleInputChange('status', e.target.value)}
                className="w-full px-3 py-2 text-xs bg-white border border-slate-300 rounded-lg focus:outline-none focus:border-sky-500 focus:ring-2 focus:ring-sky-100 text-slate-800 cursor-pointer"
              >
                <option value="ALL">All Statuses</option>
                {statuses.map((st) => (
                  <option key={st} value={st}>
                    {st}
                  </option>
                ))}
              </select>
            </div>

            {/* Date From */}
            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-600 mb-1 flex items-center gap-1">
                <Calendar className="w-3 h-3 text-slate-400" />
                <span>Date From</span>
              </label>
              <input
                type="date"
                value={localFilters.dateFrom}
                onChange={(e) => handleInputChange('dateFrom', e.target.value)}
                className="w-full px-3 py-2 text-xs bg-white border border-slate-300 rounded-lg focus:outline-none focus:border-sky-500 focus:ring-2 focus:ring-sky-100 text-slate-800"
              />
            </div>

            {/* Date To */}
            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-600 mb-1 flex items-center gap-1">
                <Calendar className="w-3 h-3 text-slate-400" />
                <span>Date To</span>
              </label>
              <input
                type="date"
                value={localFilters.dateTo}
                onChange={(e) => handleInputChange('dateTo', e.target.value)}
                className="w-full px-3 py-2 text-xs bg-white border border-slate-300 rounded-lg focus:outline-none focus:border-sky-500 focus:ring-2 focus:ring-sky-100 text-slate-800"
              />
            </div>
          </div>

          {/* Action Row */}
          <div className="mt-3.5 pt-3 border-t border-slate-200/70 flex items-center justify-between">
            <div className="text-[11px] text-slate-500">
              {activeCount > 0 ? (
                <span className="text-sky-700 font-medium">
                  {activeCount} filter{activeCount > 1 ? 's' : ''} actively restricting table output
                </span>
              ) : (
                <span>No active filters. Showing full dataset.</span>
              )}
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={handleClear}
                disabled={activeCount === 0}
                className="px-3 py-1.5 text-xs font-semibold text-slate-600 bg-white border border-slate-300 rounded-lg hover:bg-slate-100 transition disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
              >
                Reset Filters
              </button>
              <button
                type="button"
                onClick={handleApply}
                className="px-3.5 py-1.5 text-xs font-bold text-white bg-sky-600 hover:bg-sky-700 rounded-lg transition shadow-2xs cursor-pointer"
              >
                Apply Filters
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
