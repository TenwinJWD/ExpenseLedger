/**
 * LactaFlow Enterprise Dairy Management - Schemas & Column Configurations
 */

import { FormSchema, TableColumn, PrimaryTabId, SubTabId } from '../types/dairy.ts';

export interface TabConfig {
  id: PrimaryTabId;
  label: string;
  badgeLabel: string;
  tagline: string;
  description: string;
}

export interface SubTabConfig {
  id: SubTabId;
  label: string;
  badgeLabel: string;
  tagline: string;
  description: string;
}

export const PRIMARY_TABS: TabConfig[] = [
  {
    id: 'intake',
    label: 'Raw Milk Intake & Reception',
    badgeLabel: 'Primary Tab 1',
    tagline: 'Farm Procurement & Silo Storage Intake',
    description: 'Log new raw milk tanker shipments, supplier details, fat/SNF composition, and silo storage allocations.',
  },
  {
    id: 'operations',
    label: 'Processing & Cold-Chain Operations',
    badgeLabel: 'Primary Tab 2',
    tagline: 'Pasteurization, Lab QA & Distribution Logistics',
    description: 'Monitor laboratory chemical analysis, pasteurization test batches, and outbound refrigerated tanker logistics.',
  },
];

export const SECONDARY_TABS: SubTabConfig[] = [
  {
    id: 'quality',
    label: 'Pasteurization & Quality Testing',
    badgeLabel: 'Sub-tab 1',
    tagline: 'Chemical assays, pH, Somatic cell counts & antibiotic screening',
    description: 'Validate milk safety standards before packaging and processing.',
  },
  {
    id: 'logistics',
    label: 'Cold-Chain Logistics & Dispatch',
    badgeLabel: 'Sub-tab 2',
    tagline: 'Outbound refrigerated fleet, dispatch hubs & temperature tracking',
    description: 'Track refrigerated fleet departures, delivery hubs, and seal numbers.',
  },
];

// --- Form Schemas ---

export const INTAKE_FORM_SCHEMA: FormSchema = {
  id: 'intake_form',
  title: 'Raw Milk Reception & Supplier Entry',
  description: 'Enter incoming tanker arrival details, supplier contact credentials, temperature compliance, and silo allocation.',
  submitButtonText: 'Record Milk Intake Batch',
  fields: [
    {
      name: 'id',
      label: 'Intake Record ID',
      type: 'text',
      readOnly: true,
      defaultValue: '',
      colSpan: 1,
      helpText: 'System-generated unique batch identifier',
    },
    {
      name: 'name',
      label: 'Supplier / Dairy Farm Name',
      type: 'text',
      required: true,
      placeholder: 'e.g. Highland Valley Dairy Co-op',
      colSpan: 1,
    },
    {
      name: 'phone',
      label: 'Contact Phone Number',
      type: 'tel',
      required: true,
      placeholder: 'e.g. (555) 382-9102',
      colSpan: 1,
    },
    {
      name: 'email',
      label: 'Contact Email ID',
      type: 'email',
      required: true,
      placeholder: 'e.g. dispatch@highlanddairy.com',
      colSpan: 1,
    },
    {
      name: 'location',
      label: 'Farm Origin / Facility Location',
      type: 'text',
      required: true,
      placeholder: 'e.g. Green Pastures - Shed B, Wisconsin',
      colSpan: 2,
    },
    {
      name: 'category',
      label: 'Milk Category / Breed Type',
      type: 'select',
      required: true,
      options: [
        { label: 'Grade A Whole Cow Milk (Raw)', value: 'Grade A Whole Cow Milk' },
        { label: 'Organic Pasture-Fed Cow Milk', value: 'Organic Pasture-Fed Cow Milk' },
        { label: 'A2 Jersey High-Fat Cream Milk', value: 'A2 Jersey High-Fat Cream Milk' },
        { label: 'Buffalo Whole Milk (High SNF)', value: 'Buffalo Whole Milk' },
        { label: 'Chilled Skimmed Milk Batch', value: 'Chilled Skimmed Milk' },
      ],
      colSpan: 1,
    },
    {
      name: 'status',
      label: 'Reception Status',
      type: 'select',
      required: true,
      options: [
        { label: 'Accepted - Chilled in Silo', value: 'Accepted' },
        { label: 'Under Lab Quality Testing', value: 'Testing' },
        { label: 'Quarantined - High Temp Warning', value: 'Quarantined' },
        { label: 'Approved for Pasteurization', value: 'Approved' },
        { label: 'Rejected - Acidic / Souring', value: 'Rejected' },
      ],
      colSpan: 1,
    },
    {
      name: 'date',
      label: 'Reception Date & Time',
      type: 'datetime-local',
      required: true,
      colSpan: 1,
    },
    {
      name: 'liters',
      label: 'Received Volume',
      type: 'number',
      required: true,
      unit: 'Liters',
      placeholder: 'e.g. 12500',
      validationRules: { min: 100, max: 100000 },
      colSpan: 1,
    },
    {
      name: 'fatPercentage',
      label: 'Fat Content',
      type: 'number',
      required: true,
      unit: '%',
      placeholder: 'e.g. 3.85',
      validationRules: { min: 2.0, max: 12.0 },
      colSpan: 1,
    },
    {
      name: 'snfPercentage',
      label: 'SNF (Solids-Not-Fat)',
      type: 'number',
      required: true,
      unit: '%',
      placeholder: 'e.g. 8.75',
      validationRules: { min: 6.0, max: 14.0 },
      colSpan: 1,
    },
    {
      name: 'temperature',
      label: 'Milk Chilling Temp',
      type: 'number',
      required: true,
      unit: '°C',
      placeholder: 'e.g. 3.4',
      validationRules: { min: -2.0, max: 20.0 },
      colSpan: 1,
      helpText: 'Acceptable range: 2.0°C to 4.5°C',
    },
    {
      name: 'siloId',
      label: 'Target Storage Silo',
      type: 'select',
      required: true,
      options: [
        { label: 'Silo Alpha (Cold Chilled 3.2°C)', value: 'Silo Alpha' },
        { label: 'Silo Bravo (Dedicated Organic)', value: 'Silo Bravo' },
        { label: 'Silo Charlie (Buffer Tank)', value: 'Silo Charlie' },
        { label: 'Silo Delta (Premium A2 Tank)', value: 'Silo Delta' },
      ],
      colSpan: 1,
    },
    {
      name: 'notes',
      label: 'Quality Notes & Sensor Observations',
      type: 'textarea',
      placeholder: 'Record driver remarks, odor check, sample tube IDs, or chilling anomalies...',
      colSpan: 4,
    },
  ],
};

export const QUALITY_FORM_SCHEMA: FormSchema = {
  id: 'quality_form',
  title: 'Pasteurization & Quality Assurance Entry',
  description: 'Log laboratory chemical and microbial parameters for processed dairy batches before release.',
  submitButtonText: 'Save Quality Inspection Record',
  fields: [
    {
      name: 'id',
      label: 'QA Record ID',
      type: 'text',
      readOnly: true,
      defaultValue: '',
      colSpan: 1,
      helpText: 'System-generated laboratory test ID',
    },
    {
      name: 'name',
      label: 'Lead Chemist / Inspector Name',
      type: 'text',
      required: true,
      placeholder: 'e.g. Dr. Emily Chen, QC Lead',
      colSpan: 1,
    },
    {
      name: 'phone',
      label: 'Inspector Phone',
      type: 'tel',
      required: true,
      placeholder: 'e.g. (555) 789-1029',
      colSpan: 1,
    },
    {
      name: 'email',
      label: 'Laboratory Email',
      type: 'email',
      required: true,
      placeholder: 'e.g. qc.lab@lactaflow.com',
      colSpan: 1,
    },
    {
      name: 'location',
      label: 'Testing Lab Station / Plant',
      type: 'text',
      required: true,
      placeholder: 'e.g. Processing Plant 1 - Cleanroom Lab 2B',
      colSpan: 2,
    },
    {
      name: 'category',
      label: 'Tested Product Line',
      type: 'select',
      required: true,
      options: [
        { label: 'Pasteurized Whole Milk', value: 'Pasteurized Whole Milk' },
        { label: 'Standardized Skimmed Milk', value: 'Standardized Skimmed Milk' },
        { label: 'Heavy Cream 40%', value: 'Heavy Cream 40%' },
        { label: 'Cultured Buttermilk Assay', value: 'Cultured Buttermilk' },
        { label: 'Homogenized A2 Whole Milk', value: 'Homogenized A2 Whole Milk' },
      ],
      colSpan: 1,
    },
    {
      name: 'status',
      label: 'Quality Verdict',
      type: 'select',
      required: true,
      options: [
        { label: 'Passed - Grade A Certified', value: 'Passed' },
        { label: 'Conditional Pass (Secondary Review)', value: 'Conditional' },
        { label: 'Retest Required', value: 'Retest' },
        { label: 'Failed - Contamination Alert', value: 'Failed' },
      ],
      colSpan: 1,
    },
    {
      name: 'date',
      label: 'Inspection Date & Time',
      type: 'datetime-local',
      required: true,
      colSpan: 1,
    },
    {
      name: 'phLevel',
      label: 'pH Acidity Level',
      type: 'number',
      required: true,
      unit: 'pH',
      placeholder: 'e.g. 6.68',
      validationRules: { min: 5.5, max: 8.0 },
      colSpan: 1,
      helpText: 'Ideal milk pH: 6.60 - 6.80',
    },
    {
      name: 'somaticCount',
      label: 'Somatic Cell Count',
      type: 'number',
      required: true,
      unit: 'CFU/ml',
      placeholder: 'e.g. 115000',
      validationRules: { min: 5000, max: 2000000 },
      colSpan: 1,
      helpText: 'Grade A standard: < 200,000 CFU/ml',
    },
    {
      name: 'antibioticResidue',
      label: 'Antibiotic Residue Assay',
      type: 'select',
      required: true,
      options: [
        { label: 'Negative / Clear (Passed)', value: 'Negative' },
        { label: 'Trace Detected (Hold Batch)', value: 'Trace' },
        { label: 'Positive (Contaminated - Discard)', value: 'Positive' },
      ],
      colSpan: 1,
    },
    {
      name: 'pasteurTemp',
      label: 'HTST Pasteurization Temp',
      type: 'number',
      required: true,
      unit: '°C',
      placeholder: 'e.g. 72.5',
      validationRules: { min: 60.0, max: 95.0 },
      colSpan: 1,
      helpText: 'HTST standard: 72°C for 15 sec',
    },
    {
      name: 'notes',
      label: 'Lab Findings & Batch Observations',
      type: 'textarea',
      placeholder: 'Record phosphatase test, sensory odor score, fat globule dispersion...',
      colSpan: 4,
    },
  ],
};

export const LOGISTICS_FORM_SCHEMA: FormSchema = {
  id: 'logistics_form',
  title: 'Cold-Chain Logistics & Outbound Dispatch',
  description: 'Schedule refrigerated fleet dispatches, track driver contacts, temperature loggers, and tamper seal numbers.',
  submitButtonText: 'Register Logistics Dispatch',
  fields: [
    {
      name: 'id',
      label: 'Dispatch Record ID',
      type: 'text',
      readOnly: true,
      defaultValue: '',
      colSpan: 1,
      helpText: 'System-generated manifest dispatch ID',
    },
    {
      name: 'name',
      label: 'Dispatch Supervisor / Driver Name',
      type: 'text',
      required: true,
      placeholder: 'e.g. Marcus Vance (Fleet Lead)',
      colSpan: 1,
    },
    {
      name: 'phone',
      label: 'Driver Mobile Phone',
      type: 'tel',
      required: true,
      placeholder: 'e.g. (555) 441-2093',
      colSpan: 1,
    },
    {
      name: 'email',
      label: 'Fleet Dispatch Email',
      type: 'email',
      required: true,
      placeholder: 'e.g. logistics.ops@lactaflow.com',
      colSpan: 1,
    },
    {
      name: 'location',
      label: 'Destination Hub / Regional Warehouse',
      type: 'text',
      required: true,
      placeholder: 'e.g. Midwest Cold Hub - Bay 14, Chicago IL',
      colSpan: 2,
    },
    {
      name: 'category',
      label: 'Dispatched Product Line',
      type: 'select',
      required: true,
      options: [
        { label: 'Chilled Whole Milk 1L Bottles (1,200 crates)', value: 'Whole Milk 1L Bottles' },
        { label: 'Organic Pasteurized Milk Cartons', value: 'Organic Milk Cartons' },
        { label: 'Bulk Insulated Cream Tanker', value: 'Bulk Insulated Cream Tanker' },
        { label: 'Artisan Salted Butter Tubs', value: 'Artisan Salted Butter' },
        { label: 'Low-Fat Skimmed Milk Pails', value: 'Skimmed Milk Pails' },
      ],
      colSpan: 1,
    },
    {
      name: 'status',
      label: 'Logistics Status',
      type: 'select',
      required: true,
      options: [
        { label: 'Dispatched - In Transit (Cold OK)', value: 'In Transit' },
        { label: 'Scheduled / Loading in Bay', value: 'Scheduled' },
        { label: 'Arrived at Regional Hub', value: 'Arrived' },
        { label: 'Delivered & Consignee Signed', value: 'Delivered' },
        { label: 'Temperature Alert (> 4.8°C)', value: 'Temp Alert' },
      ],
      colSpan: 1,
    },
    {
      name: 'date',
      label: 'Departure Date & Time',
      type: 'datetime-local',
      required: true,
      colSpan: 1,
    },
    {
      name: 'tankerId',
      label: 'Refrigerated Fleet Unit ID',
      type: 'text',
      required: true,
      placeholder: 'e.g. TK-CHILL-904',
      colSpan: 1,
    },
    {
      name: 'cargoTemp',
      label: 'Chamber Temp at Departure',
      type: 'number',
      required: true,
      unit: '°C',
      placeholder: 'e.g. 2.8',
      validationRules: { min: -4.0, max: 12.0 },
      colSpan: 1,
    },
    {
      name: 'quantity',
      label: 'Quantity Dispatched',
      type: 'number',
      required: true,
      unit: 'Units/L',
      placeholder: 'e.g. 8400',
      validationRules: { min: 10, max: 100000 },
      colSpan: 1,
    },
    {
      name: 'sealNumber',
      label: 'Tamper-Evident Seal Barcode',
      type: 'text',
      required: true,
      placeholder: 'e.g. SEAL-LF-884920',
      colSpan: 1,
    },
    {
      name: 'notes',
      label: 'Route Instructions & Delivery SLA',
      type: 'textarea',
      placeholder: 'Highway routing, expected arrival window, consignee contact on arrival...',
      colSpan: 4,
    },
  ],
};
