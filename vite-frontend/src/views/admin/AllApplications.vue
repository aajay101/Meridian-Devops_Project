<template>
  <div>
    <PageHeader title="All Applications" subtitle="View all student applications" />

    <SectionCard>
      <div class="table-toolbar">
        <div></div>
        <input
          v-model="query"
          type="text"
          class="form-control form-control-sm search-input"
          placeholder="Search applications..."
        />
      </div>

      <div v-if="loading" class="table-skeleton">
        <div v-for="n in 5" :key="n" class="skeleton-row"></div>
      </div>

      <div v-else-if="error" class="text-center py-5">
        <div class="alert alert-danger" role="alert">{{ error }}</div>
      </div>

      <div v-else-if="filteredApplications.length === 0" class="text-center py-5">
        <EmptyState icon="bi bi-file-text" title="No applications" description="No student applications have been submitted yet." />
      </div>

      <div v-else class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead>
            <tr>
              <th>Student</th>
              <th>Email</th>
              <th class="d-none d-lg-table-cell">Branch</th>
              <th class="d-none d-lg-table-cell">CGPA</th>
              <th>Company</th>
              <th>Position</th>
              <th>Status</th>
              <th class="d-none d-lg-table-cell">Resume</th>
              <th class="d-none d-lg-table-cell">Applied</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="app in filteredApplications" :key="app.application_id">
              <td class="fw-medium">{{ app.student_name }}</td>
              <td>{{ app.student_email }}</td>
              <td class="d-none d-lg-table-cell">{{ app.branch }}</td>
              <td class="d-none d-lg-table-cell">{{ app.cgpa }}</td>
              <td>{{ app.company_name }}</td>
              <td>{{ app.job_title }}</td>
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
              <td class="d-none d-lg-table-cell">
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
              <td class="d-none d-lg-table-cell">{{ formatDate(app.application_date) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </SectionCard>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getApplications } from '@/api/admin'
import PageHeader from '@/components/common/PageHeader.vue'
import SectionCard from '@/components/common/SectionCard.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const applications = ref([])
const loading = ref(false)
const query = ref('')
const error = ref('')

const filteredApplications = computed(() => {
  if (!query.value.trim()) return applications.value
  const q = query.value.toLowerCase()
  return applications.value.filter(
    (a) =>
      a.student_name.toLowerCase().includes(q) ||
      a.student_email.toLowerCase().includes(q) ||
      a.company_name.toLowerCase().includes(q) ||
      a.job_title.toLowerCase().includes(q) ||
      a.status.toLowerCase().includes(q) ||
      (a.offer_status && a.offer_status.toLowerCase().includes(q))
  )
})

const getResumeUrl = (path) => {
  if (!path) return ''
  return `/${path}`
}

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

const fetchData = async () => {
  loading.value = true
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

onMounted(fetchData)
</script>

<style scoped>
.table-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--color-border);
  margin-bottom: var(--space-4);
}

.search-input {
  width: 280px;
  max-width: 100%;
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

@media (max-width: 575.98px) {
  .table-toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  .search-input {
    width: 100%;
  }
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
