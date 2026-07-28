import {
  Barcode,
  Beaker,
  Building2,
  Calendar,
  CalendarDays,
  CalendarX,
  FileText,
  Hash,
  PackageSearch,
  Pill,
  Store,
  Tag,
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import type { Complaint } from '@/types/complaint.types'
import { formatDate } from '@/utils/formatters'

export interface ComplaintFieldConfig {
  key: string
  label: string
  icon: LucideIcon
  span?: 'full' | 'half'
  multiline?: boolean
  getValue: (complaint: Complaint) => string | undefined
}

export const COMPLAINT_FIELDS: ComplaintFieldConfig[] = [
  { key: 'id', label: 'Complaint ID', icon: Hash, getValue: (c) => c.id },
  { key: 'dateReported', label: 'Date Reported', icon: Calendar, getValue: (c) => formatDate(c.dateReported) },
  { key: 'customerName', label: 'Customer Name', icon: Building2, getValue: (c) => c.customerName },
  { key: 'customerType', label: 'Customer Type', icon: Store, getValue: (c) => c.customerType },
  { key: 'productName', label: 'Product Name', icon: Pill, getValue: (c) => c.productName },
  { key: 'strength', label: 'Strength', icon: Beaker, getValue: (c) => c.strength },
  { key: 'batchNumber', label: 'Batch Number', icon: Barcode, getValue: (c) => c.batchNumber },
  { key: 'complaintType', label: 'Complaint Type', icon: Tag, getValue: (c) => c.complaintType },
  {
    key: 'manufacturingDate',
    label: 'Manufacturing Date',
    icon: CalendarDays,
    getValue: (c) => formatDate(c.manufacturingDate),
  },
  { key: 'expiryDate', label: 'Expiry Date', icon: CalendarX, getValue: (c) => formatDate(c.expiryDate) },
  {
    key: 'affectedQuantity',
    label: 'Affected Quantity',
    icon: PackageSearch,
    getValue: (c) => (c.affectedQuantity !== undefined ? `${c.affectedQuantity} ${c.unitOfMeasure ?? ''}`.trim() : undefined),
  },
  {
    key: 'description',
    label: 'Complaint Description',
    icon: FileText,
    span: 'full',
    multiline: true,
    getValue: (c) => c.description,
  },
]
