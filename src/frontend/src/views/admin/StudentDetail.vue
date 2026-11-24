<template>
  <div>
    <router-link to="/admin/students" class="back-link">
      <i class="bi bi-arrow-left"></i> Back to Students
    </router-link>

    <div v-if="loading" class="detail-grid">
      <div class="skeleton-card" style="height: 280px"></div>
      <div class="skeleton-card" style="height: 140px"></div>
    </div>

    <template v-else-if="student">
      <PageHeader :title="student.name" subtitle="Student Details" />

      <div class="detail-grid mb-4">
        <div>
          <SectionCard title="Student Information">
            <div class="detail-info-grid">
              <div class="detail-info-field">
                <span class="detail-info-label">Email</span>
                <span class="detail-info-value data-value">{{ student.email }}</span>
              </div>
              <div class="detail-info-field">
                <span class="detail-info-label">Branch</span>
                <span class="detail-info-value data-value">{{ student.branch }}</span>
              </div>
              <div class="detail-info-field">
                <span class="detail-info-label">CGPA</span>
                <span class="detail-info-value data-value">{{ student.cgpa }}</span>
              </div>
              <div class="detail-info-field">
                <span class="detail-info-label">Year</span>
                <span class="detail-info-value data-value">{{ student.year }}</span>
              </div>
              <div class="detail-info-field">
                <span class="detail-info-label">Resume</span>
                <span class="detail-info-value data-value">{{ student.resume_path || 'Not uploaded' }}</span>
              </div>
              <div class="detail-info-field">
                <span class="detail-info-label">Created</span>
                <span class="detail-info-value data-value">{{ formatDate(student.created_at) }}</span>
              </div>
            </div>
          </SectionCard>
        </div>
        <div>
          <SectionCard title="Status">
            <div class="detail-info-grid">
              <div class="detail-info-field">
                <span class="detail-info-label">Account</span>
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
