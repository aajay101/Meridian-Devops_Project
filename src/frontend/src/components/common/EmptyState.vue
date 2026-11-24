<template>
  <div class="empty-state">
    <div class="empty-state-icon">
      <i :class="icon"></i>
    </div>
    <h3 class="empty-state-title">{{ title }}</h3>
    <p v-if="description" class="empty-state-description">{{ description }}</p>
    <div v-if="$slots.action" class="empty-state-action">
      <slot name="action" />
    </div>
  </div>
</template>

<script setup>
defineProps({
  icon: {
    type: String,
    default: 'bi bi-inbox'
  },
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: ''
  }
})
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-12) var(--space-6);
  text-align: center;
}

.empty-state-icon {
  width: 64px;
  height: 64px;
  border-radius: var(--radius-full);
  background-color: var(--color-surface-hover);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: var(--text-tertiary);
  margin-bottom: var(--space-5);
}

.empty-state-title {
  font-size: var(--text-md);
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-2) 0;
}

.empty-state-description {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0 0 var(--space-5) 0;
  max-width: 320px;
  line-height: var(--leading-relaxed);
}

.empty-state-action {
  display: flex;
  gap: var(--space-3);
}
</style>
