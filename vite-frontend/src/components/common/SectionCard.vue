<template>
  <div class="section-card">
    <div v-if="title" class="section-card-header">
      <h2 class="section-card-title">{{ title }}</h2>
      <div v-if="$slots.headerAction" class="section-card-header-action">
        <slot name="headerAction" />
      </div>
    </div>
    <div class="section-card-body">
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    default: ''
  }
})
</script>

<style scoped>
.section-card {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  overflow: hidden;
  box-shadow: var(--shadow-card);
  transition: box-shadow var(--duration-normal) var(--ease-default);
}

.section-card:hover {
  box-shadow: var(--shadow-card-hover);
}

.section-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--color-border);
}

.section-card-title {
  font-size: var(--text-base);
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
  margin: 0;
}

.section-card-body {
  padding: var(--space-5);
}
</style>
