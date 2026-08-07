<template>
  <header class="navbar">
    <div class="navbar-left">
      <button class="navbar-toggler d-md-none" @click="$emit('toggleSidebar')">
        <i class="bi bi-list"></i>
      </button>
      <nav aria-label="breadcrumb">
        <ol class="breadcrumb mb-0">
          <li class="breadcrumb-item"><router-link to="/">Home</router-link></li>
          <li class="breadcrumb-item active" aria-current="page">{{ currentPage }}</li>
        </ol>
      </nav>
    </div>

    <div class="navbar-right">
      <div class="dropdown" ref="dropdownRef">
        <button
          class="btn btn-link navbar-user-btn"
          type="button"
          @click="dropdownOpen = !dropdownOpen"
        >
          <i class="bi bi-person-circle"></i>
          <span class="navbar-user-name">{{ userEmail }}</span>
          <i class="bi bi-chevron-down dropdown-arrow" :class="{ 'rotate-180': dropdownOpen }"></i>
        </button>
        <ul class="dropdown-menu dropdown-menu-end" :class="{ show: dropdownOpen }">
          <li>
            <router-link :to="profileRoute" class="dropdown-item" @click="dropdownOpen = false">
              <i class="bi bi-person me-2"></i>Profile
            </router-link>
          </li>
          <li><hr class="dropdown-divider" /></li>
          <li><a class="dropdown-item" href="#" @click.prevent="handleLogout"><i class="bi bi-box-arrow-left me-2"></i>Logout</a></li>
        </ul>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

defineProps({
  userEmail: {
    type: String,
    default: 'Account'
  }
})

defineEmits(['toggleSidebar'])

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const dropdownOpen = ref(false)
const dropdownRef = ref(null)

const profileRoute = computed(() => {
  const role = authStore.user?.role
  if (role === 'admin') return '/admin/dashboard'
  if (role === 'company') return '/company/profile'
  if (role === 'student') return '/student/profile'
  return '/'
})

const currentPage = computed(() => {
  const name = route.name || ''
  return name.replace(/([A-Z])/g, ' $1').trim() || 'Home'
})

const handleClickOutside = (event) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    dropdownOpen.value = false
  }
}

const handleLogout = async () => {
  dropdownOpen.value = false
  await authStore.logout()
  router.push('/login')
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.navbar {
  height: 60px;
  background-color: var(--color-navbar-bg);
  border-bottom: 1px solid var(--color-navbar-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-6);
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.navbar-toggler {
  background: none;
  border: none;
  font-size: var(--text-xl);
  color: var(--color-navbar-text);
  padding: var(--space-2);
  cursor: pointer;
}

.navbar-toggler:hover {
  color: var(--color-primary);
}

.breadcrumb {
  font-size: var(--text-sm);
}

.breadcrumb-item a {
  color: var(--text-secondary);
  text-decoration: none;
}

.breadcrumb-item a:hover {
  color: var(--color-primary);
  text-decoration: underline;
}

.breadcrumb-item.active {
  color: var(--text-primary);
  font-weight: var(--weight-medium);
}

.navbar-right {
  display: flex;
  align-items: center;
  position: relative;
}

.navbar-user-btn {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--color-navbar-text);
  text-decoration: none;
  font-size: var(--text-sm);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  transition: background-color var(--duration-base) var(--ease-default);
}

.navbar-user-btn:hover {
  background-color: var(--color-surface-hover);
}

.navbar-user-btn i {
  font-size: var(--text-lg);
}

.navbar-user-name {
  font-weight: var(--weight-medium);
}

.dropdown-arrow {
  font-size: var(--text-xs);
  transition: transform var(--duration-base) var(--ease-default);
}

.dropdown-arrow.rotate-180 {
  transform: rotate(180deg);
}

.dropdown {
  position: relative;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  min-width: 180px;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  padding: var(--space-1) 0;
  display: none;
  z-index: 200;
}

.dropdown-menu.show {
  display: block;
}

.dropdown-item {
  display: flex;
  align-items: center;
  padding: var(--space-2) var(--space-4);
  color: var(--text-primary);
  font-size: var(--text-sm);
  text-decoration: none;
  transition: background-color var(--duration-base) var(--ease-default);
}

.dropdown-item:hover {
  background-color: var(--color-surface-hover);
  color: var(--text-primary);
  text-decoration: none;
}

.dropdown-divider {
  margin: var(--space-1) 0;
  border-color: var(--color-border);
}

@media (max-width: 767.98px) {
  .navbar {
    padding: 0 var(--space-4);
  }

  .navbar-user-name {
    display: none;
  }
}
</style>
