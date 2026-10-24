/**
 * LactaFlow Enterprise TablePagination Component
 */

import React from 'react';
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';

interface TablePaginationProps {
  currentPage: number;
  totalPages: number;
  pageSize: number;
  totalRecords: number;
  startIndex: number;
  endIndex: number;
  onPageChange: (page: number) => void;
  onPageSizeChange: (size: number) => void;
  pageSizeOptions?: number[];
}

export const TablePagination: React.FC<TablePaginationProps> = ({
  currentPage,
  totalPages,
  pageSize,
  totalRecords,
  startIndex,
  endIndex,
  onPageChange,
  onPageSizeChange,
  pageSizeOptions = [5, 10, 20, 50],
}) => {
  // Generate smart page numbers list
  const getPageNumbers = () => {
    const pages: (number | string)[] = [];
    if (totalPages <= 7) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
    } else {
      pages.push(1);
      if (currentPage > 3) pages.push('...');
      const start = Math.max(2, currentPage - 1);
      const end = Math.min(totalPages - 1, currentPage + 1);
      for (let i = start; i <= end; i++) pages.push(i);
      if (currentPage < totalPages - 2) pages.push('...');
      pages.push(totalPages);
    }
    return pages;
  };

  return (
    <div className="bg-white border-t border-slate-200/80 px-4 py-3 flex flex-wrap items-center justify-between gap-4">
      {/* Left: Record Range and Total Count */}
      <div className="flex items-center gap-4 text-xs text-slate-600">
        <div>
          Showing{' '}
          <span className="font-semibold text-slate-900 font-mono">
            {totalRecords === 0 ? 0 : startIndex}
          </span>{' '}
          to{' '}
          <span className="font-semibold text-slate-900 font-mono">{endIndex}</span> of{' '}
          <span className="font-semibold text-slate-900 font-mono">{totalRecords}</span> records
        </div>

        {/* Rows per page selector */}
        <div className="flex items-center gap-1.5 border-l border-slate-200 pl-4">
          <label htmlFor="page-size-select" className="text-slate-500">
            Rows per page:
          </label>
          <select
            id="page-size-select"
            value={pageSize}
            onChange={(e) => onPageSizeChange(Number(e.target.value))}
            className="px-2 py-1 text-xs font-semibold bg-slate-50 border border-slate-300 rounded text-slate-800 cursor-pointer focus:outline-none focus:border-sky-500"
          >
            {pageSizeOptions.map((opt) => (
              <option key={opt} value={opt}>
                {opt}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Right: Page Navigation Buttons */}
      <div className="flex items-center gap-1">
        {/* First Page */}
        <button
          type="button"
          onClick={() => onPageChange(1)}
          disabled={currentPage <= 1}
          className="p-1.5 text-slate-600 hover:text-slate-900 hover:bg-slate-100 disabled:opacity-30 disabled:hover:bg-transparent rounded transition cursor-pointer"
          title="First page"
          aria-label="First page"
        >
          <ChevronsLeft className="w-4 h-4" />
        </button>

        {/* Previous Page */}
        <button
          type="button"
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage <= 1}
          className="p-1.5 text-slate-600 hover:text-slate-900 hover:bg-slate-100 disabled:opacity-30 disabled:hover:bg-transparent rounded transition cursor-pointer"
          title="Previous page"
          aria-label="Previous page"
        >
          <ChevronLeft className="w-4 h-4" />
        </button>

        {/* Page numbers */}
        <div className="flex items-center gap-1 mx-1">
          {getPageNumbers().map((p, idx) =>
            typeof p === 'number' ? (
              <button
                key={p}
                type="button"
                onClick={() => onPageChange(p)}
                className={`min-w-[28px] h-7 px-2 text-xs font-semibold rounded transition cursor-pointer ${
                  currentPage === p
                    ? 'bg-sky-600 text-white font-bold shadow-2xs'
                    : 'text-slate-700 hover:bg-slate-100'
                }`}
                aria-current={currentPage === p ? 'page' : undefined}
              >
                {p}
              </button>
            ) : (
              <span key={`ellipsis-${idx}`} className="px-1 text-slate-400 text-xs">
                ...
              </span>
            )
          )}
        </div>

        {/* Next Page */}
        <button
          type="button"
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage >= totalPages}
          className="p-1.5 text-slate-600 hover:text-slate-900 hover:bg-slate-100 disabled:opacity-30 disabled:hover:bg-transparent rounded transition cursor-pointer"
          title="Next page"
          aria-label="Next page"
        >
          <ChevronRight className="w-4 h-4" />
        </button>

        {/* Last Page */}
        <button
          type="button"
          onClick={() => onPageChange(totalPages)}
          disabled={currentPage >= totalPages}
          className="p-1.5 text-slate-600 hover:text-slate-900 hover:bg-slate-100 disabled:opacity-30 disabled:hover:bg-transparent rounded transition cursor-pointer"
          title="Last page"
          aria-label="Last page"
        >
          <ChevronsRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
