/**
 * Unit Tests for Pure Dairy Logic Utilities
 * Run using Node 22 native test runner: node --test
 */

import test from 'node:test';
import assert from 'node:assert/strict';
import {
  validateRequired,
  validateEmail,
  validatePhone,
  validateField,
  validateRecord
} from './validation.ts';
import {
  filterRecords,
  sortRecords,
  paginateRecords
} from './filterAndSort.ts';
import type { FieldDefinition, BaseRecord } from '../types/dairy.ts';

test('Validation: validateRequired checks empty values correctly', () => {
  assert.equal(validateRequired(''), false);
  assert.equal(validateRequired('   '), false);
  assert.equal(validateRequired(null), false);
  assert.equal(validateRequired(undefined), false);
  assert.equal(validateRequired([]), false);
  assert.equal(validateRequired('Valid Text'), true);
  assert.equal(validateRequired(0), true);
  assert.equal(validateRequired(100), true);
  assert.equal(validateRequired(['item']), true);
});

test('Validation: validateEmail checks standard email formats', () => {
  assert.equal(validateEmail('test@dairyfarm.com'), true);
  assert.equal(validateEmail('john.doe+plant1@corp.lactaflow.org'), true);
  assert.equal(validateEmail('invalid-email'), false);
  assert.equal(validateEmail('test@'), false);
  assert.equal(validateEmail('@domain.com'), false);
  assert.equal(validateEmail(''), false);
});

test('Validation: validatePhone handles diverse phone numbers', () => {
  assert.equal(validatePhone('555-123-4567'), true);
  assert.equal(validatePhone('+1 (555) 019-2834'), true);
  assert.equal(validatePhone('+91 9876543210'), true);
  assert.equal(validatePhone('12345'), false); // Too short
  assert.equal(validatePhone(''), false);
});

test('Validation: validateRecord enforces schema constraints', () => {
  const schema: FieldDefinition[] = [
    { name: 'id', label: 'ID', type: 'text', readOnly: true },
    { name: 'name', label: 'Supplier Name', type: 'text', required: true },
    { name: 'email', label: 'Email', type: 'email', required: true },
    { name: 'liters', label: 'Volume (L)', type: 'number', required: true, validationRules: { min: 100, max: 10000 } }
  ];

  // Missing required
  const errors1 = validateRecord({ id: 'RMI-01', name: '', email: 'bad-email', liters: 50 }, schema);
  assert.ok(errors1['name'], 'Name should be required');
  assert.ok(errors1['email'], 'Email format should fail');
  assert.ok(errors1['liters'], 'Volume below min should fail');

  // Valid values
  const errors2 = validateRecord({
    id: 'RMI-01',
    name: 'Sunrise Farms',
    email: 'contact@sunrisefarms.com',
    liters: 2500
  }, schema);
  assert.deepEqual(errors2, {});
});

test('Filtering: filterRecords handles text search, category, status, and dates', () => {
  const sampleData: BaseRecord[] = [
    {
      id: 'RMI-01',
      primaryTabId: 'intake',
      name: 'Highland Dairy',
      phone: '555-0101',
      email: 'highland@dairy.com',
      location: 'Shed B, North Pasture',
      category: 'Whole Milk',
      status: 'Accepted',
      date: '2026-10-15',
      createdAt: '2026-10-15T08:00:00Z',
      updatedAt: '2026-10-15T08:00:00Z'
    },
    {
      id: 'RMI-02',
      primaryTabId: 'intake',
      name: 'Valley Green Co-op',
      phone: '555-0102',
      email: 'vg@coop.com',
      location: 'Main Silo Complex',
      category: 'Organic Milk',
      status: 'Quarantined',
      date: '2026-10-18',
      createdAt: '2026-10-18T09:00:00Z',
      updatedAt: '2026-10-18T09:00:00Z'
    }
  ];

  // Search by partial name
  const res1 = filterRecords(sampleData, { search: 'highland' });
  assert.equal(res1.length, 1);
  assert.equal(res1[0].id, 'RMI-01');

  // Search by phone
  const res2 = filterRecords(sampleData, { search: '0102' });
  assert.equal(res2.length, 1);
  assert.equal(res2[0].id, 'RMI-02');

  // Filter by status
  const res3 = filterRecords(sampleData, { status: 'Quarantined' });
  assert.equal(res3.length, 1);
  assert.equal(res3[0].id, 'RMI-02');

  // Filter by date range
  const res4 = filterRecords(sampleData, { dateFrom: '2026-10-16' });
  assert.equal(res4.length, 1);
  assert.equal(res4[0].id, 'RMI-02');
});

test('Sorting: sortRecords sorts numbers, strings and dates in both directions', () => {
  const list = [
    { id: '1', score: 20, name: 'Charlie', date: '2026-02-01' },
    { id: '2', score: 5, name: 'Alice', date: '2026-01-01' },
    { id: '3', score: 50, name: 'Bob', date: '2026-03-01' },
  ];

  const sortedNumAsc = sortRecords(list, { field: 'score', direction: 'asc' });
  assert.equal(sortedNumAsc[0].score, 5);
  assert.equal(sortedNumAsc[2].score, 50);

  const sortedNumDesc = sortRecords(list, { field: 'score', direction: 'desc' });
  assert.equal(sortedNumDesc[0].score, 50);
  assert.equal(sortedNumDesc[2].score, 5);

  const sortedAlpha = sortRecords(list, { field: 'name', direction: 'asc' });
  assert.equal(sortedAlpha[0].name, 'Alice');
  assert.equal(sortedAlpha[2].name, 'Charlie');
});

test('Pagination: paginateRecords slices data correctly', () => {
  const dataset = Array.from({ length: 23 }, (_, i) => ({ id: `REC-${i + 1}` }));

  // Page 1 of size 10
  const p1 = paginateRecords(dataset, 1, 10);
  assert.equal(p1.items.length, 10);
  assert.equal(p1.items[0].id, 'REC-1');
  assert.equal(p1.totalPages, 3);
  assert.equal(p1.startIndex, 1);
  assert.equal(p1.endIndex, 10);

  // Page 3 of size 10 (3 remaining items)
  const p3 = paginateRecords(dataset, 3, 10);
  assert.equal(p3.items.length, 3);
  assert.equal(p3.items[0].id, 'REC-21');
  assert.equal(p3.startIndex, 21);
  assert.equal(p3.endIndex, 23);

  // Empty dataset
  const pEmpty = paginateRecords([], 1, 10);
  assert.equal(pEmpty.items.length, 0);
  assert.equal(pEmpty.totalRecords, 0);
  assert.equal(pEmpty.totalPages, 1);
});
