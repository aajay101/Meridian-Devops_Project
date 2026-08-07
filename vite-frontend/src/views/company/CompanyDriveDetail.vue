<template>
  <div>
    <router-link to="/company/drives" class="back-link">
      <i class="bi bi-arrow-left"></i> My Drives
    </router-link>

    <div v-if="loading" class="skeleton-card"></div>

    <template v-else-if="drive">
      <PageHeader :title="drive.job_title" :subtitle="driveStatus">
        <template #action>
          <div v-if="drive.status === 'Pending'" class="d-flex gap-2">
            <router-link :to="`/company/drives/${drive.drive_id}/edit`" class="btn btn-outline-primary btn-sm">
              <i class="bi bi-pencil me-1"></i> Edit
            </router-link>
            <button class="btn btn-outline-danger btn-sm" @click="showDeleteDialog = true">
              <i class="bi bi-trash me-1"></i> Delete
            </button>
          </div>
          <div v-else-if="drive.status === 'Approved'" class="d-flex gap-2">
            <router-link :to="`/company/drives/${drive.drive_id}/applicants`" class="btn btn-primary btn-sm">
              <i class="bi bi-people me-1"></i> View Applicants
            </router-link>
            <button class="btn btn-outline-danger btn-sm" @click="showCloseDialog = true">
              <i class="bi bi-x-circle me-1"></i> Close
            </button>
          </div>
          <div v-else-if="drive.status === 'Closed'" class="d-flex gap-2">
            <router-link :to="`/company/drives/${drive.drive_id}/applicants`" class="btn btn-primary btn-sm">
              <i class="bi bi-people me-1"></i> View Applicants
            </router-link>
          </div>
          <div v-else-if="drive.status === 'Rejected'" class="d-flex gap-2">
            <button class="btn btn-outline-danger btn-sm" @click="showDeleteDialog = true">
              <i class="bi bi-trash me-1"></i> Delete
            </button>
          </div>
        </template>
      </PageHeader>

      <div class="row g-4 mb-4">
        <div class="col-lg-8">
          <SectionCard title="Drive Information">
            <div class="info-grid">
              <div class="info-field">
                <span class="info-label">Job Title</span>
                <span class="info-value">{{ drive.job_title }}</span>
              </div>
              <div class="info-field">
                <span class="info-label">Status</span>
                <StatusBadge :status="drive.status" />
              </div>
              <div class="info-field">
                <span class="info-label">Created</span>
                <span class="info-value">{{ formatDate(drive.created_at) }}</span>
              </div>
            </div>
          </SectionCard>

          <SectionCard v-if="drive.job_description" title="Job Description" class="mt-4">
            <pre class="job-description">{{ drive.job_description }}</pre>
          </SectionCard>
        </div>
        <div class="col-lg-4">
          <SectionCard title="Eligibility Criteria">
            <div class="info-grid">
              <div class="info-field">
                <span class="info-label">Branches</span>
                <span class="info-value">
                  {{ Array.isArray(drive.eligibility_branches) ? drive.eligibility_branches.join(', ') : drive.eligibility_branch }}
                </span>
              </div>
              <div class="info-field">
                <span class="info-label">Minimum CGPA</span>
                <span class="info-value">{{ drive.eligibility_cgpa }}</span>
              </div>
              <div class="info-field">
                <span class="info-label">Year</span>
                <span class="info-value">{{ drive.eligibility_year }}</span>
              </div>
              <div class="info-field">
                <span class="info-label">Year Mode</span>
                <span class="info-value">{{ drive.eligibility_year_mode === 'minimum' ? 'This Year & Above' : 'This Year Only' }}</span>
              </div>
              <div class="info-field">
                <span class="info-label">Application Deadline</span>
                <span class="info-value" :class="{ 'text-danger': isPastDeadline(drive.application_deadline) }">
                  {{ formatDate(drive.application_deadline) }}
                </span>
              </div>
            </div>
          </SectionCard>
        </div>
      </div>
    </template>

    <ConfirmDialog
      :show="showCloseDialog"
      title="Close Drive"
      message="Are you sure you want to close this drive? Students will no longer be able to apply."
      confirm-text="Close Drive"
      confirm-variant="danger"
      :loading="closing"
      @confirm="handleClose"
      @cancel="showCloseDialog = false"
    />

    <ConfirmDialog
      :show="showDeleteDialog"
      title="Delete Drive"
      message="Are you sure you want to delete this drive? This action cannot be undone."
      confirm-text="Delete"
      confirm-variant="danger"
      :loading="deleting"
      @confirm="handleDelete"
      @cancel="showDeleteDialog = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getDrive, closeDrive, deleteDrive } from '@/api/company'
import PageHeader from '@/components/common/PageHeader.vue'
import SectionCard from '@/components/common/SectionCard.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'

const route = useRoute()
const router = useRouter()
const drive = ref(null)
const loading = ref(false)
const showCloseDialog = ref(false)
const showDeleteDialog = ref(false)
const closing = ref(false)
const deleting = ref(false)

const driveStatus = computed(() => {
  if (!drive.value) return ''
  return `Status: ${drive.value.status}`
})

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

const isPastDeadline = (dateStr) => {
  if (!dateStr) return false
  return new Date(dateStr) < new Date()
}

const handleClose = async () => {
  closing.value = true
  try {
    await closeDrive(route.params.id)
    showCloseDialog.value = false
    await fetchData()
  } catch (err) {
    showCloseDialog.value = false
  } finally {
    closing.value = false
  }
}

const handleDelete = async () => {
  deleting.value = true
  try {
    await deleteDrive(route.params.id)
    showDeleteDialog.value = false
    router.push('/company/drives')
  } catch (err) {
    showDeleteDialog.value = false
  } finally {
    deleting.value = false
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getDrive(route.params.id)
    if (res.data.success) {
      drive.value = res.data.drive
    } else {
      router.push('/company/drives')
    }
  } catch (err) {
    router.push('/company/drives')
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.back-link {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  text-decoration: none;
  margin-bottom: var(--space-4);
}

.back-link:hover {
  color: var(--color-primary);
  text-decoration: none;
}

.info-grid {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.info-field {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.info-label {
  font-size: var(--text-xs);
  font-weight: var(--weight-medium);
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.info-value {
  font-size: var(--text-sm);
  color: var(--text-primary);
}

.job-description {
  font-family: var(--font-family);
  font-size: var(--text-sm);
  color: var(--text-primary);
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
  background: none;
  border: none;
}

.skeleton-card {
  height: 200px;
  background: linear-gradient(90deg, var(--color-surface-muted) 25%, var(--color-surface-hover) 50%, var(--color-surface-muted) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-lg);
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
