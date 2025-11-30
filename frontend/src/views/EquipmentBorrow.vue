<template>
  <div class="equipment-borrow">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>借用设备</span>
              <el-button type="primary" @click="showBorrowDialog = true">登记借用</el-button>
            </div>
          </template>

          <el-table :data="myBorrows" style="width: 100%" v-loading="loading">
            <el-table-column prop="equipment_name" label="设备名称" />
            <el-table-column prop="equipment_type" label="设备类型" width="100" />
            <el-table-column prop="borrow_time" label="借用时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.borrow_time) }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'borrowed' ? 'warning' : 'success'">
                  {{ row.status === 'borrowed' ? '借用中' : '已归还' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button
                  v-if="row.status === 'borrowed'"
                  type="success"
                  size="small"
                  @click="handleReturn(row.id)"
                >
                  归还
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>当前借用情况</span>
            </div>
          </template>

          <el-table :data="allBorrows" style="width: 100%" v-loading="loadingAll">
            <el-table-column prop="user_name" label="借用人" width="100" />
            <el-table-column prop="student_id" label="学号" width="120" />
            <el-table-column prop="equipment_name" label="设备名称" />
            <el-table-column prop="equipment_type" label="类型" width="100" />
            <el-table-column prop="borrow_time" label="借用时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.borrow_time) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 借用对话框 -->
    <el-dialog v-model="showBorrowDialog" title="登记借用设备" width="500px">
      <el-form :model="borrowForm" label-width="100px">
        <el-form-item label="设备名称">
          <el-input v-model="borrowForm.equipment_name" placeholder="请输入设备名称" />
        </el-form-item>
        <el-form-item label="设备类型">
          <el-input v-model="borrowForm.equipment_type" placeholder="如：吉他、键盘、鼓等" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="borrowForm.notes"
            type="textarea"
            :rows="3"
            placeholder="可选"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showBorrowDialog = false">取消</el-button>
        <el-button type="primary" @click="handleBorrow" :loading="borrowing">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { equipmentService } from '@/services/api'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'EquipmentBorrow',
  setup() {
    const myBorrows = ref([])
    const allBorrows = ref([])
    const loading = ref(false)
    const loadingAll = ref(false)
    const showBorrowDialog = ref(false)
    const borrowing = ref(false)

    const borrowForm = ref({
      equipment_name: '',
      equipment_type: '',
      notes: ''
    })

    const formatTime = (timeStr) => {
      return new Date(timeStr).toLocaleString('zh-CN')
    }

    const loadMyBorrows = async () => {
      loading.value = true
      try {
        myBorrows.value = await equipmentService.getMyBorrows()
      } catch (error) {
        console.error('Failed to load my borrows:', error)
      } finally {
        loading.value = false
      }
    }

    const loadAllBorrows = async () => {
      loadingAll.value = true
      try {
        allBorrows.value = await equipmentService.getBorrows('borrowed')
      } catch (error) {
        console.error('Failed to load all borrows:', error)
      } finally {
        loadingAll.value = false
      }
    }

    const handleBorrow = async () => {
      if (!borrowForm.value.equipment_name) {
        ElMessage.warning('请输入设备名称')
        return
      }

      borrowing.value = true
      try {
        await equipmentService.borrowEquipment(borrowForm.value)
        ElMessage.success('登记成功')
        showBorrowDialog.value = false
        borrowForm.value = {
          equipment_name: '',
          equipment_type: '',
          notes: ''
        }
        loadMyBorrows()
        loadAllBorrows()
      } catch (error) {
        console.error('Failed to borrow equipment:', error)
      } finally {
        borrowing.value = false
      }
    }

    const handleReturn = async (borrowId) => {
      try {
        await ElMessageBox.confirm('确认归还此设备？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'info'
        })

        await equipmentService.returnEquipment(borrowId)
        ElMessage.success('归还成功')
        loadMyBorrows()
        loadAllBorrows()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Failed to return equipment:', error)
        }
      }
    }

    onMounted(() => {
      loadMyBorrows()
      loadAllBorrows()
    })

    return {
      myBorrows,
      allBorrows,
      loading,
      loadingAll,
      showBorrowDialog,
      borrowing,
      borrowForm,
      formatTime,
      handleBorrow,
      handleReturn
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
}
</style>
