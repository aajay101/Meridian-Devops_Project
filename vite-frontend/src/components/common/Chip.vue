<template>
  <span class="chip" :class="`chip--${variant}`">
    <slot />
    <button
      v-if="removable"
      class="chip__remove"
      type="button"
      :aria-label="`Remove ${$slots.default?.[0]?.text || ''}`"
      @click.stop="$emit('remove')"
    >
      <i class="bi bi-x"></i>
    </button>
  </span>
</template>

<script setup>
defineProps({
  variant: {
    type: String,
    default: 'default',
    validator: (v) => ['default', 'primary', 'success', 'warning', 'danger', 'info'].includes(v)
  },
  removable: {
    type: Boolean,
    default: false
  }
})

defineEmits(['remove'])
</script>

<style scoped>
.chip {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-1) var(--space-2-5);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--weight-medium);
  line-height: 1;
  white-space: nowrap;
  background-color: var(--color-surface-hover);
  color: var(--text-secondary);
  border: 1px solid var(--color-border);
  transition: background-color var(--duration-fast) var(--ease-default);
}

.chip--primary {
  background-color: var(--color-primary-subtle);
  color: var(--color-primary);
  border-color: var(--color-primary-muted);
}

.chip--success {
  background-color: var(--color-success-subtle);
  color: var(--color-success);
  border-color: var(--color-success-muted);
}

.chip--warning {
  background-color: var(--color-warning-subtle);
  color: var(--color-warning);
  border-color: var(--color-warning-muted);
}

.chip--danger {
  background-color: var(--color-danger-subtle);
  color: var(--color-danger);
  border-color: var(--color-danger-muted);
}

.chip--info {
  background-color: var(--color-info-subtle);
  color: var(--color-info);
  border-color: var(--color-info-muted);
}

.chip__remove {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 14px;
  height: 14px;
  padding: 0;
  border: none;
  border-radius: 50%;
  background: transparent;
  color: inherit;
  cursor: pointer;
  transition: background-color var(--duration-fast) var(--ease-default);
  font-size: 10px;
  line-height: 1;
  opacity: 0.6;
}

.chip__remove:hover {
  opacity: 1;
  background-color: rgba(0, 0, 0, 0.1);
}
</style>
