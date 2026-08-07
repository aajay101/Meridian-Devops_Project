<template>
  <div>
    <router-link to="/admin/students" class="back-link">
      <i class="bi bi-arrow-left"></i> Students
    </router-link>

    <div v-if="loading" class="skeleton-card"></div>

    <template v-else-if="student">
      <PageHeader :title="student.name" subtitle="Student Details" />

      <div class="row g-4 mb-4">
        <div class="col-lg-8">
          <SectionCard title="Student Information">
            <div class="info-grid">
              <div class="info-field">
                <span class="info-label">Email</span>
                <span class="info-value">{{ student.email }}</span>
              </div>
              <div class="info-field">
                <span class="info-label">Branch</span>
                <span class="info-value">{{ student.branch }}</span>
              </div>
              <div class="info-field">
                <span class="info-label">CGPA</span>
                <span class="info-value">{{ student.cgpa }}</span>
              </div>
              <div class="info-field">
                <span class="info-label">Year</span>
                <span class="info-value">{{ student.year }}</span>
              </div>
              <div class="info-field">
                <span class="info-label">Resume</span>
                <span class="info-value">{{ student.resume_path || 'Not uploaded' }}</span>
              </div>
              <div class="info-field">
                <span class="info-label">Created</span>
                <span class="info-value">{{ formatDate(student.created_at) }}</span>
              </div>
            </div>
          </SectionCard>
        </div>
        <div class="col-lg-4">
          <SectionCard title="Status">
            <div class="status-group">
              <div class="status-item">
                <span class="info-label">Account</span>
                <StatusBadge :status="student.is_active !== false ? 'Active' : 'Inactive'" />
              </div>
            </div>
          </SectionCard>
        </div>
      </div>

      <div class="action-bar">
        <button
          v-if="student.is_active !== false"
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
      </div>
    </template>

    <ConfirmDialog
      :show="dialog.open"
      :title="dialogTitle"
      :message="dialogMessage"
      :confirm-text="dialog.action === 'deactivate' ? 'Deactivate' : 'Activate'"
      :confirm-variant="dialog.action === 'deactivate' ? 'danger' : 'success'"
      :loading="submitting"
      @confirm="executeAction"
      @cancel="dialog.open = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getStudent, deactivateStudent, activateStudent } from '@/api/admin'
import PageHeader from '@/components/common/PageHeader.vue'
import SectionCard from '@/components/common/SectionCard.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'

const route = useRoute()
const router = useRouter()
const student = ref(null)
const loading = ref(false)
const submitting = ref(false)
const dialog = ref({ open: false, action: null })

const dialogTitle = computed(() => {
  return dialog.value.action === 'deactivate' ? 'Deactivate Student' : 'Activate Student'
})

const dialogMessage = computed(() => {
  const name = student.value?.name || ''
  return dialog.value.action === 'deactivate'
    ? `Are you sure you want to deactivate ${name}?`
    : `Are you sure you want to activate ${name}?`
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
    const fn = dialog.value.action === 'deactivate' ? deactivateStudent : activateStudent
    await fn(id)
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
    const res = await getStudent(route.params.id)
    if (res.data.success) {
      student.value = res.data.student
    } else {
      router.push('/admin/students')
    }
  } catch (err) {
    router.push('/admin/students')
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
