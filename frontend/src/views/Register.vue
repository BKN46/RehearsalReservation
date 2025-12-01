<template>
  <div class="register-container">
    <el-card class="register-card">
      <template #header>
        <div class="card-header">
          <h2>注册 - 排练室预约系统</h2>
        </div>
      </template>

      <el-form :model="form" :rules="rules" ref="registerForm" label-width="100px">
        <el-form-item label="学号" prop="student_id">
          <el-input v-model="form.student_id" placeholder="请输入学号" />
        </el-form-item>

        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" placeholder="请输入姓名" />
        </el-form-item>

        <el-form-item label="校内邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入@buaa.edu.cn邮箱" />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码（至少6位）" />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" placeholder="请再次输入密码" />
        </el-form-item>

        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号（可选）" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleRegister" :loading="loading" style="width: 100%">
            注册
          </el-button>
        </el-form-item>

        <el-form-item>
          <div style="text-align: center; width: 100%">
            <span>已有账号？</span>
            <el-link type="primary" @click="$router.push('/login')">立即登录</el-link>
          </div>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

export default {
  name: 'Register',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const registerForm = ref(null)
    const loading = ref(false)

    const form = ref({
      student_id: '',
      name: '',
      email: '',
      password: '',
      confirmPassword: '',
      phone: ''
    })

    const validateEmail = (rule, value, callback) => {
      if (!value.endsWith('@buaa.edu.cn')) {
        callback(new Error('邮箱必须以@buaa.edu.cn结尾'))
      } else {
        callback()
      }
    }

    const validateConfirmPassword = (rule, value, callback) => {
      if (value !== form.value.password) {
        callback(new Error('两次输入的密码不一致'))
      } else {
        callback()
      }
    }

    const rules = {
      student_id: [
        { required: true, message: '请输入学号', trigger: 'blur' }
      ],
      name: [
        { required: true, message: '请输入姓名', trigger: 'blur' }
      ],
      email: [
        { required: true, message: '请输入邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
        { validator: validateEmail, trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码长度至少6位', trigger: 'blur' }
      ],
      confirmPassword: [
        { required: true, message: '请再次输入密码', trigger: 'blur' },
        { validator: validateConfirmPassword, trigger: 'blur' }
      ],
      phone: [
        { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
      ]
    }

    const handleRegister = async () => {
      await registerForm.value.validate(async (valid) => {
        if (valid) {
          loading.value = true
          try {
            const { confirmPassword, ...userData } = form.value
            const response = await authStore.register(userData)
            
            // 检查是否发送了验证邮件
            if (response?.email_sent) {
              ElMessage.success({
                message: '注册成功！验证邮件已发送到您的邮箱，请查收并完成验证。',
                duration: 5000
              })
            } else if (response?.requires_activation) {
              ElMessage.warning({
                message: '注册成功！您的账号需要管理员激活后才能使用。',
                duration: 5000
              })
            } else {
              ElMessage.success('注册成功')
            }
            
            router.push('/login')
          } catch (error) {
            console.error('Registration failed:', error)
          } finally {
            loading.value = false
          }
        }
      })
    }

    return {
      form,
      rules,
      registerForm,
      loading,
      handleRegister
    }
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-card {
  width: 100%;
  max-width: 500px;
}

.card-header h2 {
  margin: 0;
  text-align: center;
  color: #303133;
  font-size: 22px;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .register-container {
    padding: 15px;
    align-items: flex-start;
    padding-top: 30px;
  }
  
  .card-header h2 {
    font-size: 20px;
  }
}
</style>
