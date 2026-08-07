<template>
  <nav class="sidebar" :class="{ 'sidebar-open': isOpen }">
    <div class="sidebar-header">
      <i class="bi bi-mortarboard-fill sidebar-logo"></i>
      <span class="sidebar-app-name">Placement Portal</span>
    </div>

    <div class="sidebar-role-badge">
      <span class="badge">{{ role }}</span>
    </div>

    <ul class="sidebar-nav">
      <li v-for="item in filteredNavItems" :key="item.label" class="sidebar-nav-item">
        <router-link :to="item.to" class="sidebar-nav-link">
          <i :class="item.icon"></i>
          <span>{{ item.label }}</span>
        </router-link>
      </li>
    </ul>

    <div class="sidebar-footer">
      <div class="sidebar-user">
        <i class="bi bi-person-circle"></i>
        <span class="sidebar-user-email">{{ userEmail }}</span>
      </div>
      <a href="#" class="sidebar-logout" @click.prevent="handleLogout">
        <i class="bi bi-box-arrow-left"></i>
        <span>Logout</span>
      </a>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  role: {
    type: String,
    default: 'Role'
  },
  userEmail: {
    type: String,
    default: 'user@placeholder.com'
  }
})

defineEmits(['close'])

const router = useRouter()
const authStore = useAuthStore()

const allNavItems = {
  admin: [
    { label: 'Dashboard', icon: 'bi bi-speedometer2', to: '/admin/dashboard' },
    { label: 'Companies', icon: 'bi bi-building', to: '/admin/companies' },
    { label: 'Students', icon: 'bi bi-people', to: '/admin/students' },
    { label: 'Drives', icon: 'bi bi-briefcase', to: '/admin/drives' },
    { label: 'Applications', icon: 'bi bi-file-earmark-text', to: '/admin/applications' },
    { label: 'Reports', icon: 'bi bi-bar-chart-line', to: '/admin/reports' }
  ],
  company: [
    { label: 'Dashboard', icon: 'bi bi-speedometer2', to: '/company/dashboard' },
    { label: 'Profile', icon: 'bi bi-building', to: '/company/profile' },
    { label: 'My Drives', icon: 'bi bi-briefcase', to: '/company/drives' }
  ],
  student: [
    { label: 'Dashboard', icon: 'bi bi-speedometer2', to: '/student/dashboard' },
    { label: 'Profile', icon: 'bi bi-person', to: '/student/profile' },
    { label: 'Available Drives', icon: 'bi bi-briefcase', to: '/student/drives' },
    { label: 'Applications', icon: 'bi bi-file-earmark-text', to: '/student/applications' },
    { label: 'Placement History', icon: 'bi bi-clock-history', to: '/student/history' }
  ]
}

const filteredNavItems = computed(() => {
  return allNavItems[props.role] || []
})

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.sidebar {
  width: 240px;
  height: 100vh;
  background-color: var(--color-sidebar-bg);
  position: fixed;
  top: 0;
  left: 0;
  display: flex;
  flex-direction: column;
  z-index: 1000;
  overflow-y: auto;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-6) var(--space-4);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-logo {
  font-size: var(--text-xl);
  color: var(--color-sidebar-logo);
}

.sidebar-app-name {
  font-size: var(--text-md);
  font-weight: var(--weight-semibold);
  color: var(--color-sidebar-active);
}

.sidebar-role-badge {
  padding: var(--space-4);
}

.sidebar-role-badge .badge {
  background-color: var(--color-primary);
  color: var(--text-on-primary);
  font-size: var(--text-xs);
  font-weight: var(--weight-medium);
  padding: var(--space-1) var(--space-3);
  text-transform: capitalize;
}

.sidebar-nav {
  list-style: none;
  padding: 0;
  margin: 0;
  flex: 1;
}

.sidebar-nav-item {
  margin: var(--space-1) var(--space-2);
}

.sidebar-nav-link {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  color: var(--color-sidebar-text);
  text-decoration: none;
  border-radius: var(--radius-md);
  transition: all var(--duration-base) var(--ease-default);
}

.sidebar-nav-link:hover {
  background-color: var(--color-sidebar-hover-bg);
  color: var(--color-sidebar-active);
  text-decoration: none;
}

.sidebar-nav-link.router-link-active {
  background-color: var(--color-sidebar-hover-bg);
  color: var(--color-sidebar-active);
}

.sidebar-nav-link i {
  font-size: var(--text-md);
  width: 20px;
  text-align: center;
}

.sidebar-footer {
  padding: var(--space-4);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-user {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2);
  color: var(--color-sidebar-text);
  font-size: var(--text-sm);
  margin-bottom: var(--space-2);
}

.sidebar-user i {
  font-size: var(--text-lg);
}

.sidebar-user-email {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sidebar-logout {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  color: var(--color-sidebar-text);
  text-decoration: none;
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  transition: all var(--duration-base) var(--ease-default);
}

.sidebar-logout:hover {
  background-color: var(--color-danger-bg);
  color: var(--color-danger);
  text-decoration: none;
}

@media (max-width: 767.98px) {
  .sidebar {
    transform: translateX(-100%);
    transition: transform var(--duration-slow) var(--ease-out);
  }

  .sidebar.sidebar-open {
    transform: translateX(0);
  }
}
</style>
