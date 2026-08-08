<template>
  <div>
    <PageHeader title="Manage Students" subtitle="View and manage student accounts">
      <template #action>
        <span class="result-count" v-if="!loading">{{ filteredStudents.length }} students</span>
      </template>
    </PageHeader>

    <SectionCard>
      <FilterBar
        v-model="activeFilter"
        v-model:searchValue="query"
        :filters="filterOptions"
        searchPlaceholder="Search students..."
        ariaLabel="Filter students by status"
      />

      <div v-if="loading" class="table-skeleton">
        <div v-for="n in 5" :key="n" class="skeleton-row"></div>
      </div>

      <div v-else-if="filteredStudents.length === 0" class="text-center py-5">
        <EmptyState icon="bi bi-people" title="No students found" description="No students match your current filters.">
          <template #action>
            <button class="btn btn-outline-secondary btn-sm" @click="resetFilters">
              <i class="bi bi-arrow-counterclockwise me-1"></i> Reset Filters
            </button>
          </template>
        </EmptyState>
      </div>

      <div v-else class="table-responsive">
        <table class="data-table" aria-label="Students list">
          <thead>
            <tr>
              <th scope="col">Name</th>
              <th scope="col">Email</th>
              <th scope="col" class="d-none d-md-table-cell">Branch</th>
              <th scope="col" class="d-none d-md-table-cell">CGPA</th>
              <th scope="col" class="d-none d-md-table-cell">Year</th>
              <th scope="col">Status</th>
              <th scope="col">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="student in filteredStudents" :key="student.student_profile_id">
              <td data-label="Name">
              <router-link :to="`/admin/students/${student.student_profile_id}`" class="td-link data-value">
                    {{ student.name }}
                  </router-link>
              </td>
              <td data-label="Email" class="td-secondary data-value">{{ student.email }}</td>
              <td data-label="Branch" class="d-none d-md-table-cell td-secondary data-value">{{ student.branch }}</td>
              <td data-label="CGPA" class="d-none d-md-table-cell td-secondary data-value">{{ student.cgpa }}</td>
              <td data-label="Year" class="d-none d-md-table-cell td-secondary data-value">{{ student.year }}</td>
              <td data-label="Status">
                <StatusBadge :status="student.is_active !== false ? 'Active' : 'Inactive'" />
              </td>
              <td data-label="Actions">
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
import FilterBar from '@/components/common/FilterBar.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'

const students = ref([])
const loading = ref(false)
const submitting = ref(false)
const query = ref('')
const activeFilter = ref('all')
const dialog = ref({ open: false, student: null, action: null })

const filterOptions = computed(() => [
  { key: 'all', label: 'All', count: students.value.length },
  { key: 'Active', label: 'Active', count: students.value.filter((s) => s.is_active !== false).length },
  { key: 'Inactive', label: 'Inactive', count: students.value.filter((s) => s.is_active === false).length }
])

const filteredStudents = computed(() => {
  let list = students.value
  if (activeFilter.value !== 'all') {
    list = list.filter((s) => {
      if (activeFilter.value === 'Active') return s.is_active !== false
      if (activeFilter.value === 'Inactive') return s.is_active === false
      return true
    })
  }
  if (query.value.trim()) {
    const q = query.value.toLowerCase()
    list = list.filter(
      (s) =>
        s.name.toLowerCase().includes(q) ||
        s.email.toLowerCase().includes(q) ||
        s.branch.toLowerCase().includes(q) ||
        String(s.cgpa).includes(q) ||
        String(s.year).includes(q)
    )
  }
  return list
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

const resetFilters = () => {
  activeFilter.value = 'all'
  query.value = ''
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
.result-count {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  font-weight: var(--weight-medium);
}
</style>
