<template>
  <div>
    <PageHeader title="Placement History" subtitle="Your complete placement opportunity history" />

    <SectionCard>
      <div v-if="loading" class="table-skeleton">
        <div v-for="n in 5" :key="n" class="skeleton-row"></div>
      </div>

      <div v-else-if="error" class="alert alert-danger" role="alert">
        {{ error }}
      </div>

      <div v-else-if="placements.length === 0" class="text-center py-5">
        <EmptyState
          icon="bi bi-trophy"
          title="No placement history yet"
          description="Expired placement opportunities and applications will appear here."
        />
      </div>

      <div v-else class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead>
            <tr>
              <th>Company</th>
              <th>Job Title</th>
              <th class="d-none d-md-table-cell">Deadline</th>
              <th class="d-none d-lg-table-cell">Selected On</th>
              <th>Status</th>
              <th>Offer Status</th>
              <th class="d-none d-lg-table-cell">Remarks</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in placements" :key="p.application_id || `drive-${p.drive_id}`">
              <td class="fw-medium data-value">{{ p.company_name }}</td>
              <td class="data-value">{{ p.job_title }}</td>
              <td class="d-none d-md-table-cell data-value">{{ formatDate(p.application_deadline) }}</td>
              <td class="d-none d-lg-table-cell data-value">{{ formatDate(p.selection_date) }}</td>
              <td><StatusBadge :status="p.status" /></td>
              <td>
                <StatusBadge v-if="p.offer_status" :status="p.offer_status" />
                <span v-else class="text-secondary small">—</span>
              </td>
              <td class="d-none d-lg-table-cell">
                <span v-if="p.remarks" class="text-secondary">{{ p.remarks }}</span>
                <span v-else class="text-tertiary">—</span>
              </td>
              <td>
                <router-link v-if="p.drive_available !== false" :to="`/student/drives/${p.drive_id}`" class="btn btn-outline-primary btn-sm">
                  View Drive
                </router-link>
                <span v-else class="text-secondary small">
                  {{ p.drive_status === 'Closed' ? 'Drive closed' : 'Deadline passed' }}
                </span>
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
import { getPlacementHistory } from '@/api/student'
import PageHeader from '@/components/common/PageHeader.vue'
import SectionCard from '@/components/common/SectionCard.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const placements = ref([])
const loading = ref(false)
const error = ref('')

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

const fetchPlacementHistory = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await getPlacementHistory()
    if (res.data.success) {
      placements.value = res.data.placement_history
    }
  } catch (err) {
    error.value = 'Failed to load placement history. Please try again.'
  } finally {
    loading.value = false
  }
}

onMounted(fetchPlacementHistory)
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
