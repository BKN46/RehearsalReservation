<template>
  <div class="reservations">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>我的预约</span>
          <el-button type="primary" @click="$router.push('/')">新建预约</el-button>
        </div>
      </template>

      <el-table :data="reservations" style="width: 100%" v-loading="loading">
        <el-table-column prop="campus_name" label="校区" width="120" />
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column label="时间" width="180">
          <template #default="{ row }">
            {{ row.start_hour }}:00 - {{ row.end_hour }}:00
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '有效' : '已取消' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="key_picked_up" label="钥匙状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.key_picked_up ? 'success' : 'warning'">
              {{ row.key_picked_up ? '已领取' : '未领取' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="预约时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button
              v-if="!row.key_picked_up && row.status === 'active'"
              type="success"
              size="small"
              @click="handlePickupKey(row.id)"
            >
              登记取钥匙
            </el-button>
            <el-button
              v-if="row.status === 'active'"
              type="danger"
              size="small"
              @click="handleCancel(row.id)"
            >
              取消预约
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { reservationService, keyService } from '@/services/api'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'Reservations',
  setup() {
    const reservations = ref([])
    const loading = ref(false)

    const formatTime = (timeStr) => {
      return new Date(timeStr).toLocaleString('zh-CN')
    }

    const loadReservations = async () => {
      loading.value = true
      try {
        reservations.value = await reservationService.getMyReservations()
      } catch (error) {
        console.error('Failed to load reservations:', error)
      } finally {
        loading.value = false
      }
    }

    const handlePickupKey = async (reservationId) => {
      try {
        await ElMessageBox.confirm('确认已领取钥匙？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'info'
        })

        await keyService.pickupKey(reservationId)
        ElMessage.success('登记成功')
        loadReservations()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Failed to pickup key:', error)
        }
      }
    }

    const handleCancel = async (reservationId) => {
      try {
        await ElMessageBox.confirm('确定要取消这个预约吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        await reservationService.cancelReservation(reservationId)
        ElMessage.success('预约已取消')
        loadReservations()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Failed to cancel reservation:', error)
        }
      }
    }

    onMounted(() => {
      loadReservations()
    })

    return {
      reservations,
      loading,
      formatTime,
      handlePickupKey,
      handleCancel
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
  
  /* 表格紧凑显示 */
  :deep(.el-table) {
    font-size: 12px;
  }
  
  :deep(.el-button) {
    padding: 5px 10px;
    font-size: 12px;
  }
}
</style>
