<template>
  <el-container class="layout-container">
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="header-content">
        <el-icon class="menu-icon" @click="toggleSidebar">
          <Menu />
        </el-icon>
        <div class="header-title">
          <h1>音协预约</h1>
        </div>
        <div class="header-right">
          <span class="username" v-if="!isMobile">{{ user?.name }}</span>
          <el-button @click="handleLogout" type="danger" :size="isMobile ? 'small' : 'default'">退出</el-button>
        </div>
      </div>
    </el-header>

    <el-container class="container-body">
      <!-- 侧边栏 - 桌面端使用 Aside，移动端使用 Drawer -->
      <el-aside 
        v-if="!isMobile" 
        :width="sidebarCollapsed ? '64px' : '200px'" 
        class="sidebar"
        :class="{ collapsed: sidebarCollapsed }"
      >
        <el-menu
          :default-active="activeMenu"
          @select="handleMenuSelect"
          :collapse="sidebarCollapsed"
          :router="true"
        >
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <template #title><span>首页</span></template>
          </el-menu-item>
          <el-menu-item index="/reservations">
            <el-icon><Calendar /></el-icon>
            <template #title><span>我的预约</span></template>
          </el-menu-item>
          <el-menu-item index="/equipment-borrow">
            <el-icon><Box /></el-icon>
            <template #title><span>设备借用</span></template>
          </el-menu-item>
          <el-menu-item index="/equipment-register">
            <el-icon><List /></el-icon>
            <template #title><span>设备登记</span></template>
          </el-menu-item>
          <el-menu-item index="/equipment-list">
            <el-icon><Document /></el-icon>
            <template #title><span>设备列表</span></template>
          </el-menu-item>
          <el-menu-item index="/profile">
            <el-icon><User /></el-icon>
            <template #title><span>个人信息</span></template>
          </el-menu-item>
          <el-menu-item v-if="authStore.isAdmin" index="/admin">
            <el-icon><Setting /></el-icon>
            <template #title><span>系统管理</span></template>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 移动端抽屉菜单 -->
      <el-drawer
        v-model="drawerVisible"
        title="菜单"
        direction="ltr"
        :size="isMobile ? '75%' : '280px'"
      >
        <div class="mobile-user-info">
          <el-avatar :size="50">{{ user?.name?.charAt(0) }}</el-avatar>
          <div class="user-details">
            <div class="user-name">{{ user?.name }}</div>
            <div class="user-id">{{ user?.student_id }}</div>
          </div>
        </div>
        <el-menu
          :default-active="activeMenu"
          @select="handleMobileMenuSelect"
        >
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="/reservations">
            <el-icon><Calendar /></el-icon>
            <span>我的预约</span>
          </el-menu-item>
          <el-menu-item index="/equipment-borrow">
            <el-icon><Box /></el-icon>
            <span>设备借用</span>
          </el-menu-item>
          <el-menu-item index="/equipment-register">
            <el-icon><List /></el-icon>
            <span>设备登记</span>
          </el-menu-item>
          <el-menu-item index="/equipment-list">
            <el-icon><Document /></el-icon>
            <span>设备列表</span>
          </el-menu-item>
          <el-menu-item index="/profile">
            <el-icon><User /></el-icon>
            <span>个人信息</span>
          </el-menu-item>
          <el-menu-item v-if="authStore.isAdmin" index="/admin">
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </el-menu-item>
        </el-menu>
      </el-drawer>

      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>

    <!-- 移动端底部导航栏 -->
    <el-footer class="mobile-footer" v-if="isMobile">
      <div class="footer-nav">
        <div class="nav-item" @click="handleBottomNavClick('/')" :class="{ active: activeMenu === '/' }">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </div>
        <div class="nav-item" @click="handleBottomNavClick('/reservations')" :class="{ active: activeMenu === '/reservations' }">
          <el-icon><Calendar /></el-icon>
          <span>预约</span>
        </div>
        <div class="nav-item" @click="handleBottomNavClick('/equipment-borrow')" :class="{ active: activeMenu === '/equipment-borrow' }">
          <el-icon><Document /></el-icon>
          <span>借用</span>
        </div>
        <div class="nav-item" @click="handleBottomNavClick('/equipment-list')" :class="{ active: activeMenu === '/equipment-list' }">
          <el-icon><Box /></el-icon>
          <span>设备</span>
        </div>
        <div class="nav-item" @click="handleBottomNavClick('/profile')" :class="{ active: activeMenu === '/profile' }">
          <el-icon><User /></el-icon>
          <span>我的</span>
        </div>
      </div>
    </el-footer>
  </el-container>
</template>

<script>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessageBox } from 'element-plus'

export default {
  name: 'Layout',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const authStore = useAuthStore()

    const user = computed(() => authStore.user)
    const activeMenu = computed(() => route.path)
    
    // 响应式状态
    const isMobile = ref(false)
    const drawerVisible = ref(false)
    const sidebarCollapsed = ref(false)

    // 检测屏幕尺寸
    const checkMobile = () => {
      isMobile.value = window.innerWidth <= 768
      // 在移动端自动关闭侧边栏折叠状态
      if (isMobile.value) {
        sidebarCollapsed.value = false
      }
    }

    // 切换侧边栏
    const toggleSidebar = () => {
      if (isMobile.value) {
        drawerVisible.value = !drawerVisible.value
      } else {
        sidebarCollapsed.value = !sidebarCollapsed.value
      }
    }

    const handleMenuSelect = (index) => {
      router.push(index)
    }

    const handleMobileMenuSelect = (index) => {
      router.push(index)
      drawerVisible.value = false
    }

    const handleBottomNavClick = (path) => {
      router.push(path)
    }

    const handleLogout = async () => {
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      
      authStore.logout()
      router.push('/login')
    }

    onMounted(() => {
      checkMobile()
      window.addEventListener('resize', checkMobile)
    })

    onUnmounted(() => {
      window.removeEventListener('resize', checkMobile)
    })

    return {
      user,
      activeMenu,
      authStore,
      isMobile,
      drawerVisible,
      sidebarCollapsed,
      toggleSidebar,
      handleMenuSelect,
      handleMobileMenuSelect,
      handleBottomNavClick,
      handleLogout
    }
  }
}
</script>

<style scoped>
/* 移动优先设计 */
.layout-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  background-color: #409eff;
  color: white;
  display: flex;
  align-items: center;
  padding: 0 12px;
  height: 50px;
  flex-shrink: 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.menu-icon {
  font-size: 24px;
  cursor: pointer;
  margin-right: 12px;
  transition: transform 0.3s;
}

.menu-icon:hover {
  transform: scale(1.1);
}

.header-content h1 {
  margin: 0;
  font-size: 18px;
  flex: 1;
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.username {
  font-size: 14px;
  display: none;
}

.container-body {
  flex: 1;
  overflow: hidden;
}

.sidebar {
  background-color: #fff;
  border-right: 1px solid #e4e7ed;
  transition: width 0.3s;
  overflow-x: hidden;
  display: none;
}

.sidebar.collapsed :deep(.el-menu) {
  border-right: none;
}

.main-content {
  background-color: #f5f5f5;
  padding: 10px;
  padding-bottom: 70px;
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  -webkit-overflow-scrolling: touch;
}

/* 移动端抽屉样式 */
.mobile-user-info {
  display: flex;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  margin: -20px -20px 20px -20px;
  color: white;
}

.user-details {
  margin-left: 15px;
  flex: 1;
}

.user-name {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 5px;
}

.user-id {
  font-size: 14px;
  opacity: 0.9;
}

/* 移动端底部导航 */
.mobile-footer {
  height: 56px;
  padding: 0;
  background-color: white;
  border-top: 1px solid #e4e7ed;
  flex-shrink: 0;
  box-shadow: 0 -2px 4px rgba(0, 0, 0, 0.05);
}

.footer-nav {
  display: flex;
  height: 100%;
}

.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #909399;
  transition: all 0.3s;
  position: relative;
}

.nav-item:active {
  background-color: #f5f5f5;
}

.nav-item.active {
  color: #409eff;
}

.nav-item.active::before {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 30px;
  height: 3px;
  background-color: #409eff;
  border-radius: 0 0 3px 3px;
}

.nav-item .el-icon {
  font-size: 22px;
  margin-bottom: 2px;
}

.nav-item span {
  font-size: 11px;
}

/* 平板和桌面端适配 */
@media (min-width: 769px) {
  .header {
    height: 60px;
    padding: 0 20px;
  }
  
  .header-content h1 {
    font-size: 20px;
  }
  
  .username {
    display: inline;
  }
  
  .sidebar {
    display: block;
  }
  
  .main-content {
    padding: 20px;
    padding-bottom: 20px;
  }
  
  .mobile-footer {
    display: none;
  }
}

/* 大屏幕优化 */
@media (min-width: 1200px) {
  .main-content {
    padding: 24px;
  }
}

/* 针对小屏手机的额外优化 */
@media (max-width: 375px) {
  .header-content h1 {
    font-size: 16px;
  }
  
  .nav-item .el-icon {
    font-size: 20px;
  }
  
  .nav-item span {
    font-size: 10px;
  }
}

/* 横屏适配 */
@media (max-height: 500px) and (orientation: landscape) {
  .main-content {
    padding-bottom: 10px;
  }
  
  .mobile-footer {
    height: 48px;
  }
  
  .nav-item .el-icon {
    font-size: 18px;
  }
  
  .nav-item span {
    font-size: 10px;
  }
}
</style>
