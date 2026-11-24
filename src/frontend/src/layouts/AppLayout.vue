<template>
  <div class="app-layout">
    <Sidebar
      :is-open="sidebarOpen"
      :role="authStore.user?.role || 'Role'"
      :user-email="authStore.user?.email || 'user@placeholder.com'"
      @close="sidebarOpen = false"
    />

    <div class="offcanvas-backdrop" :class="{ show: sidebarOpen }" @click="sidebarOpen = false"></div>

    <div class="app-content">
      <Navbar
        :user-email="authStore.user?.email || 'Account'"
        @toggle-sidebar="sidebarOpen = !sidebarOpen"
      />
      <main class="app-main">
        <router-view />
      </main>
    </div>
    <ToastContainer ref="toastRef" />
  </div>
</template>

<script setup>
import { ref, provide } from 'vue'
import { useAuthStore } from '@/stores/auth'
import Sidebar from '@/components/layout/Sidebar.vue'
import Navbar from '@/components/layout/Navbar.vue'
import ToastContainer from '@/components/common/ToastContainer.vue'

const authStore = useAuthStore()
const sidebarOpen = ref(false)
const toastRef = ref(null)

provide('toast', {
  success: (title, msg) => toastRef.value?.success(title, msg),
  error: (title, msg) => toastRef.value?.error(title, msg),
  warning: (title, msg) => toastRef.value?.warning(title, msg),
  info: (title, msg) => toastRef.value?.info(title, msg)
})
</script>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
}

.app-content {
  flex: 1;
  margin-left: 240px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-main {
  flex: 1;
  padding: var(--space-6);
  background-color: var(--color-bg);
}

.offcanvas-backdrop {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 999;
}

.offcanvas-backdrop.show {
  display: block;
}

@media (max-width: 767.98px) {
  .app-content {
    margin-left: 0;
  }
}
</style>
