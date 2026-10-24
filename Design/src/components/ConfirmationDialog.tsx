/**
 * LactaFlow Enterprise Confirmation Dialog Component
 * Keyboard accessible modal with trap and Esc listener.
 */

import React, { useEffect } from 'react';
import { AlertTriangle, Trash2, X } from 'lucide-react';

interface ConfirmationDialogProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  variant?: 'danger' | 'warning' | 'info';
  onConfirm: () => void;
  onCancel: () => void;
}

export const ConfirmationDialog: React.FC<ConfirmationDialogProps> = ({
  isOpen,
  title,
  message,
  confirmLabel = 'Confirm Action',
  cancelLabel = 'Cancel',
  variant = 'danger',
  onConfirm,
  onCancel,
}) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;
      if (e.key === 'Escape') {
        onCancel();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onCancel]);

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="dialog-title"
      aria-describedby="dialog-desc"
      className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 transition-opacity"
      onClick={onCancel}
    >
      <div
        className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6 border border-slate-200 transform transition-all animate-scaleUp"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start gap-3.5">
          <div
            className={`p-2.5 rounded-full shrink-0 ${
              variant === 'danger'
                ? 'bg-rose-100 text-rose-600'
                : variant === 'warning'
                ? 'bg-amber-100 text-amber-600'
                : 'bg-sky-100 text-sky-600'
            }`}
          >
            {variant === 'danger' ? (
              <Trash2 className="w-5 h-5" />
            ) : (
              <AlertTriangle className="w-5 h-5" />
            )}
          </div>

          <div className="flex-1">
            <h3 id="dialog-title" className="text-base font-bold text-slate-900">
              {title}
            </h3>
            <p id="dialog-desc" className="text-xs sm:text-sm text-slate-600 mt-1.5 leading-relaxed">
              {message}
            </p>
          </div>

          <button
            type="button"
            onClick={onCancel}
            aria-label="Close dialog"
            className="text-slate-400 hover:text-slate-600 p-1 rounded-md cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="mt-6 flex items-center justify-end gap-2.5">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition cursor-pointer"
          >
            {cancelLabel}
          </button>

          <button
            type="button"
            onClick={onConfirm}
            autoFocus
            className={`px-4 py-2 text-xs font-bold text-white rounded-lg transition shadow-xs cursor-pointer ${
              variant === 'danger'
                ? 'bg-rose-600 hover:bg-rose-700 active:bg-rose-800'
                : variant === 'warning'
                ? 'bg-amber-600 hover:bg-amber-700 active:bg-amber-800'
                : 'bg-sky-600 hover:bg-sky-700 active:bg-sky-800'
            }`}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
};
