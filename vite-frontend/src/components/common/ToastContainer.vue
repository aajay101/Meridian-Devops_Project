<template>
  <Teleport to="body">
    <div class="toast-container" aria-live="polite" aria-label="Notifications">
      <Toast
        v-for="toast in toasts"
        :key="toast.id"
        :show="true"
        :variant="toast.variant"
        :title="toast.title"
        :message="toast.message"
        :duration="toast.duration"
        @close="remove(toast.id)"
      />
    </div>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'
import Toast from './Toast.vue'

const toasts = ref([])
let nextId = 0

const add = ({ variant = 'info', title, message = '', duration = 5000 } = {}) => {
  const id = nextId++
  toasts.value.push({ id, variant, title, message, duration })
  return id
}

const remove = (id) => {
  toasts.value = toasts.value.filter((t) => t.id !== id)
}

const success = (title, message = '') => add({ variant: 'success', title, message })
const error = (title, message = '') => add({ variant: 'error', title, message, duration: 8000 })
const warning = (title, message = '') => add({ variant: 'warning', title, message })
const info = (title, message = '') => add({ variant: 'info', title, message })

defineExpose({ add, remove, success, error, warning, info })
</script>
