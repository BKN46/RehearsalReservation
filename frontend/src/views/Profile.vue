<template>
  <div class="profile">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>个人信息</span>
        </div>
      </template>

      <el-form :model="form" :rules="rules" ref="profileForm" label-width="100px" style="max-width: 600px">
        <el-form-item label="学号">
          <el-input v-model="form.student_id" disabled />
        </el-form-item>

        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>

        <el-form-item label="邮箱">
          <el-input v-model="form.email" disabled />
        </el-form-item>

        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>

        <el-form-item label="新密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="不修改请留空" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleUpdate" :loading="loading">保存修改</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

export default {
  name: 'Profile',
  setup() {
    const authStore = useAuthStore()
    const profileForm = ref(null)
    const loading = ref(false)

    const form = ref({
      student_id: '',
      name: '',
      email: '',
      phone: '',
      password: ''
    })

    const rules = {
      name: [
        { required: true, message: '请输入姓名', trigger: 'blur' }
      ],
      phone: [
        { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
      ],
      password: [
        { min: 6, message: '密码长度至少6位', trigger: 'blur' }
      ]
    }

    const loadProfile = () => {
      const user = authStore.user
      if (user) {
        form.value = {
          student_id: user.student_id,
          name: user.name,
          email: user.email,
          phone: user.phone || '',
          password: ''
        }
      }
    }

    const handleUpdate = async () => {
      await profileForm.value.validate(async (valid) => {
        if (valid) {
          loading.value = true
          try {
            const updateData = {
              name: form.value.name,
              phone: form.value.phone
            }
            
            if (form.value.password) {
              updateData.password = form.value.password
            }

            await authStore.updateProfile(updateData)
            ElMessage.success('更新成功')
            form.value.password = ''
          } catch (error) {
            console.error('Update failed:', error)
          } finally {
            loading.value = false
          }
        }
      })
    }

    onMounted(() => {
      loadProfile()
    })

    return {
      form,
      rules,
      profileForm,
      loading,
      handleUpdate
    }
  }
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 移动端适配 */
@media (max-width: 768px) {
  :deep(.el-form) {
    max-width: 100% !important;
  }
  
  :deep(.el-form-item__label) {
    width: 80px !important;
  }
}
</style>
