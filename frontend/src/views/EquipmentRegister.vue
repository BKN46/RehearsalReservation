<template>
  <div class="equipment-register">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>我的设备</span>
              <el-button type="primary" @click="showRegisterDialog = true">登记设备</el-button>
            </div>
          </template>

          <el-table :data="myEquipment" style="width: 100%" v-loading="loading">
            <el-table-column prop="campus_name" label="校区" width="100" />
            <el-table-column prop="equipment_type" label="类型" width="100" />
            <el-table-column prop="equipment_name" label="名称" />
            <el-table-column prop="location" label="位置" width="120" />
            <el-table-column prop="is_shared" label="共享" width="80">
              <template #default="{ row }">
                <el-tag :type="row.is_shared ? 'success' : 'info'" size="small">
                  {{ row.is_shared ? '是' : '否' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
                <el-button type="danger" size="small" @click="handleDelete(row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>设备列表</span>
              <div>
                <el-select v-model="filterCampusId" placeholder="校区" style="width: 120px; margin-right: 10px" @change="loadAllEquipment">
                  <el-option label="全部" :value="null" />
                  <el-option v-for="campus in campuses" :key="campus.id" :label="campus.name" :value="campus.id" />
                </el-select>
                <el-checkbox v-model="filterShared" @change="loadAllEquipment">仅显示共享</el-checkbox>
              </div>
            </div>
          </template>

          <el-table :data="allEquipment" style="width: 100%" v-loading="loadingAll">
            <el-table-column prop="campus_name" label="校区" width="100" />
            <el-table-column prop="equipment_type" label="类型" width="100" />
            <el-table-column prop="equipment_name" label="名称" />
            <el-table-column prop="location" label="位置" width="120" />
            <el-table-column prop="owner_name" label="所有者" width="100" />
            <el-table-column prop="contact" label="联系方式" width="120" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 登记/编辑对话框 -->
    <el-dialog v-model="showRegisterDialog" :title="editMode ? '编辑设备' : '登记设备'" width="600px">
      <el-form :model="equipmentForm" label-width="100px">
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
        <el-button @click="showRegisterDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { equipmentService, reservationService } from '@/services/api'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'EquipmentRegister',
  setup() {
    const myEquipment = ref([])
    const allEquipment = ref([])
    const campuses = ref([])
    const loading = ref(false)
    const loadingAll = ref(false)
    const showRegisterDialog = ref(false)
    const submitting = ref(false)
    const editMode = ref(false)
    const filterCampusId = ref(null)
    const filterShared = ref(false)

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

    const loadAllEquipment = async () => {
      loadingAll.value = true
      try {
        const params = {}
        if (filterCampusId.value) {
          params.campus_id = filterCampusId.value
        }
        if (filterShared.value) {
          params.is_shared = true
        }
        allEquipment.value = await equipmentService.getEquipmentList(params)
      } catch (error) {
        console.error('Failed to load all equipment:', error)
      } finally {
        loadingAll.value = false
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
        loadAllEquipment()
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
        loadAllEquipment()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Failed to delete equipment:', error)
        }
      }
    }

    onMounted(() => {
      loadCampuses()
      loadMyEquipment()
      loadAllEquipment()
    })

    return {
      myEquipment,
      allEquipment,
      campuses,
      loading,
      loadingAll,
      showRegisterDialog,
      submitting,
      editMode,
      filterCampusId,
      filterShared,
      equipmentForm,
      handleEdit,
      handleSubmit,
      handleDelete,
      loadAllEquipment
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
  
  .card-header > div {
    flex-wrap: wrap;
  }
  
  :deep(.el-col) {
    width: 100% !important;
    max-width: 100% !important;
  }
  
  :deep(.el-table) {
    font-size: 12px;
  }
  
  :deep(.el-button) {
    padding: 5px 10px;
    font-size: 12px;
  }
  
  :deep(.el-select) {
    width: 100% !important;
  }
}
</style>
