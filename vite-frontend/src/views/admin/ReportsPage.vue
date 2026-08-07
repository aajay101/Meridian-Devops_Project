<template>
  <div>
    <PageHeader title="Reports" subtitle="Placement statistics and reports" />

    <div v-if="loading" class="row g-4">
      <div v-for="n in 4" :key="n" class="col-sm-6 col-md-3">
        <div class="skeleton-card"></div>
      </div>
    </div>

    <div v-else-if="error" class="alert alert-danger" role="alert">
      {{ error }}
    </div>

    <template v-else-if="report">
      <div class="row g-4 mb-4">
        <div class="col-sm-6 col-md-3">
          <StatCard label="Total Students" :value="report.total_students" icon="bi bi-people-fill" color="primary" />
        </div>
        <div class="col-sm-6 col-md-3">
          <StatCard label="Total Companies" :value="report.total_companies" icon="bi bi-building" color="success" />
        </div>
        <div class="col-sm-6 col-md-3">
          <StatCard label="Total Drives" :value="report.total_drives" icon="bi bi-briefcase-fill" color="info" />
        </div>
        <div class="col-sm-6 col-md-3">
          <StatCard label="Total Applications" :value="report.total_applications" icon="bi bi-file-text" color="warning" />
        </div>
      </div>

      <div class="row g-4 mb-4">
        <div class="col-lg-6">
          <SectionCard title="Applications by Status">
            <div class="status-breakdown">
              <div class="breakdown-item">
                <span class="breakdown-dot" style="background-color: var(--color-primary)"></span>
                <span class="breakdown-label">Applied</span>
                <span class="breakdown-value">{{ report.applications_by_status?.Applied || 0 }}</span>
              </div>
              <div class="breakdown-item">
                <span class="breakdown-dot" style="background-color: var(--color-warning)"></span>
                <span class="breakdown-label">Shortlisted</span>
                <span class="breakdown-value">{{ report.applications_by_status?.Shortlisted || 0 }}</span>
              </div>
              <div class="breakdown-item">
                <span class="breakdown-dot" style="background-color: var(--color-success)"></span>
                <span class="breakdown-label">Selected</span>
                <span class="breakdown-value">{{ report.applications_by_status?.Selected || 0 }}</span>
              </div>
              <div class="breakdown-item">
                <span class="breakdown-dot" style="background-color: var(--color-danger)"></span>
                <span class="breakdown-label">Rejected</span>
                <span class="breakdown-value">{{ report.applications_by_status?.Rejected || 0 }}</span>
              </div>
              <div class="breakdown-item">
                <span class="breakdown-dot" style="background-color: var(--color-info)"></span>
                <span class="breakdown-label">Interview Scheduled</span>
                <span class="breakdown-value">{{ report.applications_by_status?.['Interview Scheduled'] || 0 }}</span>
              </div>
            </div>
          </SectionCard>
        </div>
        <div class="col-lg-6">
          <SectionCard title="Selection Rate">
            <div class="selection-rate">
              <span class="selection-rate-value">{{ selectionRate }}%</span>
              <div class="progress" style="height: 8px;">
                <div
                  class="progress-bar"
                  role="progressbar"
                  :style="{ width: selectionRate + '%', backgroundColor: 'var(--color-success)' }"
                ></div>
              </div>
              <p class="selection-rate-desc">
                {{ report.applications_by_status?.Selected || 0 }} selected out of {{ report.total_applications || 0 }} applications
              </p>
            </div>
          </SectionCard>
        </div>
      </div>

      <div class="row g-4 mb-4">
        <div class="col-lg-6">
          <SectionCard title="Offer Response Breakdown">
            <div class="status-breakdown">
              <div class="breakdown-item">
                <span class="breakdown-dot" style="background-color: #0f5132"></span>
                <span class="breakdown-label">Accepted</span>
                <span class="breakdown-value">{{ report.offer_status_counts?.Accepted || 0 }}</span>
              </div>
              <div class="breakdown-item">
                <span class="breakdown-dot" style="background-color: #664d03"></span>
                <span class="breakdown-label">Declined</span>
                <span class="breakdown-value">{{ report.offer_status_counts?.Declined || 0 }}</span>
              </div>
              <div class="breakdown-item">
                <span class="breakdown-dot" style="background-color: #41464b"></span>
                <span class="breakdown-label">Auto Declined</span>
                <span class="breakdown-value">{{ report.offer_status_counts?.['Auto Declined'] || 0 }}</span>
              </div>
            </div>
          </SectionCard>
        </div>
        <div class="col-lg-6">
          <SectionCard title="Placement Rate">
            <div class="selection-rate">
              <span class="selection-rate-value" style="color: var(--color-primary)">{{ placementRate }}%</span>
              <div class="progress" style="height: 8px;">
                <div
                  class="progress-bar"
                  role="progressbar"
                  :style="{ width: placementRate + '%', backgroundColor: 'var(--color-primary)' }"
                ></div>
              </div>
              <p class="selection-rate-desc">
                {{ report.offer_status_counts?.Accepted || 0 }} accepted out of {{ report.total_applications || 0 }} applications
              </p>
            </div>
          </SectionCard>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getReportsSummary } from '@/api/admin'
import PageHeader from '@/components/common/PageHeader.vue'
import StatCard from '@/components/common/StatCard.vue'
import SectionCard from '@/components/common/SectionCard.vue'

const report = ref(null)
const loading = ref(false)
const error = ref('')

const selectionRate = computed(() => {
  if (!report.value) return 0
  const total = report.value.total_applications || 0
  const selected = report.value.applications_by_status?.Selected || 0
  if (total === 0) return 0
  return Math.round((selected / total) * 100)
})

const placementRate = computed(() => {
  if (!report.value) return 0
  const total = report.value.total_applications || 0
  const accepted = report.value.offer_status_counts?.Accepted || 0
  if (total === 0) return 0
  return Math.round((accepted / total) * 100)
})

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getReportsSummary()
    if (res.data.success) {
      report.value = res.data
    }
  } catch (err) {
    error.value = 'Failed to load reports. Please try again.'
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.status-breakdown {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.breakdown-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.breakdown-dot {
  width: 12px;
  height: 12px;
  border-radius: var(--radius-full);
  flex-shrink: 0;
}

.breakdown-label {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  flex: 1;
}

.breakdown-value {
  font-size: var(--text-md);
  font-weight: var(--weight-bold);
  color: var(--text-primary);
}

.selection-rate {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-4) 0;
}

.selection-rate-value {
  font-size: var(--text-3xl);
  font-weight: var(--weight-bold);
  color: var(--color-success);
}

.selection-rate-desc {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
  text-align: center;
}

.skeleton-card {
  height: 120px;
  background: linear-gradient(90deg, var(--color-surface-muted) 25%, var(--color-surface-hover) 50%, var(--color-surface-muted) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-lg);
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
