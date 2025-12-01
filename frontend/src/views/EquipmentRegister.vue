<template>
  <div class="equipment-register">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>我的设备</span>
          <el-button type="primary" @click="showRegisterDialog = true" :size="isMobile ? 'default' : 'default'">
            登记设备
          </el-button>
        </div>
      </template>

      <!-- 移动端卡片布局 -->
      <div v-if="isMobile" class="mobile-list">
        <div v-if="myEquipment.length === 0" class="empty-state">
          <el-empty description="暂无设备" />
        </div>
        <div v-else>
          <div v-for="equipment in myEquipment" :key="equipment.id" class="equipment-card">
            <div class="equipment-header">
              <span class="equipment-name">{{ equipment.equipment_name }}</span>
              <el-tag :type="equipment.is_shared ? 'success' : 'info'" size="small">
                {{ equipment.is_shared ? '共享' : '私有' }}
              </el-tag>
            </div>
            <div class="equipment-info">
              <div class="info-row">
                <span class="label">校区：</span>
                <span class="value">{{ equipment.campus_name }}</span>
              </div>
              <div class="info-row">
                <span class="label">类型：</span>
                <span class="value">{{ equipment.equipment_type }}</span>
              </div>
              <div class="info-row">
                <span class="label">位置：</span>
                <span class="value">{{ equipment.location }}</span>
              </div>
              <div class="info-row">
                <span class="label">联系方式：</span>
                <span class="value">{{ equipment.contact }}</span>
              </div>
              <div v-if="equipment.notes" class="info-row">
                <span class="label">备注：</span>
                <span class="value">{{ equipment.notes }}</span>
              </div>
            </div>
            <div class="equipment-actions">
              <el-button type="primary" size="small" @click="handleEdit(equipment)">编辑</el-button>
              <el-button type="danger" size="small" @click="handleDelete(equipment.id)">删除</el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 桌面端表格布局 -->
      <el-table v-else :data="myEquipment" style="width: 100%" v-loading="loading">
        <el-table-column prop="campus_name" label="校区" width="100" />
        <el-table-column prop="equipment_type" label="类型" width="100" />
        <el-table-column prop="equipment_name" label="名称" min-width="120" />
        <el-table-column prop="location" label="位置" width="120" />
        <el-table-column prop="contact" label="联系方式" width="120" />
        <el-table-column prop="is_shared" label="共享" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_shared ? 'success' : 'info'" size="small">
              {{ row.is_shared ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="notes" label="备注" min-width="120" show-overflow-tooltip />
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" size="small" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 登记/编辑对话框 -->
    <el-dialog 
      v-model="showRegisterDialog" 
      :title="editMode ? '编辑设备' : '登记设备'" 
      :width="isMobile ? '95%' : '600px'"
      :fullscreen="isMobile"
    >
      <el-form :model="equipmentForm" label-width="100px" :label-position="isMobile ? 'top' : 'right'">
        <el-form-item label="校区">
          <el-select v-model="equipmentForm.campus_id" placeholder="请选择校区" style="width: 100%">
            <el-option v-for="campus in campuses" :key="campus.id" :label="campus.name" :value="campus.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="设备类型">
          <el-input v-model="equipmentForm.equipment_type" placeholder="如：吉他、键盘、鼓等" />
        </el-form-item>
        <el-form-item label="设备名称">
          <el-input v-model="equipmentForm.equipment_name" placeholder="请输入设备名称" />
        </el-form-item>
        <el-form-item label="放置位置">
          <el-input v-model="equipmentForm.location" placeholder="请输入设备放置位置" />
        </el-form-item>
        <el-form-item label="是否共享">
          <el-switch v-model="equipmentForm.is_shared" />
        </el-form-item>
        <el-form-item label="联系方式">
          <el-input v-model="equipmentForm.contact" placeholder="请输入联系方式" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="equipmentForm.notes"
            type="textarea"
            :rows="3"
            placeholder="可选"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showRegisterDialog = false" :size="isMobile ? 'default' : 'default'">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting" :size="isMobile ? 'default' : 'default'">
            确定
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { equipmentService, reservationService } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'EquipmentRegister',
  setup() {
    const authStore = useAuthStore()
    const myEquipment = ref([])
    const campuses = ref([])
    const loading = ref(false)
    const showRegisterDialog = ref(false)
    const submitting = ref(false)
    const editMode = ref(false)
    const isMobile = ref(false)

    const equipmentForm = ref({
      id: null,
      campus_id: null,
      equipment_type: '',
      equipment_name: '',
      location: '',
      is_shared: false,
      contact: '',
      notes: ''
    })

    // 检测移动端
    const checkMobile = () => {
      isMobile.value = window.innerWidth <= 768
    }

    const resetForm = () => {
      equipmentForm.value = {
        id: null,
        campus_id: null,
        equipment_type: '',
        equipment_name: '',
        location: '',
        is_shared: false,
        contact: '',
        notes: ''
      }
    }

    const loadCampuses = async () => {
      try {
        campuses.value = await reservationService.getCampuses()
        // 如果用户设置了默认校区，使用默认校区
        const preferredCampusId = authStore.user?.preferred_campus_id
        if (preferredCampusId && campuses.value.find(c => c.id === preferredCampusId)) {
          equipmentForm.value.campus_id = preferredCampusId
        }
      } catch (error) {
        console.error('Failed to load campuses:', error)
      }
    }

    const loadMyEquipment = async () => {
      loading.value = true
      try {
        myEquipment.value = await equipmentService.getMyEquipment()
      } catch (error) {
        console.error('Failed to load my equipment:', error)
      } finally {
        loading.value = false
      }
    }

    const handleEdit = (equipment) => {
      editMode.value = true
      equipmentForm.value = { ...equipment }
      showRegisterDialog.value = true
    }

    const handleSubmit = async () => {
      if (!equipmentForm.value.campus_id || !equipmentForm.value.equipment_type || 
          !equipmentForm.value.equipment_name || !equipmentForm.value.location || 
          !equipmentForm.value.contact) {
        ElMessage.warning('请填写所有必填项')
        return
      }

      submitting.value = true
      try {
        if (editMode.value) {
          await equipmentService.updateEquipment(equipmentForm.value.id, equipmentForm.value)
          ElMessage.success('更新成功')
        } else {
          await equipmentService.registerEquipment(equipmentForm.value)
          ElMessage.success('登记成功')
        }
        
        showRegisterDialog.value = false
        resetForm()
        editMode.value = false
        loadMyEquipment()
      } catch (error) {
        console.error('Failed to submit equipment:', error)
      } finally {
        submitting.value = false
      }
    }

    const handleDelete = async (equipmentId) => {
      try {
        await ElMessageBox.confirm('确定要删除这个设备吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        await equipmentService.deleteEquipment(equipmentId)
        ElMessage.success('删除成功')
        loadMyEquipment()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Failed to delete equipment:', error)
        }
      }
    }

    onMounted(() => {
      checkMobile()
      window.addEventListener('resize', checkMobile)
      loadCampuses()
      loadMyEquipment()
    })

    onUnmounted(() => {
      window.removeEventListener('resize', checkMobile)
    })

    return {
      myEquipment,
      campuses,
      loading,
      showRegisterDialog,
      submitting,
      editMode,
      isMobile,
      equipmentForm,
      handleEdit,
      handleSubmit,
      handleDelete
    }
  }
}
</script>

<style scoped>
.equipment-register {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
}

/* 移动端卡片样式 */
.mobile-list {
  margin-top: 10px;
}

.equipment-card {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.equipment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid #f0f0f0;
}

.equipment-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  flex: 1;
  margin-right: 10px;
}

.equipment-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.info-row {
  display: flex;
  font-size: 14px;
  line-height: 1.5;
}

.info-row .label {
  color: #909399;
  min-width: 80px;
  flex-shrink: 0;
}

.info-row .value {
  color: #606266;
  flex: 1;
  word-break: break-word;
}

.equipment-actions {
  display: flex;
  gap: 10px;
  padding-top: 10px;
  border-top: 1px solid #f0f0f0;
}

.equipment-actions .el-button {
  flex: 1;
}

.empty-state {
  padding: 40px 0;
  text-align: center;
}

.dialog-footer {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .card-header {
    font-size: 16px;
  }
  
  .dialog-footer {
    justify-content: stretch;
  }
  
  .dialog-footer .el-button {
    flex: 1;
  }
}

/* 桌面端优化 */
@media (min-width: 769px) {
  .card-header {
    font-size: 18px;
  }
}
</style>
