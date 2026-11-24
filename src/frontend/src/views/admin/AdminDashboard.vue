<template>
  <div class="admin-dashboard">
    <PageHeader title="Dashboard" subtitle="Overview of the placement portal" />

    <!-- Stats -->
    <div v-if="loading" class="row g-4 mb-4">
      <div v-for="n in 3" :key="n" class="col-sm-6 col-xl-4">
        <div class="skeleton-card" style="height: 96px"></div>
      </div>
    </div>

    <div v-else-if="error" class="error-banner" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      <span>{{ error }}</span>
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
          color="info"
        />
      </div>
    </div>

    <!-- Quick Actions -->
    <SectionCard title="Quick Actions">
      <div class="row g-3">
        <div v-for="link in navLinks" :key="link.to" class="col-sm-6 col-lg-4 col-xl-3">
          <router-link :to="link.to" class="nav-card">
            <div class="nav-card-icon" :class="`nav-card-icon--${link.color}`">
              <i :class="link.icon"></i>
            </div>
            <div class="nav-card-content">
              <h3 class="nav-card-title">{{ link.title }}</h3>
              <p class="nav-card-desc">{{ link.desc }}</p>
              <span v-if="link.badge" class="nav-card-badge">{{ link.badge }}</span>
            </div>
            <i class="bi bi-chevron-right nav-card-arrow"></i>
          </router-link>
        </div>
      </div>
    </SectionCard>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getDashboard, getCompanies, getDrives } from '@/api/admin'
import PageHeader from '@/components/common/PageHeader.vue'
import StatCard from '@/components/common/StatCard.vue'
import SectionCard from '@/components/common/SectionCard.vue'

const stats = ref({
  total_students: 0,
  total_companies: 0,
  total_drives: 0
})
const loading = ref(true)
const error = ref('')
const pendingCounts = ref({ companies: 0, drives: 0 })

const navLinks = ref([
  { to: '/admin/companies', icon: 'bi bi-building', title: 'Companies', desc: 'Approve registrations', color: 'blue', badge: 0 },
  { to: '/admin/students', icon: 'bi bi-people', title: 'Students', desc: 'Manage accounts', color: 'violet', badge: 0 },
  { to: '/admin/drives', icon: 'bi bi-briefcase', title: 'Drives', desc: 'Review placements', color: 'green', badge: 0 },
  { to: '/admin/applications', icon: 'bi bi-file-text', title: 'Applications', desc: 'View all applications', color: 'cyan', badge: 0 },
  { to: '/admin/reports', icon: 'bi bi-bar-chart-line', title: 'Reports', desc: 'Placement statistics', color: 'orange', badge: 0 }
])

onMounted(async () => {
  loading.value = true
  error.value = ''
  try {
    const [dashRes, companiesRes, drivesRes] = await Promise.all([
      getDashboard(),
      getCompanies().catch(() => ({ data: { companies: [] } })),
      getDrives().catch(() => ({ data: { drives: [] } }))
    ])
    if (dashRes.data.success) {
      stats.value = dashRes.data
    } else {
      error.value = 'Failed to load dashboard data.'
    }
    const companies = companiesRes.data.companies || []
    const drives = drivesRes.data.drives || []
    pendingCounts.value.companies = companies.filter(c => c.approval_status === 'Pending').length
    pendingCounts.value.drives = drives.filter(d => d.status === 'Pending').length

    navLinks.value[0].badge = pendingCounts.value.companies
    navLinks.value[2].badge = pendingCounts.value.drives
  } catch (err) {
    error.value = 'Unable to connect to server. Please try again later.'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.error-banner {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-5);
  background-color: var(--color-danger-subtle);
  border: 1px solid var(--color-danger-muted);
  border-radius: var(--radius-lg);
  color: var(--color-danger);
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  margin-bottom: var(--space-6);
}

.nav-card {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-4) var(--space-5);
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  text-decoration: none;
  transition: all var(--duration-normal) var(--ease-default);
  height: 100%;
  box-shadow: var(--shadow-card);
}

.nav-card:hover {
  box-shadow: var(--shadow-card-hover);
  text-decoration: none;
  border-color: var(--color-border-strong);
  transform: translateY(-1px);
}

.nav-card:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.nav-card-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
  transition: transform var(--duration-fast) var(--ease-default);
}

.nav-card:hover .nav-card-icon {
  transform: scale(1.05);
}

.nav-card-icon--blue {
  background-color: var(--color-primary-subtle);
  color: var(--text-primary);
}

.nav-card-icon--violet {
  background-color: var(--color-primary-subtle);
  color: var(--text-secondary);
}

.nav-card-icon--green {
  background-color: var(--color-success-subtle);
  color: var(--color-success);
}

.nav-card-icon--cyan {
  background-color: var(--color-info-subtle);
  color: var(--color-info);
}

.nav-card-icon--orange {
  background-color: var(--color-warning-subtle);
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
  margin: var(--space-0-5) 0 0 0;
  line-height: var(--leading-snug);
}

.nav-card-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  border-radius: var(--radius-full);
  font-size: 10px;
  font-weight: var(--weight-bold);
  background-color: var(--color-danger);
  color: var(--text-inverse);
  margin-top: var(--space-1-5);
}

.nav-card-arrow {
  color: var(--text-tertiary);
  font-size: var(--text-xs);
  flex-shrink: 0;
  transition: all var(--duration-fast) var(--ease-default);
}

.nav-card:hover .nav-card-arrow {
  transform: translateX(3px);
  color: var(--text-primary);
}

@media (max-width: 575.98px) {
  .nav-card {
    padding: var(--space-3) var(--space-4);
  }
}
</style>
