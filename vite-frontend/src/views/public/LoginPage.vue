<template>
  <div>
    <h2 class="auth-subtitle">Sign in to your account</h2>

    <div class="login-tabs">
      <button
        type="button"
        class="login-tab"
        :class="{ active: activeTab === 'student' }"
        @click="activeTab = 'student'"
      >
        <i class="bi bi-person me-1"></i> Student
      </button>
      <button
        type="button"
        class="login-tab"
        :class="{ active: activeTab === 'company' }"
        @click="activeTab = 'company'"
      >
        <i class="bi bi-building me-1"></i> Company
      </button>
      <button
        type="button"
        class="login-tab"
        :class="{ active: activeTab === 'admin' }"
        @click="activeTab = 'admin'"
      >
        <i class="bi bi-shield-lock me-1"></i> Admin
      </button>
    </div>

    <div class="role-hint">
      <template v-if="activeTab === 'student'">Student login — use your student credentials</template>
      <template v-else-if="activeTab === 'company'">Company login — use your HR credentials</template>
      <template v-else>Admin login — use your admin credentials</template>
    </div>

    <div v-if="errorMessage" class="alert alert-danger" role="alert">
      {{ errorMessage }}
    </div>

    <form @submit.prevent="handleLogin">
      <div class="mb-3">
        <label for="email" class="form-label">Email</label>
        <input
          id="email"
          v-model="email"
          type="email"
          class="form-control"
          :class="{ 'is-invalid': emailError }"
          placeholder="Enter your email"
          required
        />
        <div v-if="emailError" class="invalid-feedback">{{ emailError }}</div>
      </div>

      <div class="mb-4">
        <label for="password" class="form-label">Password</label>
        <input
          id="password"
          v-model="password"
          type="password"
          class="form-control"
          :class="{ 'is-invalid': passwordError }"
          placeholder="Enter your password"
          required
        />
        <div v-if="passwordError" class="invalid-feedback">{{ passwordError }}</div>
      </div>

      <button
        type="submit"
        class="btn btn-primary w-100"
        :disabled="authStore.loading"
      >
        <span v-if="authStore.loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
        {{ authStore.loading ? 'Signing in...' : 'Sign In' }}
      </button>
    </form>

    <p class="auth-link text-center mt-4">
      Don't have an account?
      <router-link to="/register">Register here</router-link>
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const activeTab = ref('student')
const email = ref('')
const password = ref('')
const emailError = ref('')
const passwordError = ref('')
const errorMessage = ref('')

const validate = () => {
  emailError.value = ''
  passwordError.value = ''
  let valid = true

  if (!email.value) {
    emailError.value = 'Email is required'
    valid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
    emailError.value = 'Please enter a valid email'
    valid = false
  }

  if (!password.value) {
    passwordError.value = 'Password is required'
    valid = false
  } else if (password.value.length < 8) {
    passwordError.value = 'Password must be at least 8 characters'
    valid = false
  }

  return valid
}

const getErrorMessage = (code) => {
  const messages = {
    invalid_credentials: 'Invalid email or password',
    account_disabled: 'Your account has been disabled',
    company_not_approved: 'Your company account is awaiting admin approval',
    role_mismatch: 'These credentials belong to a different account type. Please select the correct login option.',
    missing_fields: 'Please fill in all fields',
    server_error: 'Server error. Please try again later'
  }
  return messages[code] || 'An error occurred. Please try again'
}

const handleLogin = async () => {
  errorMessage.value = ''

  if (!validate()) return

  try {
    const role = await authStore.login(email.value, password.value, activeTab.value)
    const roleRoutes = {
      admin: '/admin/dashboard',
      company: '/company/dashboard',
      student: '/student/dashboard'
    }
    router.push(roleRoutes[role] || '/login')
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

.login-tabs {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-4);
  background-color: var(--color-bg);
  border-radius: var(--radius-md);
  padding: var(--space-1);
}

.login-tab {
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

.login-tab:hover {
  color: var(--text-primary);
  background-color: var(--color-surface);
}

.login-tab.active {
  background-color: var(--color-surface);
  color: var(--color-primary);
  box-shadow: var(--shadow-sm);
}

.role-hint {
  font-size: var(--text-xs);
  color: var(--text-muted);
  text-align: center;
  margin-bottom: var(--space-6);
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
