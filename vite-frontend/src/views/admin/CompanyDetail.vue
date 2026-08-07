<template>
  <div>
    <router-link to="/admin/companies" class="back-link">
      <i class="bi bi-arrow-left"></i> Companies
    </router-link>

    <div v-if="loading" class="skeleton-card"></div>

    <template v-else-if="company">
      <PageHeader :title="company.company_name" subtitle="Company Details" />

      <div class="row g-4 mb-4">
        <div class="col-lg-8">
          <SectionCard title="Company Information">
            <div class="info-grid">
              <div class="info-field">
                <span class="info-label">Email</span>
                <span class="info-value">{{ company.email }}</span>
              </div>
              <div class="info-field">
                <span class="info-label">HR Contact</span>
                <span class="info-value">{{ company.hr_contact }}</span>
              </div>
              <div class="info-field">
                <span class="info-label">Website</span>
                <span class="info-value">{{ company.website || '—' }}</span>
              </div>
              <div class="info-field">
                <span class="info-label">Created</span>
                <span class="info-value">{{ formatDate(company.created_at) }}</span>
              </div>
            </div>
          </SectionCard>
        </div>
        <div class="col-lg-4">
          <SectionCard title="Status">
            <div class="status-group">
              <div class="status-item">
                <span class="info-label">Approval</span>
                <StatusBadge :status="company.approval_status" />
              </div>
              <div class="status-item">
                <span class="info-label">Account</span>
                <StatusBadge :status="company.is_active !== false ? 'Active' : 'Inactive'" />
              </div>
            </div>
          </SectionCard>
        </div>
      </div>

      <div class="action-bar">
        <template v-if="company.approval_status === 'Pending'">
          <button class="btn btn-success" @click="confirmAction('approve')" :disabled="submitting">
            <i class="bi bi-check-lg me-1"></i> Approve
          </button>
          <button class="btn btn-danger" @click="confirmAction('reject')" :disabled="submitting">
            <i class="bi bi-x-lg me-1"></i> Reject
          </button>
        </template>
        <template v-else-if="company.approval_status === 'Approved'">
          <button
            v-if="company.is_active !== false"
            class="btn btn-outline-danger"
            @click="confirmAction('deactivate')"
            :disabled="submitting"
          >
            <i class="bi bi-person-x me-1"></i> Deactivate
          </button>
          <button
            v-else
            class="btn btn-outline-success"
            @click="confirmAction('activate')"
            :disabled="submitting"
          >
            <i class="bi bi-person-check me-1"></i> Activate
          </button>
        </template>
      </div>
    </template>

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
import { useRoute, useRouter } from 'vue-router'
import { getCompany, approveCompany, rejectCompany, deactivateCompany, activateCompany } from '@/api/admin'
import PageHeader from '@/components/common/PageHeader.vue'
import SectionCard from '@/components/common/SectionCard.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'

const route = useRoute()
const router = useRouter()
const company = ref(null)
const loading = ref(false)
const submitting = ref(false)
const dialog = ref({ open: false, action: null })

const dialogTitle = computed(() => {
  const map = { approve: 'Approve Company', reject: 'Reject Company', deactivate: 'Deactivate Company', activate: 'Activate Company' }
  return map[dialog.value.action] || ''
})

const dialogMessage = computed(() => {
  const name = company.value?.company_name || ''
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

const confirmAction = (action) => {
  dialog.value = { open: true, action }
}

const executeAction = async () => {
  submitting.value = true
  try {
    const id = route.params.id
    const map = { approve: approveCompany, reject: rejectCompany, deactivate: deactivateCompany, activate: activateCompany }
    await map[dialog.value.action](id)
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
    const res = await getCompany(route.params.id)
    if (res.data.success) {
      company.value = res.data.company
    } else {
      router.push('/admin/companies')
    }
  } catch (err) {
    router.push('/admin/companies')
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.back-link {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  text-decoration: none;
  margin-bottom: var(--space-4);
}

.back-link:hover {
  color: var(--color-primary);
  text-decoration: none;
}

.info-grid {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.info-field {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.info-label {
  font-size: var(--text-xs);
  font-weight: var(--weight-medium);
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.info-value {
  font-size: var(--text-sm);
  color: var(--text-primary);
}

.status-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.status-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.action-bar {
  display: flex;
  gap: var(--space-3);
  padding-top: var(--space-4);
  border-top: 1px solid var(--color-border);
}

.skeleton-card {
  height: 200px;
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
