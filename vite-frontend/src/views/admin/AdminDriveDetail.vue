<template>
  <div>
    <router-link to="/admin/drives" class="back-link">
      <i class="bi bi-arrow-left"></i> Back to Drives
    </router-link>

    <div v-if="loading" class="detail-grid">
      <div class="skeleton-card" style="height: 280px"></div>
      <div class="skeleton-card" style="height: 220px"></div>
    </div>

    <template v-else-if="drive">
      <PageHeader :title="drive.job_title" :subtitle="drive.company_name" />

      <div class="detail-grid mb-4">
        <div>
          <SectionCard title="Drive Information">
            <div class="detail-info-grid">
              <div class="detail-info-field">
                <span class="detail-info-label">Status</span>
                <StatusBadge :status="drive.status" />
              </div>
              <div class="detail-info-field">
                <span class="detail-info-label">Created</span>
                <span class="detail-info-value data-value">{{ formatDate(drive.created_at) }}</span>
              </div>
              <div class="detail-info-field">
                <span class="detail-info-label">Application Deadline</span>
                <span class="detail-info-value data-value" :class="isPastDeadline(drive.application_deadline) ? 'deadline-urgent' : ''">
                  <i v-if="isPastDeadline(drive.application_deadline)" class="bi bi-exclamation-circle me-1"></i>
                  {{ formatDate(drive.application_deadline) }}
                </span>
              </div>
            </div>
          </SectionCard>

          <SectionCard v-if="drive.job_description" title="Job Description" class="mt-4">
            <pre class="job-description">{{ drive.job_description }}</pre>
          </SectionCard>
        </div>
        <div>
          <SectionCard title="Eligibility Criteria">
            <div class="detail-info-grid">
              <div class="detail-info-field">
                <span class="detail-info-label">Branches</span>
                <span class="detail-info-value data-value">{{ drive.eligibility_branches.join(', ') }}</span>
              </div>
              <div class="detail-info-field">
                <span class="detail-info-label">Minimum CGPA</span>
                <span class="detail-info-value data-value">{{ drive.eligibility_cgpa }}</span>
              </div>
              <div class="detail-info-field">
                <span class="detail-info-label">Year</span>
                <span class="detail-info-value data-value">{{ drive.eligibility_year }}</span>
              </div>
              <div class="detail-info-field">
                <span class="detail-info-label">Year Mode</span>
                <span class="detail-info-value data-value">{{ drive.eligibility_year_mode === 'minimum' ? 'This Year & Above' : 'This Year Only' }}</span>
              </div>
            </div>
          </SectionCard>
        </div>
      </div>

      <div class="action-bar">
        <template v-if="drive.status === 'Pending'">
          <button class="btn btn-success" @click="confirmAction('approve')" :disabled="submitting">
            <i class="bi bi-check-lg me-1"></i> Approve
          </button>
          <button class="btn btn-danger" @click="confirmAction('reject')" :disabled="submitting">
            <i class="bi bi-x-lg me-1"></i> Reject
          </button>
        </template>
        <template v-else-if="drive.status === 'Approved'">
          <button class="btn btn-secondary" @click="confirmAction('close')" :disabled="submitting">
            <i class="bi bi-x-circle me-1"></i> Close
          </button>
        </template>
      </div>
    </template>

    <ConfirmDialog
      :show="dialog.open"
      :title="dialogTitle"
      :message="dialogMessage"
      :confirm-text="dialogConfirmText"
      :confirm-variant="dialogConfirmVariant"
      :loading="submitting"
      @confirm="executeAction"
      @cancel="dialog.open = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getDrive, approveDrive, rejectDrive, closeDrive } from '@/api/admin'
import PageHeader from '@/components/common/PageHeader.vue'
import SectionCard from '@/components/common/SectionCard.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'

const route = useRoute()
const router = useRouter()
const drive = ref(null)
const loading = ref(false)
const submitting = ref(false)
const dialog = ref({ open: false, action: null })

const dialogTitle = computed(() => {
  const map = { approve: 'Approve Drive', reject: 'Reject Drive', close: 'Close Drive' }
  return map[dialog.value.action] || ''
})

const dialogMessage = computed(() => {
  const title = drive.value?.job_title || ''
  const map = {
    approve: `Are you sure you want to approve "${title}"?`,
    reject: `Are you sure you want to reject "${title}"?`,
    close: `Are you sure you want to close "${title}"?`
  }
  return map[dialog.value.action] || ''
})

const dialogConfirmText = computed(() => {
  const map = { approve: 'Approve', reject: 'Reject', close: 'Close' }
  return map[dialog.value.action] || 'Confirm'
})

const dialogConfirmVariant = computed(() => {
  const map = { approve: 'success', reject: 'danger', close: 'secondary' }
  return map[dialog.value.action] || 'primary'
})

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

const isPastDeadline = (dateStr) => {
  if (!dateStr) return false
  return new Date(dateStr) < new Date()
}

const confirmAction = (action) => {
  dialog.value = { open: true, action }
}

const executeAction = async () => {
  submitting.value = true
  try {
    const id = route.params.id
    const map = { approve: approveDrive, reject: rejectDrive, close: closeDrive }
    await map[dialog.value.action](id)
    dialog.value.open = false
    await fetchData()
  } catch (err) {
    // error handled silently
  } finally {
    submitting.value = false
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getDrive(route.params.id)
    if (res.data.success) {
      drive.value = res.data.drive
    } else {
      router.push('/admin/drives')
    }
  } catch (err) {
    router.push('/admin/drives')
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.job-description {
  font-family: var(--font-family);
  font-size: var(--text-sm);
  color: var(--text-primary);
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
  background: none;
  border: none;
  line-height: var(--leading-relaxed);
}
</style>
