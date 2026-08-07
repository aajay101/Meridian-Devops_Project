<template>
  <div>
    <router-link to="/student/drives" class="back-link">
      <i class="bi bi-arrow-left"></i> Available Drives
    </router-link>

    <div v-if="loading" class="skeleton-card"></div>

    <template v-else-if="drive">
      <PageHeader :title="drive.job_title" :subtitle="drive.company_name" />

      <div class="row g-4 mb-4">
        <div class="col-lg-8">
          <SectionCard title="Job Description">
            <pre class="job-description">{{ drive.job_description }}</pre>
          </SectionCard>

          <SectionCard title="Application Deadline" class="mt-4">
            <div class="d-flex align-items-center gap-3">
              <span :class="{ 'text-danger fw-bold': isPastDeadline }">
                {{ formatDate(drive.application_deadline) }}
              </span>
              <span v-if="isPastDeadline" class="badge bg-danger">Deadline Passed</span>
              <span v-else class="badge bg-success">Open</span>
            </div>
          </SectionCard>
        </div>

        <div class="col-lg-4">
          <SectionCard title="Eligibility Criteria">
            <div class="info-grid">
              <div class="info-field">
                <span class="info-label">Branches</span>
                <span class="info-value">{{ drive.eligibility_branches.join(', ') }}</span>
              </div>
              <div class="info-field">
                <span class="info-label">Minimum CGPA</span>
                <span class="info-value">{{ drive.eligibility_cgpa }}</span>
              </div>
              <div class="info-field">
                <span class="info-label">Year</span>
                <span class="info-value">
                  {{ drive.eligibility_year }}
                  <span class="text-secondary ms-1">({{ drive.eligibility_year_mode === 'minimum' ? 'Minimum' : 'Exact' }})</span>
                </span>
              </div>
            </div>
          </SectionCard>

          <SectionCard title="Your Eligibility" class="mt-4">
            <div v-if="studentProfile" class="info-grid">
              <div class="info-field">
                <span class="info-label">Your Branch</span>
                <span class="info-value" :class="drive.eligibility_branches.includes(studentProfile.branch) ? 'text-success' : 'text-danger'">
                  {{ studentProfile.branch }}
                  <i v-if="drive.eligibility_branches.includes(studentProfile.branch)" class="bi bi-check-circle-fill ms-1"></i>
                  <i v-else class="bi bi-x-circle-fill ms-1"></i>
                </span>
              </div>
              <div class="info-field">
                <span class="info-label">Your CGPA</span>
                <span class="info-value" :class="studentProfile.cgpa >= drive.eligibility_cgpa ? 'text-success' : 'text-danger'">
                  {{ studentProfile.cgpa }}
                  <i v-if="studentProfile.cgpa >= drive.eligibility_cgpa" class="bi bi-check-circle-fill ms-1"></i>
                  <i v-else class="bi bi-x-circle-fill ms-1"></i>
                </span>
              </div>
              <div class="info-field">
                <span class="info-label">Your Year</span>
                <span class="info-value" :class="isYearEligible ? 'text-success' : 'text-danger'">
                  {{ studentProfile.year }}
                  <i v-if="isYearEligible" class="bi bi-check-circle-fill ms-1"></i>
                  <i v-else class="bi bi-x-circle-fill ms-1"></i>
                </span>
              </div>
            </div>
            <div v-else class="text-secondary small">
              Loading your profile...
            </div>
          </SectionCard>

          <SectionCard class="mt-4">
            <div v-if="successMessage" class="alert alert-success mb-0" role="alert">
              <i class="bi bi-check-circle me-2"></i>{{ successMessage }}
            </div>
            <div v-else-if="errorMessage" class="alert alert-danger mb-0" role="alert">
              {{ errorMessage }}
            </div>
            <div v-else>
              <button
                v-if="alreadyApplied"
                class="btn btn-success w-100"
                disabled
              >
                <i class="bi bi-check-circle me-2"></i> Already Applied
              </button>
              <button
                v-else-if="isPastDeadline"
                class="btn btn-secondary w-100"
                disabled
              >
                Application Closed
              </button>
              <button
                v-else-if="!eligible"
                class="btn btn-secondary w-100"
                disabled
              >
                Not Eligible
              </button>
              <div v-else-if="maxOffersReached" class="alert alert-warning mb-0">
                <div class="d-flex align-items-center">
                  <i class="bi bi-exclamation-triangle-fill me-2"></i>
                  <div>
                    <strong>Maximum Active Offers Reached</strong>
                    <div class="small mt-1">
                      You currently have the maximum number of pending offers.
                      Accept or decline an existing offer before applying to more drives.
                    </div>
                  </div>
                </div>
              </div>
              <button
                v-else
                class="btn btn-primary w-100"
                @click="openApplyDialog"
                :disabled="submitting"
              >
                <span v-if="submitting" class="spinner-border spinner-border-sm me-2" role="status"></span>
                {{ submitting ? 'Applying...' : 'Apply Now' }}
              </button>
            </div>
          </SectionCard>
        </div>
      </div>
    </template>

    <!-- Apply Dialog -->
    <div v-if="showApplyDialog" class="confirm-dialog-backdrop" @click.self="closeApplyDialog">
      <div class="confirm-dialog" role="dialog" aria-modal="true">
        <div class="confirm-dialog-header">
          <h3 class="confirm-dialog-title">Apply for {{ drive?.job_title }}</h3>
          <button class="confirm-dialog-close" @click="closeApplyDialog" aria-label="Close">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
        <div class="confirm-dialog-body">
          <p class="dialog-subtitle">Choose the resume you want to submit for this specific job application.</p>

          <div v-if="applyError" class="alert alert-danger py-2 mb-3">{{ applyError }}</div>

          <!-- Option 1: Use Profile Resume -->
          <div class="resume-option" :class="{ selected: resumeChoice === 'profile' }">
            <label class="resume-option-header">
              <input type="radio" v-model="resumeChoice" value="profile" class="form-check-input" />
              <span class="fw-medium">Use Current Profile Resume</span>
            </label>
            <div v-if="resumeChoice === 'profile'" class="resume-option-detail">
              <div v-if="profileResumePath">
                <div class="d-flex align-items-center gap-2">
                  <i class="bi bi-file-earmark-pdf text-danger"></i>
                  <span class="text-secondary small">{{ profileResumeName }}</span>
                </div>
              </div>
              <div v-else class="text-warning small">
                <i class="bi bi-exclamation-triangle me-1"></i>
                No profile resume uploaded. Please upload a resume first or choose Option 2.
              </div>
            </div>
          </div>

          <!-- Option 2: Upload Job-Specific Resume -->
          <div class="resume-option" :class="{ selected: resumeChoice === 'upload' }">
            <label class="resume-option-header">
              <input type="radio" v-model="resumeChoice" value="upload" class="form-check-input" />
              <span class="fw-medium">Upload Resume for This Job</span>
            </label>
            <div v-if="resumeChoice === 'upload'" class="resume-option-detail">
              <label class="btn btn-outline-primary btn-sm mb-0">
                <i class="bi bi-upload me-1"></i> Choose PDF
                <input
                  type="file"
                  accept=".pdf"
                  class="d-none"
                  @change="handleFileSelect"
                  ref="fileInput"
                />
              </label>
              <div v-if="selectedFile" class="d-flex align-items-center gap-2 mt-2">
                <i class="bi bi-file-earmark-pdf text-success"></i>
                <span class="text-secondary small">{{ selectedFile.name }}</span>
                <button class="btn btn-link btn-sm p-0 text-danger" @click="clearFile">
                  <i class="bi bi-x-circle"></i>
                </button>
              </div>
              <div class="form-text mt-2">PDF only. Maximum 5 MB.</div>
            </div>
          </div>
        </div>
        <div class="confirm-dialog-footer">
          <button class="btn btn-secondary" @click="closeApplyDialog" :disabled="submitting">Cancel</button>
          <button
            class="btn btn-primary"
            @click="handleApplySubmit"
            :disabled="submitting || !canSubmit"
          >
            <span v-if="submitting" class="spinner-border spinner-border-sm me-2" role="status"></span>
            {{ submitting ? 'Submitting...' : 'Submit Application' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getDrive, applyToDrive, applyToDriveWithResume, getApplications, getProfile } from '@/api/student'
import PageHeader from '@/components/common/PageHeader.vue'
import SectionCard from '@/components/common/SectionCard.vue'

const route = useRoute()
const router = useRouter()

const drive = ref(null)
const loading = ref(false)
const submitting = ref(false)
const alreadyApplied = ref(false)
const studentProfile = ref(null)
const successMessage = ref('')
const errorMessage = ref('')
const maxOffersReached = ref(false)

const showApplyDialog = ref(false)
const resumeChoice = ref('profile')
const selectedFile = ref(null)
const applyError = ref('')
const fileInput = ref(null)

const hasProfileResume = computed(() => !!studentProfile.value?.resume_path)

const profileResumePath = computed(() => studentProfile.value?.resume_path || '')

const profileResumeName = computed(() => {
  const p = profileResumePath.value
  if (!p) return ''
  const parts = p.split('/')
  return parts[parts.length - 1]
})

const canSubmit = computed(() => {
  if (resumeChoice.value === 'profile') return hasProfileResume.value
  if (resumeChoice.value === 'upload') return !!selectedFile.value
  return false
})

const isPastDeadline = computed(() => {
  if (!drive.value) return false
  return new Date(drive.value.application_deadline) < new Date()
})

const isYearEligible = computed(() => {
  if (!studentProfile.value || !drive.value) return false
  if (drive.value.eligibility_year_mode === 'minimum') {
    return studentProfile.value.year >= drive.value.eligibility_year
  }
  return studentProfile.value.year === drive.value.eligibility_year
})

const eligible = computed(() => {
  if (!studentProfile.value || !drive.value) return false
  const sp = studentProfile.value
  if (!drive.value.eligibility_branches.includes(sp.branch)) return false
  if (sp.cgpa < drive.value.eligibility_cgpa) return false
  return isYearEligible.value
})

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

const openApplyDialog = () => {
  errorMessage.value = ''
  applyError.value = ''
  selectedFile.value = null
  resumeChoice.value = hasProfileResume.value ? 'profile' : 'upload'
  showApplyDialog.value = true
}

const closeApplyDialog = () => {
  showApplyDialog.value = false
  applyError.value = ''
  selectedFile.value = null
  if (fileInput.value) fileInput.value.value = ''
}

const handleFileSelect = (event) => {
  const file = event.target.files?.[0]
  event.target.value = ''
  applyError.value = ''

  if (!file) return

  if (!file.name.toLowerCase().endsWith('.pdf')) {
    applyError.value = 'Only PDF files are accepted.'
    return
  }

  if (file.size > 5 * 1024 * 1024) {
    applyError.value = 'File size must be 5 MB or less.'
    return
  }

  selectedFile.value = file
}

const clearFile = () => {
  selectedFile.value = null
  if (fileInput.value) fileInput.value.value = ''
}

const handleApplySubmit = async () => {
  applyError.value = ''
  submitting.value = true

  try {
    if (resumeChoice.value === 'upload' && selectedFile.value) {
      await applyToDriveWithResume(route.params.id, selectedFile.value)
    } else {
      await applyToDrive(route.params.id)
    }

    showApplyDialog.value = false
    alreadyApplied.value = true
    successMessage.value = 'Application submitted successfully!'
  } catch (err) {
    const code = err.response?.data?.error
    if (code === 'ineligible') {
      const violations = err.response?.data?.violations || []
      const labels = { branch: 'branch', cgpa: 'CGPA', year: 'year' }
      const reasons = violations.map(v => labels[v] || v).join(', ')
      applyError.value = `You are not eligible for this drive. Mismatched: ${reasons}`
    } else if (code === 'already_applied') {
      alreadyApplied.value = true
      showApplyDialog.value = false
      successMessage.value = 'You have already applied to this drive.'
    } else if (code === 'drive_not_available') {
      applyError.value = 'This drive is no longer available.'
    } else if (code === 'missing_file') {
      applyError.value = 'Please select a PDF file to upload.'
    } else if (code === 'invalid_file_type') {
      applyError.value = 'Only PDF files are accepted.'
    } else if (code === 'max_offers_reached') {
      maxOffersReached.value = true
      applyError.value = 'Maximum Active Offers Reached. Accept or decline an existing offer before applying to more drives.'
    } else {
      applyError.value = 'An error occurred. Please try again.'
    }
  } finally {
    submitting.value = false
  }
}

const fetchAll = async () => {
  loading.value = true
  try {
    const driveId = route.params.id
    const [driveRes, appsRes, profileRes] = await Promise.all([
      getDrive(driveId),
      getApplications().catch(() => ({ data: { success: false } })),
      getProfile().catch(() => ({ data: { success: false } }))
    ])

    if (driveRes.data.success) {
      drive.value = driveRes.data.drive
    } else {
      router.push('/student/drives')
      return
    }

    if (appsRes.data.success) {
      const ids = appsRes.data.applications.map(a => a.drive_id)
      alreadyApplied.value = ids.includes(drive.value.drive_id)
      if (alreadyApplied.value) {
        successMessage.value = 'You have already applied to this drive.'
      }
    }

    if (profileRes.data.success) {
      studentProfile.value = {
        branch: profileRes.data.branch,
        cgpa: profileRes.data.cgpa,
        year: profileRes.data.year,
        resume_path: profileRes.data.resume_path
      }
    }
  } catch (err) {
    router.push('/student/drives')
  } finally {
    loading.value = false
  }
}

onMounted(fetchAll)
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

.job-description {
  font-family: var(--font-family);
  font-size: var(--text-sm);
  color: var(--text-primary);
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
  background: none;
  border: none;
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

.confirm-dialog-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: var(--space-4);
}

.confirm-dialog {
  background-color: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  width: 100%;
  max-width: 520px;
  overflow: hidden;
}

.confirm-dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--color-border);
}

.confirm-dialog-title {
  font-size: var(--text-md);
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
  margin: 0;
}

.confirm-dialog-close {
  background: none;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  padding: var(--space-1);
  font-size: var(--text-sm);
  transition: color var(--duration-base) var(--ease-default);
}

.confirm-dialog-close:hover {
  color: var(--text-primary);
}

.confirm-dialog-body {
  padding: var(--space-5);
}

.dialog-subtitle {
  margin: 0 0 var(--space-4) 0;
  color: var(--text-secondary);
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
}

.resume-option {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-3) var(--space-4);
  margin-bottom: var(--space-3);
  transition: border-color var(--duration-base) var(--ease-default);
}

.resume-option.selected {
  border-color: var(--color-primary);
  background-color: color-mix(in srgb, var(--color-primary) 5%, transparent);
}

.resume-option-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  cursor: pointer;
  margin-bottom: 0;
}

.resume-option-header .form-check-input {
  margin-top: 0;
}

.resume-option-detail {
  margin-top: var(--space-2);
  padding-left: calc(var(--space-2) + 18px);
}

.confirm-dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-5);
  border-top: 1px solid var(--color-border);
}
</style>
