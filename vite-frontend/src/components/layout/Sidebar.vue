<template>
  <nav class="sidebar" :class="{ 'sidebar-open': isOpen }">
    <div class="sidebar-header">
      <div class="sidebar-logo-mark">P</div>
      <span class="sidebar-app-name">Recruit Link</span>
    </div>

    <div class="sidebar-nav-scroll">
      <template v-for="(section, idx) in navSections" :key="idx">
        <div class="sidebar-section-heading">{{ section.heading }}</div>
        <ul class="sidebar-nav">
          <li v-for="item in section.items" :key="item.label" class="sidebar-nav-item">
            <router-link :to="item.to" class="sidebar-nav-link" @click="emit('close')">
              <i :class="item.icon"></i>
              <span>{{ item.label }}</span>
            </router-link>
          </li>
        </ul>
      </template>
    </div>

    <div class="sidebar-footer">
      <div class="sidebar-user">
        <div class="sidebar-user-avatar">{{ userEmail.charAt(0).toUpperCase() }}</div>
        <div class="sidebar-user-info">
          <span class="sidebar-user-email">{{ userEmail }}</span>
          <span class="sidebar-user-role">{{ role }}</span>
        </div>
      </div>
      <a href="#" class="sidebar-logout" @click.prevent="handleLogout">
        <i class="bi bi-box-arrow-left"></i>
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

const emit = defineEmits(['close'])

const router = useRouter()
const authStore = useAuthStore()

const allNavItems = {
  admin: [
    {
      heading: 'Overview',
      items: [
        { label: 'Dashboard', icon: 'bi bi-grid-1x2', to: '/admin/dashboard' }
      ]
    },
    {
      heading: 'Management',
      items: [
        { label: 'Companies', icon: 'bi bi-building', to: '/admin/companies' },
        { label: 'Students', icon: 'bi bi-people', to: '/admin/students' },
        { label: 'Drives', icon: 'bi bi-briefcase', to: '/admin/drives' },
        { label: 'Applications', icon: 'bi bi-file-text', to: '/admin/applications' }
      ]
    },
    {
      heading: 'Analytics',
      items: [
        { label: 'Reports', icon: 'bi bi-bar-chart-line', to: '/admin/reports' }
      ]
    }
  ],
  company: [
    {
      heading: 'Overview',
      items: [
        { label: 'Dashboard', icon: 'bi bi-grid-1x2', to: '/company/dashboard' }
      ]
    },
    {
      heading: 'Management',
      items: [
        { label: 'Profile', icon: 'bi bi-building', to: '/company/profile' },
        { label: 'My Drives', icon: 'bi bi-briefcase', to: '/company/drives' }
      ]
    }
  ],
  student: [
    {
      heading: 'Overview',
      items: [
        { label: 'Dashboard', icon: 'bi bi-grid-1x2', to: '/student/dashboard' }
      ]
    },
    {
      heading: 'Placement',
      items: [
        { label: 'Profile', icon: 'bi bi-person', to: '/student/profile' },
        { label: 'Available Drives', icon: 'bi bi-briefcase', to: '/student/drives' },
        { label: 'Applications', icon: 'bi bi-file-text', to: '/student/applications' }
      ]
    },
    {
      heading: 'History',
      items: [
        { label: 'Placement History', icon: 'bi bi-clock-history', to: '/student/history' }
      ]
    }
  ]
}

const navSections = computed(() => {
  return allNavItems[props.role] || []
})

const handleLogout = async () => {
  await authStore.logout()
  emit('close')
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
  overflow: hidden;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-5) var(--space-5);
  border-bottom: 1px solid var(--color-sidebar-border);
}

.sidebar-logo-mark {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-md);
  background-color: var(--color-sidebar-surface);
  color: var(--color-sidebar-text-active);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: var(--weight-bold);
  flex-shrink: 0;
}

.sidebar-app-name {
  font-size: 14px;
  font-weight: var(--weight-semibold);
  color: var(--color-sidebar-text-active);
  letter-spacing: -0.01em;
}

.sidebar-nav-scroll {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-3) 0;
}

.sidebar-section-heading {
  font-size: 10px;
  font-weight: var(--weight-semibold);
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: var(--space-4) var(--space-5) var(--space-1-5);
}

.sidebar-nav {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar-nav-item {
  padding: 1px var(--space-3);
}

.sidebar-nav-link {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: 7px var(--space-3);
  color: var(--color-sidebar-text);
  text-decoration: none;
  border-radius: var(--radius-md);
  font-size: 13px;
  font-weight: var(--weight-medium);
  transition: all var(--duration-fast) var(--ease-default);
}

.sidebar-nav-link:hover {
  background-color: var(--color-sidebar-hover-bg);
  color: var(--color-sidebar-text-active);
  text-decoration: none;
}

.sidebar-nav-link.router-link-active {
  background-color: var(--color-sidebar-active-bg);
  color: var(--color-sidebar-text-active);
  font-weight: var(--weight-semibold);
}

.sidebar-nav-link i {
  font-size: 15px;
  width: 20px;
  text-align: center;
  opacity: 0.6;
}

.sidebar-nav-link:hover i {
  opacity: 0.9;
}

.sidebar-nav-link.router-link-active i {
  opacity: 1;
}

.sidebar-footer {
  padding: var(--space-3) var(--space-4);
  border-top: 1px solid var(--color-sidebar-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sidebar-user {
  display: flex;
  align-items: center;
  gap: var(--space-2-5);
  min-width: 0;
  flex: 1;
}

.sidebar-user-avatar {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-full);
  background-color: var(--color-sidebar-surface);
  color: var(--color-sidebar-text-active);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: var(--weight-semibold);
  flex-shrink: 0;
}

.sidebar-user-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.sidebar-user-email {
  font-size: 12px;
  color: var(--color-sidebar-text-active);
  font-weight: var(--weight-medium);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.2;
}

.sidebar-user-role {
  font-size: 10px;
  color: var(--color-sidebar-text);
  text-transform: capitalize;
  line-height: 1.4;
}

.sidebar-logout {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  color: var(--color-sidebar-text);
  text-decoration: none;
  border-radius: var(--radius-md);
  font-size: 14px;
  transition: all var(--duration-fast) var(--ease-default);
  flex-shrink: 0;
}

.sidebar-logout:hover {
  background-color: rgba(220, 38, 38, 0.15);
  color: #FCA5A5;
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
