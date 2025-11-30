<template>
  <div class="home">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>校区选择</span>
            </div>
          </template>
          <el-radio-group v-model="selectedCampusId" @change="handleCampusChange">
            <el-radio-button v-for="campus in campuses" :key="campus.id" :label="campus.id">
              {{ campus.name }}
            </el-radio-button>
          </el-radio-group>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>本周预约情况（{{ weekRange }}）</span>
              <el-button type="primary" @click="showReserveDialog = true">新建预约</el-button>
            </div>
          </template>
          <el-table :data="weeklyReservations" style="width: 100%" v-loading="loading">
            <el-table-column prop="date" label="日期" width="120" />
            <el-table-column prop="start_hour" label="开始时间" width="100">
              <template #default="{ row }">
                {{ row.start_hour }}:00
              </template>
            </el-table-column>
            <el-table-column prop="end_hour" label="结束时间" width="100">
              <template #default="{ row }">
                {{ row.end_hour }}:00
              </template>
            </el-table-column>
            <el-table-column prop="user_name" label="预约人" />
            <el-table-column prop="student_id" label="学号" />
            <el-table-column prop="key_picked_up" label="钥匙状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.key_picked_up ? 'success' : 'info'">
                  {{ row.key_picked_up ? '已领取' : '未领取' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card style="margin-bottom: 20px">
          <template #header>
            <div class="card-header">
              <span>当前钥匙管理员</span>
            </div>
          </template>
          <div v-if="keyManagers.length > 0">
            <div v-for="manager in keyManagers" :key="manager.id" class="manager-item">
              <p><strong>{{ manager.name }}</strong></p>
              <p>联系方式：{{ manager.contact }}</p>
            </div>
          </div>
          <el-empty v-else description="暂无钥匙管理员" :image-size="60" />
        </el-card>

        <el-card>
          <template #header>
            <div class="card-header">
              <span>近期钥匙领取</span>
            </div>
          </template>
          <el-timeline v-if="keyPickups.length > 0">
            <el-timeline-item
              v-for="pickup in keyPickups.slice(0, 5)"
              :key="pickup.id"
              :timestamp="formatTime(pickup.key_pickup_time)"
            >
              {{ pickup.user_name }} - {{ pickup.date }} {{ pickup.start_hour }}:00-{{ pickup.end_hour }}:00
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else description="暂无领取记录" :image-size="60" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 新建预约对话框 -->
    <el-dialog v-model="showReserveDialog" title="新建预约" width="500px">
      <el-form :model="reserveForm" label-width="100px">
        <el-form-item label="日期">
          <el-date-picker
            v-model="reserveForm.date"
            type="date"
            placeholder="选择日期"
            :disabled-date="disabledDate"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="时间段">
          <el-select v-model="reserveForm.timeSlot" placeholder="请选择时间段" style="width: 100%">
            <el-option label="上午 8:00-12:00" value="morning" />
            <el-option label="下午 13:00-18:00" value="afternoon" />
            <el-option label="晚上 19:00-22:00" value="evening" />
          </el-select>
        </el-form-item>
        <el-form-item label="自定义时间">
          <el-row :gutter="10">
            <el-col :span="12">
              <el-input-number v-model="reserveForm.start_hour" :min="8" :max="21" placeholder="开始" />
            </el-col>
            <el-col :span="12">
              <el-input-number v-model="reserveForm.end_hour" :min="9" :max="22" placeholder="结束" />
            </el-col>
          </el-row>
          <small style="color: #999">可预约时间：8:00-12:00, 13:00-18:00, 19:00-22:00</small>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showReserveDialog = false">取消</el-button>
        <el-button type="primary" @click="handleReserve" :loading="reserving">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { reservationService, keyService } from '@/services/api'
import { ElMessage } from 'element-plus'

export default {
  name: 'Home',
  setup() {
    const campuses = ref([])
    const selectedCampusId = ref(null)
    const weeklyReservations = ref([])
    const keyManagers = ref([])
    const keyPickups = ref([])
    const loading = ref(false)
    const showReserveDialog = ref(false)
    const reserving = ref(false)
    const weekRange = ref('')

    const reserveForm = ref({
      date: null,
      timeSlot: '',
      start_hour: 8,
      end_hour: 12
    })

    const timeSlots = {
      morning: { start: 8, end: 12 },
      afternoon: { start: 13, end: 18 },
      evening: { start: 19, end: 22 }
    }

    const disabledDate = (time) => {
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      const oneWeekLater = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000)
      return time.getTime() < today.getTime() || time.getTime() > oneWeekLater.getTime()
    }

    const formatTime = (timeStr) => {
      return new Date(timeStr).toLocaleString('zh-CN')
    }

    const loadCampuses = async () => {
      try {
        campuses.value = await reservationService.getCampuses()
        if (campuses.value.length > 0) {
          selectedCampusId.value = campuses.value[0].id
          handleCampusChange(selectedCampusId.value)
        }
      } catch (error) {
        console.error('Failed to load campuses:', error)
      }
    }

    const loadWeeklyReservations = async () => {
      if (!selectedCampusId.value) return
      
      loading.value = true
      try {
        const data = await reservationService.getWeeklyReservations(selectedCampusId.value)
        weeklyReservations.value = data.reservations
        weekRange.value = `${data.start_date} 至 ${data.end_date}`
      } catch (error) {
        console.error('Failed to load reservations:', error)
      } finally {
        loading.value = false
      }
    }

    const loadKeyManagers = async () => {
      if (!selectedCampusId.value) return
      
      try {
        keyManagers.value = await keyService.getKeyManagers(selectedCampusId.value)
      } catch (error) {
        console.error('Failed to load key managers:', error)
      }
    }

    const loadKeyPickups = async () => {
      if (!selectedCampusId.value) return
      
      try {
        keyPickups.value = await keyService.getKeyPickups(selectedCampusId.value)
      } catch (error) {
        console.error('Failed to load key pickups:', error)
      }
    }

    const handleCampusChange = (campusId) => {
      loadWeeklyReservations()
      loadKeyManagers()
      loadKeyPickups()
    }

    const handleReserve = async () => {
      if (!reserveForm.value.date) {
        ElMessage.warning('请选择日期')
        return
      }

      let startHour = reserveForm.value.start_hour
      let endHour = reserveForm.value.end_hour

      if (reserveForm.value.timeSlot) {
        const slot = timeSlots[reserveForm.value.timeSlot]
        startHour = slot.start
        endHour = slot.end
      }

      if (startHour >= endHour) {
        ElMessage.warning('结束时间必须大于开始时间')
        return
      }

      reserving.value = true
      try {
        const date = new Date(reserveForm.value.date)
        const dateStr = date.toISOString().split('T')[0]

        await reservationService.createReservation({
          campus_id: selectedCampusId.value,
          date: dateStr,
          start_hour: startHour,
          end_hour: endHour
        })

        ElMessage.success('预约成功')
        showReserveDialog.value = false
        reserveForm.value = {
          date: null,
          timeSlot: '',
          start_hour: 8,
          end_hour: 12
        }
        loadWeeklyReservations()
      } catch (error) {
        console.error('Reservation failed:', error)
      } finally {
        reserving.value = false
      }
    }

    onMounted(() => {
      loadCampuses()
    })

    return {
      campuses,
      selectedCampusId,
      weeklyReservations,
      keyManagers,
      keyPickups,
      loading,
      showReserveDialog,
      reserving,
      reserveForm,
      weekRange,
      disabledDate,
      formatTime,
      handleCampusChange,
      handleReserve
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

.manager-item {
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.manager-item:last-child {
  border-bottom: none;
}

.manager-item p {
  margin: 5px 0;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .card-header {
    font-size: 16px;
  }
  
  .card-header span {
    flex: 1 1 100%;
    margin-bottom: 5px;
  }
  
  /* 隐藏表格的某些列 */
  :deep(.el-table__header-wrapper) .el-table__cell:nth-child(5),
  :deep(.el-table__body-wrapper) .el-table__cell:nth-child(5) {
    display: none;
  }
}
</style>
