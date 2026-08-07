<template>
  <div>
    <PageHeader title="My Profile" subtitle="Manage your personal information and resume" />

    <div v-if="loading" class="row g-4">
      <div class="col-lg-8">
        <div class="skeleton-card"></div>
      </div>
      <div class="col-lg-4">
        <div class="skeleton-card"></div>
      </div>
    </div>

    <template v-else>
      <div v-if="successMessage" class="alert alert-success alert-dismissible fade show" role="alert">
        <i class="bi bi-check-circle me-2"></i>{{ successMessage }}
        <button type="button" class="btn-close" @click="successMessage = ''" aria-label="Close"></button>
      </div>

      <div v-if="errorMessage" class="alert alert-danger alert-dismissible fade show" role="alert">
        {{ errorMessage }}
        <button type="button" class="btn-close" @click="errorMessage = ''" aria-label="Close"></button>
      </div>

      <div class="row g-4">
        <div class="col-lg-8">
          <SectionCard title="Personal Information">
            <form @submit.prevent="handleSaveProfile">
              <div class="mb-3">
                <label for="name" class="form-label">Full Name <span class="text-danger">*</span></label>
                <input
                  id="name"
                  v-model="form.name"
                  type="text"
                  class="form-control"
                  :class="{ 'is-invalid': errors.name }"
                  required
                />
                <div v-if="errors.name" class="invalid-feedback">{{ errors.name }}</div>
              </div>

              <div class="mb-3">
                <label for="email" class="form-label">Email</label>
                <input
                  id="email"
                  :value="profile?.email"
                  type="email"
                  class="form-control"
                  disabled
                />
                <div class="form-text">Email is managed by your account settings.</div>
              </div>

              <div class="row mb-3">
                <div class="col-md-6">
                  <label for="branch" class="form-label">Branch <span class="text-danger">*</span></label>
                  <select
                    id="branch"
                    v-model="form.branch"
                    class="form-select"
                    :class="{ 'is-invalid': errors.branch }"
                    required
                  >
                    <option value="" disabled>Select your branch</option>
                    <option v-for="b in branches" :key="b" :value="b">{{ b }}</option>
                  </select>
                  <div v-if="errors.branch" class="invalid-feedback">{{ errors.branch }}</div>
                </div>
                <div class="col-md-6">
                  <label for="year" class="form-label">Year <span class="text-danger">*</span></label>
                  <input
                    id="year"
                    v-model="form.year"
                    type="number"
                    min="1"
                    max="4"
                    class="form-control"
                    :class="{ 'is-invalid': errors.year }"
                    required
                  />
                  <div v-if="errors.year" class="invalid-feedback">{{ errors.year }}</div>
                </div>
              </div>

              <div class="mb-4">
                <label for="cgpa" class="form-label">CGPA <span class="text-danger">*</span></label>
                <input
                  id="cgpa"
                  v-model="form.cgpa"
                  type="number"
                  step="0.01"
                  min="0"
                  max="10"
                  class="form-control"
                  :class="{ 'is-invalid': errors.cgpa }"
                  required
                />
                <div v-if="errors.cgpa" class="invalid-feedback">{{ errors.cgpa }}</div>
              </div>

              <button type="submit" class="btn btn-primary" :disabled="saving">
                <span v-if="saving" class="spinner-border spinner-border-sm me-2" role="status"></span>
                {{ saving ? 'Saving...' : 'Save Changes' }}
              </button>
            </form>
          </SectionCard>
        </div>

        <div class="col-lg-4">
          <SectionCard title="Resume">
            <div v-if="profile?.resume_path" class="resume-preview">
              <div class="resume-info">
                <i class="bi bi-file-earmark-pdf resume-icon"></i>
                <div>
                  <div class="fw-medium">Resume uploaded</div>
                  <div class="text-secondary small">PDF document</div>
                </div>
              </div>
              <div class="d-flex gap-2 mt-3">
                <a
                  :href="resumeUrl"
                  target="_blank"
                  class="btn btn-outline-primary btn-sm flex-grow-1"
                >
                  <i class="bi bi-eye me-1"></i> View
                </a>
                <label class="btn btn-outline-secondary btn-sm flex-grow-1 mb-0">
                  <i class="bi bi-arrow-repeat me-1"></i> Replace
                  <input
                    type="file"
                    accept=".pdf"
                    class="d-none"
                    @change="handleResumeUpload"
                    :disabled="uploading"
                  />
                </label>
              </div>
            </div>

            <div v-else class="text-center py-4">
              <div class="mb-3">
                <i class="bi bi-cloud-arrow-up resume-upload-icon"></i>
              </div>
              <p class="text-secondary mb-3">No resume uploaded yet</p>
              <label class="btn btn-primary btn-sm mb-0">
                <i class="bi bi-upload me-1"></i> Upload Resume
                <input
                  type="file"
                  accept=".pdf"
                  class="d-none"
                  @change="handleResumeUpload"
                  :disabled="uploading"
                />
              </label>
            </div>

            <div v-if="uploading" class="text-center mt-3">
              <div class="spinner-border spinner-border-sm text-primary me-2" role="status"></div>
              <span class="text-secondary small">Uploading...</span>
            </div>

            <div v-if="resumeError" class="alert alert-danger mt-3 mb-0" role="alert">
              {{ resumeError }}
            </div>

            <div class="form-text mt-3">PDF only. Maximum file size: 5MB.</div>
          </SectionCard>

          <SectionCard title="Profile Info" class="mt-4">
            <div class="info-grid">
              <div class="info-field">
                <span class="info-label">Member Since</span>
                <span class="info-value">{{ formatDate(profile?.created_at) }}</span>
              </div>
            </div>
          </SectionCard>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { getProfile, updateProfile, uploadResume } from '@/api/student'
import { getBranches } from '@/api/auth'
import PageHeader from '@/components/common/PageHeader.vue'
import SectionCard from '@/components/common/SectionCard.vue'

const profile = ref(null)
const loading = ref(true)
const saving = ref(false)
const uploading = ref(false)
const successMessage = ref('')
const errorMessage = ref('')
const resumeError = ref('')
const branches = ref([])

const form = reactive({
  name: '',
  branch: '',
  cgpa: '',
  year: ''
})

const errors = reactive({
  name: '',
  branch: '',
  cgpa: '',
  year: ''
})

const resumeUrl = computed(() => {
  if (!profile.value?.resume_path) return ''
  return `/${profile.value.resume_path}`
})

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

const populateForm = (data) => {
  form.name = data.name || ''
  form.branch = data.branch || ''
  form.cgpa = data.cgpa ?? ''
  form.year = data.year ?? ''
}

const validate = () => {
  Object.keys(errors).forEach(k => (errors[k] = ''))
  let valid = true

  if (!form.name.trim()) {
    errors.name = 'Name is required'
    valid = false
  } else if (form.name.length > 120) {
    errors.name = 'Name must be 120 characters or less'
    valid = false
  }

  if (!form.branch) {
    errors.branch = 'Branch is required'
    valid = false
  }

  const cgpa = parseFloat(form.cgpa)
  if (isNaN(cgpa) || cgpa < 0 || cgpa > 10) {
    errors.cgpa = 'CGPA must be between 0 and 10'
    valid = false
  }

  const year = parseInt(form.year)
  if (isNaN(year) || year < 1) {
    errors.year = 'Year must be a positive integer'
    valid = false
  }

  return valid
}

const handleSaveProfile = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  if (!validate()) return

  saving.value = true
  try {
    const res = await updateProfile({
      name: form.name.trim(),
      branch: form.branch,
      cgpa: parseFloat(form.cgpa),
      year: parseInt(form.year)
    })
    if (res.data.success) {
      profile.value = {
        ...profile.value,
        name: res.data.name,
        email: res.data.email,
        branch: res.data.branch,
        cgpa: res.data.cgpa,
        year: res.data.year
      }
      successMessage.value = 'Profile updated successfully!'
    }
  } catch (err) {
    const code = err.response?.data?.error
    if (code === 'validation_failed') {
      const details = err.response?.data?.details || []
      errorMessage.value = details.join('. ')
    } else {
      errorMessage.value = 'Failed to update profile. Please try again.'
    }
  } finally {
    saving.value = false
  }
}

const handleResumeUpload = async (event) => {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file) return

  resumeError.value = ''
  successMessage.value = ''

  if (!file.name.toLowerCase().endsWith('.pdf')) {
    resumeError.value = 'Only PDF files are accepted.'
    return
  }

  if (file.size > 5 * 1024 * 1024) {
    resumeError.value = 'File size must be 5MB or less.'
    return
  }

  uploading.value = true
  try {
    const res = await uploadResume(file)
    if (res.data.success) {
      profile.value = {
        ...profile.value,
        resume_path: res.data.stored_path
      }
      successMessage.value = 'Resume uploaded successfully!'
    }
  } catch (err) {
    const code = err.response?.data?.error
    if (code === 'invalid_file_type') {
      resumeError.value = 'Only PDF files are accepted.'
    } else if (code === 'missing_file') {
      resumeError.value = 'Please select a file to upload.'
    } else {
      resumeError.value = 'Failed to upload resume. Please try again.'
    }
  } finally {
    uploading.value = false
  }
}

const fetchProfile = async () => {
  loading.value = true
  try {
    const [profileRes, branchesRes] = await Promise.all([
      getProfile(),
      getBranches().catch(() => ({ data: { success: false } }))
    ])
    if (profileRes.data.success) {
      profile.value = profileRes.data
      populateForm(profileRes.data)
    }
    if (branchesRes.data.success) branches.value = branchesRes.data.branches
  } catch (err) {
    errorMessage.value = 'Failed to load profile.'
  } finally {
    loading.value = false
  }
}

onMounted(fetchProfile)
</script>

<style scoped>
.skeleton-card {
  height: 300px;
  background: linear-gradient(90deg, var(--color-surface-muted) 25%, var(--color-surface-hover) 50%, var(--color-surface-muted) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-lg);
}

.resume-preview {
  text-align: center;
}

.resume-info {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  background: var(--color-surface-muted);
  border-radius: var(--radius-md);
}

.resume-icon {
  font-size: 2rem;
  color: var(--color-danger);
}

.resume-upload-icon {
  font-size: 3rem;
  color: var(--text-tertiary);
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

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
