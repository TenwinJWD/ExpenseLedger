/**
 * LactaFlow Enterprise ToastNotification Component
 */

import React from 'react';
import { ToastMessage } from '../types/dairy.ts';
import { CheckCircle2, AlertCircle, Info, AlertTriangle, X } from 'lucide-react';

interface ToastContainerProps {
  toasts: ToastMessage[];
  onDismiss: (id: string) => void;
}

export const ToastNotification: React.FC<ToastContainerProps> = ({ toasts, onDismiss }) => {
  if (toasts.length === 0) return null;

  const getIcon = (type: ToastMessage['type']) => {
    switch (type) {
      case 'success':
        return <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />;
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />;
      case 'info':
      default:
        return <Info className="w-4 h-4 text-sky-600 shrink-0" />;
    }
  };

  const getStyle = (type: ToastMessage['type']) => {
    switch (type) {
      case 'success':
        return 'border-emerald-200 bg-emerald-50 text-emerald-950';
      case 'error':
        return 'border-rose-200 bg-rose-50 text-rose-950';
      case 'warning':
        return 'border-amber-200 bg-amber-50 text-amber-950';
      case 'info':
      default:
        return 'border-sky-200 bg-sky-50 text-sky-950';
    }
  };

  return (
    <div
      aria-live="polite"
      aria-atomic="true"
      className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none"
    >
      {toasts.map((t) => (
        <div
          key={t.id}
          role="status"
          className={`pointer-events-auto p-3.5 rounded-xl border shadow-lg flex items-start gap-3 transition-all transform animate-slideIn ${getStyle(
            t.type
          )}`}
        >
          {getIcon(t.type)}
          <div className="flex-1 text-xs">
            {t.title && <p className="font-bold mb-0.5">{t.title}</p>}
            <p className="font-medium leading-relaxed">{t.message}</p>
          </div>
          <button
            type="button"
            onClick={() => onDismiss(t.id)}
            aria-label="Dismiss notification"
            className="text-slate-400 hover:text-slate-700 p-0.5 rounded cursor-pointer"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      ))}
    </div>
  );
};
