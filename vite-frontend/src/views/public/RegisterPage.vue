<template>
  <div>
    <h2 class="auth-subtitle">Create your account</h2>

    <div class="register-tabs">
      <button
        type="button"
        class="register-tab"
        :class="{ active: activeTab === 'student' }"
        @click="activeTab = 'student'"
      >
        <i class="bi bi-person me-1"></i> Student
      </button>
      <button
        type="button"
        class="register-tab"
        :class="{ active: activeTab === 'company' }"
        @click="activeTab = 'company'"
      >
        <i class="bi bi-building me-1"></i> Company
      </button>
    </div>

    <div v-if="successMessage" class="alert alert-success" role="alert">
      {{ successMessage }}
    </div>

    <div v-if="errorMessage" class="alert alert-danger" role="alert">
      {{ errorMessage }}
    </div>

    <!-- Student Registration -->
    <form v-if="activeTab === 'student'" @submit.prevent="handleStudentRegister">
      <div class="mb-3">
        <label for="student-name" class="form-label">Full Name</label>
        <input
          id="student-name"
          v-model="studentForm.name"
          type="text"
          class="form-control"
          :class="{ 'is-invalid': studentErrors.name }"
          placeholder="Enter your full name"
          required
        />
        <div v-if="studentErrors.name" class="invalid-feedback">{{ studentErrors.name }}</div>
      </div>

      <div class="mb-3">
        <label for="student-email" class="form-label">Email</label>
        <input
          id="student-email"
          v-model="studentForm.email"
          type="email"
          class="form-control"
          :class="{ 'is-invalid': studentErrors.email }"
          placeholder="Enter your email"
          required
        />
        <div v-if="studentErrors.email" class="invalid-feedback">{{ studentErrors.email }}</div>
      </div>

      <div class="mb-3">
        <label for="student-password" class="form-label">Password</label>
        <input
          id="student-password"
          v-model="studentForm.password"
          type="password"
          class="form-control"
          :class="{ 'is-invalid': studentErrors.password }"
          placeholder="Min 8 characters"
          required
        />
        <div v-if="studentErrors.password" class="invalid-feedback">{{ studentErrors.password }}</div>
      </div>

      <div class="mb-3">
        <label for="student-branch" class="form-label">Branch</label>
        <select
          id="student-branch"
          v-model="studentForm.branch"
          class="form-select"
          :class="{ 'is-invalid': studentErrors.branch }"
          required
        >
          <option value="" disabled>Select your branch</option>
          <option v-for="b in branches" :key="b" :value="b">{{ b }}</option>
        </select>
        <div v-if="studentErrors.branch" class="invalid-feedback">{{ studentErrors.branch }}</div>
      </div>

      <div class="row mb-4">
        <div class="col-6">
          <label for="student-cgpa" class="form-label">CGPA</label>
          <input
            id="student-cgpa"
            v-model="studentForm.cgpa"
            type="number"
            step="0.01"
            min="0"
            max="10"
            class="form-control"
            :class="{ 'is-invalid': studentErrors.cgpa }"
            placeholder="0.00"
            required
          />
          <div v-if="studentErrors.cgpa" class="invalid-feedback">{{ studentErrors.cgpa }}</div>
        </div>
        <div class="col-6">
          <label for="student-year" class="form-label">Year</label>
          <input
            id="student-year"
            v-model="studentForm.year"
            type="number"
            min="1"
            class="form-control"
            :class="{ 'is-invalid': studentErrors.year }"
            placeholder="1-4"
            required
          />
          <div v-if="studentErrors.year" class="invalid-feedback">{{ studentErrors.year }}</div>
        </div>
      </div>

      <button
        type="submit"
        class="btn btn-primary w-100"
        :disabled="authStore.loading"
      >
        <span v-if="authStore.loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
        {{ authStore.loading ? 'Creating account...' : 'Create Student Account' }}
      </button>
    </form>

    <!-- Company Registration -->
    <form v-if="activeTab === 'company'" @submit.prevent="handleCompanyRegister">
      <div class="mb-3">
        <label for="company-name" class="form-label">Company Name</label>
        <input
          id="company-name"
          v-model="companyForm.company_name"
          type="text"
          class="form-control"
          :class="{ 'is-invalid': companyErrors.company_name }"
          placeholder="Enter company name"
          required
        />
        <div v-if="companyErrors.company_name" class="invalid-feedback">{{ companyErrors.company_name }}</div>
      </div>

      <div class="mb-3">
        <label for="company-email" class="form-label">Email</label>
        <input
          id="company-email"
          v-model="companyForm.email"
          type="email"
          class="form-control"
          :class="{ 'is-invalid': companyErrors.email }"
          placeholder="Enter company email"
          required
        />
        <div v-if="companyErrors.email" class="invalid-feedback">{{ companyErrors.email }}</div>
      </div>

      <div class="mb-3">
        <label for="company-password" class="form-label">Password</label>
        <input
          id="company-password"
          v-model="companyForm.password"
          type="password"
          class="form-control"
          :class="{ 'is-invalid': companyErrors.password }"
          placeholder="Min 8 characters"
          required
        />
        <div v-if="companyErrors.password" class="invalid-feedback">{{ companyErrors.password }}</div>
      </div>

      <div class="mb-3">
        <label for="company-hr" class="form-label">HR Contact</label>
        <input
          id="company-hr"
          v-model="companyForm.hr_contact"
          type="text"
          class="form-control"
          :class="{ 'is-invalid': companyErrors.hr_contact }"
          placeholder="10-digit phone number"
          required
        />
        <div v-if="companyErrors.hr_contact" class="invalid-feedback">{{ companyErrors.hr_contact }}</div>
      </div>

      <div class="mb-4">
        <label for="company-website" class="form-label">Website <span class="text-secondary">(optional)</span></label>
        <input
          id="company-website"
          v-model="companyForm.website"
          type="url"
          class="form-control"
          placeholder="https://example.com"
        />
      </div>

      <button
        type="submit"
        class="btn btn-primary w-100"
        :disabled="authStore.loading"
      >
        <span v-if="authStore.loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
        {{ authStore.loading ? 'Creating account...' : 'Create Company Account' }}
      </button>
    </form>

    <p class="auth-link text-center mt-4">
      Already have an account?
      <router-link to="/login">Sign in here</router-link>
    </p>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getBranches } from '@/api/auth'

const router = useRouter()
const authStore = useAuthStore()

const activeTab = ref('student')
const successMessage = ref('')
const errorMessage = ref('')
const branches = ref([])

const studentForm = reactive({
  name: '',
  email: '',
  password: '',
  branch: '',
  cgpa: '',
  year: ''
})

const companyForm = reactive({
  company_name: '',
  email: '',
  password: '',
  hr_contact: '',
  website: ''
})

const studentErrors = reactive({
  name: '',
  email: '',
  password: '',
  branch: '',
  cgpa: '',
  year: ''
})

const companyErrors = reactive({
  company_name: '',
  email: '',
  password: '',
  hr_contact: ''
})

onMounted(async () => {
  try {
    const res = await getBranches()
    if (res.data.success) branches.value = res.data.branches
  } catch (err) {
    // silently handle
  }
})

const validateStudent = () => {
  let valid = true
  Object.keys(studentErrors).forEach((k) => (studentErrors[k] = ''))

  if (!studentForm.name.trim()) {
    studentErrors.name = 'Name is required'
    valid = false
  } else if (studentForm.name.length > 120) {
    studentErrors.name = 'Name must be 120 characters or less'
    valid = false
  }

  if (!studentForm.email) {
    studentErrors.email = 'Email is required'
    valid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(studentForm.email)) {
    studentErrors.email = 'Please enter a valid email'
    valid = false
  }

  if (!studentForm.password) {
    studentErrors.password = 'Password is required'
    valid = false
  } else if (studentForm.password.length < 8) {
    studentErrors.password = 'Password must be at least 8 characters'
    valid = false
  }

  if (!studentForm.branch.trim()) {
    studentErrors.branch = 'Branch is required'
    valid = false
  }

  const cgpa = parseFloat(studentForm.cgpa)
  if (isNaN(cgpa) || cgpa < 0 || cgpa > 10) {
    studentErrors.cgpa = 'CGPA must be between 0 and 10'
    valid = false
  }

  const year = parseInt(studentForm.year)
  if (isNaN(year) || year < 1) {
    studentErrors.year = 'Year must be at least 1'
    valid = false
  }

  return valid
}

const validateCompany = () => {
  let valid = true
  Object.keys(companyErrors).forEach((k) => (companyErrors[k] = ''))

  if (!companyForm.company_name.trim()) {
    companyErrors.company_name = 'Company name is required'
    valid = false
  } else if (companyForm.company_name.length > 120) {
    companyErrors.company_name = 'Company name must be 120 characters or less'
    valid = false
  }

  if (!companyForm.email) {
    companyErrors.email = 'Email is required'
    valid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(companyForm.email)) {
    companyErrors.email = 'Please enter a valid email'
    valid = false
  }

  if (!companyForm.password) {
    companyErrors.password = 'Password is required'
    valid = false
  } else if (companyForm.password.length < 8) {
    companyErrors.password = 'Password must be at least 8 characters'
    valid = false
  }

  if (!companyForm.hr_contact) {
    companyErrors.hr_contact = 'HR contact is required'
    valid = false
  } else if (!/^\d{10}$/.test(companyForm.hr_contact)) {
    companyErrors.hr_contact = 'HR contact must be a 10-digit number'
    valid = false
  }

  return valid
}

const getErrorMessage = (code) => {
  const messages = {
    email_exists: 'An account with this email already exists',
    invalid_email_format: 'Please enter a valid email',
    password_too_short: 'Password must be at least 8 characters',
    invalid_cgpa: 'Please enter a valid CGPA (0-10)',
    invalid_year: 'Please enter a valid year',
    invalid_hr_contact: 'HR contact must be a 10-digit number',
    invalid_branch: 'Please select a valid branch',
    missing_fields: 'Please fill in all required fields',
    string_too_long: 'One or more fields exceed maximum length',
    server_error: 'Server error. Please try again later'
  }
  return messages[code] || 'An error occurred. Please try again'
}

const handleStudentRegister = async () => {
  successMessage.value = ''
  errorMessage.value = ''

  if (!validateStudent()) return

  try {
    await authStore.registerStudent({
      name: studentForm.name.trim(),
      email: studentForm.email.trim().toLowerCase(),
      password: studentForm.password,
      branch: studentForm.branch.trim(),
      cgpa: parseFloat(studentForm.cgpa),
      year: parseInt(studentForm.year)
    })
    successMessage.value = 'Account created successfully! Please sign in.'
    setTimeout(() => router.push('/login'), 2000)
  } catch (err) {
    errorMessage.value = getErrorMessage(authStore.error)
  }
}

const handleCompanyRegister = async () => {
  successMessage.value = ''
  errorMessage.value = ''

  if (!validateCompany()) return

  try {
    const payload = {
      company_name: companyForm.company_name.trim(),
      email: companyForm.email.trim().toLowerCase(),
      password: companyForm.password,
      hr_contact: companyForm.hr_contact.trim()
    }
    if (companyForm.website.trim()) {
      payload.website = companyForm.website.trim()
    }
    await authStore.registerCompany(payload)
    successMessage.value = 'Account created successfully! Please sign in.'
    setTimeout(() => router.push('/login'), 2000)
  } catch (err) {
    errorMessage.value = getErrorMessage(authStore.error)
  }
}
</script>

<style scoped>
.auth-subtitle {
  font-size: var(--text-md);
  font-weight: var(--weight-medium);
  color: var(--text-secondary);
  text-align: center;
  margin-bottom: var(--space-6);
}

.register-tabs {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-6);
  background-color: var(--color-bg);
  border-radius: var(--radius-md);
  padding: var(--space-1);
}

.register-tab {
  flex: 1;
  padding: var(--space-2) var(--space-3);
  background: none;
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--duration-base) var(--ease-default);
}

.register-tab:hover {
  color: var(--text-primary);
  background-color: var(--color-surface);
}

.register-tab.active {
  background-color: var(--color-surface);
  color: var(--color-primary);
  box-shadow: var(--shadow-sm);
}

.auth-link {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.auth-link a {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: var(--weight-medium);
}

.auth-link a:hover {
  text-decoration: underline;
}
</style>
