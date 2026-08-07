<template>
  <span class="status-badge" :class="`status-badge--${variant}`">
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
  display: inline-block;
  font-size: 11px;
  font-weight: var(--weight-semibold);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  line-height: 1;
}

.status-badge--pending {
  background-color: #FFF7ED;
  color: #C2410C;
  border: 1px solid #FDBA74;
}

.status-badge--approved {
  background-color: #DCFCE7;
  color: #15803D;
  border: 1px solid #86EFAC;
}

.status-badge--rejected {
  background-color: #FEF2F2;
  color: #B91C1C;
  border: 1px solid #FECACA;
}

.status-badge--closed {
  background-color: var(--color-surface-muted);
  color: var(--text-secondary);
  border: 1px solid var(--color-border);
}

.status-badge--active {
  background-color: #DCFCE7;
  color: #15803D;
}

.status-badge--inactive {
  background-color: var(--color-surface-muted);
  color: var(--text-secondary);
}

.status-badge--applied {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
}

.status-badge--shortlisted {
  background-color: var(--color-warning-bg);
  color: var(--color-warning);
}

.status-badge--interview-scheduled {
  background-color: #E0F2FE;
  color: #0369A1;
  border: 1px solid #7DD3FC;
}

.status-badge--selected {
  background-color: var(--color-success-bg);
  color: var(--color-success);
}

.status-badge--accepted {
  background-color: #DCFCE7;
  color: #15803D;
  border: 1px solid #86EFAC;
}

.status-badge--declined {
  background-color: #FFF7ED;
  color: #C2410C;
  border: 1px solid #FDBA74;
}

.status-badge--auto-declined {
  background-color: var(--color-surface-muted);
  color: var(--text-secondary);
  border: 1px solid var(--color-border);
}

.status-badge--default {
  background-color: var(--color-surface-muted);
  color: var(--text-secondary);
}
</style>
