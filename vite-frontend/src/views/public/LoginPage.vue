<template>
  <div>
    <h2 class="auth-subtitle">Sign in to your account</h2>

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
    missing_fields: 'Please fill in all fields',
    server_error: 'Server error. Please try again later'
  }
  return messages[code] || 'An error occurred. Please try again'
}

const handleLogin = async () => {
  errorMessage.value = ''

  if (!validate()) return

  try {
    const role = await authStore.login(email.value, password.value)
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
