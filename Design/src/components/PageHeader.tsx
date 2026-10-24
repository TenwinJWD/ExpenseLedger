/**
 * LactaFlow Enterprise PageHeader Component
 * Luminous dairy milk aesthetic with transparent frosted-glass styling,
 * live plant telemetry, facility status indicators, and operational KPIs.
 */

import React from 'react';
import { Milk, Download, RefreshCw, Activity, MapPin, ThermometerSnowflake, CheckCircle2, ShieldCheck, Droplets, FileCode, LayoutTemplate } from 'lucide-react';

interface PageHeaderProps {
  title?: string;
  subtitle?: string;
  facilityName?: string;
  onExportCsv: () => void;
  onResetData: () => void;
  onOpenWireframe?: () => void;
  totalBatchesToday: number;
  totalLitersIntake?: number;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  title = 'LactaFlow Enterprise Dairy OS',
  subtitle = 'Multi-Tab Milk Intake Reception, Laboratory QA Analysis & Cold-Chain Logistics Hub',
  facilityName = 'Silo Plant Delta-01 (Wisconsin Central)',
  onExportCsv,
  onResetData,
  totalBatchesToday,
  totalLitersIntake = 48500,
}) => {
  return (
    <header className="frosted-glass-header sticky top-0 z-40 transition-all">
      {/* Top micro-bar for breadcrumbs & real-time telemetry */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2 flex flex-wrap items-center justify-between gap-3 text-xs border-b border-sky-100/70 text-slate-600">
        <nav aria-label="Breadcrumb" className="flex items-center gap-1.5 font-medium">
          <span className="text-slate-400">Dairy Operations</span>
          <span className="text-slate-300">/</span>
          <span className="text-slate-500">Intake & Logistics Portal</span>
          <span className="text-slate-300">/</span>
          <span className="text-sky-700 font-bold flex items-center gap-1 bg-sky-50 px-2 py-0.5 rounded-md border border-sky-200/60">
            <MapPin className="w-3 h-3 text-sky-600" />
            {facilityName}
          </span>
        </nav>

        <div className="flex items-center gap-3.5">
          <div className="flex items-center gap-1 text-[11px] font-semibold text-sky-800 bg-sky-50 px-2 py-0.5 rounded-full border border-sky-200/70">
            <ThermometerSnowflake className="w-3.5 h-3.5 text-sky-600" />
            <span>Silo Chilling: <strong>3.2°C</strong></span>
          </div>

          <div className="flex items-center gap-1 text-[11px] font-semibold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200/70">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            <span>HACCP Quality: Certified</span>
          </div>

          <div className="flex items-center gap-1 text-[11px] font-semibold text-amber-800 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-200/70 hidden sm:inline-flex">
            <Droplets className="w-3.5 h-3.5 text-amber-600" />
            <span>Avg Fat: <strong>4.1%</strong></span>
          </div>
        </div>
      </div>

      {/* Main Header Row */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4">
        {/* Brand & Title with Milk Splash Emblem */}
        <div className="flex items-center gap-3.5">
          <div className="relative group">
            <div className="w-11 h-11 rounded-2xl bg-gradient-to-tr from-sky-600 via-sky-500 to-cyan-400 flex items-center justify-center text-white shadow-md shadow-sky-600/25 border-2 border-white">
              <Milk className="w-6 h-6 drop-shadow-xs" />
            </div>
            <span className="absolute -bottom-1 -right-1 w-4 h-4 bg-emerald-500 border-2 border-white rounded-full flex items-center justify-center text-[8px] text-white font-bold" title="Operational">
              ✓
            </span>
          </div>

          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg sm:text-xl font-extrabold tracking-tight text-slate-900">
                {title}
              </h1>
              <span className="px-2 py-0.5 text-[10px] font-extrabold tracking-wider uppercase bg-gradient-to-r from-sky-100 to-blue-50 text-sky-800 border border-sky-200/80 rounded-md">
                Dairy Core v2.4
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5 font-medium">{subtitle}</p>
          </div>
        </div>

        {/* Header Telemetry Cards + Quick Actions */}
        <div className="flex items-center gap-3">
          {/* Live Batch Metric Pill */}
          <div className="hidden md:flex items-center gap-3 px-3 py-1.5 rounded-xl bg-white/70 border border-sky-100/90 shadow-2xs">
            <div className="text-left">
              <span className="text-[10px] uppercase font-bold text-slate-400 block tracking-wider">
                Logged Batches
              </span>
              <span className="text-sm font-extrabold text-sky-950 font-mono">
                {totalBatchesToday} Batches
              </span>
            </div>
            <div className="w-px h-6 bg-slate-200" />
            <div className="text-left">
              <span className="text-[10px] uppercase font-bold text-slate-400 block tracking-wider">
                Intake Volume
              </span>
              <span className="text-sm font-extrabold text-emerald-700 font-mono">
                {totalLitersIntake.toLocaleString()} L
              </span>
            </div>
          </div>

          {/* Action Buttons with Frosted Glass Styling */}
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={onOpenWireframe}
              title="View full architectural wireframe and export Figma vector assets"
              className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-bold text-sky-900 bg-sky-50 hover:bg-sky-100 active:bg-sky-200 border border-sky-300/80 rounded-xl transition shadow-xs hover:shadow-sm cursor-pointer"
            >
              <LayoutTemplate className="w-3.5 h-3.5 text-sky-600" />
              <span>Figma Wireframe</span>
            </button>

            <a
              href="/standalone-dairy-app.html"
              download="lactaflow-dairy-management.html"
              title="Download standalone HTML file to send or open anywhere without AI Studio"
              className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-bold text-emerald-900 bg-emerald-50 hover:bg-emerald-100 active:bg-emerald-200 border border-emerald-300/80 rounded-xl transition shadow-xs hover:shadow-sm cursor-pointer"
            >
              <FileCode className="w-3.5 h-3.5 text-emerald-600" />
              <span className="hidden sm:inline">Shareable</span> HTML
            </a>

            <button
              type="button"
              onClick={onExportCsv}
              title="Download active records as CSV"
              className="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-bold text-sky-900 bg-white/80 hover:bg-white active:bg-sky-50 border border-sky-200 rounded-xl transition shadow-xs hover:shadow-sm cursor-pointer"
            >
              <Download className="w-3.5 h-3.5 text-sky-600" />
              <span className="hidden sm:inline">Export</span> CSV
            </button>

            <button
              type="button"
              onClick={onResetData}
              title="Reset data back to factory demo records"
              className="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-bold text-slate-700 bg-white/60 hover:bg-white border border-slate-200 rounded-xl transition shadow-xs hover:shadow-sm cursor-pointer"
            >
              <RefreshCw className="w-3.5 h-3.5 text-slate-500" />
              <span className="hidden sm:inline">Reset</span> Demo Data
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
