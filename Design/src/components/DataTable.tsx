/**
 * LactaFlow Enterprise DataTable Component
 * Supports configurable column definitions, sorting, row actions,
 * status badge rendering, empty states, and pagination.
 */

import React from 'react';
import { TableColumn, BaseRecord, SortConfig } from '../types/dairy.ts';
import { TablePagination } from './TablePagination.tsx';
import {
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  Edit2,
  Trash2,
  FileSpreadsheet,
  AlertCircle,
  Copy,
  Check,
  Eye,
} from 'lucide-react';

interface DataTableProps {
  columns: TableColumn[];
  records: BaseRecord[];
  allRecordsCount: number;
  sortConfig: SortConfig | null;
  onSort: (columnKey: string) => void;
  currentPage: number;
  pageSize: number;
  totalPages: number;
  startIndex: number;
  endIndex: number;
  onPageChange: (page: number) => void;
  onPageSizeChange: (size: number) => void;
  onEdit: (record: BaseRecord) => void;
  onDelete: (record: BaseRecord) => void;
  onClearFilters?: () => void;
  isLoading?: boolean;
}

export const DataTable: React.FC<DataTableProps> = ({
  columns,
  records,
  allRecordsCount,
  sortConfig,
  onSort,
  currentPage,
  pageSize,
  totalPages,
  startIndex,
  endIndex,
  onPageChange,
  onPageSizeChange,
  onEdit,
  onDelete,
  onClearFilters,
  isLoading = false,
}) => {
  const [copiedId, setCopiedId] = React.useState<string | null>(null);
  const [selectedRecordForDetail, setSelectedRecordForDetail] = React.useState<BaseRecord | null>(null);

  const copyToClipboard = (text: string) => {
    navigator.clipboard?.writeText(text);
    setCopiedId(text);
    setTimeout(() => setCopiedId(null), 2000);
  };

  // Status badge styling helper
  const renderStatusBadge = (status: string) => {
    const s = (status || '').toLowerCase();
    let badgeClass = 'bg-slate-100 text-slate-700 border-slate-200';

    if (
      s.includes('accept') ||
      s.includes('pass') ||
      s.includes('approved') ||
      s.includes('delivered')
    ) {
      badgeClass = 'bg-emerald-50 text-emerald-800 border-emerald-200';
    } else if (
      s.includes('quarantin') ||
      s.includes('transit') ||
      s.includes('test') ||
      s.includes('conditional') ||
      s.includes('scheduled')
    ) {
      badgeClass = 'bg-amber-50 text-amber-800 border-amber-200';
    } else if (
      s.includes('reject') ||
      s.includes('alert') ||
      s.includes('fail')
    ) {
      badgeClass = 'bg-rose-50 text-rose-800 border-rose-200';
    }

    return (
      <span
        className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold border ${badgeClass} whitespace-nowrap`}
      >
        <span
          className={`w-1.5 h-1.5 rounded-full mr-1.5 ${
            badgeClass.includes('emerald')
              ? 'bg-emerald-500'
              : badgeClass.includes('amber')
              ? 'bg-amber-500'
              : badgeClass.includes('rose')
              ? 'bg-rose-500'
              : 'bg-slate-400'
          }`}
        />
        {status}
      </span>
    );
  };

  return (
    <div className="frosted-glass-card rounded-2xl overflow-hidden transition-all">
      {/* Table Title Bar */}
      <div className="px-5 py-3.5 border-b border-slate-100 flex flex-wrap items-center justify-between gap-3 bg-gradient-to-r from-slate-50/70 to-white">
        <div className="flex items-center gap-2">
          <FileSpreadsheet className="w-4 h-4 text-sky-600" />
          <h3 className="text-sm font-bold text-slate-800">
            Registered Production Records
          </h3>
          <span className="text-xs text-slate-400 font-mono">
            ({records.length} shown of {allRecordsCount} total)
          </span>
        </div>

        <div className="text-xs text-slate-500 hidden sm:block">
          Click column headers to sort table ascending or descending
        </div>
      </div>

      {/* Main Table Container */}
      <div className="overflow-x-auto min-h-[300px]">
        {isLoading ? (
          <div className="py-20 flex flex-col items-center justify-center text-slate-400">
            <div className="w-8 h-8 border-3 border-sky-600 border-t-transparent rounded-full animate-spin mb-3" />
            <p className="text-sm font-medium text-slate-600">Loading production records...</p>
          </div>
        ) : records.length === 0 ? (
          <div className="py-16 px-4 flex flex-col items-center justify-center text-center">
            <div className="w-12 h-12 bg-slate-100 rounded-full flex items-center justify-center text-slate-400 mb-3 border border-slate-200">
              <AlertCircle className="w-6 h-6" />
            </div>
            <h4 className="text-sm font-bold text-slate-800 mb-1">No Matching Records Found</h4>
            <p className="text-xs text-slate-500 max-w-md mb-4">
              {allRecordsCount === 0
                ? 'No records exist in this view yet. Fill out the form above to record your first batch.'
                : 'Current filter and search parameters did not match any records. Try adjusting or clearing your filters.'}
            </p>
            {allRecordsCount > 0 && onClearFilters && (
              <button
                type="button"
                onClick={onClearFilters}
                className="px-3.5 py-1.5 text-xs font-semibold text-sky-700 bg-sky-50 hover:bg-sky-100 border border-sky-200 rounded-lg transition cursor-pointer"
              >
                Reset All Filters
              </button>
            )}
          </div>
        ) : (
          <table className="w-full text-left border-collapse text-xs sm:text-sm">
            <thead>
              <tr className="bg-slate-50/90 border-b border-slate-200 text-slate-700 text-xs font-bold uppercase tracking-wider">
                {columns.map((col) => (
                  <th
                    key={col.key}
                    scope="col"
                    style={{ width: col.width }}
                    className={`px-4 py-3 select-none ${
                      col.sortable ? 'cursor-pointer hover:bg-slate-100/80 transition-colors' : ''
                    } ${
                      col.align === 'right'
                        ? 'text-right'
                        : col.align === 'center'
                        ? 'text-center'
                        : 'text-left'
                    }`}
                    onClick={() => col.sortable && onSort(col.key)}
                  >
                    <div
                      className={`inline-flex items-center gap-1.5 ${
                        col.align === 'right'
                          ? 'justify-end'
                          : col.align === 'center'
                          ? 'justify-center'
                          : 'justify-start'
                      }`}
                    >
                      <span>{col.label}</span>
                      {col.sortable && (
                        <span className="text-slate-400">
                          {sortConfig?.field === col.key ? (
                            sortConfig.direction === 'asc' ? (
                              <ArrowUp className="w-3.5 h-3.5 text-sky-600 font-bold" />
                            ) : (
                              <ArrowDown className="w-3.5 h-3.5 text-sky-600 font-bold" />
                            )
                          ) : (
                            <ArrowUpDown className="w-3 h-3 opacity-40 hover:opacity-100" />
                          )}
                        </span>
                      )}
                    </div>
                  </th>
                ))}
                <th scope="col" className="px-4 py-3 text-right text-xs font-bold uppercase tracking-wider w-24">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {records.map((record) => (
                <tr
                  key={record.id}
                  className="hover:bg-sky-50/40 transition-colors group"
                >
                  {columns.map((col) => {
                    const val = record[col.key];

                    return (
                      <td
                        key={col.key}
                        className={`px-4 py-3 text-slate-800 ${
                          col.align === 'right'
                            ? 'text-right'
                            : col.align === 'center'
                            ? 'text-center'
                            : 'text-left'
                        }`}
                      >
                        {col.render ? (
                          col.render(val, record)
                        ) : col.key === 'id' ? (
                          <div className="flex items-center gap-1 font-mono text-xs font-bold text-sky-900">
                            <span>{val}</span>
                            <button
                              type="button"
                              onClick={() => copyToClipboard(val)}
                              title="Copy ID to clipboard"
                              className="p-1 text-slate-400 hover:text-sky-600 opacity-0 group-hover:opacity-100 transition rounded"
                            >
                              {copiedId === val ? (
                                <Check className="w-3 h-3 text-emerald-600" />
                              ) : (
                                <Copy className="w-3 h-3" />
                              )}
                            </button>
                          </div>
                        ) : col.key === 'status' ? (
                          renderStatusBadge(val)
                        ) : col.key === 'date' || col.key === 'createdAt' || col.key === 'updatedAt' ? (
                          <span className="text-xs text-slate-600 font-mono">
                            {val ? String(val).replace('T', ' ').slice(0, 16) : '—'}
                          </span>
                        ) : typeof val === 'number' ? (
                          <span className="font-semibold text-slate-900 font-mono">
                            {val.toLocaleString()}
                          </span>
                        ) : (
                          <span className="truncate max-w-[200px] inline-block" title={String(val || '')}>
                            {val ?? '—'}
                          </span>
                        )}
                      </td>
                    );
                  })}

                  {/* Row Actions */}
                  <td className="px-4 py-3 text-right whitespace-nowrap">
                    <div className="inline-flex items-center justify-end gap-1">
                      <button
                        type="button"
                        onClick={() => setSelectedRecordForDetail(record)}
                        title="View Full Record Details"
                        aria-label={`View details for record ${record.id}`}
                        className="p-1.5 text-slate-500 hover:text-sky-700 hover:bg-sky-50 rounded-md transition cursor-pointer"
                      >
                        <Eye className="w-3.5 h-3.5" />
                      </button>

                      <button
                        type="button"
                        onClick={() => onEdit(record)}
                        title="Edit Record"
                        aria-label={`Edit record ${record.id}`}
                        className="p-1.5 text-slate-500 hover:text-sky-700 hover:bg-sky-50 rounded-md transition cursor-pointer"
                      >
                        <Edit2 className="w-3.5 h-3.5" />
                      </button>

                      <button
                        type="button"
                        onClick={() => onDelete(record)}
                        title="Delete Record"
                        aria-label={`Delete record ${record.id}`}
                        className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-md transition cursor-pointer"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Pagination Footer */}
      {!isLoading && records.length > 0 && (
        <TablePagination
          currentPage={currentPage}
          totalPages={totalPages}
          pageSize={pageSize}
          totalRecords={allRecordsCount}
          startIndex={startIndex}
          endIndex={endIndex}
          onPageChange={onPageChange}
          onPageSizeChange={onPageSizeChange}
        />
      )}

      {/* Quick Details Modal */}
      {selectedRecordForDetail && (
        <div
          className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4"
          onClick={() => setSelectedRecordForDetail(null)}
        >
          <div
            className="bg-white rounded-xl shadow-xl max-w-lg w-full p-6 border border-slate-200"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div>
                <span className="text-[11px] font-bold text-sky-600 tracking-wider uppercase font-mono">
                  {selectedRecordForDetail.id}
                </span>
                <h4 className="text-base font-bold text-slate-900">
                  {selectedRecordForDetail.name}
                </h4>
              </div>
              <div>{renderStatusBadge(selectedRecordForDetail.status)}</div>
            </div>

            <div className="py-4 space-y-2.5 text-xs">
              <div className="grid grid-cols-2 gap-3 bg-slate-50 p-3 rounded-lg border border-slate-100">
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-bold">Contact Email</span>
                  <span className="font-medium text-slate-800 break-all">{selectedRecordForDetail.email}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-bold">Contact Phone</span>
                  <span className="font-medium text-slate-800">{selectedRecordForDetail.phone}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-bold">Category</span>
                  <span className="font-medium text-slate-800">{selectedRecordForDetail.category}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-bold">Date / Time</span>
                  <span className="font-medium text-slate-800 font-mono">
                    {selectedRecordForDetail.date?.replace('T', ' ')}
                  </span>
                </div>
              </div>

              <div>
                <span className="text-slate-400 block text-[10px] uppercase font-bold mb-0.5">Location / Facility</span>
                <span className="text-slate-800">{selectedRecordForDetail.location}</span>
              </div>

              {selectedRecordForDetail.notes && (
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-bold mb-0.5">Notes & Remarks</span>
                  <p className="text-slate-700 bg-slate-50 p-2.5 rounded border border-slate-200/60 text-xs">
                    {selectedRecordForDetail.notes}
                  </p>
                </div>
              )}
            </div>

            <div className="pt-3 border-t border-slate-100 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => {
                  onEdit(selectedRecordForDetail);
                  setSelectedRecordForDetail(null);
                }}
                className="px-3 py-1.5 text-xs font-semibold text-sky-700 bg-sky-50 hover:bg-sky-100 border border-sky-200 rounded-lg transition"
              >
                Edit This Record
              </button>
              <button
                type="button"
                onClick={() => setSelectedRecordForDetail(null)}
                className="px-3 py-1.5 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
