<template>
  <div class="table-toolbar">
    <div class="filter-tabs" role="tablist" :aria-label="ariaLabel">
      <button
        v-for="filter in filters"
        :key="filter.key"
        class="filter-tab"
        :class="{ active: modelValue === filter.key }"
        role="tab"
        :aria-selected="modelValue === filter.key"
        @click="$emit('update:modelValue', filter.key)"
      >
        {{ filter.label }}
        <span v-if="filter.count !== undefined" class="count-badge">{{ filter.count }}</span>
      </button>
    </div>
    <div class="table-toolbar-search">
      <i class="bi bi-search search-icon"></i>
      <input
        :value="searchValue"
        type="text"
        class="form-control form-control-sm"
        :placeholder="searchPlaceholder"
        :aria-label="searchPlaceholder"
        @input="$emit('update:searchValue', $event.target.value)"
      />
    </div>
  </div>
</template>

<script setup>
defineProps({
  filters: {
    type: Array,
    required: true,
    validator: (v) => v.every((f) => f.key && f.label)
  },
  modelValue: {
    type: String,
    required: true
  },
  searchValue: {
    type: String,
    default: ''
  },
  searchPlaceholder: {
    type: String,
    default: 'Search...'
  },
  ariaLabel: {
    type: String,
    default: 'Filter by status'
  }
})

defineEmits(['update:modelValue', 'update:searchValue'])
</script>
