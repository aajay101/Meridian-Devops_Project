<template>
  <div>
    <PageHeader title="Manage Drives" subtitle="Approve or reject placement drives" />

    <SectionCard>
      <div class="table-toolbar">
        <ul class="nav nav-pills">
          <li class="nav-item">
            <button class="nav-link" :class="{ active: activeFilter === 'all' }" @click="setFilter('all')">All</button>
          </li>
          <li class="nav-item">
            <button class="nav-link" :class="{ active: activeFilter === 'Pending' }" @click="setFilter('Pending')">Pending</button>
          </li>
          <li class="nav-item">
            <button class="nav-link" :class="{ active: activeFilter === 'Approved' }" @click="setFilter('Approved')">Approved</button>
          </li>
          <li class="nav-item">
            <button class="nav-link" :class="{ active: activeFilter === 'Rejected' }" @click="setFilter('Rejected')">Rejected</button>
          </li>
          <li class="nav-item">
            <button class="nav-link" :class="{ active: activeFilter === 'Closed' }" @click="setFilter('Closed')">Closed</button>
          </li>
        </ul>
        <input
          v-model="query"
          type="text"
          class="form-control form-control-sm search-input"
          placeholder="Search drives..."
        />
      </div>

      <div v-if="loading" class="table-skeleton">
        <div v-for="n in 5" :key="n" class="skeleton-row"></div>
      </div>

      <div v-else-if="filteredDrives.length === 0" class="text-center py-5">
        <EmptyState icon="bi bi-briefcase" title="No drives found" description="No drives match your current filters." />
      </div>

      <div v-else class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead>
            <tr>
              <th>Job Title</th>
              <th>Company</th>
              <th class="d-none d-lg-table-cell">Branches</th>
              <th class="d-none d-lg-table-cell">CGPA</th>
              <th class="d-none d-lg-table-cell">Deadline</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="drive in filteredDrives" :key="drive.drive_id">
              <td>
                <router-link :to="`/admin/drives/${drive.drive_id}`" class="fw-medium text-decoration-none">
                  {{ drive.job_title }}
                </router-link>
              </td>
              <td>{{ drive.company_name }}</td>
              <td class="d-none d-lg-table-cell">{{ drive.eligibility_branches.join(', ') }}</td>
              <td class="d-none d-lg-table-cell">{{ drive.eligibility_cgpa }}</td>
              <td class="d-none d-lg-table-cell" :class="{ 'text-danger': isPastDeadline(drive.application_deadline) }">
                {{ formatDate(drive.application_deadline) }}
              </td>
              <td><StatusBadge :status="drive.status" /></td>
              <td>
                <div class="d-flex gap-2">
                  <template v-if="drive.status === 'Pending'">
                    <button class="btn btn-success btn-sm" @click="confirmAction(drive, 'approve')" :disabled="submitting">
                      Approve
                    </button>
                    <button class="btn btn-danger btn-sm" @click="confirmAction(drive, 'reject')" :disabled="submitting">
                      Reject
                    </button>
                  </template>
                  <template v-else-if="drive.status === 'Approved'">
                    <button class="btn btn-secondary btn-sm" @click="confirmAction(drive, 'close')" :disabled="submitting">
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
import StatusBadge from '@/components/common/StatusBadge.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'

const drives = ref([])
const loading = ref(false)
const submitting = ref(false)
const query = ref('')
const activeFilter = ref('all')
const dialog = ref({ open: false, drive: null, action: null })

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
        String(d.eligibility_cgpa).includes(q) ||
        d.status.toLowerCase().includes(q)
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

const setFilter = (filter) => {
  activeFilter.value = filter
}

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
</style>
