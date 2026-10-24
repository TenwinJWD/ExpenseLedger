/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useMemo, useEffect, useCallback } from 'react';
import {
  PrimaryTabId,
  SubTabId,
  BaseRecord,
  FilterState,
  SortConfig,
  ToastMessage,
  TableColumn,
} from './types/dairy.ts';
import {
  PRIMARY_TABS,
  SECONDARY_TABS,
  INTAKE_FORM_SCHEMA,
  QUALITY_FORM_SCHEMA,
  LOGISTICS_FORM_SCHEMA,
} from './config/dairyConfig.ts';
import {
  loadStoredRecords,
  saveStoredRecords,
  resetToSeedData,
} from './data/seedData.ts';
import { filterRecords, sortRecords, paginateRecords } from './utils/filterAndSort.ts';
import { PageHeader } from './components/PageHeader.tsx';
import { PrimaryTabs } from './components/PrimaryTabs.tsx';
import { SecondaryTabs } from './components/SecondaryTabs.tsx';
import { DynamicForm } from './components/DynamicForm.tsx';
import { FilterToolbar } from './components/FilterToolbar.tsx';
import { DataTable } from './components/DataTable.tsx';
import { ConfirmationDialog } from './components/ConfirmationDialog.tsx';
import { ToastNotification } from './components/ToastNotification.tsx';
import { PlusCircle, ChevronUp, ChevronDown, Sparkles, Filter } from 'lucide-react';

const DEFAULT_FILTER_STATE: FilterState = {
  search: '',
  category: 'ALL',
  status: 'ALL',
  location: 'ALL',
  dateFrom: '',
  dateTo: '',
};

export default function App() {
  // --- Persistent Storage State ---
  const [allRecords, setAllRecords] = useState<BaseRecord[]>(() => loadStoredRecords());

  // Save to localStorage whenever allRecords changes
  useEffect(() => {
    saveStoredRecords(allRecords);
  }, [allRecords]);

  // --- Tab Navigation State ---
  const [activePrimaryTab, setActivePrimaryTab] = useState<PrimaryTabId>('intake');
  const [activeSubTab, setActiveSubTab] = useState<SubTabId>('quality');

  // --- Sub-Tab Form Collapse State ---
  const [showSubTabForm, setShowSubTabForm] = useState<boolean>(true);

  // --- Edit Mode & Active Record State ---
  const [editingRecord, setEditingRecord] = useState<BaseRecord | null>(null);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  // --- Independent Filter States ---
  const [filtersTab1, setFiltersTab1] = useState<FilterState>({ ...DEFAULT_FILTER_STATE });
  const [filtersQuality, setFiltersQuality] = useState<FilterState>({ ...DEFAULT_FILTER_STATE });
  const [filtersLogistics, setFiltersLogistics] = useState<FilterState>({ ...DEFAULT_FILTER_STATE });

  // --- Independent Sorting & Pagination States ---
  const [sortConfigTab1, setSortConfigTab1] = useState<SortConfig>({ field: 'date', direction: 'desc' });
  const [sortConfigQuality, setSortConfigQuality] = useState<SortConfig>({ field: 'date', direction: 'desc' });
  const [sortConfigLogistics, setSortConfigLogistics] = useState<SortConfig>({ field: 'date', direction: 'desc' });

  const [pageTab1, setPageTab1] = useState<number>(1);
  const [pageSizeTab1, setPageSizeTab1] = useState<number>(5);

  const [pageQuality, setPageQuality] = useState<number>(1);
  const [pageSizeQuality, setPageSizeQuality] = useState<number>(5);

  const [pageLogistics, setPageLogistics] = useState<number>(1);
  const [pageSizeLogistics, setPageSizeLogistics] = useState<number>(5);

  // --- Toast & Confirmation States ---
  const [toasts, setToasts] = useState<ToastMessage[]>([]);
  const [deleteConfirmTarget, setDeleteConfirmTarget] = useState<BaseRecord | null>(null);
  const [showResetConfirm, setShowResetConfirm] = useState<boolean>(false);
  const [showWireframeModal, setShowWireframeModal] = useState<boolean>(false);

  const addToast = useCallback((type: ToastMessage['type'], message: string, title?: string) => {
    const newToast: ToastMessage = {
      id: `toast-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
      type,
      message,
      title,
      timestamp: Date.now(),
    };
    setToasts((prev) => [...prev, newToast]);
    // Auto dismiss after 4 seconds
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== newToast.id));
    }, 4500);
  }, []);

  const dismissToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  // --- Data Partitioning per Tab ---
  const tab1Records = useMemo(
    () => allRecords.filter((r) => r.primaryTabId === 'intake'),
    [allRecords]
  );

  const totalLitersIntake = useMemo(
    () => tab1Records.reduce((sum, r) => sum + (Number(r.liters) || 0), 0),
    [tab1Records]
  );

  const qualityRecords = useMemo(
    () => allRecords.filter((r) => r.primaryTabId === 'operations' && r.subTabId === 'quality'),
    [allRecords]
  );

  const logisticsRecords = useMemo(
    () => allRecords.filter((r) => r.primaryTabId === 'operations' && r.subTabId === 'logistics'),
    [allRecords]
  );

  // Counts for tabs
  const tabCounts = useMemo<Record<PrimaryTabId, number>>(
    () => ({
      intake: tab1Records.length,
      operations: qualityRecords.length + logisticsRecords.length,
    }),
    [tab1Records.length, qualityRecords.length, logisticsRecords.length]
  );

  const subTabCounts = useMemo<Record<SubTabId, number>>(
    () => ({
      quality: qualityRecords.length,
      logistics: logisticsRecords.length,
    }),
    [qualityRecords.length, logisticsRecords.length]
  );

  // --- Dynamic Category & Status Options for Filters ---
  const tab1Categories = useMemo(
    () => Array.from(new Set(tab1Records.map((r) => r.category))).filter(Boolean),
    [tab1Records]
  );
  const tab1Statuses = useMemo(
    () => Array.from(new Set(tab1Records.map((r) => r.status))).filter(Boolean),
    [tab1Records]
  );

  const qualityCategories = useMemo(
    () => Array.from(new Set(qualityRecords.map((r) => r.category))).filter(Boolean),
    [qualityRecords]
  );
  const qualityStatuses = useMemo(
    () => Array.from(new Set(qualityRecords.map((r) => r.status))).filter(Boolean),
    [qualityRecords]
  );

  const logisticsCategories = useMemo(
    () => Array.from(new Set(logisticsRecords.map((r) => r.category))).filter(Boolean),
    [logisticsRecords]
  );
  const logisticsStatuses = useMemo(
    () => Array.from(new Set(logisticsRecords.map((r) => r.status))).filter(Boolean),
    [logisticsRecords]
  );

  // --- Active View Calculations ---
  // Determine current active filter and sort objects
  const currentFilters =
    activePrimaryTab === 'intake'
      ? filtersTab1
      : activeSubTab === 'quality'
      ? filtersQuality
      : filtersLogistics;

  const currentRecordsPool =
    activePrimaryTab === 'intake'
      ? tab1Records
      : activeSubTab === 'quality'
      ? qualityRecords
      : logisticsRecords;

  const currentSortConfig =
    activePrimaryTab === 'intake'
      ? sortConfigTab1
      : activeSubTab === 'quality'
      ? sortConfigQuality
      : sortConfigLogistics;

  const currentPage =
    activePrimaryTab === 'intake'
      ? pageTab1
      : activeSubTab === 'quality'
      ? pageQuality
      : pageLogistics;

  const currentPageSize =
    activePrimaryTab === 'intake'
      ? pageSizeTab1
      : activeSubTab === 'quality'
      ? pageSizeQuality
      : pageSizeLogistics;

  // Filter & Sort Pipeline
  const filteredRecords = useMemo(
    () => filterRecords(currentRecordsPool, currentFilters),
    [currentRecordsPool, currentFilters]
  );

  const sortedRecords = useMemo(
    () => sortRecords(filteredRecords, currentSortConfig),
    [filteredRecords, currentSortConfig]
  );

  const paginationInfo = useMemo(
    () => paginateRecords(sortedRecords, currentPage, currentPageSize),
    [sortedRecords, currentPage, currentPageSize]
  );

  // --- Handlers for Filter Updates ---
  const handleFilterChange = (newFilters: FilterState) => {
    if (activePrimaryTab === 'intake') {
      setFiltersTab1(newFilters);
      setPageTab1(1);
    } else if (activeSubTab === 'quality') {
      setFiltersQuality(newFilters);
      setPageQuality(1);
    } else {
      setFiltersLogistics(newFilters);
      setPageLogistics(1);
    }
  };

  const handleClearFilters = () => {
    handleFilterChange({ ...DEFAULT_FILTER_STATE });
  };

  // --- Handlers for Sorting ---
  const handleSort = (columnKey: string) => {
    const updateSort = (current: SortConfig, setSort: (sc: SortConfig) => void) => {
      if (current.field === columnKey) {
        setSort({
          field: columnKey,
          direction: current.direction === 'asc' ? 'desc' : 'asc',
        });
      } else {
        setSort({
          field: columnKey,
          direction: 'asc',
        });
      }
    };

    if (activePrimaryTab === 'intake') {
      updateSort(sortConfigTab1, setSortConfigTab1);
    } else if (activeSubTab === 'quality') {
      updateSort(sortConfigQuality, setSortConfigQuality);
    } else {
      updateSort(sortConfigLogistics, setSortConfigLogistics);
    }
  };

  // --- Handlers for Pagination ---
  const handlePageChange = (page: number) => {
    if (activePrimaryTab === 'intake') setPageTab1(page);
    else if (activeSubTab === 'quality') setPageQuality(page);
    else setPageLogistics(page);
  };

  const handlePageSizeChange = (size: number) => {
    if (activePrimaryTab === 'intake') {
      setPageSizeTab1(size);
      setPageTab1(1);
    } else if (activeSubTab === 'quality') {
      setPageSizeQuality(size);
      setPageQuality(1);
    } else {
      setPageSizeLogistics(size);
      setPageLogistics(1);
    }
  };

  // Switch Primary Tab
  const handlePrimaryTabChange = (tabId: PrimaryTabId) => {
    setActivePrimaryTab(tabId);
    setEditingRecord(null); // Cancel any ongoing edit when switching tabs
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Switch Sub-Tab
  const handleSubTabChange = (subTabId: SubTabId) => {
    setActiveSubTab(subTabId);
    setEditingRecord(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // --- Form Submission (Create / Update) ---
  const handleFormSubmit = async (values: Record<string, any>): Promise<boolean> => {
    setIsSubmitting(true);
    // Simulate brief processing delay for realistic enterprise feel
    await new Promise((resolve) => setTimeout(resolve, 300));

    try {
      const nowIso = new Date().toISOString();

      if (editingRecord) {
        // Update existing record
        const updatedRecord: BaseRecord = {
          ...editingRecord,
          ...values,
          id: editingRecord.id, // Guarantee ID cannot be mutated
          primaryTabId: editingRecord.primaryTabId,
          subTabId: editingRecord.subTabId,
          updatedAt: nowIso,
        };

        setAllRecords((prev) =>
          prev.map((r) => (r.id === editingRecord.id ? updatedRecord : r))
        );

        setEditingRecord(null);
        addToast(
          'success',
          `Record ${updatedRecord.id} successfully updated with latest parameters.`,
          'Record Updated'
        );
      } else {
        // Create new record with unique ID
        const prefix =
          activePrimaryTab === 'intake'
            ? 'RMI'
            : activeSubTab === 'quality'
            ? 'QLT'
            : 'LOG';
        const randomNum = Math.floor(1000 + Math.random() * 9000);
        const newId = `${prefix}-2026-${randomNum}`;

        const newRecord: BaseRecord = {
          ...values,
          id: newId,
          primaryTabId: activePrimaryTab,
          subTabId: activePrimaryTab === 'operations' ? activeSubTab : undefined,
          createdAt: nowIso,
          updatedAt: nowIso,
        } as BaseRecord;

        setAllRecords((prev) => [newRecord, ...prev]);

        addToast(
          'success',
          `New batch ${newId} recorded into ${
            activePrimaryTab === 'intake'
              ? 'Raw Milk Reception'
              : activeSubTab === 'quality'
              ? 'Quality Control QA'
              : 'Logistics Fleet Dispatch'
          }.`,
          'Entry Created'
        );
      }
      setIsSubmitting(false);
      return true;
    } catch (err) {
      console.error('Error submitting form:', err);
      addToast('error', 'Failed to save record. Please check inputs and try again.', 'Error');
      setIsSubmitting(false);
      return false;
    }
  };

  // --- Row Action Handlers ---
  const handleEditRecord = (record: BaseRecord) => {
    setEditingRecord(record);
    setShowSubTabForm(true); // Ensure form is expanded if in Sub-tab
    // Smooth scroll to form
    const formEl = document.getElementById('dynamic-form-card');
    formEl?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  };

  const handleCancelEdit = () => {
    setEditingRecord(null);
  };

  const handleDeleteRequest = (record: BaseRecord) => {
    setDeleteConfirmTarget(record);
  };

  const handleConfirmDelete = () => {
    if (!deleteConfirmTarget) return;
    const targetId = deleteConfirmTarget.id;

    setAllRecords((prev) => prev.filter((r) => r.id !== targetId));

    if (editingRecord?.id === targetId) {
      setEditingRecord(null);
    }

    addToast('info', `Record ${targetId} was permanently removed.`, 'Record Deleted');
    setDeleteConfirmTarget(null);
  };

  // --- Export CSV Handler ---
  const handleExportCsv = () => {
    if (sortedRecords.length === 0) {
      addToast('warning', 'No records to export in the current view.', 'Export Empty');
      return;
    }

    const headers = Object.keys(sortedRecords[0]);
    const csvRows: string[] = [];
    csvRows.push(headers.join(','));

    for (const row of sortedRecords) {
      const values = headers.map((header) => {
        const val = row[header];
        const escaped = ('' + (val ?? '')).replace(/"/g, '""');
        return `"${escaped}"`;
      });
      csvRows.push(values.join(','));
    }

    const csvBlob = new Blob([csvRows.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(csvBlob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute(
      'download',
      `LactaFlow_${activePrimaryTab}_${activePrimaryTab === 'operations' ? activeSubTab : 'intake'}_${
        new Date().toISOString().slice(0, 10)
      }.csv`
    );
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    addToast('success', `Exported ${sortedRecords.length} records to CSV.`, 'Export Completed');
  };

  // --- Reset Sample Data ---
  const handleResetSampleData = () => {
    const refreshed = resetToSeedData();
    setAllRecords(refreshed);
    setEditingRecord(null);
    setShowResetConfirm(false);
    addToast('info', 'Factory sample data restored for all tabs.', 'Data Reset');
  };

  // --- Active Form Schema Determination ---
  const activeFormSchema = useMemo(() => {
    if (activePrimaryTab === 'intake') {
      return INTAKE_FORM_SCHEMA;
    }
    if (activeSubTab === 'quality') {
      return QUALITY_FORM_SCHEMA;
    }
    return LOGISTICS_FORM_SCHEMA;
  }, [activePrimaryTab, activeSubTab]);

  // --- Table Column Definitions for Each Tab/Sub-Tab ---
  const intakeColumns: TableColumn[] = [
    { key: 'id', label: 'Record ID', sortable: true, width: '130px' },
    { key: 'name', label: 'Dairy Farm / Supplier', sortable: true },
    { key: 'phone', label: 'Contact Phone', sortable: false },
    { key: 'location', label: 'Farm Origin', sortable: true },
    { key: 'category', label: 'Milk Category', sortable: true },
    {
      key: 'liters',
      label: 'Volume (L)',
      sortable: true,
      align: 'right',
      render: (val) => (
        <span className="font-mono font-bold text-slate-900">
          {Number(val).toLocaleString()} L
        </span>
      ),
    },
    {
      key: 'fatPercentage',
      label: 'Fat %',
      sortable: true,
      align: 'right',
      render: (val) => (
        <span className="font-mono font-semibold text-amber-900 bg-amber-50 px-1.5 py-0.5 rounded border border-amber-200/60">
          {val}%
        </span>
      ),
    },
    {
      key: 'temperature',
      label: 'Chilled Temp',
      sortable: true,
      align: 'right',
      render: (val) => (
        <span
          className={`font-mono text-xs font-semibold px-1.5 py-0.5 rounded border ${
            val > 4.5
              ? 'bg-rose-50 text-rose-800 border-rose-200'
              : 'bg-cyan-50 text-cyan-800 border-cyan-200'
          }`}
        >
          {val}°C
        </span>
      ),
    },
    { key: 'siloId', label: 'Assigned Silo', sortable: true },
    { key: 'status', label: 'Intake Status', sortable: true },
    { key: 'date', label: 'Received Time', sortable: true },
  ];

  const qualityColumns: TableColumn[] = [
    { key: 'id', label: 'QA Test ID', sortable: true, width: '130px' },
    { key: 'name', label: 'Lead Chemist / Inspector', sortable: true },
    { key: 'location', label: 'Testing Station', sortable: true },
    { key: 'category', label: 'Product Batch', sortable: true },
    {
      key: 'phLevel',
      label: 'pH Level',
      sortable: true,
      align: 'right',
      render: (val) => (
        <span
          className={`font-mono font-bold text-xs px-1.5 py-0.5 rounded border ${
            val < 6.5 || val > 6.9
              ? 'bg-amber-50 text-amber-800 border-amber-200'
              : 'bg-emerald-50 text-emerald-800 border-emerald-200'
          }`}
        >
          {val} pH
        </span>
      ),
    },
    {
      key: 'somaticCount',
      label: 'Somatic Cells',
      sortable: true,
      align: 'right',
      render: (val) => (
        <span className="font-mono text-xs text-slate-700">
          {Number(val).toLocaleString()} CFU/ml
        </span>
      ),
    },
    {
      key: 'antibioticResidue',
      label: 'Antibiotic Assay',
      sortable: true,
      render: (val) => (
        <span
          className={`text-[11px] font-semibold px-2 py-0.5 rounded border ${
            val === 'Negative'
              ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
              : 'bg-rose-50 text-rose-800 border-rose-200'
          }`}
        >
          {val}
        </span>
      ),
    },
    {
      key: 'pasteurTemp',
      label: 'HTST Temp',
      sortable: true,
      align: 'right',
      render: (val) => <span className="font-mono text-xs">{val}°C</span>,
    },
    { key: 'status', label: 'QA Verdict', sortable: true },
    { key: 'date', label: 'Assay Date', sortable: true },
  ];

  const logisticsColumns: TableColumn[] = [
    { key: 'id', label: 'Dispatch ID', sortable: true, width: '130px' },
    { key: 'name', label: 'Driver / Dispatch Lead', sortable: true },
    { key: 'tankerId', label: 'Fleet Unit', sortable: true },
    { key: 'location', label: 'Destination Hub', sortable: true },
    { key: 'category', label: 'Dispatched Line', sortable: true },
    {
      key: 'quantity',
      label: 'Quantity (Units)',
      sortable: true,
      align: 'right',
      render: (val) => (
        <span className="font-mono font-bold text-slate-900">
          {Number(val).toLocaleString()}
        </span>
      ),
    },
    {
      key: 'cargoTemp',
      label: 'Cargo Temp',
      sortable: true,
      align: 'right',
      render: (val) => (
        <span
          className={`font-mono text-xs px-1.5 py-0.5 rounded border ${
            val > 4.5
              ? 'bg-rose-50 text-rose-800 border-rose-200'
              : 'bg-sky-50 text-sky-800 border-sky-200'
          }`}
        >
          {val}°C
        </span>
      ),
    },
    { key: 'sealNumber', label: 'Seal Barcode', sortable: false },
    { key: 'status', label: 'Transit Status', sortable: true },
    { key: 'date', label: 'Departure Time', sortable: true },
  ];

  const currentColumns =
    activePrimaryTab === 'intake'
      ? intakeColumns
      : activeSubTab === 'quality'
      ? qualityColumns
      : logisticsColumns;

  return (
    <div className="dairy-milk-bg min-h-screen flex flex-col font-sans selection:bg-sky-100 selection:text-sky-900 relative overflow-x-hidden">
      {/* Decorative ambient liquid milk background layers */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
        {/* Soft milky glow orbs */}
        <div className="absolute -top-32 -left-32 w-96 h-96 rounded-full bg-sky-200/40 blur-3xl animate-milk-flow" />
        <div className="absolute top-1/3 -right-32 w-[30rem] h-[30rem] rounded-full bg-amber-100/40 blur-3xl animate-milk-flow" style={{ animationDelay: '-6s' }} />
        <div className="absolute -bottom-32 left-1/4 w-[36rem] h-[36rem] rounded-full bg-cyan-100/40 blur-3xl animate-milk-flow" style={{ animationDelay: '-12s' }} />

        {/* Ambient SVG Milk Wave ribbon */}
        <svg
          className="absolute top-24 left-0 w-full h-48 opacity-30 text-sky-100"
          preserveAspectRatio="none"
          viewBox="0 0 1440 120"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M0 30C240 70 480 0 720 40C960 80 1200 10 1440 50V0H0V30Z"
            fill="currentColor"
          />
        </svg>

        <svg
          className="absolute bottom-0 left-0 w-full h-40 opacity-40 text-blue-50"
          preserveAspectRatio="none"
          viewBox="0 0 1440 100"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M0 60C360 10 720 90 1080 30C1260 0 1380 40 1440 50V100H0V60Z"
            fill="currentColor"
          />
        </svg>
      </div>

      {/* 1. Application Header with Translucent Frosted Glass */}
      <PageHeader
        title="LactaFlow Enterprise Dairy OS"
        subtitle="Multi-Tab Milk Intake Reception, Laboratory QA Analysis & Cold-Chain Logistics Hub"
        facilityName="Silo Plant Delta-01 (Wisconsin Central)"
        onExportCsv={handleExportCsv}
        onResetData={() => setShowResetConfirm(true)}
        onOpenWireframe={() => setShowWireframeModal(true)}
        totalBatchesToday={allRecords.length}
        totalLitersIntake={totalLitersIntake}
      />

      {/* 2. Fixed / Sticky Primary Tab Navigation */}
      <PrimaryTabs
        tabs={PRIMARY_TABS}
        activeTab={activePrimaryTab}
        onTabChange={handlePrimaryTabChange}
        tabCounts={tabCounts}
      />

      {/* Main Page Content Body with z-10 for clean layering over milk waves */}
      <main className="relative z-10 flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* TAB 1: FORM AND COMPLETE DATA TABLE */}
        {activePrimaryTab === 'intake' && (
          <div
            id="primary-panel-intake"
            role="tabpanel"
            aria-labelledby="primary-tab-intake"
            className="space-y-6 animate-fadeIn"
          >
            {/* 3A. Form Section */}
            <section aria-labelledby="form-heading">
              <DynamicForm
                schema={INTAKE_FORM_SCHEMA}
                initialValues={editingRecord}
                isEditMode={!!editingRecord}
                onSubmit={handleFormSubmit}
                onCancelEdit={handleCancelEdit}
                isSubmitting={isSubmitting}
              />
            </section>

            {/* Quick Filter Section for Tab 1 */}
            <section aria-labelledby="filter-heading">
              <FilterToolbar
                filters={filtersTab1}
                onFilterChange={handleFilterChange}
                categories={tab1Categories}
                statuses={tab1Statuses}
                totalResults={filteredRecords.length}
                unfilteredCount={tab1Records.length}
              />
            </section>

            {/* 3C. Data Table for Tab 1 */}
            <section aria-labelledby="datatable-heading">
              <DataTable
                columns={currentColumns}
                records={paginationInfo.items}
                allRecordsCount={filteredRecords.length}
                sortConfig={sortConfigTab1}
                onSort={handleSort}
                currentPage={paginationInfo.currentPage}
                pageSize={pageSizeTab1}
                totalPages={paginationInfo.totalPages}
                startIndex={paginationInfo.startIndex}
                endIndex={paginationInfo.endIndex}
                onPageChange={handlePageChange}
                onPageSizeChange={handlePageSizeChange}
                onEdit={handleEditRecord}
                onDelete={handleDeleteRequest}
                onClearFilters={handleClearFilters}
              />
            </section>
          </div>
        )}

        {/* TAB 2: SUB-TABS, FILTERS AND DATA TABLE */}
        {activePrimaryTab === 'operations' && (
          <div
            id="primary-panel-operations"
            role="tabpanel"
            aria-labelledby="primary-tab-operations"
            className="space-y-6 animate-fadeIn"
          >
            {/* 4A. Secondary Tab Navigation */}
            <section aria-label="Secondary modules">
              <SecondaryTabs
                subTabs={SECONDARY_TABS}
                activeSubTab={activeSubTab}
                onSubTabChange={handleSubTabChange}
                subTabCounts={subTabCounts}
              />
            </section>

            {/* 4B. Sub-Tab Specific Form (Collapsible / Toggleable) */}
            <section aria-label="Sub-tab data entry form">
              <div className="flex items-center justify-between mb-2 px-1">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                  {activeSubTab === 'quality'
                    ? 'Lab Quality Inspection Form'
                    : 'Refrigerated Outbound Dispatch Form'}
                </span>
                <button
                  type="button"
                  onClick={() => setShowSubTabForm(!showSubTabForm)}
                  className="inline-flex items-center gap-1.5 text-xs font-semibold text-sky-700 hover:text-sky-800 bg-sky-50 hover:bg-sky-100/80 px-2.5 py-1 rounded-md transition cursor-pointer"
                >
                  {showSubTabForm ? (
                    <>
                      <ChevronUp className="w-3.5 h-3.5" />
                      Hide Form
                    </>
                  ) : (
                    <>
                      <PlusCircle className="w-3.5 h-3.5" />
                      Add New {activeSubTab === 'quality' ? 'QA Record' : 'Dispatch Record'}
                    </>
                  )}
                </button>
              </div>

              {showSubTabForm && (
                <DynamicForm
                  schema={activeFormSchema}
                  initialValues={editingRecord}
                  isEditMode={!!editingRecord}
                  onSubmit={handleFormSubmit}
                  onCancelEdit={handleCancelEdit}
                  isSubmitting={isSubmitting}
                />
              )}
            </section>

            {/* 4C. Filter Section (Placed right between Sub-tabs/form and Data Table per sketch layout) */}
            <section aria-label="Sub-tab records filter toolbar">
              <FilterToolbar
                filters={activeSubTab === 'quality' ? filtersQuality : filtersLogistics}
                onFilterChange={handleFilterChange}
                categories={activeSubTab === 'quality' ? qualityCategories : logisticsCategories}
                statuses={activeSubTab === 'quality' ? qualityStatuses : logisticsStatuses}
                totalResults={filteredRecords.length}
                unfilteredCount={currentRecordsPool.length}
              />
            </section>

            {/* 4D. Data Table for Tab 2 */}
            <section aria-label="Filtered sub-tab data table">
              <DataTable
                columns={currentColumns}
                records={paginationInfo.items}
                allRecordsCount={filteredRecords.length}
                sortConfig={activeSubTab === 'quality' ? sortConfigQuality : sortConfigLogistics}
                onSort={handleSort}
                currentPage={paginationInfo.currentPage}
                pageSize={currentPageSize}
                totalPages={paginationInfo.totalPages}
                startIndex={paginationInfo.startIndex}
                endIndex={paginationInfo.endIndex}
                onPageChange={handlePageChange}
                onPageSizeChange={handlePageSizeChange}
                onEdit={handleEditRecord}
                onDelete={handleDeleteRequest}
                onClearFilters={handleClearFilters}
              />
            </section>
          </div>
        )}
      </main>

      {/* Wireframe & Figma Blueprint Modal */}
      {showWireframeModal && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="wireframe-modal-title"
          className="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-md flex items-center justify-center p-3 sm:p-6 animate-fadeIn"
          onClick={() => setShowWireframeModal(false)}
        >
          <div
            className="bg-white rounded-2xl shadow-2xl max-w-5xl w-full max-h-[92vh] flex flex-col overflow-hidden border border-slate-200"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Top Bar */}
            <div className="px-6 py-4 bg-slate-900 text-white flex flex-wrap items-center justify-between gap-3 border-b border-slate-800">
              <div className="flex items-center gap-3">
                <span className="p-2 bg-sky-600 rounded-lg text-lg">🥛</span>
                <div>
                  <h3 id="wireframe-modal-title" className="text-base font-bold text-white flex items-center gap-2">
                    <span>LactaFlow UI Wireframe &amp; Figma Vector Blueprint</span>
                    <span className="text-[10px] font-extrabold uppercase px-2 py-0.5 bg-sky-950 text-sky-300 border border-sky-800 rounded">
                      Figma Compatible
                    </span>
                  </h3>
                  <p className="text-xs text-slate-400">
                    Dual-screen wireframe specifications, 4-column responsive grid, and design tokens
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2.5">
                <a
                  href="/wireframe.svg"
                  download="lactaflow-dairy-wireframe.svg"
                  className="inline-flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-bold text-white bg-sky-600 hover:bg-sky-500 rounded-lg transition shadow-xs"
                >
                  <span>⬇️ Download Figma SVG</span>
                </a>

                <a
                  href="/figma-design-tokens.json"
                  download="figma-design-tokens.json"
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-300 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg transition"
                >
                  <span>🎨 Design Tokens (.JSON)</span>
                </a>

                <button
                  type="button"
                  onClick={() => setShowWireframeModal(false)}
                  className="p-1.5 text-slate-400 hover:text-white rounded-lg cursor-pointer"
                  aria-label="Close modal"
                >
                  ✕
                </button>
              </div>
            </div>

            {/* Figma Drag-and-Drop Instruction Tip */}
            <div className="bg-sky-50 px-6 py-2.5 border-b border-sky-100 flex items-center gap-2 text-xs text-sky-900">
              <span className="font-bold">💡 How to edit in Figma:</span>
              <span>Click <strong>"Download Figma SVG"</strong> &rarr; drag and drop the downloaded <code>.svg</code> file straight into your Figma canvas to get fully editable vectors, text frames, and layers!</span>
            </div>

            {/* Scrollable SVG Canvas Preview */}
            <div className="flex-1 overflow-auto p-4 bg-slate-100/80 flex justify-center">
              <div className="bg-white rounded-xl shadow-md border border-slate-300 overflow-hidden max-w-4xl w-full">
                <img
                  src="/wireframe.svg"
                  alt="LactaFlow Enterprise Dairy OS UI Wireframe Blueprint"
                  className="w-full h-auto block select-none"
                />
              </div>
            </div>

            {/* Modal Footer */}
            <div className="px-6 py-3 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-xs text-slate-500">
              <span>Resolution: 1600 × 2200 px &bull; Responsive 4-Column Grid &bull; Dual-Tab Layout</span>
              <button
                type="button"
                onClick={() => setShowWireframeModal(false)}
                className="px-4 py-1.5 text-xs font-semibold text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-100 transition cursor-pointer"
              >
                Close Blueprint
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Confirmation Dialog for Record Deletion */}
      <ConfirmationDialog
        isOpen={!!deleteConfirmTarget}
        title="Confirm Record Deletion"
        message={
          deleteConfirmTarget
            ? `Are you sure you want to permanently delete record ${deleteConfirmTarget.id} (${deleteConfirmTarget.name})? This action cannot be undone.`
            : ''
        }
        confirmLabel="Yes, Delete Record"
        cancelLabel="Keep Record"
        variant="danger"
        onConfirm={handleConfirmDelete}
        onCancel={() => setDeleteConfirmTarget(null)}
      />

      {/* Confirmation Dialog for Factory Sample Data Reset */}
      <ConfirmationDialog
        isOpen={showResetConfirm}
        title="Restore Factory Sample Data?"
        message="This will reset all milk reception batches, quality control records, and cold-chain manifests back to the default demonstration seed data. Any customized entries will be replaced."
        confirmLabel="Yes, Reset All Data"
        cancelLabel="Cancel"
        variant="warning"
        onConfirm={handleResetSampleData}
        onCancel={() => setShowResetConfirm(false)}
      />

      {/* Toast Notification Container */}
      <ToastNotification toasts={toasts} onDismiss={dismissToast} />
    </div>
  );
}
