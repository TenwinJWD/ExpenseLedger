/**
 * LactaFlow Enterprise Filter, Sort & Pagination Utilities
 */

import type { BaseRecord, FilterState, SortConfig } from '../types/dairy.ts';

export function filterRecords<T extends BaseRecord>(
  records: T[],
  filters: Partial<FilterState>
): T[] {
  return records.filter((item) => {
    // 1. Text Search across multiple fields: id, name, email, phone, location, notes, category
    if (filters.search && filters.search.trim() !== '') {
      const q = filters.search.trim().toLowerCase();
      const searchableText = [
        item.id,
        item.name,
        item.email,
        item.phone,
        item.location,
        item.category,
        item.status,
        item.notes || '',
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase();

      if (!searchableText.includes(q)) {
        return false;
      }
    }

    // 2. Category filter
    if (filters.category && filters.category !== 'ALL') {
      if (item.category !== filters.category) {
        return false;
      }
    }

    // 3. Status filter
    if (filters.status && filters.status !== 'ALL') {
      if (item.status !== filters.status) {
        return false;
      }
    }

    // 4. Location filter
    if (filters.location && filters.location !== 'ALL') {
      if (item.location !== filters.location) {
        return false;
      }
    }

    // 5. Date From filter (ISO or YYYY-MM-DD)
    if (filters.dateFrom) {
      const itemDateStr = item.date ? item.date.slice(0, 10) : '';
      if (itemDateStr && itemDateStr < filters.dateFrom) {
        return false;
      }
    }

    // 6. Date To filter
    if (filters.dateTo) {
      const itemDateStr = item.date ? item.date.slice(0, 10) : '';
      if (itemDateStr && itemDateStr > filters.dateTo) {
        return false;
      }
    }

    return true;
  });
}

export function sortRecords<T extends Record<string, any>>(
  records: T[],
  sortConfig: SortConfig | null
): T[] {
  if (!sortConfig || !sortConfig.field) {
    return [...records];
  }

  const { field, direction } = sortConfig;
  const modifier = direction === 'asc' ? 1 : -1;

  return [...records].sort((a, b) => {
    const valA = a[field];
    const valB = b[field];

    if (valA === valB) return 0;
    if (valA === undefined || valA === null) return 1;
    if (valB === undefined || valB === null) return -1;

    // Number comparison
    if (typeof valA === 'number' && typeof valB === 'number') {
      return (valA - valB) * modifier;
    }

    // Date or string comparison
    const strA = String(valA).toLowerCase();
    const strB = String(valB).toLowerCase();

    return strA.localeCompare(strB, undefined, { numeric: true }) * modifier;
  });
}

export function paginateRecords<T>(
  records: T[],
  page: number,
  pageSize: number
): {
  items: T[];
  totalRecords: number;
  totalPages: number;
  currentPage: number;
  startIndex: number;
  endIndex: number;
} {
  const totalRecords = records.length;
  const safePageSize = Math.max(1, pageSize);
  const totalPages = Math.max(1, Math.ceil(totalRecords / safePageSize));
  const currentPage = Math.min(Math.max(1, page), totalPages);

  const startIndex = (currentPage - 1) * safePageSize;
  const endIndex = Math.min(startIndex + safePageSize, totalRecords);
  const items = totalRecords === 0 ? [] : records.slice(startIndex, endIndex);

  return {
    items,
    totalRecords,
    totalPages,
    currentPage,
    startIndex: totalRecords === 0 ? 0 : startIndex + 1,
    endIndex,
  };
}
