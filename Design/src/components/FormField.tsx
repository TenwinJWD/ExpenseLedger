/**
 * Reusable FormField Component with accessible labels, units, and validation
 */

import React from 'react';
import { FieldDefinition } from '../types/dairy.ts';
import { AlertCircle } from 'lucide-react';

interface FormFieldProps {
  field: FieldDefinition;
  value: any;
  error?: string;
  onChange: (name: string, value: any) => void;
  onBlur?: (name: string) => void;
  disabled?: boolean;
}

export const FormField: React.FC<FormFieldProps> = ({
  field,
  value,
  error,
  onChange,
  onBlur,
  disabled = false,
}) => {
  const inputId = `field-${field.name}`;
  const errorId = `error-${field.name}`;
  const helpId = `help-${field.name}`;

  // Calculate grid column classes based on colSpan
  const getColSpanClass = () => {
    switch (field.colSpan) {
      case 2:
        return 'col-span-1 md:col-span-2';
      case 3:
        return 'col-span-1 md:col-span-2 lg:col-span-3';
      case 4:
        return 'col-span-1 md:col-span-2 lg:col-span-4';
      case 1:
      default:
        return 'col-span-1';
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const val = field.type === 'number' ? (e.target.value === '' ? '' : Number(e.target.value)) : e.target.value;
    onChange(field.name, val);
  };

  const handleBlur = () => {
    if (onBlur) {
      onBlur(field.name);
    }
  };

  const commonInputClasses = `
    w-full px-3.5 py-2.5 text-sm bg-white border rounded-lg transition-all
    ${field.readOnly ? 'bg-slate-100 text-slate-500 cursor-not-allowed border-slate-200' : ''}
    ${error ? 'border-rose-300 ring-2 ring-rose-100 text-rose-950 focus:border-rose-500 focus:ring-rose-200' : 'border-slate-300 text-slate-800 hover:border-slate-400 focus:border-sky-500 focus:ring-2 focus:ring-sky-100'}
    disabled:bg-slate-100 disabled:text-slate-400 disabled:cursor-not-allowed
    outline-none
  `;

  return (
    <div className={`${getColSpanClass()} flex flex-col`}>
      <label
        htmlFor={inputId}
        className="block text-xs font-semibold text-slate-700 tracking-wide uppercase mb-1.5"
      >
        <span>{field.label}</span>
        {field.required && !field.readOnly && (
          <span className="text-rose-500 ml-1 font-bold" title="Required field">
            *
          </span>
        )}
      </label>

      <div className="relative rounded-lg shadow-2xs">
        {field.type === 'select' ? (
          <select
            id={inputId}
            name={field.name}
            value={value ?? ''}
            onChange={handleChange}
            onBlur={handleBlur}
            disabled={disabled || field.readOnly}
            aria-invalid={!!error}
            aria-describedby={error ? errorId : field.helpText ? helpId : undefined}
            className={`${commonInputClasses} appearance-none pr-9 bg-[url("data:image/svg+xml;charset=UTF-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2216%22%20height%3D%2216%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%23475569%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22m6%209%206%206%206-6%22%2F%3E%3C%2Fsvg%3E")] bg-[length:1.2rem_1.2rem] bg-[right_0.75rem_center] bg-no-repeat cursor-pointer`}
          >
            <option value="">-- Select {field.label} --</option>
            {field.options?.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        ) : field.type === 'textarea' ? (
          <textarea
            id={inputId}
            name={field.name}
            rows={3}
            value={value ?? ''}
            onChange={handleChange}
            onBlur={handleBlur}
            placeholder={field.placeholder}
            disabled={disabled || field.readOnly}
            aria-invalid={!!error}
            aria-describedby={error ? errorId : field.helpText ? helpId : undefined}
            className={`${commonInputClasses} resize-y min-h-[76px]`}
          />
        ) : (
          <div className="relative flex items-center">
            <input
              id={inputId}
              name={field.name}
              type={field.type}
              value={value ?? ''}
              onChange={handleChange}
              onBlur={handleBlur}
              placeholder={field.placeholder || (field.readOnly ? 'Auto-generated on submit' : '')}
              readOnly={field.readOnly}
              disabled={disabled}
              min={field.validationRules?.min}
              max={field.validationRules?.max}
              aria-invalid={!!error}
              aria-describedby={error ? errorId : field.helpText ? helpId : undefined}
              className={`${commonInputClasses} ${field.unit ? 'pr-14' : ''}`}
            />
            {field.unit && (
              <span className="absolute right-3 text-xs font-semibold text-slate-500 bg-slate-100 px-2 py-0.5 rounded pointer-events-none border border-slate-200">
                {field.unit}
              </span>
            )}
          </div>
        )}
      </div>

      {/* Inline Validation Error Message */}
      {error ? (
        <p id={errorId} className="flex items-center gap-1.5 text-xs font-medium text-rose-600 mt-1.5">
          <AlertCircle className="w-3.5 h-3.5 shrink-0" />
          <span>{error}</span>
        </p>
      ) : field.helpText ? (
        <p id={helpId} className="text-xs text-slate-500 mt-1.5">
          {field.helpText}
        </p>
      ) : null}
    </div>
  );
};
