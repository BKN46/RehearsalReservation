<template>
  <div class="admin">
    <el-tabs v-model="activeTab">
      <!-- 用户管理 -->
      <el-tab-pane label="用户管理" name="users">
        <el-card>
          <el-table :data="users" style="width: 100%" v-loading="loadingUsers">
            <el-table-column prop="student_id" label="学号" width="120" />
            <el-table-column prop="name" label="姓名" width="100" />
            <el-table-column prop="email" label="邮箱" width="200" />
            <el-table-column prop="phone" label="手机号" width="120" />
            <el-table-column prop="is_admin" label="管理员" width="80">
              <template #default="{ row }">
                <el-tag :type="row.is_admin ? 'danger' : 'info'" size="small">
                  {{ row.is_admin ? '是' : '否' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="is_active" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
                  {{ row.is_active ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="注册时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button
                  :type="row.is_active ? 'danger' : 'success'"
                  size="small"
                  @click="handleToggleUserActive(row.id)"
                  :disabled="row.is_admin"
                >
                  {{ row.is_active ? '禁用' : '启用' }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 不可预约时间段 -->
      <el-tab-pane label="不可预约时间" name="unavailable">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>不可预约时间段管理</span>
              <el-button type="primary" @click="showUnavailableDialog = true">添加</el-button>
            </div>
          </template>

          <el-table :data="unavailableTimes" style="width: 100%" v-loading="loadingUnavailable">
            <el-table-column prop="campus_name" label="校区" width="120" />
            <el-table-column prop="date" label="日期" width="120" />
            <el-table-column label="时间" width="180">
              <template #default="{ row }">
                {{ row.start_hour }}:00 - {{ row.end_hour }}:00
              </template>
            </el-table-column>
            <el-table-column prop="reason" label="原因" />
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button type="danger" size="small" @click="handleDeleteUnavailable(row.id)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 钥匙管理员 -->
      <el-tab-pane label="钥匙管理员" name="keyManagers">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>钥匙管理员</span>
              <el-button type="primary" @click="showKeyManagerDialog = true">添加</el-button>
            </div>
          </template>

          <el-table :data="keyManagers" style="width: 100%" v-loading="loadingKeyManagers">
            <el-table-column prop="campus_name" label="校区" width="120" />
            <el-table-column prop="name" label="姓名" width="150" />
            <el-table-column prop="contact" label="联系方式" />
            <el-table-column prop="is_active" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
                  {{ row.is_active ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="handleEditKeyManager(row)">
                  编辑
                </el-button>
                <el-button type="danger" size="small" @click="handleDeleteKeyManager(row.id)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 不可预约时间对话框 -->
    <el-dialog v-model="showUnavailableDialog" title="添加不可预约时间" width="500px">
      <el-form :model="unavailableForm" label-width="100px">
        <el-form-item label="校区">
          <el-select v-model="unavailableForm.campus_id" placeholder="请选择校区" style="width: 100%">
            <el-option v-for="campus in campuses" :key="campus.id" :label="campus.name" :value="campus.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker
            v-model="unavailableForm.date"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="开始时间">
          <el-input-number v-model="unavailableForm.start_hour" :min="8" :max="21" />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-input-number v-model="unavailableForm.end_hour" :min="9" :max="22" />
        </el-form-item>
        <el-form-item label="原因">
          <el-input v-model="unavailableForm.reason" placeholder="请输入原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUnavailableDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAddUnavailable">确定</el-button>
      </template>
    </el-dialog>

    <!-- 钥匙管理员对话框 -->
    <el-dialog v-model="showKeyManagerDialog" :title="editingKeyManager ? '编辑钥匙管理员' : '添加钥匙管理员'" width="500px">
      <el-form :model="keyManagerForm" label-width="100px">
        <el-form-item label="校区">
          <el-select v-model="keyManagerForm.campus_id" placeholder="请选择校区" style="width: 100%">
            <el-option v-for="campus in campuses" :key="campus.id" :label="campus.name" :value="campus.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="keyManagerForm.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="联系方式">
          <el-input v-model="keyManagerForm.contact" placeholder="请输入联系方式" />
        </el-form-item>
        <el-form-item v-if="editingKeyManager" label="状态">
          <el-switch v-model="keyManagerForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showKeyManagerDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitKeyManager">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { adminService, reservationService } from '@/services/api'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'Admin',
  setup() {
    const activeTab = ref('users')
    const users = ref([])
    const unavailableTimes = ref([])
    const keyManagers = ref([])
    const campuses = ref([])
    const loadingUsers = ref(false)
    const loadingUnavailable = ref(false)
    const loadingKeyManagers = ref(false)
    const showUnavailableDialog = ref(false)
    const showKeyManagerDialog = ref(false)
    const editingKeyManager = ref(false)

    const unavailableForm = ref({
      campus_id: null,
      date: null,
      start_hour: 8,
      end_hour: 12,
      reason: ''
    })

    const keyManagerForm = ref({
      id: null,
      campus_id: null,
      name: '',
      contact: '',
      is_active: true
    })

    const formatTime = (timeStr) => {
      return new Date(timeStr).toLocaleString('zh-CN')
    }

    const loadCampuses = async () => {
      try {
        campuses.value = await reservationService.getCampuses()
      } catch (error) {
        console.error('Failed to load campuses:', error)
      }
    }

    const loadUsers = async () => {
      loadingUsers.value = true
      try {
        users.value = await adminService.getAllUsers()
      } catch (error) {
        console.error('Failed to load users:', error)
      } finally {
        loadingUsers.value = false
      }
    }

    const loadUnavailableTimes = async () => {
      loadingUnavailable.value = true
      try {
        unavailableTimes.value = await adminService.getUnavailableTimes()
      } catch (error) {
        console.error('Failed to load unavailable times:', error)
      } finally {
        loadingUnavailable.value = false
      }
    }

    const loadKeyManagers = async () => {
      loadingKeyManagers.value = true
      try {
        keyManagers.value = await adminService.getKeyManagers()
      } catch (error) {
        console.error('Failed to load key managers:', error)
      } finally {
        loadingKeyManagers.value = false
      }
    }

    const handleToggleUserActive = async (userId) => {
      try {
        await adminService.toggleUserActive(userId)
        ElMessage.success('操作成功')
        loadUsers()
      } catch (error) {
        console.error('Failed to toggle user active:', error)
      }
    }

    const handleAddUnavailable = async () => {
      if (!unavailableForm.value.campus_id || !unavailableForm.value.date) {
        ElMessage.warning('请填写所有必填项')
        return
      }

      try {
        const date = new Date(unavailableForm.value.date)
        const dateStr = date.toISOString().split('T')[0]

        await adminService.createUnavailableTime({
          ...unavailableForm.value,
          date: dateStr
        })
        
        ElMessage.success('添加成功')
        showUnavailableDialog.value = false
        unavailableForm.value = {
          campus_id: null,
          date: null,
          start_hour: 8,
          end_hour: 12,
          reason: ''
        }
        loadUnavailableTimes()
      } catch (error) {
        console.error('Failed to add unavailable time:', error)
      }
    }

    const handleDeleteUnavailable = async (id) => {
      try {
        await ElMessageBox.confirm('确定要删除这个不可预约时间段吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        await adminService.deleteUnavailableTime(id)
        ElMessage.success('删除成功')
        loadUnavailableTimes()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Failed to delete unavailable time:', error)
        }
      }
    }

    const handleEditKeyManager = (manager) => {
      editingKeyManager.value = true
      keyManagerForm.value = { ...manager }
      showKeyManagerDialog.value = true
    }

    const handleSubmitKeyManager = async () => {
      if (!keyManagerForm.value.campus_id || !keyManagerForm.value.name || !keyManagerForm.value.contact) {
        ElMessage.warning('请填写所有必填项')
        return
      }

      try {
        if (editingKeyManager.value) {
          await adminService.updateKeyManager(keyManagerForm.value.id, keyManagerForm.value)
          ElMessage.success('更新成功')
        } else {
          await adminService.createKeyManager(keyManagerForm.value)
          ElMessage.success('添加成功')
        }
        
        showKeyManagerDialog.value = false
        editingKeyManager.value = false
        keyManagerForm.value = {
          id: null,
          campus_id: null,
          name: '',
          contact: '',
          is_active: true
        }
        loadKeyManagers()
      } catch (error) {
        console.error('Failed to submit key manager:', error)
      }
    }

    const handleDeleteKeyManager = async (id) => {
      try {
        await ElMessageBox.confirm('确定要删除这个钥匙管理员吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        await adminService.deleteKeyManager(id)
        ElMessage.success('删除成功')
        loadKeyManagers()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Failed to delete key manager:', error)
        }
      }
    }

    onMounted(() => {
      loadCampuses()
      loadUsers()
      loadUnavailableTimes()
      loadKeyManagers()
    })

    return {
      activeTab,
      users,
      unavailableTimes,
      keyManagers,
      campuses,
      loadingUsers,
      loadingUnavailable,
      loadingKeyManagers,
      showUnavailableDialog,
      showKeyManagerDialog,
      editingKeyManager,
      unavailableForm,
      keyManagerForm,
      formatTime,
      handleToggleUserActive,
      handleAddUnavailable,
      handleDeleteUnavailable,
      handleEditKeyManager,
      handleSubmitKeyManager,
      handleDeleteKeyManager
    }
  }
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .card-header {
    font-size: 16px;
  }
  
  :deep(.el-table) {
    font-size: 12px;
  }
  
  :deep(.el-button) {
    padding: 5px 10px;
    font-size: 12px;
  }
  
  :deep(.el-tabs__item) {
    padding: 0 10px;
    font-size: 14px;
  }
}
</style>
