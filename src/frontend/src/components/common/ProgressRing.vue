<template>
  <div class="progress-ring" :aria-valuenow="percent" aria-valuemin="0" aria-valuemax="100" role="progressbar">
    <svg :width="size" :height="size" class="progress-ring__svg">
      <circle
        class="progress-ring__track"
        :cx="center"
        :cy="center"
        :r="radius"
        fill="none"
        :stroke-width="strokeWidth"
      />
      <circle
        class="progress-ring__fill"
        :class="`progress-ring__fill--${color}`"
        :cx="center"
        :cy="center"
        :r="radius"
        fill="none"
        :stroke-width="strokeWidth"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="dashOffset"
        :style="{ transition: animated ? 'stroke-dashoffset 0.6s cubic-bezier(0.4, 0, 0.2, 1)' : 'none' }"
      />
    </svg>
    <div class="progress-ring__label">
      <slot>
        <span class="progress-ring__value">{{ percent }}%</span>
      </slot>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  percent: {
    type: Number,
    required: true,
    validator: (v) => v >= 0 && v <= 100
  },
  size: {
    type: Number,
    default: 120
  },
  strokeWidth: {
    type: Number,
    default: 8
  },
  color: {
    type: String,
    default: 'primary',
    validator: (v) => ['primary', 'success', 'warning', 'danger', 'info'].includes(v)
  },
  animated: {
    type: Boolean,
    default: true
  }
})

const center = computed(() => props.size / 2)
const radius = computed(() => (props.size - props.strokeWidth) / 2)
const circumference = computed(() => 2 * Math.PI * radius.value)
const dashOffset = computed(() => circumference.value * (1 - props.percent / 100))
</script>

<style scoped>
.progress-ring {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.progress-ring__svg {
  transform: rotate(-90deg);
}

.progress-ring__track {
  stroke: var(--color-border);
}

.progress-ring__fill {
  stroke-linecap: round;
}

.progress-ring__fill--primary {
  stroke: var(--color-primary);
}

.progress-ring__fill--success {
  stroke: var(--color-success);
}

.progress-ring__fill--warning {
  stroke: var(--color-warning);
}

.progress-ring__fill--danger {
  stroke: var(--color-danger);
}

.progress-ring__fill--info {
  stroke: var(--color-info);
}

.progress-ring__label {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.progress-ring__value {
  font-size: var(--text-md);
  font-weight: var(--weight-bold);
  color: var(--text-primary);
  line-height: 1;
}
</style>
