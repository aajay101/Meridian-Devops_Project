<template>
  <div>
    <PageHeader title="Reports" subtitle="Placement statistics and analytics" />

    <div v-if="loading" class="row g-4 mb-4">
      <div v-for="n in 4" :key="n" class="col-sm-6 col-xl-3">
        <div class="skeleton-card" style="height: 96px"></div>
      </div>
    </div>

    <div v-else-if="error" class="text-center py-5">
      <EmptyState icon="bi bi-exclamation-triangle" title="Error loading reports" :description="error" />
    </div>

    <template v-else-if="report">
      <div class="row g-4 mb-4">
        <div class="col-sm-6 col-xl-3">
          <StatCard label="Total Students" :value="report.total_students" icon="bi bi-people-fill" color="primary" />
        </div>
        <div class="col-sm-6 col-xl-3">
          <StatCard label="Total Companies" :value="report.total_companies" icon="bi bi-building" color="success" />
        </div>
        <div class="col-sm-6 col-xl-3">
          <StatCard label="Total Drives" :value="report.total_drives" icon="bi bi-briefcase-fill" color="info" />
        </div>
        <div class="col-sm-6 col-xl-3">
          <StatCard label="Total Applications" :value="report.total_applications" icon="bi bi-file-text" color="warning" />
        </div>
      </div>

      <div class="row g-4 mb-4">
        <div class="col-lg-6">
          <SectionCard title="Applications by Status">
            <div class="breakdown-list">
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
            <div class="rate-ring-display">
              <ProgressRing :percent="selectionRate" color="success" :size="120" :stroke-width="8" />
              <div class="rate-ring-info">
                <p class="rate-ring-description">
                  {{ report.applications_by_status?.Selected || 0 }} selected out of {{ report.total_applications || 0 }} applications
                </p>
              </div>
            </div>
          </SectionCard>
        </div>
      </div>

      <div class="row g-4 mb-4">
        <div class="col-lg-6">
          <SectionCard title="Offer Response Breakdown">
            <div class="breakdown-list">
              <div class="breakdown-item">
                <span class="breakdown-dot" style="background-color: var(--color-success)"></span>
                <span class="breakdown-label">Accepted</span>
                <span class="breakdown-value">{{ report.offer_status_counts?.Accepted || 0 }}</span>
              </div>
              <div class="breakdown-item">
                <span class="breakdown-dot" style="background-color: var(--color-warning)"></span>
                <span class="breakdown-label">Declined</span>
                <span class="breakdown-value">{{ report.offer_status_counts?.Declined || 0 }}</span>
              </div>
              <div class="breakdown-item">
                <span class="breakdown-dot" style="background-color: var(--text-tertiary)"></span>
                <span class="breakdown-label">Auto Declined</span>
                <span class="breakdown-value">{{ report.offer_status_counts?.['Auto Declined'] || 0 }}</span>
              </div>
            </div>
          </SectionCard>
        </div>
        <div class="col-lg-6">
          <SectionCard title="Placement Rate">
            <div class="rate-ring-display">
              <ProgressRing :percent="placementRate" color="primary" :size="120" :stroke-width="8" />
              <div class="rate-ring-info">
                <p class="rate-ring-description">
                  {{ report.offer_status_counts?.Accepted || 0 }} accepted out of {{ report.total_applications || 0 }} applications
                </p>
              </div>
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
import EmptyState from '@/components/common/EmptyState.vue'
import ProgressRing from '@/components/common/ProgressRing.vue'

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
.rate-ring-display {
  display: flex;
  align-items: center;
  gap: var(--space-6);
}

.rate-ring-info {
  flex: 1;
}

.rate-ring-description {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
  line-height: var(--leading-relaxed);
}

@media (max-width: 575.98px) {
  .rate-ring-display {
    flex-direction: column;
    text-align: center;
  }
}
</style>
