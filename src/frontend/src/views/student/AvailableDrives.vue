<template>
  <div>
    <PageHeader title="Available Drives" subtitle="Browse and apply to placement drives" />

    <SectionCard>
      <div class="mb-3">
        <input
          v-model="searchQuery"
          type="text"
          class="form-control"
          placeholder="Search by job title, company, or branch..."
          @input="handleSearch"
        />
      </div>

      <div v-if="loading" class="table-skeleton">
        <div v-for="n in 5" :key="n" class="skeleton-row"></div>
      </div>

      <div v-else-if="error" class="alert alert-danger" role="alert">
        {{ error }}
      </div>

      <div v-else-if="drives.length === 0" class="text-center py-5">
        <EmptyState
          icon="bi bi-briefcase"
          title="No drives available"
          description="No placement drives match your search criteria."
        />
      </div>

      <div v-else class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead>
            <tr>
              <th>Job Title</th>
              <th class="d-none d-lg-table-cell">Company</th>
              <th class="d-none d-md-table-cell">Branch</th>
              <th class="d-none d-lg-table-cell">CGPA</th>
              <th class="d-none d-lg-table-cell">Year</th>
              <th class="d-none d-lg-table-cell">Deadline</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="drive in drives" :key="drive.drive_id">
              <td>
                <router-link :to="`/student/drives/${drive.drive_id}`" class="fw-medium text-decoration-none data-value">
                  {{ drive.job_title }}
                </router-link>
                <div class="text-secondary small d-lg-none">{{ drive.company_name }}</div>
              </td>
              <td class="d-none d-lg-table-cell data-value">{{ drive.company_name }}</td>
              <td class="d-none d-md-table-cell data-value">{{ drive.eligibility_branches.join(', ') }}</td>
              <td class="d-none d-lg-table-cell data-value">{{ drive.eligibility_cgpa }}</td>
              <td class="d-none d-lg-table-cell">
                {{ drive.eligibility_year }}
                <span class="text-secondary ms-1">({{ drive.eligibility_year_mode === 'minimum' ? 'min' : 'exact' }})</span>
              </td>
              <td class="d-none d-lg-table-cell data-value" :class="{ 'text-danger': isPastDeadline(drive.application_deadline) }">
                {{ formatDate(drive.application_deadline) }}
              </td>
              <td>
                <span v-if="isApplied(drive.drive_id)" class="badge bg-success">Applied</span>
                <span v-else-if="isPastDeadline(drive.application_deadline)" class="badge bg-secondary">Closed</span>
                <span v-else-if="isEligible(drive)" class="badge bg-primary">Open</span>
                <span v-else class="badge bg-warning text-dark">Ineligible</span>
              </td>
              <td>
                <router-link :to="`/student/drives/${drive.drive_id}`" class="btn btn-outline-primary btn-sm">
                  View
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </SectionCard>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getDrives, getApplications, getProfile } from '@/api/student'
import PageHeader from '@/components/common/PageHeader.vue'
import SectionCard from '@/components/common/SectionCard.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const drives = ref([])
const loading = ref(false)
const error = ref('')
const searchQuery = ref('')
const searchTimeout = ref(null)

const appliedDriveIds = ref(new Set())
const studentProfile = ref(null)

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

const isPastDeadline = (dateStr) => {
  if (!dateStr) return false
  return new Date(dateStr) < new Date()
}

const isApplied = (driveId) => {
  return appliedDriveIds.value.has(driveId)
}

const isEligible = (drive) => {
  if (!studentProfile.value) return false
  const sp = studentProfile.value
  if (!drive.eligibility_branches.includes(sp.branch)) return false
  if (sp.cgpa < drive.eligibility_cgpa) return false
  if (drive.eligibility_year_mode === 'minimum') {
    if (sp.year < drive.eligibility_year) return false
  } else {
    if (sp.year !== drive.eligibility_year) return false
  }
  return true
}

const handleSearch = () => {
  if (searchTimeout.value) clearTimeout(searchTimeout.value)
  searchTimeout.value = setTimeout(() => {
    fetchDrives()
  }, 300)
}

const fetchDrives = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await getDrives(searchQuery.value)
    if (res.data.success) {
      drives.value = res.data.drives
    }
  } catch (err) {
    error.value = 'Failed to load drives. Please try again.'
  } finally {
    loading.value = false
  }
}

const fetchApplications = async () => {
  try {
    const res = await getApplications()
    if (res.data.success) {
      const ids = new Set(res.data.applications.map(a => a.drive_id))
      appliedDriveIds.value = ids
    }
  } catch (err) {
    // silently handle
  }
}

const fetchProfile = async () => {
  try {
    const res = await getProfile()
    if (res.data.success) {
      studentProfile.value = {
        branch: res.data.branch,
        cgpa: res.data.cgpa,
        year: res.data.year
      }
    }
  } catch (err) {
    // silently handle
  }
}

onMounted(async () => {
  loading.value = true
  await Promise.all([fetchDrives(), fetchApplications(), fetchProfile()])
  loading.value = false
})
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

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
