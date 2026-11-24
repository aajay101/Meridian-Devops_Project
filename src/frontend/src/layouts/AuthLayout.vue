<template>
  <div class="auth-layout">
    <div class="auth-card">
      <div class="auth-header">
        <i class="bi bi-mortarboard-fill text-primary auth-logo"></i>
        <h1 class="auth-title">Recruit Link</h1>
      </div>
      <router-view />
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.auth-layout {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-bg);
  padding: var(--space-4);
}

.auth-card {
  width: 100%;
  max-width: 420px;
  background-color: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  padding: var(--space-8);
}

.auth-header {
  text-align: center;
  margin-bottom: var(--space-8);
}

.auth-logo {
  font-size: var(--text-3xl);
  display: block;
  margin-bottom: var(--space-3);
}

.auth-title {
  font-size: var(--text-xl);
  font-weight: var(--weight-bold);
  color: var(--text-primary);
  margin: 0;
}
</style>
