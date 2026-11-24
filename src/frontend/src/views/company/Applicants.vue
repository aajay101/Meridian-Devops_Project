<template>
  <div>
    <router-link :to="`/company/drives/${route.params.id}`" class="back-link">
      <i class="bi bi-arrow-left"></i> Drive Details
    </router-link>

    <PageHeader title="Applicants" :subtitle="subtitle">
      <template #action>
        <span class="badge bg-primary">{{ applicants.length }} applicant{{ applicants.length !== 1 ? 's' : '' }}</span>
      </template>
    </PageHeader>

    <SectionCard>
      <div v-if="loading" class="table-skeleton">
        <div v-for="n in 5" :key="n" class="skeleton-row"></div>
      </div>

      <div v-else-if="applicants.length === 0" class="text-center py-5">
        <EmptyState
          icon="bi bi-people"
          title="No applicants yet"
          description="No students have applied to this drive yet."
        />
      </div>

      <div v-else class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead>
            <tr>
              <th>Student</th>
              <th class="d-none d-lg-table-cell">Branch</th>
              <th class="d-none d-md-table-cell">CGPA</th>
              <th class="d-none d-lg-table-cell">Year</th>
              <th class="d-none d-lg-table-cell">Applied</th>
              <th>Status</th>
              <th>Resume</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="app in applicants" :key="app.application_id">
              <td>
                <div class="fw-medium data-value">{{ app.student_name }}</div>
                <div class="text-secondary small">{{ app.student_email }}</div>
              </td>
              <td class="d-none d-lg-table-cell data-value">{{ app.branch }}</td>
              <td class="d-none d-md-table-cell data-value">{{ app.cgpa }}</td>
              <td class="d-none d-lg-table-cell data-value">{{ app.year }}</td>
              <td class="d-none d-lg-table-cell data-value">{{ formatDate(app.application_date) }}</td>
              <td>
                <StatusBadge :status="app.status" />
                <span
                  v-if="app.status === 'Selected' && app.offer_status && app.offer_status !== 'Pending'"
                  class="offer-status-badge"
                  :class="'offer-status-badge--' + app.offer_status.toLowerCase().replace(' ', '-')"
                >
                  {{ app.offer_status }}
                </span>
              </td>
              <td>
                <a
                  v-if="app.resume_path"
                  :href="getResumeUrl(app.resume_path)"
                  target="_blank"
                  class="btn btn-outline-secondary btn-sm"
                  title="View Resume"
                >
                  <i class="bi bi-file-earmark-pdf"></i>
                </a>
                <span v-else class="text-secondary small">—</span>
              </td>
              <td>
                <div class="d-flex gap-1 flex-wrap">
                  <button
                    v-if="app.status === 'Applied'"
                    class="btn btn-outline-success btn-sm"
                    @click="confirmShortlist(app)"
                    :disabled="acting"
                  >
                    <i class="bi bi-check-lg"></i> Shortlist
                  </button>
                  <button
                    v-if="app.status === 'Shortlisted'"
                    class="btn btn-outline-primary btn-sm"
                    @click="openScheduleInterview(app)"
                    :disabled="acting"
                  >
                    <i class="bi bi-calendar-event"></i> Interview
                  </button>
                  <button
                    v-if="app.status === 'Interview Scheduled'"
                    class="btn btn-outline-success btn-sm"
                    @click="confirmSelect(app)"
                    :disabled="acting"
                  >
                    <i class="bi bi-trophy"></i> Select
                  </button>
                  <button
                    v-if="['Applied', 'Shortlisted', 'Interview Scheduled'].includes(app.status)"
                    class="btn btn-outline-danger btn-sm"
                    @click="confirmReject(app)"
                    :disabled="acting"
                  >
                    <i class="bi bi-x-lg"></i> Reject
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </SectionCard>

    <ConfirmDialog
      :show="dialog.open"
      :title="dialog.title"
      :message="dialog.message"
      :confirm-text="dialog.confirmText"
      :confirm-variant="dialog.confirmVariant"
      :loading="acting"
      @confirm="dialog.onConfirm"
      @cancel="dialog.open = false"
    />

    <div v-if="actionError" class="alert alert-danger mt-3" role="alert">
      {{ actionError }}
    </div>

    <div v-if="showInterviewModal" class="confirm-dialog-backdrop" @click.self="showInterviewModal = false">
      <div class="confirm-dialog" role="dialog" aria-modal="true">
        <div class="confirm-dialog-header">
          <h3 class="confirm-dialog-title">Schedule Interview</h3>
          <button class="confirm-dialog-close" @click="showInterviewModal = false" aria-label="Close">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
        <div class="confirm-dialog-body">
          <p class="mb-3">Schedule an interview for <strong>{{ interviewTarget?.student_name }}</strong></p>
          <div class="mb-3">
            <label for="interview_datetime" class="form-label">Date &amp; Time <span class="text-danger">*</span></label>
            <input
              id="interview_datetime"
              v-model="interviewForm.datetime"
              type="datetime-local"
              class="form-control"
              :class="{ 'is-invalid': interviewErrors.datetime }"
            />
            <div v-if="interviewErrors.datetime" class="invalid-feedback">{{ interviewErrors.datetime }}</div>
          </div>
          <div class="mb-3">
            <label for="interview_location" class="form-label">Location</label>
            <input
              id="interview_location"
              v-model="interviewForm.location"
              type="text"
              class="form-control"
              placeholder="e.g. Conference Room A or Zoom link"
            />
          </div>
          <div v-if="interviewErrors.submit" class="alert alert-danger" role="alert">
            {{ interviewErrors.submit }}
          </div>
        </div>
        <div class="confirm-dialog-footer">
          <button class="btn btn-secondary" @click="showInterviewModal = false" :disabled="acting">Cancel</button>
          <button class="btn btn-primary" @click="handleScheduleInterview" :disabled="acting">
            <span v-if="acting" class="spinner-border spinner-border-sm me-2" role="status"></span>
            {{ acting ? 'Scheduling...' : 'Schedule' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  getDrive,
  getApplicants,
  shortlistApplicant,
  rejectApplicant,
  scheduleInterview,
  selectApplicant,
  getDashboard
} from '@/api/company'
import PageHeader from '@/components/common/PageHeader.vue'
import SectionCard from '@/components/common/SectionCard.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'

const route = useRoute()
const router = useRouter()

const drive = ref(null)
const applicants = ref([])
const loading = ref(false)
const acting = ref(false)
const actionError = ref('')

const dialog = reactive({
  open: false,
  title: '',
  message: '',
  confirmText: '',
  confirmVariant: 'primary',
  onConfirm: () => {}
})

const showInterviewModal = ref(false)
const interviewTarget = ref(null)
const interviewForm = reactive({ datetime: '', location: '' })
const interviewErrors = reactive({ datetime: '', submit: '' })

const subtitle = computed(() => {
  if (!drive.value) return ''
  return drive.value.job_title
})

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

const getResumeUrl = (path) => {
  if (!path) return ''
  return `/${path}`
}

const openDialog = ({ title, message, confirmText, confirmVariant, onConfirm }) => {
  dialog.title = title
  dialog.message = message
  dialog.confirmText = confirmText
  dialog.confirmVariant = confirmVariant
  dialog.onConfirm = onConfirm
  dialog.open = true
}

const confirmShortlist = (app) => {
  openDialog({
    title: 'Shortlist Applicant',
    message: `Shortlist ${app.student_name}? They will move to the next stage.`,
    confirmText: 'Shortlist',
    confirmVariant: 'success',
    onConfirm: () => handleShortlist(app)
  })
}

const confirmReject = (app) => {
  openDialog({
    title: 'Reject Applicant',
    message: `Reject ${app.student_name}? This action cannot be undone.`,
    confirmText: 'Reject',
    confirmVariant: 'danger',
    onConfirm: () => handleReject(app)
  })
}

const confirmSelect = (app) => {
  openDialog({
    title: 'Select Applicant',
    message: `Select ${app.student_name}? They will be marked as selected for this drive.`,
    confirmText: 'Select',
    confirmVariant: 'success',
    onConfirm: () => handleSelect(app)
  })
}

const openScheduleInterview = (app) => {
  interviewTarget.value = app
  interviewForm.datetime = ''
  interviewForm.location = ''
  interviewErrors.datetime = ''
  interviewErrors.submit = ''
  showInterviewModal.value = true
}

const refreshAll = async () => {
  const driveId = route.params.id
  try {
    const [appRes] = await Promise.all([
      getApplicants(driveId),
      getDashboard().catch(() => {})
    ])
    if (appRes.data.success) {
      applicants.value = appRes.data.applicants
    }
  } catch (err) {
    // silently handle
  }
}

const handleShortlist = async (app) => {
  acting.value = true
  actionError.value = ''
  try {
    await shortlistApplicant(app.application_id)
    dialog.open = false
    await refreshAll()
  } catch (err) {
    const code = err.response?.data?.error
    if (code === 'already_finalized') {
      actionError.value = 'This applicant is no longer eligible for shortlisting.'
    } else {
      actionError.value = 'Failed to shortlist applicant. Please try again.'
    }
  } finally {
    acting.value = false
  }
}

const handleReject = async (app) => {
  acting.value = true
  actionError.value = ''
  try {
    await rejectApplicant(app.application_id)
    dialog.open = false
    await refreshAll()
  } catch (err) {
    const code = err.response?.data?.error
    if (code === 'already_finalized') {
      actionError.value = 'This applicant is no longer eligible for rejection.'
    } else {
      actionError.value = 'Failed to reject applicant. Please try again.'
    }
  } finally {
    acting.value = false
  }
}

const handleSelect = async (app) => {
  acting.value = true
  actionError.value = ''
  try {
    await selectApplicant(app.application_id)
    dialog.open = false
    await refreshAll()
  } catch (err) {
    const code = err.response?.data?.error
    if (code === 'max_offers_reached') {
      actionError.value = 'Maximum active offers reached for this student. They must accept or decline an existing offer first.'
    } else if (code === 'already_finalized') {
      actionError.value = 'This applicant is no longer eligible for selection.'
    } else {
      actionError.value = 'Failed to select applicant. Please try again.'
    }
  } finally {
    acting.value = false
  }
}

const handleScheduleInterview = async () => {
  interviewErrors.datetime = ''
  interviewErrors.submit = ''

  if (!interviewForm.datetime) {
    interviewErrors.datetime = 'Date and time are required'
    return
  }

  const dt = new Date(interviewForm.datetime)
  if (isNaN(dt.getTime())) {
    interviewErrors.datetime = 'Please enter a valid date and time'
    return
  }
  if (dt <= new Date()) {
    interviewErrors.datetime = 'Interview must be scheduled in the future'
    return
  }

  acting.value = true
  try {
    const payload = { interview_datetime: dt.toISOString() }
    if (interviewForm.location.trim()) {
      payload.interview_location = interviewForm.location.trim()
    }
    await scheduleInterview(interviewTarget.value.application_id, payload)
    showInterviewModal.value = false
    await refreshAll()
  } catch (err) {
    const code = err.response?.data?.error
    if (code === 'already_finalized') {
      interviewErrors.submit = 'This applicant is no longer eligible for interview scheduling'
    } else if (code === 'missing_fields') {
      interviewErrors.submit = 'Please fill in all required fields'
    } else {
      interviewErrors.submit = 'An error occurred. Please try again'
    }
  } finally {
    acting.value = false
  }
}

const fetchAll = async () => {
  loading.value = true
  const driveId = route.params.id
  try {
    const [driveRes, appRes] = await Promise.all([
      getDrive(driveId),
      getApplicants(driveId)
    ])
    if (driveRes.data.success) {
      drive.value = driveRes.data.drive
    } else {
      router.push('/company/drives')
      return
    }
    if (appRes.data.success) {
      applicants.value = appRes.data.applicants
    }
  } catch (err) {
    router.push('/company/drives')
  } finally {
    loading.value = false
  }
}

onMounted(fetchAll)
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

.table-skeleton {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.skeleton-row {
  height: 48px;
  background: linear-gradient(90deg, var(--color-surface-muted) 25%, var(--color-surface-hover) 50%, var(--color-surface-muted) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-md);
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

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

.offer-status-badge {
  display: inline-block;
  font-size: var(--text-xs);
  font-weight: var(--weight-medium);
  padding: 2px 8px;
  border-radius: var(--radius-full);
  margin-left: var(--space-2);
  vertical-align: middle;
}

.offer-status-badge--accepted {
  background-color: #d1e7dd;
  color: #0f5132;
}

.offer-status-badge--declined {
  background-color: #fff3cd;
  color: #664d03;
}

.offer-status-badge--auto-declined {
  background-color: #e2e3e5;
  color: #41464b;
}
</style>
