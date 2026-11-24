<template>
  <div
    v-if="visible"
    class="toast"
    :class="[`toast--${variant}`, { 'toast-exiting': exiting }]"
    role="alert"
    :aria-live="variant === 'error' ? 'assertive' : 'polite'"
  >
    <div class="toast-icon">
      <i :class="iconClass"></i>
    </div>
    <div class="toast-content">
      <div class="toast-title">{{ title }}</div>
      <div v-if="message" class="toast-message">{{ message }}</div>
    </div>
    <button class="toast-close" @click="dismiss" aria-label="Dismiss notification">
      <i class="bi bi-x-lg"></i>
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  variant: {
    type: String,
    default: 'info',
    validator: (v) => ['success', 'error', 'warning', 'info'].includes(v)
  },
  title: {
    type: String,
    required: true
  },
  message: {
    type: String,
    default: ''
  },
  duration: {
    type: Number,
    default: 5000
  }
})

const emit = defineEmits(['close'])

const visible = ref(false)
const exiting = ref(false)
let timer = null

const iconClass = computed(() => {
  const icons = {
    success: 'bi bi-check-circle-fill',
    error: 'bi bi-x-circle-fill',
    warning: 'bi bi-exclamation-triangle-fill',
    info: 'bi bi-info-circle-fill'
  }
  return icons[props.variant] || icons.info
})

const dismiss = () => {
  exiting.value = true
  setTimeout(() => {
    visible.value = false
    exiting.value = false
    emit('close')
  }, 150)
}

onMounted(() => {
  if (props.show) {
    visible.value = true
    if (props.duration > 0) {
      timer = setTimeout(dismiss, props.duration)
    }
  }
})

onUnmounted(() => {
  if (timer) clearTimeout(timer)
})
</script>
