<template>
  <div>
    <PageHeader title="Applications" subtitle="Track your placement applications">
      <template #action>
        <ExportButton />
      </template>
    </PageHeader>

    <SectionCard>
      <div v-if="loading" class="table-skeleton">
        <div v-for="n in 5" :key="n" class="skeleton-row"></div>
      </div>

      <div v-else-if="error" class="alert alert-danger" role="alert">
        {{ error }}
      </div>

      <div v-else-if="applications.length === 0" class="text-center py-5">
        <EmptyState
          icon="bi bi-file-earmark-text"
          title="No applications yet"
          description="You haven't applied to any drives yet. Browse available drives to get started."
        />
      </div>

      <div v-else class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead>
            <tr>
              <th>Job Title</th>
              <th class="d-none d-lg-table-cell">Company</th>
              <th class="d-none d-md-table-cell">Applied</th>
              <th>Status</th>
              <th>Details</th>
              <th class="d-none d-md-table-cell">Resume</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="app in applications" :key="app.application_id">
              <td>
                <div class="fw-medium">{{ app.job_title }}</div>
                <div class="text-secondary small d-lg-none">{{ app.company_name }}</div>
              </td>
              <td class="d-none d-lg-table-cell">{{ app.company_name }}</td>
              <td class="d-none d-md-table-cell">{{ formatDate(app.application_date) }}</td>
              <td><StatusBadge :status="app.status" /></td>
              <td>
                <div v-if="app.status === 'Interview Scheduled'" class="interview-info">
                  <div class="small">
                    <i class="bi bi-calendar-event me-1"></i>
                    {{ formatDateTime(app.interview_datetime) }}
                  </div>
                  <div v-if="app.interview_location" class="small text-secondary">
                    <i class="bi bi-geo-alt me-1"></i>
                    {{ app.interview_location }}
                  </div>
                </div>
                <div v-else-if="app.status === 'Selected' && app.offer_status === 'Pending'" class="offer-pending">
                  <div class="small fw-medium mb-2">
                    <i class="bi bi-envelope me-1"></i>
                    Offer Pending
                  </div>
                  <div class="d-flex gap-1">
                    <button
                      class="btn btn-success btn-sm"
                      @click="confirmAccept(app)"
                      :disabled="acting"
                    >
                      <i class="bi bi-check-lg"></i> Accept
                    </button>
                    <button
                      class="btn btn-outline-danger btn-sm"
                      @click="confirmDecline(app)"
                      :disabled="acting"
                    >
                      <i class="bi bi-x-lg"></i> Decline
                    </button>
                  </div>
                </div>
                <div v-else-if="app.status === 'Selected' && app.offer_status === 'Accepted'" class="small text-success">
                  <i class="bi bi-check-circle-fill me-1"></i>
                  Accepted
                </div>
                <div v-else-if="app.status === 'Selected' && app.offer_status === 'Declined'" class="small text-warning">
                  <i class="bi bi-x-circle me-1"></i>
                  Declined
                </div>
                <div v-else-if="app.status === 'Selected' && app.offer_status === 'Auto Declined'" class="small text-secondary">
                  <i class="bi bi-arrow-repeat me-1"></i>
                  Auto Declined
                  <div class="text-muted mt-1" style="font-size: 0.75rem;">
                    Accepted another offer.
                  </div>
                </div>
                <div v-else-if="app.status === 'Selected' && app.selection_date" class="small text-success">
                  <i class="bi bi-trophy me-1"></i>
                  Selected {{ formatDate(app.selection_date) }}
                </div>
                <div v-else-if="app.status === 'Rejected' && app.remarks" class="small text-danger">
                  <i class="bi bi-x-circle me-1"></i>
                  {{ app.remarks }}
                </div>
                <span v-else class="text-secondary small">—</span>
              </td>
              <td class="d-none d-md-table-cell">
                <a
                  v-if="app.resume_path"
                  :href="getResumeUrl(app.resume_path)"
                  target="_blank"
                  class="btn btn-outline-secondary btn-sm"
                  title="View submitted resume"
                >
                  <i class="bi bi-file-earmark-pdf"></i>
                </a>
                <span v-else class="text-secondary small">No resume</span>
              </td>
              <td>
                <router-link :to="`/student/drives/${app.drive_id}`" class="btn btn-outline-primary btn-sm">
                  View Drive
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </SectionCard>

    <!-- Confirm Dialog -->
    <div v-if="confirmDialog.show" class="confirm-dialog-backdrop" @click.self="closeConfirmDialog">
      <div class="confirm-dialog" role="dialog" aria-modal="true">
        <div class="confirm-dialog-header">
          <h3 class="confirm-dialog-title">
            {{ confirmDialog.type === 'accept' ? 'Accept Offer' : 'Decline Offer' }}
          </h3>
          <button class="confirm-dialog-close" @click="closeConfirmDialog" aria-label="Close">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
        <div class="confirm-dialog-body">
          <template v-if="confirmDialog.type === 'accept'">
            <p class="mb-2">Accept this offer from <strong>{{ confirmDialog.application?.company_name }}</strong>?</p>
            <p class="text-secondary small mb-0">
              <i class="bi bi-info-circle me-1"></i>
              All other pending offers will automatically be declined.
            </p>
          </template>
          <template v-else>
            <p class="mb-0">Decline this offer from <strong>{{ confirmDialog.application?.company_name }}</strong>?</p>
          </template>
        </div>
        <div class="confirm-dialog-footer">
          <button class="btn btn-secondary" @click="closeConfirmDialog" :disabled="acting">Cancel</button>
          <button
            class="btn"
            :class="confirmDialog.type === 'accept' ? 'btn-success' : 'btn-danger'"
            @click="handleConfirmAction"
            :disabled="acting"
          >
            <span v-if="acting" class="spinner-border spinner-border-sm me-2" role="status"></span>
            {{ acting ? 'Processing...' : (confirmDialog.type === 'accept' ? 'Accept Offer' : 'Decline Offer') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getApplications, acceptOffer, declineOffer } from '@/api/student'
import PageHeader from '@/components/common/PageHeader.vue'
import SectionCard from '@/components/common/SectionCard.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import ExportButton from '@/components/common/ExportButton.vue'

const applications = ref([])
const loading = ref(false)
const error = ref('')
const acting = ref(false)
const confirmDialog = ref({ show: false, type: '', application: null })

const getResumeUrl = (path) => {
  if (!path) return ''
  return `/${path}`
}

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

const fetchApplications = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await getApplications()
    if (res.data.success) {
      applications.value = res.data.applications
    }
  } catch (err) {
    error.value = 'Failed to load applications. Please try again.'
  } finally {
    loading.value = false
  }
}

const confirmAccept = (app) => {
  confirmDialog.value = { show: true, type: 'accept', application: app }
}

const confirmDecline = (app) => {
  confirmDialog.value = { show: true, type: 'decline', application: app }
}

const closeConfirmDialog = () => {
  confirmDialog.value = { show: false, type: '', application: null }
}

const handleConfirmAction = async () => {
  const { type, application } = confirmDialog.value
  if (!application) return

  acting.value = true
  try {
    if (type === 'accept') {
      await acceptOffer(application.application_id)
    } else {
      await declineOffer(application.application_id)
    }
    closeConfirmDialog()
    await fetchApplications()
  } catch (err) {
    error.value = err.response?.data?.error === 'offer_not_pending'
      ? 'This offer is no longer pending.'
      : 'An error occurred. Please try again.'
    closeConfirmDialog()
  } finally {
    acting.value = false
  }
}

onMounted(fetchApplications)
</script>

<style scoped>
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

.interview-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.offer-pending {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
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
  max-width: 440px;
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

.confirm-dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-5);
  border-top: 1px solid var(--color-border);
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
