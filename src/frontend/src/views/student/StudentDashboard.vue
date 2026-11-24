<template>
  <div class="student-dashboard">
    <PageHeader
      title="Student Dashboard"
      :subtitle="welcomeMessage"
    />

    <div v-if="loading" class="row g-4 mb-4">
      <div v-for="n in 4" :key="n" class="col-sm-6 col-xl-3">
        <div class="stat-skeleton"></div>
      </div>
    </div>

    <div v-if="loading" class="row g-4 mb-4">
      <div class="col-sm-6 col-xl-3">
        <div class="stat-skeleton"></div>
      </div>
    </div>

    <div v-else-if="error" class="alert alert-danger" role="alert">
      {{ error }}
    </div>

    <template v-else>
      <div class="row g-4 mb-4">
        <div class="col-sm-6 col-xl-3">
          <StatCard label="Total Applications" :value="stats.total" icon="bi bi-file-earmark-text" color="primary" />
        </div>
        <div class="col-sm-6 col-xl-3">
          <StatCard label="Active" :value="stats.active" icon="bi bi-hourglass-split" color="info" />
        </div>
        <div class="col-sm-6 col-xl-3">
          <StatCard label="Interviews" :value="stats.interviews" icon="bi bi-calendar-check" color="success" />
        </div>
        <div class="col-sm-6 col-xl-3">
          <StatCard label="Selected" :value="stats.selected" icon="bi bi-trophy" color="warning" />
        </div>
      </div>

      <div class="row g-4 mb-4">
        <div class="col-sm-6 col-xl-3">
          <StatCard label="Pending Offers" :value="stats.pending_offers" icon="bi bi-envelope-check" color="success" />
        </div>
      </div>

      <div v-if="stats.pending_offers >= stats.max_active_offers && stats.max_active_offers > 0" class="row g-4 mb-4">
        <div class="col-12">
          <div class="alert alert-warning d-flex align-items-center" role="alert">
            <i class="bi bi-exclamation-triangle-fill me-3 fs-5"></i>
            <div>
              <strong>Maximum Active Offers Reached</strong>
              <div class="small mt-1">
                You currently have {{ stats.pending_offers }} pending offers.
                Accept or decline an existing offer before applying to more drives.
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-4 mb-4">
        <div class="col-lg-8">
          <SectionCard title="Recent Applications">
            <div v-if="recentApps.length === 0" class="text-center py-4">
              <EmptyState
                icon="bi bi-file-earmark-text"
                title="No applications yet"
                description="Browse available drives and apply to get started."
              />
            </div>
            <div v-else class="table-responsive">
              <table class="table table-hover align-middle mb-0">
                <thead>
                  <tr>
                    <th>Job Title</th>
                    <th class="d-none d-md-table-cell">Company</th>
                    <th>Status</th>
                    <th class="d-none d-lg-table-cell">Applied</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="app in recentApps" :key="app.application_id">
                    <td>
                      <router-link v-if="app.drive_available !== false" :to="`/student/drives/${app.drive_id}`" class="fw-medium text-decoration-none data-value">
                        {{ app.job_title }}
                      </router-link>
                      <span v-else class="fw-medium data-value">{{ app.job_title }}</span>
                    </td>
                    <td class="d-none d-md-table-cell data-value">{{ app.company_name }}</td>
                    <td><StatusBadge :status="app.status" /></td>
                    <td class="d-none d-lg-table-cell data-value">{{ formatDate(app.application_date) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </SectionCard>
        </div>

        <div class="col-lg-4">
          <SectionCard title="Upcoming Interviews">
            <div v-if="upcomingInterviews.length === 0" class="text-center py-4">
              <EmptyState
                icon="bi bi-calendar-x"
                title="No upcoming interviews"
                description="Interview schedules will appear here once assigned."
              />
            </div>
            <div v-else class="interview-list">
              <div v-for="app in upcomingInterviews" :key="app.application_id" class="interview-item">
                <div class="interview-header">
                  <span class="fw-medium data-value">{{ app.job_title }}</span>
                  <span class="text-secondary small">{{ app.company_name }}</span>
                </div>
                <div class="interview-details">
                  <div class="small">
                    <i class="bi bi-calendar-event me-1"></i>
                    {{ formatDateTime(app.interview_datetime) }}
                  </div>
                  <div v-if="app.interview_location" class="small text-secondary">
                    <i class="bi bi-geo-alt me-1"></i>
                    {{ app.interview_location }}
                  </div>
                </div>
              </div>
            </div>
          </SectionCard>
        </div>
      </div>

      <div class="row g-4">
        <div class="col-12">
          <SectionCard title="Quick Actions">
            <div class="quick-actions">
              <router-link to="/student/drives" class="btn btn-outline-primary">
                <i class="bi bi-briefcase me-2"></i>Browse Drives
              </router-link>
              <router-link to="/student/applications" class="btn btn-outline-primary">
                <i class="bi bi-file-earmark-text me-2"></i>My Applications
              </router-link>
              <router-link to="/student/profile" class="btn btn-outline-primary">
                <i class="bi bi-person me-2"></i>Edit Profile
              </router-link>
              <router-link to="/student/history" class="btn btn-outline-primary">
                <i class="bi bi-clock-history me-2"></i>Placement History
              </router-link>
              <ExportButton />
            </div>
          </SectionCard>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getDashboard, getApplications } from '@/api/student'
import PageHeader from '@/components/common/PageHeader.vue'
import StatCard from '@/components/common/StatCard.vue'
import SectionCard from '@/components/common/SectionCard.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import ExportButton from '@/components/common/ExportButton.vue'

const loading = ref(true)
const dashboardData = ref(null)
const applications = ref([])
const error = ref('')

const welcomeMessage = computed(() => {
  if (!dashboardData.value?.profile) return ''
  return `Welcome back, ${dashboardData.value.profile.name}`
})

const stats = computed(() => {
  if (!dashboardData.value) return { total: 0, active: 0, interviews: 0, selected: 0, pending_offers: 0, max_active_offers: 3 }
  const d = dashboardData.value
  return {
    total: d.total_applications || 0,
    active: (d.applied || 0) + (d.shortlisted || 0),
    interviews: d.interview_scheduled || 0,
    selected: d.selected || 0,
    pending_offers: d.pending_offers || 0,
    max_active_offers: d.max_active_offers || 3
  }
})

const recentApps = computed(() => {
  return applications.value.slice(0, 5)
})

const upcomingInterviews = computed(() => {
  return applications.value
    .filter(a => a.status === 'Interview Scheduled' && a.interview_datetime)
    .sort((a, b) => new Date(a.interview_datetime) - new Date(b.interview_datetime))
})

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

const fetchAll = async () => {
  loading.value = true
  try {
    const [dashRes, appsRes] = await Promise.all([
      getDashboard(),
      getApplications()
    ])
    if (dashRes.data.success) {
      dashboardData.value = dashRes.data
    }
    if (appsRes.data.success) {
      applications.value = appsRes.data.applications
    }
  } catch (err) {
    error.value = 'Failed to load dashboard. Please try again.'
  } finally {
    loading.value = false
  }
}

onMounted(fetchAll)
</script>

<style scoped>
.stat-skeleton {
  height: 96px;
  background: linear-gradient(90deg, var(--color-surface-muted) 25%, var(--color-surface-hover) 50%, var(--color-surface-muted) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-lg);
}

.interview-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.interview-item {
  padding: var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}

.interview-header {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-bottom: var(--space-2);
}

.interview-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.quick-actions {
  display: flex;
  gap: var(--space-3);
  flex-wrap: wrap;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
