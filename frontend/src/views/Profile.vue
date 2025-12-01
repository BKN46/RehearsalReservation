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

        <el-form-item label="账号状态">
          <el-tag :type="form.is_active ? 'success' : 'danger'" size="large">
            {{ form.is_active ? '已启用' : '已禁用' }}
          </el-tag>
          <div v-if="!form.is_active" style="color: #909399; font-size: 12px; margin-top: 5px;">
            账号已被禁用，请联系管理员启用
          </div>
        </el-form-item>

        <el-form-item label="默认校区" prop="preferred_campus_id">
          <el-select v-model="form.preferred_campus_id" placeholder="请选择默认校区" style="width: 100%">
            <el-option
              v-for="campus in campuses"
              :key="campus.id"
              :label="campus.name"
              :value="campus.id"
            />
          </el-select>
          <div style="color: #909399; font-size: 12px; margin-top: 5px;">
            设置后，预约和设备页面会默认选择此校区
          </div>
        </el-form-item>

        <el-divider content-position="left">修改密码</el-divider>

        <el-form-item label="新密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="不修改请留空" show-password />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" placeholder="请再次输入新密码" show-password />
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
import { reservationService } from '@/services/api'
import { ElMessage } from 'element-plus'

export default {
  name: 'Profile',
  setup() {
    const authStore = useAuthStore()
    const profileForm = ref(null)
    const loading = ref(false)
    const campuses = ref([])

    const form = ref({
      student_id: '',
      name: '',
      email: '',
      phone: '',
      is_active: true,
      preferred_campus_id: null,
      password: '',
      confirmPassword: ''
    })

    // 自定义确认密码验证器
    const validateConfirmPassword = (rule, value, callback) => {
      if (form.value.password && value !== form.value.password) {
        callback(new Error('两次输入的密码不一致'))
      } else {
        callback()
      }
    }

    const rules = {
      name: [
        { required: true, message: '请输入姓名', trigger: 'blur' }
      ],
      phone: [
        { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
      ],
      password: [
        { min: 6, message: '密码长度至少6位', trigger: 'blur' }
      ],
      confirmPassword: [
        { validator: validateConfirmPassword, trigger: 'blur' }
      ]
    }

    const loadCampuses = async () => {
      try {
        campuses.value = await reservationService.getCampuses()
      } catch (error) {
        console.error('Failed to load campuses:', error)
      }
    }

    const loadProfile = () => {
      const user = authStore.user
      if (user) {
        form.value = {
          student_id: user.student_id,
          name: user.name,
          email: user.email,
          phone: user.phone || '',
          is_active: user.is_active !== undefined ? user.is_active : true,
          preferred_campus_id: user.preferred_campus_id || null,
          password: '',
          confirmPassword: ''
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
              phone: form.value.phone,
              preferred_campus_id: form.value.preferred_campus_id
            }
            
            if (form.value.password) {
              if (form.value.password !== form.value.confirmPassword) {
                ElMessage.error('两次输入的密码不一致')
                loading.value = false
                return
              }
              updateData.password = form.value.password
            }

            await authStore.updateProfile(updateData)
            ElMessage.success('更新成功')
            form.value.password = ''
            form.value.confirmPassword = ''
          } catch (error) {
            console.error('Update failed:', error)
          } finally {
            loading.value = false
          }
        }
      })
    }

    onMounted(() => {
      loadCampuses()
      loadProfile()
    })

    return {
      form,
      rules,
      profileForm,
      loading,
      campuses,
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
