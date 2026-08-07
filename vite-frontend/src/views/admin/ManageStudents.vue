<template>
  <div>
    <PageHeader title="Manage Students" subtitle="View and manage student accounts" />

    <SectionCard>
      <div class="table-toolbar">
        <div></div>
        <input
          v-model="query"
          type="text"
          class="form-control form-control-sm search-input"
          placeholder="Search students..."
        />
      </div>

      <div v-if="loading" class="table-skeleton">
        <div v-for="n in 5" :key="n" class="skeleton-row"></div>
      </div>

      <div v-else-if="filteredStudents.length === 0" class="text-center py-5">
        <EmptyState icon="bi bi-people" title="No students found" description="No students match your search." />
      </div>

      <div v-else class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th class="d-none d-md-table-cell">Branch</th>
              <th class="d-none d-md-table-cell">CGPA</th>
              <th class="d-none d-md-table-cell">Year</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="student in filteredStudents" :key="student.student_profile_id">
              <td>
                <router-link :to="`/admin/students/${student.student_profile_id}`" class="fw-medium text-decoration-none">
                  {{ student.name }}
                </router-link>
              </td>
              <td>{{ student.email }}</td>
              <td class="d-none d-md-table-cell">{{ student.branch }}</td>
              <td class="d-none d-md-table-cell">{{ student.cgpa }}</td>
              <td class="d-none d-md-table-cell">{{ student.year }}</td>
              <td>
                <StatusBadge :status="student.is_active !== false ? 'Active' : 'Inactive'" />
              </td>
              <td>
                <div class="d-flex gap-2">
                  <button
                    v-if="student.is_active !== false"
                    class="btn btn-outline-danger btn-sm"
                    @click="confirmAction(student, 'deactivate')"
                    :disabled="submitting"
                  >
                    Deactivate
                  </button>
                  <button
                    v-else
                    class="btn btn-outline-success btn-sm"
                    @click="confirmAction(student, 'activate')"
                    :disabled="submitting"
                  >
                    Activate
                  </button>
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
import { getStudents, deactivateStudent, activateStudent } from '@/api/admin'
import PageHeader from '@/components/common/PageHeader.vue'
import SectionCard from '@/components/common/SectionCard.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'

const students = ref([])
const loading = ref(false)
const submitting = ref(false)
const query = ref('')
const dialog = ref({ open: false, student: null, action: null })

const filteredStudents = computed(() => {
  if (!query.value.trim()) return students.value
  const q = query.value.toLowerCase()
  return students.value.filter(
    (s) =>
      s.name.toLowerCase().includes(q) ||
      s.email.toLowerCase().includes(q) ||
      s.branch.toLowerCase().includes(q) ||
      String(s.cgpa).includes(q) ||
      String(s.year).includes(q) ||
      (s.is_active !== false ? 'active' : 'inactive').includes(q)
  )
})

const dialogTitle = computed(() => {
  return dialog.value.action === 'deactivate' ? 'Deactivate Student' : 'Activate Student'
})

const dialogMessage = computed(() => {
  const name = dialog.value.student?.name || ''
  return dialog.value.action === 'deactivate'
    ? `Are you sure you want to deactivate ${name}?`
    : `Are you sure you want to activate ${name}?`
})

const confirmAction = (student, action) => {
  dialog.value = { open: true, student, action }
}

const executeAction = async () => {
  const { student, action } = dialog.value
  submitting.value = true
  try {
    const fn = action === 'deactivate' ? deactivateStudent : activateStudent
    await fn(student.student_profile_id)
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
    const res = await getStudents()
    if (res.data.success) {
      students.value = res.data.students
    }
  } catch (err) {
    // students remain empty on error
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
