<template>
  <div class="error-page">
    <div class="error-content">
      <h1 class="error-code">404</h1>
      <h2 class="error-title">Page Not Found</h2>
      <p class="error-message">The page you are looking for does not exist or has been moved.</p>
      <router-link to="/login" class="btn btn-primary">
        <i class="bi bi-house me-2"></i>Go to Login
      </router-link>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.error-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-bg);
  padding: var(--space-4);
}

.error-content {
  text-align: center;
  max-width: 400px;
}

.error-code {
  font-size: 72px;
  font-weight: var(--weight-bold);
  color: var(--color-primary);
  margin: 0;
  line-height: 1;
}

.error-title {
  font-size: var(--text-xl);
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
  margin: var(--space-4) 0 var(--space-2);
}

.error-message {
  font-size: var(--text-base);
  color: var(--text-secondary);
  margin-bottom: var(--space-6);
}
</style>
