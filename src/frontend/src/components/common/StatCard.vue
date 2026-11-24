<template>
  <div class="stat-card" :class="`stat-card--${color}`" :aria-label="`${label}: ${value}`">
    <div class="stat-card-icon" aria-hidden="true">
      <i :class="icon"></i>
    </div>
    <div class="stat-card-content">
      <span class="stat-card-value" role="status">{{ value }}</span>
      <span class="stat-card-label">{{ label }}</span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  label: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    required: true
  },
  icon: {
    type: String,
    required: true
  },
  color: {
    type: String,
    default: 'primary',
    validator: (v) => ['primary', 'success', 'warning', 'danger', 'info'].includes(v)
  }
})
</script>

<style scoped>
.stat-card {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: var(--space-5) var(--space-6);
  display: flex;
  align-items: center;
  gap: var(--space-4);
  box-shadow: var(--shadow-card);
  transition: all var(--duration-normal) var(--ease-default);
}

.stat-card:hover {
  box-shadow: var(--shadow-card-hover);
  border-color: var(--color-border-strong);
  transform: translateY(-1px);
}

.stat-card-icon {
  width: 42px;
  height: 42px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 17px;
  flex-shrink: 0;
  transition: transform var(--duration-fast) var(--ease-default);
}

.stat-card:hover .stat-card-icon {
  transform: scale(1.05);
}

.stat-card--primary .stat-card-icon {
  background-color: var(--color-primary-subtle);
  color: var(--text-primary);
}

.stat-card--success .stat-card-icon {
  background-color: var(--color-success-subtle);
  color: var(--color-success);
}

.stat-card--warning .stat-card-icon {
  background-color: var(--color-warning-subtle);
  color: var(--color-warning);
}

.stat-card--danger .stat-card-icon {
  background-color: var(--color-danger-subtle);
  color: var(--color-danger);
}

.stat-card--info .stat-card-icon {
  background-color: var(--color-info-subtle);
  color: var(--color-info);
}

.stat-card-content {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.stat-card-value {
  font-size: var(--text-stat);
  font-weight: var(--weight-bold);
  color: var(--text-primary);
  line-height: 1;
  letter-spacing: var(--tracking-tight);
  font-variant-numeric: tabular-nums;
}

.stat-card-label {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  margin-top: var(--space-1);
  font-weight: var(--weight-medium);
}
</style>
