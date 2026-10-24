/**
 * LactaFlow Enterprise DynamicForm Component
 * Supports dynamic schema rendering, edit-mode banner, dirty state detection,
 * inline validation, duplicate submission locking, and reset/cancel controls.
 */

import React, { useState, useEffect } from 'react';
import { FormSchema, BaseRecord } from '../types/dairy.ts';
import { FormField } from './FormField.tsx';
import { validateRecord, validateField } from '../utils/validation.ts';
import { Check, RotateCcw, X, Edit3, Loader2, Sparkles, AlertTriangle } from 'lucide-react';

interface DynamicFormProps {
  schema: FormSchema;
  initialValues?: Partial<BaseRecord> | null;
  isEditMode?: boolean;
  onSubmit: (values: Record<string, any>) => Promise<boolean> | boolean;
  onCancelEdit?: () => void;
  onReset?: () => void;
  isSubmitting?: boolean;
}

export const DynamicForm: React.FC<DynamicFormProps> = ({
  schema,
  initialValues,
  isEditMode = false,
  onSubmit,
  onCancelEdit,
  onReset,
  isSubmitting = false,
}) => {
  const [formValues, setFormValues] = useState<Record<string, any>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const [isDirty, setIsDirty] = useState<boolean>(false);
  const [showDiscardPrompt, setShowDiscardPrompt] = useState<boolean>(false);

  // Initialize or reset form values whenever schema or initialValues change
  useEffect(() => {
    const defaultVals: Record<string, any> = {};
    for (const field of schema.fields) {
      if (initialValues && initialValues[field.name] !== undefined) {
        defaultVals[field.name] = initialValues[field.name];
      } else if (field.defaultValue !== undefined) {
        defaultVals[field.name] = field.defaultValue;
      } else if (field.type === 'datetime-local') {
        // Default to current local datetime string YYYY-MM-DDTHH:MM
        const now = new Date();
        now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
        defaultVals[field.name] = now.toISOString().slice(0, 16);
      } else if (field.type === 'number') {
        defaultVals[field.name] = '';
      } else {
        defaultVals[field.name] = '';
      }
    }
    setFormValues(defaultVals);
    setErrors({});
    setTouched({});
    setIsDirty(false);
  }, [schema, initialValues]);

  const handleFieldChange = (name: string, value: any) => {
    setIsDirty(true);
    setFormValues((prev) => {
      const updated = { ...prev, [name]: value };
      // Real-time validation for already touched field
      if (touched[name]) {
        const fieldDef = schema.fields.find((f) => f.name === name);
        if (fieldDef) {
          const fieldError = validateField(value, fieldDef, updated);
          setErrors((prevErr) => {
            const nextErr = { ...prevErr };
            if (fieldError) {
              nextErr[name] = fieldError;
            } else {
              delete nextErr[name];
            }
            return nextErr;
          });
        }
      }
      return updated;
    });
  };

  const handleFieldBlur = (name: string) => {
    setTouched((prev) => ({ ...prev, [name]: true }));
    const fieldDef = schema.fields.find((f) => f.name === name);
    if (fieldDef) {
      const fieldError = validateField(formValues[name], fieldDef, formValues);
      setErrors((prevErr) => {
        const nextErr = { ...prevErr };
        if (fieldError) {
          nextErr[name] = fieldError;
        } else {
          delete nextErr[name];
        }
        return nextErr;
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isSubmitting) return;

    // Validate all fields
    const validationErrors = validateRecord(formValues, schema.fields);
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      // Mark all fields with errors as touched
      const touchedAll: Record<string, boolean> = {};
      schema.fields.forEach((f) => {
        touchedAll[f.name] = true;
      });
      setTouched(touchedAll);

      // Scroll to the first error
      const firstErrorField = schema.fields.find((f) => validationErrors[f.name]);
      if (firstErrorField) {
        const el = document.getElementById(`field-${firstErrorField.name}`);
        el?.focus();
      }
      return;
    }

    // Call submit handler
    const success = await onSubmit(formValues);
    if (success && !isEditMode) {
      // Reset form if fresh creation
      handleReset();
    }
  };

  const handleReset = () => {
    const defaultVals: Record<string, any> = {};
    for (const field of schema.fields) {
      if (field.defaultValue !== undefined) {
        defaultVals[field.name] = field.defaultValue;
      } else if (field.type === 'datetime-local') {
        const now = new Date();
        now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
        defaultVals[field.name] = now.toISOString().slice(0, 16);
      } else {
        defaultVals[field.name] = '';
      }
    }
    setFormValues(defaultVals);
    setErrors({});
    setTouched({});
    setIsDirty(false);
    setShowDiscardPrompt(false);
    if (onReset) onReset();
  };

  const handleCancelClick = () => {
    if (isDirty) {
      setShowDiscardPrompt(true);
    } else {
      if (onCancelEdit) onCancelEdit();
    }
  };

  const confirmCancel = () => {
    setShowDiscardPrompt(false);
    setIsDirty(false);
    if (onCancelEdit) onCancelEdit();
  };

  return (
    <div
      id="dynamic-form-card"
      className="frosted-glass-card rounded-2xl overflow-hidden transition-all duration-200"
    >
      {/* Edit Mode Banner */}
      {isEditMode && (
        <div className="bg-sky-50 border-b border-sky-100 px-5 py-3 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <span className="p-1.5 bg-sky-100 text-sky-700 rounded-md">
              <Edit3 className="w-4 h-4" />
            </span>
            <div>
              <p className="text-sm font-semibold text-sky-950">
                Editing Record: <span className="font-mono text-sky-700 font-bold">{formValues.id || 'N/A'}</span>
              </p>
              <p className="text-xs text-sky-700">
                Modify any fields below and click "Update Record" to save changes.
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={handleCancelClick}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-600 bg-white border border-slate-300 rounded-md hover:bg-slate-50 hover:text-slate-800 transition shadow-2xs"
          >
            <X className="w-3.5 h-3.5" />
            Cancel Edit Mode
          </button>
        </div>
      )}

      {/* Card Header */}
      <div className="px-5 sm:px-6 py-4 border-b border-slate-100 flex flex-wrap items-center justify-between gap-3 bg-gradient-to-r from-slate-50/70 to-white">
        <div>
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <span>{schema.title}</span>
            {isEditMode ? (
              <span className="text-[11px] font-semibold tracking-wide uppercase px-2 py-0.5 bg-amber-100 text-amber-800 border border-amber-200 rounded">
                Edit Mode
              </span>
            ) : (
              <span className="text-[11px] font-semibold tracking-wide uppercase px-2 py-0.5 bg-emerald-100 text-emerald-800 border border-emerald-200 rounded">
                New Entry
              </span>
            )}
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">{schema.description}</p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[11px] text-slate-400 font-medium hidden sm:inline-block">
            Fields marked with <span className="text-rose-500 font-bold">*</span> are required
          </span>
        </div>
      </div>

      {/* Discard Confirmation Banner */}
      {showDiscardPrompt && (
        <div className="m-5 p-3.5 bg-amber-50 border border-amber-200 rounded-lg flex flex-wrap items-center justify-between gap-3 animate-fadeIn">
          <div className="flex items-center gap-2 text-xs font-semibold text-amber-900">
            <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
            <span>You have unsaved changes. Discard changes and exit?</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={confirmCancel}
              className="px-3 py-1 text-xs font-semibold text-white bg-rose-600 hover:bg-rose-700 rounded-md transition"
            >
              Yes, Discard
            </button>
            <button
              type="button"
              onClick={() => setShowDiscardPrompt(false)}
              className="px-3 py-1 text-xs font-semibold text-slate-700 bg-white border border-slate-300 rounded-md hover:bg-slate-50 transition"
            >
              Continue Editing
            </button>
          </div>
        </div>
      )}

      {/* Form Grid */}
      <form onSubmit={handleSubmit} noValidate className="p-5 sm:p-6 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-5">
          {schema.fields.map((field) => (
            <FormField
              key={field.name}
              field={field}
              value={formValues[field.name]}
              error={touched[field.name] ? errors[field.name] : undefined}
              onChange={handleFieldChange}
              onBlur={handleFieldBlur}
              disabled={isSubmitting}
            />
          ))}
        </div>

        {/* Global Error Notice if validation failed */}
        {Object.keys(errors).length > 0 && Object.keys(touched).length > 0 && (
          <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg flex items-center gap-2.5 text-xs text-rose-800">
            <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
            <span>
              Please correct the {Object.keys(errors).length} highlighted field{Object.keys(errors).length > 1 ? 's' : ''} above before submitting.
            </span>
          </div>
        )}

        {/* Form Actions Footer */}
        <div className="pt-4 border-t border-slate-100 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleReset}
              disabled={isSubmitting || (!isDirty && !isEditMode)}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200/80 active:bg-slate-200 border border-slate-300 rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              Reset Form
            </button>

            {isEditMode && (
              <button
                type="button"
                onClick={handleCancelClick}
                disabled={isSubmitting}
                className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold text-slate-700 bg-white hover:bg-slate-50 border border-slate-300 rounded-lg transition"
              >
                <X className="w-3.5 h-3.5" />
                Cancel
              </button>
            )}
          </div>

          <div className="flex items-center gap-3">
            <button
              type="submit"
              disabled={isSubmitting}
              className="inline-flex items-center justify-center gap-2 px-5 py-2.5 text-xs font-bold tracking-wide uppercase text-white bg-sky-600 hover:bg-sky-700 active:bg-sky-800 rounded-lg transition shadow-xs disabled:bg-sky-400 disabled:cursor-not-allowed cursor-pointer focus:ring-2 focus:ring-sky-500/30 outline-none"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Processing...</span>
                </>
              ) : isEditMode ? (
                <>
                  <Check className="w-4 h-4" />
                  <span>Update Record</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>{schema.submitButtonText}</span>
                </>
              )}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};
