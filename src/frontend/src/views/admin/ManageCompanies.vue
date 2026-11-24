<template>
  <div>
    <PageHeader title="Manage Companies" subtitle="Review and approve company registrations">
      <template #action>
        <span class="result-count" v-if="!loading">{{ filteredCompanies.length }} companies</span>
      </template>
    </PageHeader>

    <SectionCard>
      <FilterBar
        v-model="activeFilter"
        v-model:searchValue="query"
        :filters="filterOptions"
        searchPlaceholder="Search companies..."
        ariaLabel="Filter companies by status"
      />

      <div v-if="loading" class="table-skeleton">
        <div v-for="n in 5" :key="n" class="skeleton-row"></div>
      </div>

      <div v-else-if="filteredCompanies.length === 0" class="text-center py-5">
        <EmptyState icon="bi bi-building" title="No companies found" description="No companies match your current filters.">
          <template #action>
            <button class="btn btn-outline-secondary btn-sm" @click="resetFilters">
              <i class="bi bi-arrow-counterclockwise me-1"></i> Reset Filters
            </button>
          </template>
        </EmptyState>
      </div>

      <div v-else class="table-responsive">
        <table class="data-table" aria-label="Companies list">
          <thead>
            <tr>
              <th scope="col">Company Name</th>
              <th scope="col">Email</th>
              <th scope="col" class="d-none d-lg-table-cell">HR Contact</th>
              <th scope="col">Status</th>
              <th scope="col" class="d-none d-lg-table-cell">Created</th>
              <th scope="col">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="company in filteredCompanies" :key="company.company_profile_id">
              <td data-label="Company">
              <router-link :to="`/admin/companies/${company.company_profile_id}`" class="td-link data-value">
                    {{ company.company_name }}
                  </router-link>
              </td>
              <td data-label="Email" class="td-secondary data-value">{{ company.email }}</td>
              <td data-label="HR Contact" class="d-none d-lg-table-cell td-secondary data-value">{{ company.hr_contact }}</td>
              <td data-label="Status"><StatusBadge :status="company.approval_status" /></td>
              <td data-label="Created" class="d-none d-lg-table-cell td-secondary data-value">{{ formatDate(company.created_at) }}</td>
              <td data-label="Actions">
                <div class="d-flex gap-2">
                  <template v-if="company.approval_status === 'Pending'">
                    <button class="btn btn-outline-success btn-sm" @click="confirmAction(company, 'approve')" :disabled="submitting">
                      <i class="bi bi-check-lg"></i> Approve
                    </button>
                    <button class="btn btn-outline-danger btn-sm" @click="confirmAction(company, 'reject')" :disabled="submitting">
                      <i class="bi bi-x-lg"></i> Reject
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
import FilterBar from '@/components/common/FilterBar.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'

const companies = ref([])
const loading = ref(false)
const submitting = ref(false)
const query = ref('')
const activeFilter = ref('all')
const dialog = ref({ open: false, company: null, action: null })

const filterOptions = computed(() => [
  { key: 'all', label: 'All', count: companies.value.length },
  { key: 'Pending', label: 'Pending', count: companies.value.filter((c) => c.approval_status === 'Pending').length },
  { key: 'Approved', label: 'Approved', count: companies.value.filter((c) => c.approval_status === 'Approved').length },
  { key: 'Rejected', label: 'Rejected', count: companies.value.filter((c) => c.approval_status === 'Rejected').length }
])

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
        c.hr_contact.toLowerCase().includes(q)
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

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

const confirmAction = (company, action) => {
  dialog.value = { open: true, company, action }
}

const resetFilters = () => {
  activeFilter.value = 'all'
  query.value = ''
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
.result-count {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  font-weight: var(--weight-medium);
}
</style>
