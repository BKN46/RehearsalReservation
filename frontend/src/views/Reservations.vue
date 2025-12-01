<template>
  <div class="reservations">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>我的预约</span>
          <el-button type="primary" @click="$router.push('/')" :size="isMobile ? 'small' : 'default'">
            <span v-if="isMobile">预约</span>
            <span v-else>预约</span>
          </el-button>
        </div>
      </template>

      <!-- Tab切换 -->
      <el-tabs v-model="activeTab" class="reservation-tabs">
        <!-- 当前预约 -->
        <el-tab-pane label="当前预约" name="current">
          <!-- 移动端卡片式布局 -->
          <div v-if="isMobile" class="mobile-list" v-loading="loading">
            <div v-if="currentReservations.length === 0" class="empty-state">
              <el-empty description="暂无当前预约" />
            </div>
            <div v-else v-for="row in currentReservations" :key="row.id" class="reservation-card">
          <div class="card-row">
            <div class="label">校区</div>
            <div class="value">{{ row.campus_name }}</div>
          </div>
          <div class="card-row">
            <div class="label">日期</div>
            <div class="value">{{ row.date }}</div>
          </div>
          <div class="card-row">
            <div class="label">时间</div>
            <div class="value">{{ row.start_hour }}:00 - {{ row.end_hour }}:00</div>
          </div>
          <div class="card-row">
            <div class="label">状态</div>
            <div class="value">
              <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
                {{ row.status === 'active' ? '有效' : '已取消' }}
              </el-tag>
            </div>
          </div>
          <div class="card-row">
            <div class="label">钥匙</div>
            <div class="value">
              <el-tag v-if="row.key_returned" type="info" size="small">已归还</el-tag>
              <el-tag v-else-if="row.key_picked_up" type="success" size="small">已领取</el-tag>
              <el-tag v-else type="warning" size="small">未领取</el-tag>
            </div>
          </div>
          <div class="card-row">
            <div class="label">预约时间</div>
            <div class="value small">{{ formatTime(row.created_at) }}</div>
          </div>
          <div class="card-actions">
            <el-button
              v-if="!row.key_picked_up && row.status === 'active'"
              type="success"
              size="small"
              @click="handlePickupKey(row.id)"
            >
              登记取钥匙
            </el-button>
            <el-button
              v-if="row.key_picked_up && !row.key_returned && row.status === 'active'"
              type="primary"
              size="small"
              @click="handleReturnKey(row.id)"
            >
              归还钥匙
            </el-button>
            <el-button
              v-if="row.status === 'active' && !row.key_returned"
              type="danger"
              size="small"
              @click="handleCancel(row.id)"
            >
              取消预约
            </el-button>
          </div>
        </div>
      </div>

      <!-- 桌面端表格布局 -->
      <el-table v-else :data="currentReservations" style="width: 100%" v-loading="loading">
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
            <el-tag v-if="row.key_returned" type="info">已归还</el-tag>
            <el-tag v-else-if="row.key_picked_up" type="success">已领取</el-tag>
            <el-tag v-else type="warning">未领取</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="预约时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250">
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
              v-if="row.key_picked_up && !row.key_returned && row.status === 'active'"
              type="primary"
              size="small"
              @click="handleReturnKey(row.id)"
            >
              归还钥匙
            </el-button>
            <el-button
              v-if="row.status === 'active' && !row.key_returned"
              type="danger"
              size="small"
              @click="handleCancel(row.id)"
            >
              取消预约
            </el-button>
          </template>
        </el-table-column>
      </el-table>
        </el-tab-pane>

        <!-- 历史预约 -->
        <el-tab-pane label="历史预约" name="history">
          <!-- 移动端卡片式布局 -->
          <div v-if="isMobile" class="mobile-list" v-loading="loading">
            <div v-if="historyReservations.length === 0" class="empty-state">
              <el-empty description="暂无历史预约" />
            </div>
            <div v-else v-for="row in historyReservations" :key="row.id" class="reservation-card history">
              <div class="card-row">
                <div class="label">校区</div>
                <div class="value">{{ row.campus_name }}</div>
              </div>
              <div class="card-row">
                <div class="label">日期</div>
                <div class="value">{{ row.date }}</div>
              </div>
              <div class="card-row">
                <div class="label">时间</div>
                <div class="value">{{ row.start_hour }}:00 - {{ row.end_hour }}:00</div>
              </div>
              <div class="card-row">
                <div class="label">状态</div>
                <div class="value">
                  <el-tag v-if="row.status === 'cancelled'" type="info" size="small">已取消</el-tag>
                  <el-tag v-else-if="row.key_returned" type="success" size="small">已完成</el-tag>
                  <el-tag v-else type="warning" size="small">未完成</el-tag>
                </div>
              </div>
            </div>
          </div>

          <!-- 桌面端表格布局 -->
          <el-table v-else :data="historyReservations" style="width: 100%" v-loading="loading">
            <el-table-column prop="campus_name" label="校区" width="120" />
            <el-table-column prop="date" label="日期" width="120" />
            <el-table-column label="时间" width="180">
              <template #default="{ row }">
                {{ row.start_hour }}:00 - {{ row.end_hour }}:00
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="120">
              <template #default="{ row }">
                <el-tag v-if="row.status === 'cancelled'" type="info">已取消</el-tag>
                <el-tag v-else-if="row.key_returned" type="success">已完成</el-tag>
                <el-tag v-else type="warning">未完成</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="预约时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { reservationService, keyService } from '@/services/api'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'Reservations',
  setup() {
    const reservations = ref([])
    const loading = ref(false)
    const isMobile = ref(false)
    const activeTab = ref('current')

    const checkMobile = () => {
      isMobile.value = window.innerWidth <= 768
    }

    // 当前预约：状态为active且未归还钥匙
    const currentReservations = computed(() => {
      return reservations.value.filter(r => r.status === 'active' && !r.key_returned)
    })

    // 历史预约：已取消或已归还钥匙
    const historyReservations = computed(() => {
      return reservations.value.filter(r => 
        r.status === 'cancelled' || r.key_returned
      )
    })

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

    const handleReturnKey = async (reservationId) => {
      try {
        await ElMessageBox.confirm('确认已归还钥匙？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'info'
        })

        await keyService.returnKey(reservationId)
        ElMessage.success('归还成功')
        loadReservations()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Failed to return key:', error)
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
      checkMobile()
      window.addEventListener('resize', checkMobile)
      loadReservations()
    })

    onUnmounted(() => {
      window.removeEventListener('resize', checkMobile)
    })

    return {
      reservations,
      activeTab,
      currentReservations,
      historyReservations,
      loading,
      isMobile,
      formatTime,
      handlePickupKey,
      handleReturnKey,
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

/* Tab样式 */
.reservation-tabs {
  margin-top: -10px;
}

.reservation-tabs :deep(.el-tabs__header) {
  margin-bottom: 15px;
}

/* 移动端卡片式布局 */
.mobile-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.reservation-card {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* 历史预约卡片样式 */
.reservation-card.history {
  background: #fafafa;
  opacity: 0.9;
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

.card-row .value.small {
  font-size: 12px;
}

.card-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e4e7ed;
}

.card-actions .el-button {
  flex: 1;
}

.empty-state {
  padding: 40px 0;
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
