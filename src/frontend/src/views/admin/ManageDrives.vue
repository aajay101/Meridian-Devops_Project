<template>
  <div>
    <PageHeader title="Manage Drives" subtitle="Approve or reject placement drives">
      <template #action>
        <span class="result-count" v-if="!loading">{{ filteredDrives.length }} drives</span>
      </template>
    </PageHeader>

    <SectionCard>
      <FilterBar
        v-model="activeFilter"
        v-model:searchValue="query"
        :filters="filterOptions"
        searchPlaceholder="Search drives..."
        ariaLabel="Filter drives by status"
      />

      <div v-if="loading" class="table-skeleton">
        <div v-for="n in 5" :key="n" class="skeleton-row"></div>
      </div>

      <div v-else-if="filteredDrives.length === 0" class="text-center py-5">
        <EmptyState icon="bi bi-briefcase" title="No drives found" description="No drives match your current filters.">
          <template #action>
            <button class="btn btn-outline-secondary btn-sm" @click="resetFilters">
              <i class="bi bi-arrow-counterclockwise me-1"></i> Reset Filters
            </button>
          </template>
        </EmptyState>
      </div>

      <div v-else class="table-responsive">
        <table class="data-table" aria-label="Drives list">
          <thead>
            <tr>
              <th scope="col">Job Title</th>
              <th scope="col">Company</th>
              <th scope="col" class="d-none d-lg-table-cell">Branches</th>
              <th scope="col" class="d-none d-lg-table-cell">CGPA</th>
              <th scope="col" class="d-none d-lg-table-cell">Deadline</th>
              <th scope="col">Status</th>
              <th scope="col">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="drive in filteredDrives" :key="drive.drive_id">
              <td data-label="Job Title">
              <router-link :to="`/admin/drives/${drive.drive_id}`" class="td-link data-value">
                    {{ drive.job_title }}
                  </router-link>
              </td>
              <td data-label="Company" class="td-secondary data-value">{{ drive.company_name }}</td>
              <td data-label="Branches" class="d-none d-lg-table-cell">
                <div class="chip-overflow">
                  <template v-if="drive.eligibility_branches.length > 2">
                    <Chip v-for="branch in drive.eligibility_branches.slice(0, 2)" :key="branch">{{ branch }}</Chip>
                    <span class="chip-overflow__more">+{{ drive.eligibility_branches.length - 2 }}</span>
                  </template>
                  <template v-else>
                    <Chip v-for="branch in drive.eligibility_branches" :key="branch">{{ branch }}</Chip>
                  </template>
                </div>
              </td>
              <td data-label="CGPA" class="d-none d-lg-table-cell td-secondary data-value">{{ drive.eligibility_cgpa }}</td>
              <td data-label="Deadline" class="d-none d-lg-table-cell data-value" :class="isPastDeadline(drive.application_deadline) ? 'deadline-urgent' : 'td-secondary'">
                {{ formatDate(drive.application_deadline) }}
              </td>
              <td data-label="Status"><StatusBadge :status="drive.status" /></td>
              <td data-label="Actions">
                <div class="d-flex gap-2">
                  <template v-if="drive.status === 'Pending'">
                    <button class="btn btn-outline-success btn-sm" @click="confirmAction(drive, 'approve')" :disabled="submitting">
                      <i class="bi bi-check-lg"></i> Approve
                    </button>
                    <button class="btn btn-outline-danger btn-sm" @click="confirmAction(drive, 'reject')" :disabled="submitting">
                      <i class="bi bi-x-lg"></i> Reject
                    </button>
                  </template>
                  <template v-else-if="drive.status === 'Approved'">
                    <button class="btn btn-outline-secondary btn-sm" @click="confirmAction(drive, 'close')" :disabled="submitting">
                      Close
                    </button>
                  </template>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </SectionCard>

    <ConfirmDialog
      :show="dialog.open"
      :title="dialogTitle"
      :message="dialogMessage"
      :confirm-text="dialogConfirmText"
      :confirm-variant="dialogConfirmVariant"
      :loading="submitting"
      @confirm="executeAction"
      @cancel="dialog.open = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getDrives, approveDrive, rejectDrive, closeDrive } from '@/api/admin'
import PageHeader from '@/components/common/PageHeader.vue'
import SectionCard from '@/components/common/SectionCard.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'
import Chip from '@/components/common/Chip.vue'

const drives = ref([])
const loading = ref(false)
const submitting = ref(false)
const query = ref('')
const activeFilter = ref('all')
const dialog = ref({ open: false, drive: null, action: null })

const filterOptions = computed(() => [
  { key: 'all', label: 'All', count: drives.value.length },
  { key: 'Pending', label: 'Pending', count: drives.value.filter((d) => d.status === 'Pending').length },
  { key: 'Approved', label: 'Approved', count: drives.value.filter((d) => d.status === 'Approved').length },
  { key: 'Rejected', label: 'Rejected', count: drives.value.filter((d) => d.status === 'Rejected').length },
  { key: 'Closed', label: 'Closed', count: drives.value.filter((d) => d.status === 'Closed').length }
])

const filteredDrives = computed(() => {
  let list = drives.value
  if (activeFilter.value !== 'all') {
    list = list.filter((d) => d.status === activeFilter.value)
  }
  if (query.value.trim()) {
    const q = query.value.toLowerCase()
    list = list.filter(
      (d) =>
        d.job_title.toLowerCase().includes(q) ||
        d.company_name.toLowerCase().includes(q) ||
        d.eligibility_branches.some((b) => b.toLowerCase().includes(q)) ||
        String(d.eligibility_cgpa).includes(q)
    )
  }
  return list
})

const dialogTitle = computed(() => {
  const map = { approve: 'Approve Drive', reject: 'Reject Drive', close: 'Close Drive' }
  return map[dialog.value.action] || ''
})

const dialogMessage = computed(() => {
  const title = dialog.value.drive?.job_title || ''
  const map = {
    approve: `Are you sure you want to approve "${title}"?`,
    reject: `Are you sure you want to reject "${title}"?`,
    close: `Are you sure you want to close "${title}"?`
  }
  return map[dialog.value.action] || ''
})

const dialogConfirmText = computed(() => {
  const map = { approve: 'Approve', reject: 'Reject', close: 'Close' }
  return map[dialog.value.action] || 'Confirm'
})

const dialogConfirmVariant = computed(() => {
  const map = { approve: 'success', reject: 'danger', close: 'secondary' }
  return map[dialog.value.action] || 'primary'
})

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

const isPastDeadline = (dateStr) => {
  if (!dateStr) return false
  return new Date(dateStr) < new Date()
}

const confirmAction = (drive, action) => {
  dialog.value = { open: true, drive, action }
}

const resetFilters = () => {
  activeFilter.value = 'all'
  query.value = ''
}

const executeAction = async () => {
  const { drive, action } = dialog.value
  submitting.value = true
  try {
    const map = { approve: approveDrive, reject: rejectDrive, close: closeDrive }
    await map[action](drive.drive_id)
    dialog.value.open = false
    await fetchData()
  } catch (err) {
    // error handled silently
  } finally {
    submitting.value = false
  }
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
.result-count {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  font-weight: var(--weight-medium);
}

.chip-overflow {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-1);
  align-items: center;
}

.chip-overflow__more {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  font-weight: var(--weight-medium);
}
</style>
