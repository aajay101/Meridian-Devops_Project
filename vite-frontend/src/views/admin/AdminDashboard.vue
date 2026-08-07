<template>
  <div class="admin-dashboard">
    <PageHeader title="Dashboard" subtitle="Overview of the placement portal" />

    <!-- Stats -->
    <div v-if="loading" class="row g-4 mb-4">
      <div v-for="n in 3" :key="n" class="col-sm-6 col-xl-4">
        <div class="skeleton-card"></div>
      </div>
    </div>

    <div v-else-if="error" class="alert alert-danger d-flex align-items-center" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      <div>{{ error }}</div>
    </div>

    <div v-else class="row g-4 mb-4">
      <div class="col-sm-6 col-xl-4">
        <StatCard
          label="Total Students"
          :value="stats.total_students"
          icon="bi bi-people-fill"
          color="primary"
        />
      </div>
      <div class="col-sm-6 col-xl-4">
        <StatCard
          label="Total Companies"
          :value="stats.total_companies"
          icon="bi bi-building"
          color="success"
        />
      </div>
      <div class="col-sm-6 col-xl-4">
        <StatCard
          label="Total Drives"
          :value="stats.total_drives"
          icon="bi bi-briefcase-fill"
          color="warning"
        />
      </div>
    </div>

    <!-- Quick Actions -->
    <h2 class="section-title">Quick Actions</h2>
    <div class="row g-3">
      <div v-for="link in navLinks" :key="link.to" class="col-sm-6 col-lg-4 col-xl-3">
        <router-link :to="link.to" class="nav-card">
          <div class="nav-card-icon" :class="`nav-card-icon--${link.color}`">
            <i :class="link.icon"></i>
          </div>
          <div class="nav-card-content">
            <h3 class="nav-card-title">{{ link.title }}</h3>
            <p class="nav-card-desc">{{ link.desc }}</p>
          </div>
          <i class="bi bi-chevron-right nav-card-arrow"></i>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getDashboard } from '@/api/admin'
import PageHeader from '@/components/common/PageHeader.vue'
import StatCard from '@/components/common/StatCard.vue'

const stats = ref({
  total_students: 0,
  total_companies: 0,
  total_drives: 0
})
const loading = ref(true)
const error = ref('')

const navLinks = [
  { to: '/admin/companies', icon: 'bi bi-building', title: 'Companies', desc: 'Approve registrations', color: 'blue' },
  { to: '/admin/students', icon: 'bi bi-people', title: 'Students', desc: 'Manage accounts', color: 'violet' },
  { to: '/admin/drives', icon: 'bi bi-briefcase', title: 'Drives', desc: 'Review placements', color: 'green' },
  { to: '/admin/applications', icon: 'bi bi-file-text', title: 'Applications', desc: 'View all applications', color: 'cyan' },
  { to: '/admin/reports', icon: 'bi bi-bar-chart-line', title: 'Reports', desc: 'Placement statistics', color: 'orange' }
]

onMounted(async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await getDashboard()
    if (res.data.success) {
      stats.value = res.data
    } else {
      error.value = 'Failed to load dashboard data.'
    }
  } catch (err) {
    error.value = 'Unable to connect to server. Please try again later.'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.section-title {
  font-size: var(--text-md);
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-4) 0;
}

.nav-card {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4);
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  text-decoration: none;
  transition: all var(--duration-base) var(--ease-default);
  height: 100%;
}

.nav-card:hover {
  box-shadow: var(--shadow-md);
  text-decoration: none;
  border-color: var(--color-primary);
  transform: translateY(-1px);
}

.nav-card-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-md);
  flex-shrink: 0;
}

.nav-card-icon--blue {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
}

.nav-card-icon--violet {
  background-color: #F5F3FF;
  color: #7C3AED;
}

.nav-card-icon--green {
  background-color: var(--color-success-bg);
  color: var(--color-success);
}

.nav-card-icon--cyan {
  background-color: var(--color-info-bg);
  color: var(--color-info);
}

.nav-card-icon--orange {
  background-color: var(--color-warning-bg);
  color: var(--color-warning);
}

.nav-card-content {
  flex: 1;
  min-width: 0;
}

.nav-card-title {
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
  margin: 0;
  line-height: var(--leading-tight);
}

.nav-card-desc {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  margin: 2px 0 0 0;
  line-height: var(--leading-snug);
}

.nav-card-arrow {
  color: var(--text-tertiary);
  font-size: var(--text-xs);
  flex-shrink: 0;
  transition: transform var(--duration-base) var(--ease-default);
}

.nav-card:hover .nav-card-arrow {
  transform: translateX(2px);
  color: var(--color-primary);
}

.skeleton-card {
  height: 88px;
  background: linear-gradient(90deg, var(--color-surface-muted) 25%, var(--color-surface-hover) 50%, var(--color-surface-muted) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-lg);
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

@media (max-width: 575.98px) {
  .nav-card {
    padding: var(--space-3);
  }
}
</style>
