<template>
  <div>
    <PageHeader title="All Applications" subtitle="View all student applications">
      <template #action>
        <span class="result-count" v-if="!loading">{{ filteredApplications.length }} applications</span>
      </template>
    </PageHeader>

    <SectionCard>
      <FilterBar
        v-model="activeFilter"
        v-model:searchValue="query"
        :filters="filterOptions"
        searchPlaceholder="Search applications..."
        ariaLabel="Filter applications by status"
      />

      <div v-if="loading" class="table-skeleton">
        <div v-for="n in 5" :key="n" class="skeleton-row"></div>
      </div>

      <div v-else-if="error" class="text-center py-5">
        <EmptyState icon="bi bi-exclamation-triangle" title="Error loading applications" :description="error" />
      </div>

      <div v-else-if="filteredApplications.length === 0" class="text-center py-5">
        <EmptyState icon="bi bi-file-text" title="No applications found" description="No student applications match your current filters.">
          <template #action>
            <button class="btn btn-outline-secondary btn-sm" @click="resetFilters">
              <i class="bi bi-arrow-counterclockwise me-1"></i> Reset Filters
            </button>
          </template>
        </EmptyState>
      </div>

      <div v-else class="table-responsive">
        <table class="data-table" aria-label="Applications list">
          <thead>
            <tr>
              <th scope="col">Student</th>
              <th scope="col" class="d-none d-md-table-cell">Branch</th>
              <th scope="col" class="d-none d-md-table-cell">CGPA</th>
              <th scope="col">Company</th>
              <th scope="col">Position</th>
              <th scope="col">Status</th>
              <th scope="col" class="d-none d-lg-table-cell">Resume</th>
              <th scope="col" class="d-none d-lg-table-cell">Applied</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="app in filteredApplications" :key="app.application_id">
              <td data-label="Student">
                <div class="td-link fw-medium data-value">{{ app.student_name }}</div>
                <div class="td-secondary">{{ app.student_email }}</div>
              </td>
              <td data-label="Branch" class="d-none d-md-table-cell td-secondary data-value">{{ app.branch }}</td>
              <td data-label="CGPA" class="d-none d-md-table-cell td-secondary data-value">{{ app.cgpa }}</td>
              <td data-label="Company" class="td-secondary data-value">{{ app.company_name }}</td>
              <td data-label="Position" class="td-secondary data-value">{{ app.job_title }}</td>
              <td data-label="Status">
                <div class="d-flex align-items-center gap-1">
                  <StatusBadge :status="app.status" />
                  <StatusBadge
                    v-if="app.status === 'Selected' && app.offer_status && app.offer_status !== 'Pending'"
                    :status="app.offer_status"
                  />
                </div>
              </td>
              <td data-label="Resume" class="d-none d-lg-table-cell">
                <a
                  v-if="app.resume_path"
                  :href="getResumeUrl(app.resume_path)"
                  target="_blank"
                  class="btn btn-outline-secondary btn-sm"
                  title="View Resume"
                >
                  <i class="bi bi-file-earmark-pdf"></i>
                </a>
                <span v-else class="td-secondary">—</span>
              </td>
              <td data-label="Applied" class="d-none d-lg-table-cell td-secondary data-value">{{ formatDate(app.application_date) }}</td>
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
import FilterBar from '@/components/common/FilterBar.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const applications = ref([])
const loading = ref(false)
const query = ref('')
const error = ref('')
const activeFilter = ref('all')

const filterOptions = computed(() => [
  { key: 'all', label: 'All', count: applications.value.length },
  { key: 'Applied', label: 'Applied', count: applications.value.filter((a) => a.status === 'Applied').length },
  { key: 'Shortlisted', label: 'Shortlisted', count: applications.value.filter((a) => a.status === 'Shortlisted').length },
  { key: 'Selected', label: 'Selected', count: applications.value.filter((a) => a.status === 'Selected').length },
  { key: 'Rejected', label: 'Rejected', count: applications.value.filter((a) => a.status === 'Rejected').length }
])

const filteredApplications = computed(() => {
  let list = applications.value
  if (activeFilter.value !== 'all') {
    list = list.filter((a) => a.status === activeFilter.value)
  }
  if (query.value.trim()) {
    const q = query.value.toLowerCase()
    list = list.filter(
      (a) =>
        a.student_name.toLowerCase().includes(q) ||
        a.student_email.toLowerCase().includes(q) ||
        a.company_name.toLowerCase().includes(q) ||
        a.job_title.toLowerCase().includes(q) ||
        (a.offer_status && a.offer_status.toLowerCase().includes(q))
    )
  }
  return list
})

const getResumeUrl = (path) => {
  if (!path) return ''
  return `/${path}`
}

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

const resetFilters = () => {
  activeFilter.value = 'all'
  query.value = ''
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
.result-count {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  font-weight: var(--weight-medium);
}
</style>
