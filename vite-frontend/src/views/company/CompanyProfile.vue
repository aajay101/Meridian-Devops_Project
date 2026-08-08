<template>
  <div>
    <PageHeader title="Company Profile" subtitle="Manage your company information" />

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
          <SectionCard title="Company Information">
            <form @submit.prevent="handleSave">
              <div class="mb-3">
                <label for="company_name" class="form-label">Company Name <span class="text-danger">*</span></label>
                <input
                  id="company_name"
                  v-model="form.company_name"
                  type="text"
                  class="form-control"
                  :class="{ 'is-invalid': errors.company_name }"
                  required
                />
                <div v-if="errors.company_name" class="invalid-feedback">{{ errors.company_name }}</div>
              </div>

              <div class="mb-3">
                <label for="hr_contact" class="form-label">HR Contact <span class="text-danger">*</span></label>
                <input
                  id="hr_contact"
                  v-model="form.hr_contact"
                  type="text"
                  class="form-control"
                  :class="{ 'is-invalid': errors.hr_contact }"
                  placeholder="e.g. John Doe"
                  required
                />
                <div v-if="errors.hr_contact" class="invalid-feedback">{{ errors.hr_contact }}</div>
              </div>

              <div class="mb-3">
                <label for="website" class="form-label">Website</label>
                <input
                  id="website"
                  v-model="form.website"
                  type="url"
                  class="form-control"
                  :class="{ 'is-invalid': errors.website }"
                  placeholder="https://example.com"
                />
                <div v-if="errors.website" class="invalid-feedback">{{ errors.website }}</div>
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

              <div class="mb-3">
                <label for="phone_number" class="form-label">Account Owner Phone Number</label>
                <input id="phone_number" v-model="form.phone_number" type="tel" class="form-control" :class="{ 'is-invalid': errors.phone_number }" placeholder="9876543210" />
                <div v-if="errors.phone_number" class="invalid-feedback">{{ errors.phone_number }}</div>
              </div>

              <button type="submit" class="btn btn-primary" :disabled="saving">
                <span v-if="saving" class="spinner-border spinner-border-sm me-2" role="status"></span>
                {{ saving ? 'Saving...' : 'Save Changes' }}
              </button>
            </form>
          </SectionCard>
        </div>

        <div class="col-lg-4">
          <SectionCard title="Account Info">
            <div class="info-grid">
              <div class="info-field">
                <span class="info-label">Approval Status</span>
                <span class="info-value">
                  <span
                    class="badge"
                    :class="{
                      'bg-success': profile?.approval_status === 'Approved',
                      'bg-warning text-dark': profile?.approval_status === 'Pending',
                      'bg-danger': profile?.approval_status === 'Rejected'
                    }"
                  >
                    {{ profile?.approval_status || '—' }}
                  </span>
                </span>
              </div>
              <div class="info-field">
                <span class="info-label">Member Since</span>
                <span class="info-value data-value">{{ formatDate(profile?.created_at) }}</span>
              </div>
            </div>
          </SectionCard>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getProfile, updateProfile } from '@/api/company'
import PageHeader from '@/components/common/PageHeader.vue'
import SectionCard from '@/components/common/SectionCard.vue'

const profile = ref(null)
const loading = ref(true)
const saving = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

const form = reactive({
  company_name: '',
  phone_number: '',
  hr_contact: '',
  website: ''
})

const errors = reactive({
  company_name: '',
  phone_number: '',
  hr_contact: '',
  website: ''
})

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

const populateForm = (data) => {
  form.company_name = data.company_name || ''
  form.phone_number = data.phone_number || ''
  form.hr_contact = data.hr_contact || ''
  form.website = data.website || ''
}

const validate = () => {
  Object.keys(errors).forEach(k => (errors[k] = ''))
  let valid = true

  if (!form.company_name.trim()) {
    errors.company_name = 'Company name is required'
    valid = false
  } else if (form.company_name.length > 120) {
    errors.company_name = 'Company name must be 120 characters or less'
    valid = false
  }

  if (!form.hr_contact.trim()) {
    errors.hr_contact = 'HR contact is required'
    valid = false
  } else if (form.hr_contact.length > 120) {
    errors.hr_contact = 'HR contact must be 120 characters or less'
    valid = false
  }

  if (form.website && form.website.length > 255) {
    errors.website = 'Website must be 255 characters or less'
    valid = false
  }

  if (form.phone_number && !/^[6-9]\d{9}$/.test(form.phone_number.trim())) {
    errors.phone_number = 'Enter a valid 10-digit Indian mobile number'
    valid = false
  }

  return valid
}

const handleSave = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  if (!validate()) return

  saving.value = true
  try {
    const payload = {
      company_name: form.company_name.trim(),
      hr_contact: form.hr_contact.trim()
    }
    if (form.phone_number.trim()) payload.phone_number = form.phone_number.trim()
    if (form.website.trim()) {
      payload.website = form.website.trim()
    } else {
      payload.website = null
    }

    const res = await updateProfile(payload)
    if (res.data.success) {
      profile.value = res.data.company
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

const fetchProfile = async () => {
  loading.value = true
  try {
    const res = await getProfile()
    if (res.data.success) {
      profile.value = res.data.company
      populateForm(res.data.company)
    }
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
