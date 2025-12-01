<template>
  <div class="equipment-borrow">
    <el-row :gutter="isMobile ? 10 : 20">
      <el-col :xs="24" :sm="24" :md="12" style="margin-bottom: 12px;">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>我的借用</span>
              <el-button type="primary" @click="showBorrowDialog = true" :size="isMobile ? 'small' : 'default'">
                <span v-if="isMobile">借用</span>
                <span v-else>登记借用</span>
              </el-button>
            </div>
          </template>

          <!-- 移动端卡片式布局 -->
          <div v-if="isMobile" class="mobile-list" v-loading="loading">
            <div v-if="activeBorrows.length === 0" class="empty-state">
              <el-empty description="暂无借用记录" :image-size="60" />
            </div>
            <div v-else v-for="row in activeBorrows" :key="row.id" class="borrow-card">
              <div class="card-row">
                <div class="label">设备名称</div>
                <div class="value bold">{{ row.equipment_name }} ({{ row.equipment_type }})</div>
              </div>
              <div class="card-row">
                <div class="label">借用时间</div>
                <div class="value small">{{ formatTime(row.borrow_time) }}</div>
              </div>
              <div class="card-row">
                <div class="label">状态</div>
                <div class="value">
                  <el-tag :type="row.status === 'borrowed' ? 'warning' : 'success'" size="small">
                    {{ row.status === 'borrowed' ? '借用中' : '已归还' }}
                  </el-tag>
                </div>
              </div>
              <div class="card-actions" v-if="row.status === 'borrowed'">
                <el-button type="success" size="small" @click="handleReturn(row.id)" style="width: 100%">
                  归还
                </el-button>
              </div>
            </div>
          </div>

          <!-- 桌面端表格布局 -->
          <el-table v-else :data="activeBorrows" style="width: 100%" v-loading="loading">
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

      <el-col :xs="24" :sm="24" :md="12" style="margin-bottom: 12px;">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>当前借用</span>
            </div>
          </template>

          <!-- 移动端卡片式布局 -->
          <div v-if="isMobile" class="mobile-list" v-loading="loadingAll">
            <div v-if="allBorrows.length === 0" class="empty-state">
              <el-empty description="暂无借用记录" :image-size="60" />
            </div>
            <div v-else v-for="row in allBorrows" :key="row.id" class="borrow-card">
              <div class="card-row">
                <div class="label">借用人</div>
                <div class="value bold">{{ row.user_name }} ({{ row.student_id }})</div>
              </div>
              <div class="card-row">
                <div class="label">设备</div>
                <div class="value">{{ row.equipment_name }} ({{ row.equipment_type }})</div>
              </div>
              <div class="card-row">
                <div class="label">物主</div>
                <div class="value">{{ row.owner_name || '-' }}</div>
              </div>
              <div class="card-row">
                <div class="label">借用时间</div>
                <div class="value small">{{ formatTime(row.borrow_time) }}</div>
              </div>
            </div>
          </div>

          <!-- 桌面端表格布局 -->
          <el-table v-else :data="allBorrows" style="width: 100%" v-loading="loadingAll">
            <el-table-column prop="user_name" label="借用人" width="100" />
            <el-table-column prop="student_id" label="学号" width="120" />
            <el-table-column prop="equipment_name" label="设备名称" />
            <el-table-column prop="equipment_type" label="类型" width="100" />
            <el-table-column prop="owner_name" label="物主" width="100">
              <template #default="{ row }">
                {{ row.owner_name || '-' }}
              </template>
            </el-table-column>
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
    <el-dialog 
      v-model="showBorrowDialog" 
      title="登记借用设备" 
      :width="isMobile ? '90%' : '500px'"
      :fullscreen="isMobile"
    >
      <el-form :model="borrowForm" label-width="100px">
        <el-form-item label="设备名称">
          <el-input v-model="borrowForm.equipment_name" placeholder="请输入设备名称" />
        </el-form-item>
        <el-form-item label="设备类型">
          <el-input v-model="borrowForm.equipment_type" placeholder="如：吉他、键盘等" />
        </el-form-item>
        <el-form-item label="物主">
          <el-input v-model="borrowForm.owner_name" placeholder="物主姓名" />
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { equipmentService } from '@/services/api'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'EquipmentBorrow',
  setup() {
    const route = useRoute()
    const myBorrows = ref([])
    const allBorrows = ref([])
    const loading = ref(false)
    const loadingAll = ref(false)
    const showBorrowDialog = ref(false)
    const borrowing = ref(false)
    const isMobile = ref(false)

    // 只显示未归还的借用记录
    const activeBorrows = computed(() => {
      return myBorrows.value.filter(b => b.status === 'borrowed')
    })

    const borrowForm = ref({
      equipment_name: '',
      equipment_type: '',
      owner_name: '',
      notes: ''
    })

    const checkMobile = () => {
      isMobile.value = window.innerWidth <= 768
    }

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
          owner_name: '',
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
      checkMobile()
      window.addEventListener('resize', checkMobile)
      
      // 检查是否有从设备列表传递的参数
      if (route.query.equipment_name) {
        borrowForm.value.equipment_name = route.query.equipment_name
        borrowForm.value.equipment_type = route.query.equipment_type || ''
        borrowForm.value.owner_name = route.query.owner_name || ''
        showBorrowDialog.value = true
      }
      
      loadMyBorrows()
      loadAllBorrows()
    })

    onUnmounted(() => {
      window.removeEventListener('resize', checkMobile)
    })

    return {
      myBorrows,
      activeBorrows,
      allBorrows,
      loading,
      loadingAll,
      showBorrowDialog,
      borrowing,
      borrowForm,
      isMobile,
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

/* 移动端卡片式布局 */
.mobile-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.borrow-card {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.card-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  border-bottom: 1px solid #e4e7ed;
}

.card-row:last-of-type {
  border-bottom: none;
}

.card-row .label {
  font-size: 13px;
  color: #909399;
  font-weight: 500;
  min-width: 70px;
}

.card-row .value {
  font-size: 14px;
  color: #303133;
  text-align: right;
  flex: 1;
}

.card-row .value.bold {
  font-weight: 600;
  color: #409eff;
}

.card-row .value.small {
  font-size: 12px;
}

.card-actions {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e4e7ed;
}

.empty-state {
  padding: 20px 0;
}

/* 桌面端适配 */
@media (min-width: 769px) {
  .card-header {
    font-size: 16px;
  }
}

/* 移动端适配 */
@media (max-width: 768px) {
  .card-header {
    font-size: 16px;
  }
  
  /* 隐藏桌面端表格 */
  :deep(.el-table) {
    display: none;
  }
}
</style>
