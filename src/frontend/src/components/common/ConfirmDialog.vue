<template>
  <Teleport to="body">
    <div
      v-if="show"
      class="confirm-dialog-backdrop"
      @click.self="$emit('cancel')"
      @keydown.escape="$emit('cancel')"
    >
      <div
        class="confirm-dialog"
        role="alertdialog"
        aria-modal="true"
        :aria-labelledby="titleId"
        :aria-describedby="descId"
        ref="dialogRef"
      >
        <div class="confirm-dialog-header">
          <h3 :id="titleId" class="confirm-dialog-title">{{ title }}</h3>
          <button class="confirm-dialog-close" @click="$emit('cancel')" aria-label="Close">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
        <div class="confirm-dialog-body">
          <p :id="descId">{{ message }}</p>
          <slot />
        </div>
        <div class="confirm-dialog-footer">
          <button class="btn btn-secondary" @click="$emit('cancel')" :disabled="loading" ref="cancelBtnRef">Cancel</button>
          <button
            class="btn"
            :class="`btn-${confirmVariant}`"
            @click="$emit('confirm')"
            :disabled="loading"
          >
            <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            {{ confirmText }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
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

const titleId = `confirm-dialog-title-${Math.random().toString(36).slice(2, 9)}`
const descId = `confirm-dialog-desc-${Math.random().toString(36).slice(2, 9)}`
const cancelBtnRef = ref(null)
const previousFocus = ref(null)

watch(() => props.show, async (val) => {
  if (val) {
    previousFocus.value = document.activeElement
    await nextTick()
    cancelBtnRef.value?.focus()
  } else if (previousFocus.value) {
    previousFocus.value.focus()
    previousFocus.value = null
  }
})
</script>

<style scoped>
.confirm-dialog-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: var(--space-4);
  backdrop-filter: blur(4px);
}

.confirm-dialog {
  background-color: var(--color-surface);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  width: 100%;
  max-width: 440px;
  overflow: hidden;
  animation: dialog-in var(--duration-slow) var(--ease-out);
}

@keyframes dialog-in {
  from {
    opacity: 0;
    transform: scale(0.96) translateY(8px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.confirm-dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--color-border-subtle);
}

.confirm-dialog-title {
  font-size: var(--text-base);
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
  transition: color var(--duration-fast) var(--ease-default);
  border-radius: var(--radius-sm);
}

.confirm-dialog-close:hover {
  color: var(--text-primary);
  background-color: var(--color-surface-hover);
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
  border-top: 1px solid var(--color-border-subtle);
}
</style>
