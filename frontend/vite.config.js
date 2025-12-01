import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 8080,
    host: true, // 监听所有地址
    strictPort: false, // 端口被占用时自动尝试下一个可用端口
    open: false, // 不自动打开浏览器
    hmr: {
      overlay: true // 在浏览器中显示错误遮罩层
    },
    watch: {
      usePolling: true, // 使用轮询方式监听文件变化（在某些文件系统中更可靠）
      interval:500 // 轮询间隔
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8081',
        changeOrigin: true
      }
    }
  }
})
