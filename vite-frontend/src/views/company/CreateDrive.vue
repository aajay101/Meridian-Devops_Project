<template>
  <div>
    <router-link to="/company/drives" class="back-link">
      <i class="bi bi-arrow-left"></i> My Drives
    </router-link>

    <PageHeader title="Create Drive" subtitle="Post a new placement drive" />

    <div class="row g-4">
      <div class="col-lg-8">
        <SectionCard title="Job Details">
          <div v-if="errorMessage" class="alert alert-danger" role="alert">
            {{ errorMessage }}
          </div>

          <form @submit.prevent="handleSubmit">
            <div class="mb-3">
              <label for="job_title" class="form-label">Job Title <span class="text-danger">*</span></label>
              <input
                id="job_title"
                v-model="form.job_title"
                type="text"
                class="form-control"
                :class="{ 'is-invalid': errors.job_title }"
                placeholder="e.g. Software Development Engineer"
                required
              />
              <div v-if="errors.job_title" class="invalid-feedback">{{ errors.job_title }}</div>
            </div>

            <div class="mb-3">
              <label for="job_description" class="form-label">Job Description <span class="text-danger">*</span></label>
              <textarea
                id="job_description"
                v-model="form.job_description"
                class="form-control"
                :class="{ 'is-invalid': errors.job_description }"
                rows="6"
                placeholder="Describe the role, responsibilities, and requirements..."
                required
              ></textarea>
              <div v-if="errors.job_description" class="invalid-feedback">{{ errors.job_description }}</div>
            </div>

            <div class="mb-3">
              <label class="form-label">Eligible Branches <span class="text-danger">*</span></label>
              <div class="branch-checkboxes" :class="{ 'is-invalid': errors.eligibility_branches }">
                <div v-for="b in branches" :key="b" class="form-check">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    :id="'branch-' + b"
                    :value="b"
                    v-model="form.eligibility_branches"
                  />
                  <label class="form-check-label" :for="'branch-' + b">{{ b }}</label>
                </div>
              </div>
              <div v-if="errors.eligibility_branches" class="text-danger small mt-1">{{ errors.eligibility_branches }}</div>
            </div>

            <div class="row mb-3">
              <div class="col-md-6">
                <label for="eligibility_cgpa" class="form-label">Minimum CGPA <span class="text-danger">*</span></label>
                <input
                  id="eligibility_cgpa"
                  v-model="form.eligibility_cgpa"
                  type="number"
                  step="0.01"
                  min="0"
                  max="10"
                  class="form-control"
                  :class="{ 'is-invalid': errors.eligibility_cgpa }"
                  placeholder="e.g. 7.5"
                  required
                />
                <div v-if="errors.eligibility_cgpa" class="invalid-feedback">{{ errors.eligibility_cgpa }}</div>
              </div>
              <div class="col-md-6">
                <label for="eligibility_year" class="form-label">Eligible Semester <span class="text-danger">*</span></label>
                <select
                  id="eligibility_year"
                  v-model="form.eligibility_semester"
                  class="form-select"
                  :class="{ 'is-invalid': errors.eligibility_year }"
                  required
                >
                  <option value="" disabled>Select semester</option>
                  <option v-for="s in semesters" :key="s.value" :value="s.value">{{ s.label }}</option>
                </select>
                <div v-if="errors.eligibility_year" class="invalid-feedback">{{ errors.eligibility_year }}</div>
              </div>
            </div>

            <div class="mb-3">
              <label for="eligibility_year_mode" class="form-label">Year Mode</label>
              <select
                id="eligibility_year_mode"
                v-model="form.eligibility_year_mode"
                class="form-select"
              >
                <option value="exact">This Year Only</option>
                <option value="minimum">This Year &amp; Above</option>
              </select>
            </div>

            <div class="mb-4">
              <label for="application_deadline" class="form-label">Application Deadline <span class="text-danger">*</span></label>
              <input
                id="application_deadline"
                v-model="form.application_deadline"
                type="datetime-local"
                class="form-control"
                :class="{ 'is-invalid': errors.application_deadline }"
                required
              />
              <div v-if="errors.application_deadline" class="invalid-feedback">{{ errors.application_deadline }}</div>
            </div>

            <div class="d-flex gap-3">
              <button type="submit" class="btn btn-primary" :disabled="submitting">
                <span v-if="submitting" class="spinner-border spinner-border-sm me-2" role="status"></span>
                {{ submitting ? 'Creating...' : 'Create Drive' }}
              </button>
              <router-link to="/company/drives" class="btn btn-outline-secondary">
                Cancel
              </router-link>
            </div>
          </form>
        </SectionCard>
      </div>

      <div class="col-lg-4">
        <SectionCard title="Preview">
          <div class="preview-card">
            <div class="preview-field">
              <span class="preview-label">Job Title</span>
              <span class="preview-value">{{ form.job_title || '—' }}</span>
            </div>
            <div class="preview-field">
              <span class="preview-label">Branches</span>
              <span class="preview-value">
                <template v-if="form.eligibility_branches.length">
                  {{ form.eligibility_branches.join(', ') }}
                </template>
                <template v-else>—</template>
              </span>
            </div>
            <div class="preview-field">
              <span class="preview-label">Minimum CGPA</span>
              <span class="preview-value">{{ form.eligibility_cgpa || '—' }}</span>
            </div>
            <div class="preview-field">
              <span class="preview-label">Semester</span>
              <span class="preview-value">{{ selectedSemesterLabel || '—' }}</span>
            </div>
            <div class="preview-field">
              <span class="preview-label">Year Mode</span>
              <span class="preview-value">{{ form.eligibility_year_mode === 'minimum' ? 'This Year & Above' : 'This Year Only' }}</span>
            </div>
            <div class="preview-field">
              <span class="preview-label">Deadline</span>
              <span class="preview-value">{{ formatDeadline(form.application_deadline) }}</span>
            </div>
          </div>
        </SectionCard>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { createDrive } from '@/api/company'
import { getBranches } from '@/api/auth'
import PageHeader from '@/components/common/PageHeader.vue'
import SectionCard from '@/components/common/SectionCard.vue'

const router = useRouter()
const submitting = ref(false)
const errorMessage = ref('')
const branches = ref([])

const semesters = [
  { value: 1, label: '1st Year (1st Semester)' },
  { value: 2, label: '1st Year (2nd Semester)' },
  { value: 3, label: '2nd Year (3rd Semester)' },
  { value: 4, label: '2nd Year (4th Semester)' },
  { value: 5, label: '3rd Year (5th Semester)' },
  { value: 6, label: '3rd Year (6th Semester)' },
  { value: 7, label: '4th Year (7th Semester)' },
  { value: 8, label: '4th Year (8th Semester)' }
]

const semesterToYear = { 1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 8: 4 }

const form = reactive({
  job_title: '',
  job_description: '',
  eligibility_branches: [],
  eligibility_cgpa: '',
  eligibility_semester: '',
  eligibility_year_mode: 'exact',
  application_deadline: ''
})

const errors = reactive({
  job_title: '',
  job_description: '',
  eligibility_branches: '',
  eligibility_cgpa: '',
  eligibility_year: '',
  application_deadline: ''
})

const selectedSemesterLabel = computed(() => {
  const s = semesters.find((s) => s.value === form.eligibility_semester)
  return s ? s.label : ''
})

onMounted(async () => {
  try {
    const res = await getBranches()
    if (res.data.success) branches.value = res.data.branches
  } catch (err) {
    // silently handle
  }
})

const validate = () => {
  Object.keys(errors).forEach((k) => (errors[k] = ''))
  let valid = true

  if (!form.job_title.trim()) {
    errors.job_title = 'Job title is required'
    valid = false
  } else if (form.job_title.length > 120) {
    errors.job_title = 'Job title must be 120 characters or less'
    valid = false
  }

  if (!form.job_description.trim()) {
    errors.job_description = 'Job description is required'
    valid = false
  }

  if (!form.eligibility_branches.length) {
    errors.eligibility_branches = 'Select at least one eligible branch'
    valid = false
  }

  const cgpa = parseFloat(form.eligibility_cgpa)
  if (isNaN(cgpa) || cgpa < 0 || cgpa > 10) {
    errors.eligibility_cgpa = 'CGPA must be between 0 and 10'
    valid = false
  }

  if (form.eligibility_semester === '') {
    errors.eligibility_year = 'Semester is required'
    valid = false
  }

  if (!form.application_deadline) {
    errors.application_deadline = 'Application deadline is required'
    valid = false
  } else {
    const deadline = new Date(form.application_deadline)
    if (isNaN(deadline.getTime())) {
      errors.application_deadline = 'Please enter a valid date'
      valid = false
    } else if (deadline <= new Date()) {
      errors.application_deadline = 'Deadline must be in the future'
      valid = false
    }
  }

  return valid
}

const getErrorMessage = (code) => {
  const messages = {
    missing_fields: 'Please fill in all required fields',
    company_not_approved: 'Your company account must be approved before creating drives',
    no_company_profile: 'Company profile not found',
    invalid_branch: 'Please select a valid branch',
    invalid_deadline_format: 'Please enter a valid deadline',
    invalid_eligibility_cgpa: 'Please enter a valid CGPA',
    invalid_eligibility_year: 'Please enter a valid year',
    invalid_eligibility_year_mode: 'Please select a valid year mode',
    string_too_long: 'One or more fields exceed maximum length',
    server_error: 'Server error. Please try again later'
  }
  return messages[code] || 'An error occurred. Please try again'
}

const handleSubmit = async () => {
  errorMessage.value = ''

  if (!validate()) return

  submitting.value = true
  try {
    const deadline = new Date(form.application_deadline)
    await createDrive({
      job_title: form.job_title.trim(),
      job_description: form.job_description.trim(),
      eligibility_branches: form.eligibility_branches,
      eligibility_cgpa: parseFloat(form.eligibility_cgpa),
      eligibility_year: semesterToYear[form.eligibility_semester],
      eligibility_year_mode: form.eligibility_year_mode,
      application_deadline: deadline.toISOString()
    })
    router.push('/company/drives')
  } catch (err) {
    const code = err.response?.data?.error
    errorMessage.value = getErrorMessage(code)
  } finally {
    submitting.value = false
  }
}

const formatDeadline = (val) => {
  if (!val) return '—'
  const d = new Date(val)
  if (isNaN(d.getTime())) return '—'
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}
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

.branch-checkboxes {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-3);
  background: var(--color-surface);
}

.branch-checkboxes.is-invalid {
  border-color: var(--color-danger);
}

.branch-checkboxes .form-check {
  margin-bottom: var(--space-1);
}

.branch-checkboxes .form-check:last-child {
  margin-bottom: 0;
}

.preview-card {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.preview-field {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.preview-label {
  font-size: var(--text-xs);
  font-weight: var(--weight-medium);
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.preview-value {
  font-size: var(--text-sm);
  color: var(--text-primary);
}
</style>
