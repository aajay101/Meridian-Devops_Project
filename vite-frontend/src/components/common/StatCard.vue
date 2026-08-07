<template>
  <div class="stat-card" :class="`stat-card--${color}`">
    <div class="stat-card-icon">
      <i :class="icon"></i>
    </div>
    <div class="stat-card-content">
      <span class="stat-card-value">{{ value }}</span>
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
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  display: flex;
  align-items: center;
  gap: var(--space-4);
  transition: box-shadow var(--duration-base) var(--ease-default);
}

.stat-card:hover {
  box-shadow: var(--shadow-md);
}

.stat-card-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-xl);
  flex-shrink: 0;
}

.stat-card--primary .stat-card-icon {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
}

.stat-card--success .stat-card-icon {
  background-color: var(--color-success-bg);
  color: var(--color-success);
}

.stat-card--warning .stat-card-icon {
  background-color: var(--color-warning-bg);
  color: var(--color-warning);
}

.stat-card--danger .stat-card-icon {
  background-color: var(--color-danger-bg);
  color: var(--color-danger);
}

.stat-card--info .stat-card-icon {
  background-color: var(--color-info-bg);
  color: var(--color-info);
}

.stat-card-content {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.stat-card-value {
  font-size: var(--text-lg);
  font-weight: var(--weight-bold);
  color: var(--text-primary);
  line-height: var(--leading-tight);
}

.stat-card-label {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin-top: var(--space-1);
}
</style>
