<template>
  <div>
    <router-link to="/admin/companies" class="back-link">
      <i class="bi bi-arrow-left"></i> Back to Companies
    </router-link>

    <div v-if="loading" class="detail-grid">
      <div class="skeleton-card" style="height: 280px"></div>
      <div class="skeleton-card" style="height: 180px"></div>
    </div>

    <template v-else-if="company">
      <PageHeader :title="company.company_name" subtitle="Company Details" />

      <div class="detail-grid mb-4">
        <div>
          <SectionCard title="Company Information">
            <div class="detail-info-grid">
              <div class="detail-info-field">
                <span class="detail-info-label">Email</span>
                <span class="detail-info-value data-value">{{ company.email }}</span>
              </div>
              <div class="detail-info-field">
                <span class="detail-info-label">HR Contact</span>
                <span class="detail-info-value data-value">{{ company.hr_contact }}</span>
              </div>
              <div class="detail-info-field">
                <span class="detail-info-label">Website</span>
              <span class="detail-info-value data-value">
                <a v-if="company.website" :href="company.website" target="_blank" rel="noopener" class="external-link">
                    {{ company.website }}
                    <i class="bi bi-box-arrow-up-right ms-1" style="font-size: 11px"></i>
                  </a>
                  <span v-else class="text-muted">—</span>
                </span>
              </div>
              <div class="detail-info-field">
                <span class="detail-info-label">Created</span>
                <span class="detail-info-value data-value">{{ formatDate(company.created_at) }}</span>
              </div>
            </div>
          </SectionCard>
        </div>
        <div>
          <SectionCard title="Status">
            <div class="detail-info-grid">
              <div class="detail-info-field">
                <span class="detail-info-label">Approval</span>
                <StatusBadge :status="company.approval_status" />
              </div>
              <div class="detail-info-field">
                <span class="detail-info-label">Account</span>
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
.external-link {
  display: inline-flex;
  align-items: center;
}

.text-muted {
  color: var(--text-tertiary);
}
</style>
