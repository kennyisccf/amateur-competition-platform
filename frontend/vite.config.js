import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000',
      '/csrf': 'http://127.0.0.1:8000',
      '/media': 'http://127.0.0.1:8000'
    },
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  build: {
    rolldownOptions: {
      output: {
        codeSplitting: {
          groups: [
            { name: 'vue-vendor', test: /node_modules[\\/](@vue|vue|vue-router|pinia)[\\/]/, priority: 40 },
            { name: 'element-icons', test: /node_modules[\\/]@element-plus[\\/]icons-vue[\\/]/, priority: 30 },
            { name: 'element-plus', test: /node_modules[\\/]element-plus[\\/]/, maxSize: 300000, priority: 20 },
            { name: 'http-vendor', test: /node_modules[\\/]axios[\\/]/, priority: 10 }
          ]
        }
      }
    }
  },
  plugins: [vue()],
})
