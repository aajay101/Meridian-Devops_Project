
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  const backendTarget =
    env.VITE_API_PROXY_TARGET || 'http://localhost:8000'

  return {
    plugins: [vue()],

    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },

    server: {
      host: '0.0.0.0',

      proxy: {
        '/api': {
          target: backendTarget,
          changeOrigin: true
        },

        '/uploads': {
          target: backendTarget,
          changeOrigin: true
        }
      }
    }
  }
})
