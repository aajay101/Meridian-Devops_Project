<template>
  <div class="export-button-wrapper">
    <button
      v-if="status === 'idle'"
      class="btn btn-outline-primary btn-sm"
      @click="handleExport"
      :disabled="false"
    >
      <i class="bi bi-download me-1"></i> Export CSV
    </button>

    <button
      v-else-if="status === 'queued' || status === 'PENDING' || status === 'STARTED' || status === 'RETRY'"
      class="btn btn-outline-secondary btn-sm"
      disabled
    >
      <span class="spinner-border spinner-border-sm me-1" role="status"></span>
      Processing...
    </button>

    <a
      v-else-if="status === 'SUCCESS'"
      :href="downloadUrl"
      class="btn btn-success btn-sm"
      @click="resetState"
    >
      <i class="bi bi-check-circle me-1"></i> Download CSV
    </a>

    <button
      v-else-if="status === 'FAILURE'"
      class="btn btn-outline-danger btn-sm"
      @click="handleExport"
    >
      <i class="bi bi-arrow-repeat me-1"></i> Retry
    </button>

    <span v-if="recordCount !== null" class="export-meta ms-2">
      {{ recordCount }} record{{ recordCount !== 1 ? 's' : '' }}
    </span>

    <div v-if="errorMessage" class="export-error mt-1">
      <small class="text-danger">{{ errorMessage }}</small>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { triggerExport, getExportStatus, getExportDownloadUrl } from '@/api/student'

const MAX_POLLS = 150

const status = ref('idle')
const taskId = ref(null)
const recordCount = ref(null)
const errorMessage = ref('')
let pollInterval = null
let pollCount = 0

const downloadUrl = ref('')

const handleExport = async () => {
  errorMessage.value = ''
  recordCount.value = null

  try {
    const res = await triggerExport()
    if (res.data.success) {
      taskId.value = res.data.task_id
      status.value = res.data.status || 'PENDING'
      startPolling()
    }
  } catch (err) {
    const code = err.response?.data?.error
    if (code === 'celery_queue_failed') {
      errorMessage.value = 'Export service is temporarily unavailable. Please try again later.'
    } else if (code === 'no_student_profile') {
      errorMessage.value = 'No student profile found.'
    } else {
      errorMessage.value = 'Failed to start export. Please try again.'
    }
    status.value = 'idle'
  }
}

const startPolling = () => {
  stopPolling()
  pollCount = 0
  pollInterval = setInterval(async () => {
    if (!taskId.value) return
    pollCount++
    if (pollCount > MAX_POLLS) {
      stopPolling()
      status.value = 'idle'
      errorMessage.value = 'Export is taking longer than expected.'
      return
    }
    try {
      const res = await getExportStatus(taskId.value)
      const data = res.data
      status.value = data.status

      if (data.status === 'SUCCESS') {
        recordCount.value = data.record_count
        downloadUrl.value = getExportDownloadUrl(taskId.value)
        stopPolling()
      } else if (data.status === 'FAILURE') {
        errorMessage.value = data.error || 'Export failed.'
        stopPolling()
      }
    } catch (err) {
      stopPolling()
      status.value = 'idle'
      errorMessage.value = 'Failed to check export status.'
    }
  }, 2000)
}

const stopPolling = () => {
  if (pollInterval) {
    clearInterval(pollInterval)
    pollInterval = null
  }
}

const resetState = () => {
  setTimeout(() => {
    status.value = 'idle'
    taskId.value = null
    recordCount.value = null
    errorMessage.value = ''
  }, 3000)
}

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.export-button-wrapper {
  display: inline-flex;
  align-items: center;
  flex-wrap: wrap;
}

.export-meta {
  font-size: var(--text-xs);
  color: var(--text-secondary);
}

.export-error {
  width: 100%;
}
</style>
