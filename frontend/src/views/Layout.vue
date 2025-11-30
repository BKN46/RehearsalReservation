<template>
  <el-container class="layout-container">
    <!-- 移动端顶部导航栏 -->
    <el-header class="header">
      <div class="header-content">
        <el-icon class="menu-icon" @click="drawerVisible = true" v-if="isMobile">
          <Menu />
        </el-icon>
        <h1>排练室预约</h1>
        <div class="header-right">
          <span class="username" v-if="!isMobile">{{ user?.name }}</span>
          <el-button @click="handleLogout" type="danger" :size="isMobile ? 'small' : 'default'">退出</el-button>
        </div>
      </div>
    </el-header>

    <el-container>
      <!-- 桌面端侧边栏 -->
      <el-aside width="200px" class="sidebar" v-if="!isMobile">
        <el-menu
          :default-active="activeMenu"
          @select="handleMenuSelect"
          :router="true"
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
          <el-menu-item index="/profile">
            <el-icon><User /></el-icon>
            <span>个人信息</span>
          </el-menu-item>
          <el-menu-item v-if="authStore.isAdmin" index="/admin">
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 移动端抽屉菜单 -->
      <el-drawer
        v-model="drawerVisible"
        title="菜单"
        direction="ltr"
        size="70%"
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
        <div class="nav-item" @click="$router.push('/')" :class="{ active: activeMenu === '/' }">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </div>
        <div class="nav-item" @click="$router.push('/reservations')" :class="{ active: activeMenu === '/reservations' }">
          <el-icon><Calendar /></el-icon>
          <span>预约</span>
        </div>
        <div class="nav-item" @click="$router.push('/equipment-borrow')" :class="{ active: activeMenu === '/equipment-borrow' }">
          <el-icon><Box /></el-icon>
          <span>借用</span>
        </div>
        <div class="nav-item" @click="$router.push('/profile')" :class="{ active: activeMenu === '/profile' }">
          <el-icon><User /></el-icon>
          <span>我的</span>
        </div>
      </div>
    </el-footer>
  </el-container>
</template>

<script>
import { computed } from 'vue'
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

    const handleMenuSelect = (index) => {
      router.push(index)
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

    return {
      user,
      activeMenu,
      authStore,
      handleMenuSelect,
      handleLogout
    }
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background-color: #409eff;
  color: white;
  display: flex;
  align-items: center;
  padding: 0 15px;
  height: 60px;
  flex-shrink: 0;
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
  margin-right: 15px;
}

.header-content h1 {
  margin: 0;
  font-size: 20px;
  flex: 1;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.username {
  font-size: 14px;
}

.sidebar {
  background-color: #fff;
  border-right: 1px solid #e4e7ed;
}

.main-content {
  background-color: #f5f5f5;
  padding: 15px;
  flex: 1;
  overflow-y: auto;
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
  height: 60px;
  padding: 0;
  background-color: white;
  border-top: 1px solid #e4e7ed;
  flex-shrink: 0;
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
}

.nav-item.active {
  color: #409eff;
}

.nav-item .el-icon {
  font-size: 22px;
  margin-bottom: 4px;
}

.nav-item span {
  font-size: 12px;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .header {
    height: 50px;
  }
  
  .header-content h1 {
    font-size: 18px;
  }
  
  .main-content {
    padding: 10px;
    padding-bottom: 70px; /* 为底部导航留空间 */
  }
}
</style>
