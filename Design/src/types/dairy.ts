/**
 * LactaFlow Enterprise Dairy Management - Type Definitions
 */

export type PrimaryTabId = 'intake' | 'operations';
export type SubTabId = 'quality' | 'logistics';

export type ViewKey = 'tab1_intake' | 'tab2_quality' | 'tab2_logistics';

export type FieldType = 
  | 'text'
  | 'number'
  | 'email'
  | 'tel'
  | 'select'
  | 'textarea'
  | 'date'
  | 'datetime-local';

export interface SelectOption {
  label: string;
  value: string;
}

export interface ValidationRule {
  required?: boolean;
  min?: number;
  max?: number;
  pattern?: RegExp;
  message?: string;
  custom?: (value: any, allValues: Record<string, any>) => string | null;
}

export interface FieldDefinition {
  name: string;
  label: string;
  type: FieldType;
  required?: boolean;
  placeholder?: string;
  options?: SelectOption[];
  defaultValue?: any;
  validationRules?: ValidationRule;
  colSpan?: 1 | 2 | 3 | 4;
  unit?: string;
  helpText?: string;
  readOnly?: boolean;
}

export interface FormSchema {
  id: string;
  title: string;
  description: string;
  submitButtonText: string;
  fields: FieldDefinition[];
}

export interface TableColumn<T = any> {
  key: string;
  label: string;
  sortable?: boolean;
  align?: 'left' | 'center' | 'right';
  width?: string;
  render?: (value: any, record: T) => React.ReactNode;
}

export interface BaseRecord {
  id: string;
  primaryTabId: PrimaryTabId;
  subTabId?: SubTabId;
  name: string;
  phone: string;
  email: string;
  location: string;
  category: string;
  status: string;
  date: string;
  notes?: string;
  createdAt: string;
  updatedAt: string;
  [key: string]: any;
}

export interface FilterState {
  search: string;
  category: string;
  status: string;
  location: string;
  dateFrom: string;
  dateTo: string;
}

export interface SortConfig {
  field: string;
  direction: 'asc' | 'desc';
}

export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  title?: string;
  message: string;
  timestamp: number;
}
