export type BadgeTone = 'success' | 'warning' | 'danger' | 'info' | 'neutral'

const SEVERITY_TONE: Record<string, BadgeTone> = {
  Critical: 'danger',
  Major: 'warning',
  Minor: 'info',
  'Not Assessed': 'neutral',
}

const PRIORITY_TONE: Record<string, BadgeTone> = {
  Urgent: 'danger',
  High: 'warning',
  Medium: 'info',
  Low: 'success',
  'Not Assessed': 'neutral',
}

const STATUS_TONE: Record<string, BadgeTone> = {
  Draft: 'neutral',
  'Under Investigation': 'warning',
  'Pending CAPA': 'info',
  Closed: 'success',
}

const RISK_TONE: Record<string, BadgeTone> = {
  High: 'danger',
  Medium: 'warning',
  Low: 'success',
  'Not Assessed': 'neutral',
}

export function severityTone(value: string | undefined): BadgeTone {
  return SEVERITY_TONE[value ?? ''] ?? 'neutral'
}

export function priorityTone(value: string | undefined): BadgeTone {
  return PRIORITY_TONE[value ?? ''] ?? 'neutral'
}

export function statusTone(value: string | undefined): BadgeTone {
  return STATUS_TONE[value ?? ''] ?? 'neutral'
}

export function riskTone(value: string | undefined): BadgeTone {
  return RISK_TONE[value ?? ''] ?? 'neutral'
}
