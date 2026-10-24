/**
 * LactaFlow Enterprise Validation Utilities
 */

import type { FieldDefinition } from '../types/dairy.ts';

export function validateRequired(value: any): boolean {
  if (value === undefined || value === null) return false;
  if (typeof value === 'string') return value.trim().length > 0;
  if (typeof value === 'number') return !isNaN(value);
  if (Array.isArray(value)) return value.length > 0;
  return true;
}

export function validateEmail(email: string): boolean {
  if (!email || typeof email !== 'string') return false;
  // Standard RFC-like email pattern with local part, @, domain, and TLD
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  return emailRegex.test(email.trim());
}

export function validatePhone(phone: string): boolean {
  if (!phone || typeof phone !== 'string') return false;
  // Supports formats like: (555) 123-4567, +1-555-123-4567, 555-123-4567, 5551234567, +91 98765 43210
  const digitsOnly = phone.replace(/\D/g, '');
  return digitsOnly.length >= 7 && digitsOnly.length <= 15;
}

export function validateField(
  value: any,
  field: FieldDefinition,
  allValues: Record<string, any> = {}
): string | null {
  // If field is required, check emptiness
  if (field.required) {
    if (!validateRequired(value)) {
      return `${field.label} is required`;
    }
  }

  // If value is empty and not required, pass
  if (!validateRequired(value)) {
    return null;
  }

  // Type-specific validations
  if (field.type === 'email') {
    if (!validateEmail(String(value))) {
      return `Please enter a valid email address (e.g. name@domain.com)`;
    }
  }

  if (field.type === 'tel') {
    if (!validatePhone(String(value))) {
      return `Please enter a valid phone number (at least 7 digits)`;
    }
  }

  if (field.type === 'number') {
    const num = Number(value);
    if (isNaN(num)) {
      return `${field.label} must be a valid number`;
    }
    if (field.validationRules?.min !== undefined && num < field.validationRules.min) {
      return `${field.label} must be at least ${field.validationRules.min}${field.unit ? ' ' + field.unit : ''}`;
    }
    if (field.validationRules?.max !== undefined && num > field.validationRules.max) {
      return `${field.label} must not exceed ${field.validationRules.max}${field.unit ? ' ' + field.unit : ''}`;
    }
  }

  // Custom regex pattern
  if (field.validationRules?.pattern && typeof value === 'string') {
    if (!field.validationRules.pattern.test(value)) {
      return field.validationRules.message || `${field.label} is invalid`;
    }
  }

  // Custom validation callback
  if (field.validationRules?.custom) {
    const customError = field.validationRules.custom(value, allValues);
    if (customError) return customError;
  }

  return null;
}

export function validateRecord(
  values: Record<string, any>,
  fields: FieldDefinition[]
): Record<string, string> {
  const errors: Record<string, string> = {};

  for (const field of fields) {
    // Read-only system-generated IDs don't require user input validation
    if (field.readOnly) continue;

    const error = validateField(values[field.name], field, values);
    if (error) {
      errors[field.name] = error;
    }
  }

  return errors;
}
