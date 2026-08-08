<template>
  <span class="status-badge" :class="`status-badge--${variant}`" :aria-label="`Status: ${label || status}`">
    <span class="status-badge__dot"></span>
    {{ label || status }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    required: true
  },
  label: {
    type: String,
    default: ''
  }
})

const variant = computed(() => {
  const map = {
    Pending: 'pending',
    Approved: 'approved',
    Rejected: 'rejected',
    Closed: 'closed',
    Active: 'active',
    Inactive: 'inactive',
    Applied: 'applied',
    Shortlisted: 'shortlisted',
    'Interview Scheduled': 'interview-scheduled',
    Selected: 'selected',
    Accepted: 'accepted',
    Declined: 'declined',
    'Auto Declined': 'auto-declined'
  }
  return map[props.status] || 'default'
})
</script>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  font-weight: var(--weight-semibold);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 4px 10px;
  border-radius: var(--radius-full);
  line-height: 1;
  white-space: nowrap;
}

.status-badge__dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-badge--pending {
  background-color: var(--color-warning-subtle);
  color: var(--color-warning);
}
.status-badge--pending .status-badge__dot {
  background-color: var(--color-warning);
}

.status-badge--approved {
  background-color: var(--color-success-subtle);
  color: var(--color-success);
}
.status-badge--approved .status-badge__dot {
  background-color: var(--color-success);
}

.status-badge--rejected {
  background-color: var(--color-danger-subtle);
  color: var(--color-danger);
}
.status-badge--rejected .status-badge__dot {
  background-color: var(--color-danger);
}

.status-badge--closed {
  background-color: var(--color-surface-hover);
  color: var(--text-secondary);
}
.status-badge--closed .status-badge__dot {
  background-color: var(--text-tertiary);
}

.status-badge--active {
  background-color: var(--color-success-subtle);
  color: var(--color-success);
}
.status-badge--active .status-badge__dot {
  background-color: var(--color-success);
}

.status-badge--inactive {
  background-color: var(--color-surface-hover);
  color: var(--text-secondary);
}
.status-badge--inactive .status-badge__dot {
  background-color: var(--text-tertiary);
}

.status-badge--applied {
  background-color: var(--color-primary-subtle);
  color: var(--color-primary);
}
.status-badge--applied .status-badge__dot {
  background-color: var(--color-primary);
}

.status-badge--shortlisted {
  background-color: var(--color-warning-subtle);
  color: var(--color-warning);
}
.status-badge--shortlisted .status-badge__dot {
  background-color: var(--color-warning);
}

.status-badge--interview-scheduled {
  background-color: var(--color-info-subtle);
  color: var(--color-info);
}
.status-badge--interview-scheduled .status-badge__dot {
  background-color: var(--color-info);
}

.status-badge--selected {
  background-color: var(--color-success-subtle);
  color: var(--color-success);
}
.status-badge--selected .status-badge__dot {
  background-color: var(--color-success);
}

.status-badge--accepted {
  background-color: var(--color-success-subtle);
  color: var(--color-success);
}
.status-badge--accepted .status-badge__dot {
  background-color: var(--color-success);
}

.status-badge--declined {
  background-color: var(--color-warning-subtle);
  color: var(--color-warning);
}
.status-badge--declined .status-badge__dot {
  background-color: var(--color-warning);
}

.status-badge--auto-declined {
  background-color: var(--color-surface-hover);
  color: var(--text-secondary);
}
.status-badge--auto-declined .status-badge__dot {
  background-color: var(--text-tertiary);
}

.status-badge--default {
  background-color: var(--color-surface-hover);
  color: var(--text-secondary);
}
.status-badge--default .status-badge__dot {
  background-color: var(--text-tertiary);
}
</style>
