<template>
  <div v-if="show" class="confirm-dialog-backdrop" @click.self="$emit('cancel')">
    <div class="confirm-dialog" role="dialog" aria-modal="true">
      <div class="confirm-dialog-header">
        <h3 class="confirm-dialog-title">{{ title }}</h3>
        <button class="confirm-dialog-close" @click="$emit('cancel')" aria-label="Close">
          <i class="bi bi-x-lg"></i>
        </button>
      </div>
      <div class="confirm-dialog-body">
        <p>{{ message }}</p>
        <slot />
      </div>
      <div class="confirm-dialog-footer">
        <button class="btn btn-secondary" @click="$emit('cancel')" :disabled="loading">Cancel</button>
        <button
          class="btn"
          :class="`btn-${confirmVariant}`"
          @click="$emit('confirm')"
          :disabled="loading"
        >
          <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
          {{ confirmText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  show: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    required: true
  },
  message: {
    type: String,
    required: true
  },
  confirmText: {
    type: String,
    default: 'Confirm'
  },
  confirmVariant: {
    type: String,
    default: 'primary'
  },
  loading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['confirm', 'cancel'])
</script>

<style scoped>
.confirm-dialog-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: var(--space-4);
}

.confirm-dialog {
  background-color: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  width: 100%;
  max-width: 480px;
  overflow: hidden;
}

.confirm-dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--color-border);
}

.confirm-dialog-title {
  font-size: var(--text-md);
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
  margin: 0;
}

.confirm-dialog-close {
  background: none;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  padding: var(--space-1);
  font-size: var(--text-sm);
  transition: color var(--duration-base) var(--ease-default);
}

.confirm-dialog-close:hover {
  color: var(--text-primary);
}

.confirm-dialog-body {
  padding: var(--space-5);
}

.confirm-dialog-body p {
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
}

.confirm-dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-5);
  border-top: 1px solid var(--color-border);
}
</style>
