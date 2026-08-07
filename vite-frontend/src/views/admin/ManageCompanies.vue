<template>
  <div>
    <PageHeader title="Manage Companies" subtitle="Review and approve company registrations" />

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
        </ul>
        <input
          v-model="query"
          type="text"
          class="form-control form-control-sm search-input"
          placeholder="Search companies..."
        />
      </div>

      <div v-if="loading" class="table-skeleton">
        <div v-for="n in 5" :key="n" class="skeleton-row"></div>
      </div>

      <div v-else-if="filteredCompanies.length === 0" class="text-center py-5">
        <EmptyState icon="bi bi-building" title="No companies found" description="No companies match your current filters." />
      </div>

      <div v-else class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead>
            <tr>
              <th>Company Name</th>
              <th>Email</th>
              <th class="d-none d-lg-table-cell">HR Contact</th>
              <th>Status</th>
              <th class="d-none d-lg-table-cell">Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="company in filteredCompanies" :key="company.company_profile_id">
              <td>
                <router-link :to="`/admin/companies/${company.company_profile_id}`" class="fw-medium text-decoration-none">
                  {{ company.company_name }}
                </router-link>
              </td>
              <td>{{ company.email }}</td>
              <td class="d-none d-lg-table-cell">{{ company.hr_contact }}</td>
              <td><StatusBadge :status="company.approval_status" /></td>
              <td class="d-none d-lg-table-cell">{{ formatDate(company.created_at) }}</td>
              <td>
                <div class="d-flex gap-2">
                  <template v-if="company.approval_status === 'Pending'">
                    <button class="btn btn-success btn-sm" @click="confirmAction(company, 'approve')" :disabled="submitting">
                      Approve
                    </button>
                    <button class="btn btn-danger btn-sm" @click="confirmAction(company, 'reject')" :disabled="submitting">
                      Reject
                    </button>
                  </template>
                  <template v-else-if="company.approval_status === 'Approved'">
                    <button
                      v-if="company.is_active !== false"
                      class="btn btn-outline-danger btn-sm"
                      @click="confirmAction(company, 'deactivate')"
                      :disabled="submitting"
                    >
                      Deactivate
                    </button>
                    <button
                      v-else
                      class="btn btn-outline-success btn-sm"
                      @click="confirmAction(company, 'activate')"
                      :disabled="submitting"
                    >
                      Activate
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
import { getCompanies, approveCompany, rejectCompany, deactivateCompany, activateCompany } from '@/api/admin'
import PageHeader from '@/components/common/PageHeader.vue'
import SectionCard from '@/components/common/SectionCard.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'

const companies = ref([])
const loading = ref(false)
const submitting = ref(false)
const query = ref('')
const activeFilter = ref('all')
const dialog = ref({ open: false, company: null, action: null })

const filteredCompanies = computed(() => {
  let list = companies.value
  if (activeFilter.value !== 'all') {
    list = list.filter((c) => c.approval_status === activeFilter.value)
  }
  if (query.value.trim()) {
    const q = query.value.toLowerCase()
    list = list.filter(
      (c) =>
        c.company_name.toLowerCase().includes(q) ||
        c.email.toLowerCase().includes(q) ||
        c.hr_contact.toLowerCase().includes(q) ||
        c.approval_status.toLowerCase().includes(q)
    )
  }
  return list
})

const dialogTitle = computed(() => {
  const map = { approve: 'Approve Company', reject: 'Reject Company', deactivate: 'Deactivate Company', activate: 'Activate Company' }
  return map[dialog.value.action] || ''
})

const dialogMessage = computed(() => {
  const name = dialog.value.company?.company_name || ''
  const map = {
    approve: `Are you sure you want to approve ${name}?`,
    reject: `Are you sure you want to reject ${name}?`,
    deactivate: `Are you sure you want to deactivate ${name}?`,
    activate: `Are you sure you want to activate ${name}?`
  }
  return map[dialog.value.action] || ''
})

const dialogConfirmText = computed(() => {
  const map = { approve: 'Approve', reject: 'Reject', deactivate: 'Deactivate', activate: 'Activate' }
  return map[dialog.value.action] || 'Confirm'
})

const dialogConfirmVariant = computed(() => {
  const map = { approve: 'success', reject: 'danger', deactivate: 'danger', activate: 'success' }
  return map[dialog.value.action] || 'primary'
})

const setFilter = (filter) => {
  activeFilter.value = filter
}

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

const confirmAction = (company, action) => {
  dialog.value = { open: true, company, action }
}

const executeAction = async () => {
  const { company, action } = dialog.value
  submitting.value = true
  try {
    const map = {
      approve: approveCompany,
      reject: rejectCompany,
      deactivate: deactivateCompany,
      activate: activateCompany
    }
    await map[action](company.company_profile_id)
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
    const res = await getCompanies()
    if (res.data.success) {
      companies.value = res.data.companies
    }
  } catch (err) {
    // companies remain empty on error
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
