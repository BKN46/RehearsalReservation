<template>
  <div class="verify-email-container">
    <el-card class="verify-card">
      <template #header>
        <div class="card-header">
          <h2>邮箱验证</h2>
        </div>
      </template>

      <!-- 验证中 -->
      <div v-if="verifying" class="status-container">
        <el-icon class="loading-icon" :size="60"><Loading /></el-icon>
        <p class="status-text">正在验证您的邮箱...</p>
      </div>

      <!-- 验证成功 -->
      <div v-else-if="verificationSuccess" class="status-container success">
        <el-icon class="success-icon" :size="60"><SuccessFilled /></el-icon>
        <h3>验证成功！</h3>
        <p class="status-text">您的邮箱已成功验证，账户已激活。</p>
        <p class="redirect-text">{{ countdown }} 秒后自动跳转到登录页面...</p>
        <el-button type="primary" @click="goToLogin" style="margin-top: 20px;">
          立即登录
        </el-button>
      </div>

      <!-- 验证失败 -->
      <div v-else-if="verificationError" class="status-container error">
        <el-icon class="error-icon" :size="60"><CircleCloseFilled /></el-icon>
        <h3>验证失败</h3>
        <p class="status-text">{{ errorMessage }}</p>
        <div class="action-buttons">
          <el-button type="primary" @click="resendEmail" :loading="resending">
            重新发送验证邮件
          </el-button>
          <el-button @click="goToLogin">
            返回登录
          </el-button>
        </div>
      </div>

      <!-- 重新发送成功提示 -->
      <el-dialog v-model="showResendDialog" title="提示" width="400px">
        <p>验证邮件已重新发送到您的邮箱，请查收。</p>
        <template #footer>
          <el-button type="primary" @click="showResendDialog = false">确定</el-button>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authService } from '@/services/api'
import { ElMessage } from 'element-plus'
import { Loading, SuccessFilled, CircleCloseFilled } from '@element-plus/icons-vue'

export default {
  name: 'VerifyEmail',
  components: {
    Loading,
    SuccessFilled,
    CircleCloseFilled
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    const verifying = ref(true)
    const verificationSuccess = ref(false)
    const verificationError = ref(false)
    const errorMessage = ref('')
    const countdown = ref(5)
    const resending = ref(false)
    const showResendDialog = ref(false)
    const userEmail = ref('')

    const verifyEmail = async () => {
      const token = route.query.token

      if (!token) {
        verificationError.value = true
        errorMessage.value = '验证链接无效，缺少验证令牌。'
        verifying.value = false
        return
      }

      try {
        const response = await authService.verifyEmail(token)
        verificationSuccess.value = true
        userEmail.value = response.user?.email || ''
        
        // 启动倒计时
        startCountdown()
      } catch (error) {
        verificationError.value = true
        if (error.response?.data?.error) {
          const errorMsg = error.response.data.error
          if (errorMsg.includes('expired')) {
            errorMessage.value = '验证链接已过期，请重新发送验证邮件。'
          } else if (errorMsg.includes('Invalid')) {
            errorMessage.value = '验证链接无效，请检查链接是否正确。'
          } else {
            errorMessage.value = errorMsg
          }
        } else {
          errorMessage.value = '验证失败，请稍后重试。'
        }
      } finally {
        verifying.value = false
      }
    }

    const startCountdown = () => {
      const timer = setInterval(() => {
        countdown.value--
        if (countdown.value <= 0) {
          clearInterval(timer)
          goToLogin()
        }
      }, 1000)
    }

    const goToLogin = () => {
      router.push('/login')
    }

    const resendEmail = async () => {
      // 需要用户输入邮箱
      ElMessage.prompt('请输入您的邮箱地址', '重新发送验证邮件', {
        confirmButtonText: '发送',
        cancelButtonText: '取消',
        inputPattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
        inputErrorMessage: '请输入有效的邮箱地址'
      }).then(async ({ value }) => {
        resending.value = true
        try {
          await authService.resendVerification(value)
          showResendDialog.value = true
        } catch (error) {
          ElMessage.error(error.response?.data?.error || '发送失败，请稍后重试')
        } finally {
          resending.value = false
        }
      }).catch(() => {
        // 用户取消
      })
    }

    onMounted(() => {
      verifyEmail()
    })

    return {
      verifying,
      verificationSuccess,
      verificationError,
      errorMessage,
      countdown,
      resending,
      showResendDialog,
      goToLogin,
      resendEmail
    }
  }
}
</script>

<style scoped>
.verify-email-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.verify-card {
  width: 100%;
  max-width: 500px;
}

.card-header h2 {
  margin: 0;
  text-align: center;
  color: #303133;
}

.status-container {
  text-align: center;
  padding: 40px 20px;
}

.loading-icon {
  color: #409eff;
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.success-icon {
  color: #67c23a;
}

.error-icon {
  color: #f56c6c;
}

.status-container h3 {
  margin: 20px 0 10px;
  color: #303133;
  font-size: 20px;
}

.status-text {
  color: #606266;
  font-size: 16px;
  margin: 10px 0;
}

.redirect-text {
  color: #909399;
  font-size: 14px;
  margin-top: 20px;
}

.action-buttons {
  margin-top: 30px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: center;
}

.action-buttons .el-button {
  width: 200px;
}

@media (max-width: 768px) {
  .verify-card {
    margin: 0 10px;
  }

  .status-container {
    padding: 30px 10px;
  }

  .action-buttons .el-button {
    width: 100%;
  }
}
</style>
