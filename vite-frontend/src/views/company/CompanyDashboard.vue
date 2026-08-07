<template>
  <div class="company-dashboard">
    <PageHeader title="Dashboard" subtitle="Overview of your placement activity" />

    <div v-if="loading" class="row g-4 mb-4">
      <div v-for="n in 4" :key="n" class="col-sm-6 col-xl-3">
        <div class="skeleton-card"></div>
      </div>
    </div>

    <div v-else-if="error" class="alert alert-danger d-flex align-items-center" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      <div>{{ error }}</div>
    </div>

    <template v-else>
      <div class="row g-4 mb-4">
        <div class="col-sm-6 col-xl-3">
          <StatCard label="Total Drives" :value="stats.total_drives" icon="bi bi-briefcase-fill" color="primary" />
        </div>
        <div class="col-sm-6 col-xl-3">
          <StatCard label="Active Drives" :value="stats.approved_drives" icon="bi bi-check-circle-fill" color="success" />
        </div>
        <div class="col-sm-6 col-xl-3">
          <StatCard label="Pending Approval" :value="stats.pending_drives" icon="bi bi-clock-fill" color="warning" />
        </div>
        <div class="col-sm-6 col-xl-3">
          <StatCard label="Total Applicants" :value="stats.total_applicants" icon="bi bi-people-fill" color="info" />
        </div>
      </div>

      <div class="row g-4">
        <div class="col-lg-8">
          <SectionCard title="Recent Drives">
            <div v-if="stats.recent_drives.length === 0" class="text-center py-4">
              <EmptyState
                icon="bi bi-briefcase"
                title="No drives yet"
                description="Create your first placement drive to start hiring."
              >
                <template #action>
                  <router-link to="/company/drives/new" class="btn btn-primary btn-sm">
                    <i class="bi bi-plus-lg me-1"></i> Create Drive
                  </router-link>
                </template>
              </EmptyState>
            </div>
            <div v-else class="table-responsive">
              <table class="table table-hover align-middle mb-0">
                <thead>
                  <tr>
                    <th>Job Title</th>
                    <th>Status</th>
                    <th class="d-none d-md-table-cell">Deadline</th>
                    <th class="d-none d-md-table-cell">Applicants</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="drive in stats.recent_drives" :key="drive.drive_id">
                    <td>
                      <router-link :to="`/company/drives/${drive.drive_id}`" class="fw-medium text-decoration-none">
                        {{ drive.job_title }}
                      </router-link>
                    </td>
                    <td><StatusBadge :status="drive.status" /></td>
                    <td class="d-none d-md-table-cell" :class="{ 'text-danger': isPastDeadline(drive.application_deadline) }">
                      {{ formatDate(drive.application_deadline) }}
                    </td>
                    <td class="d-none d-md-table-cell">{{ drive.applicants }}</td>
                    <td>
                      <router-link :to="`/company/drives/${drive.drive_id}`" class="btn btn-outline-primary btn-sm">
                        View
                      </router-link>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </SectionCard>
        </div>

        <div class="col-lg-4">
          <SectionCard title="Quick Actions">
            <div class="quick-actions">
              <router-link to="/company/drives/new" class="btn btn-primary w-100">
                <i class="bi bi-plus-circle me-2"></i> Create New Drive
              </router-link>
              <router-link to="/company/drives" class="btn btn-outline-primary w-100">
                <i class="bi bi-briefcase me-2"></i> View All Drives
              </router-link>
              <router-link to="/company/profile" class="btn btn-outline-primary w-100">
                <i class="bi bi-building me-2"></i> Edit Profile
              </router-link>
            </div>
          </SectionCard>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getDashboard } from '@/api/company'
import PageHeader from '@/components/common/PageHeader.vue'
import StatCard from '@/components/common/StatCard.vue'
import SectionCard from '@/components/common/SectionCard.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const stats = ref({
  total_drives: 0,
  approved_drives: 0,
  pending_drives: 0,
  closed_drives: 0,
  total_applicants: 0,
  recent_drives: []
})
const loading = ref(true)
const error = ref('')

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

const isPastDeadline = (dateStr) => {
  if (!dateStr) return false
  return new Date(dateStr) < new Date()
}

onMounted(async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await getDashboard()
    if (res.data.success) {
      stats.value = res.data
    } else {
      error.value = 'Failed to load dashboard data.'
    }
  } catch (err) {
    error.value = 'Unable to connect to server. Please try again later.'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.quick-actions {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.skeleton-card {
  height: 88px;
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
