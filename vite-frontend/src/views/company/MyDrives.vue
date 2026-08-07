<template>
  <div>
    <PageHeader title="My Drives" subtitle="Manage your placement drives">
      <template #action>
        <router-link to="/company/drives/new" class="btn btn-primary btn-sm">
          <i class="bi bi-plus-lg me-1"></i> New Drive
        </router-link>
      </template>
    </PageHeader>

    <SectionCard>
      <div v-if="loading" class="table-skeleton">
        <div v-for="n in 5" :key="n" class="skeleton-row"></div>
      </div>

      <div v-else-if="drives.length === 0" class="text-center py-5">
        <EmptyState
          icon="bi bi-briefcase"
          title="No drives yet"
          description="Create your first placement drive to get started."
        />
      </div>

      <div v-else class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead>
            <tr>
              <th>Job Title</th>
              <th class="d-none d-lg-table-cell">Branch</th>
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
                <router-link :to="`/company/drives/${drive.drive_id}`" class="fw-medium text-decoration-none">
                  {{ drive.job_title }}
                </router-link>
              </td>
              <td class="d-none d-lg-table-cell">
                {{ Array.isArray(drive.eligibility_branches) ? drive.eligibility_branches.join(', ') : drive.eligibility_branch }}
              </td>
              <td class="d-none d-lg-table-cell">{{ drive.eligibility_cgpa }}</td>
              <td class="d-none d-lg-table-cell">
                {{ drive.eligibility_year }}
                <span class="text-secondary ms-1">({{ drive.eligibility_year_mode === 'minimum' ? 'min+' : 'exact' }})</span>
              </td>
              <td class="d-none d-lg-table-cell" :class="{ 'text-danger': isPastDeadline(drive.application_deadline) }">
                {{ formatDate(drive.application_deadline) }}
              </td>
              <td><StatusBadge :status="drive.status" /></td>
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
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getDrives } from '@/api/company'
import PageHeader from '@/components/common/PageHeader.vue'
import SectionCard from '@/components/common/SectionCard.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const drives = ref([])
const loading = ref(false)

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

const isPastDeadline = (dateStr) => {
  if (!dateStr) return false
  return new Date(dateStr) < new Date()
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getDrives()
    if (res.data.success) {
      drives.value = res.data.drives
    }
  } catch (err) {
    // drives remain empty on error
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
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
