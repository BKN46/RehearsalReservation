<template>
  <div class="home">
    <!-- 校区选择器 -->
    <CampusSelector
      :campuses="campuses"
      v-model:selectedCampusId="selectedCampusId"
      :isMobile="isMobile"
      @change="handleCampusChange"
    />

    <el-row :gutter="isMobile ? 10 : 20" style="margin-top: 12px">
      <el-col :xs="24" :sm="24" :md="16" :lg="16">
        <el-card class="schedule-card">
          <template #header>
            <div class="card-header">
              <div>
                <span>本周预约（{{ weekRange }}）</span>
                <div class="weekly-quota" v-if="userWeeklyHours !== null">
                  <el-tag :type="weeklyQuotaType" size="small">
                    本周已用 {{ userWeeklyHours }} 小时 / 剩余 {{ 6 - userWeeklyHours }} 小时
                  </el-tag>
                </div>
              </div>
              <el-button type="primary" @click="showReminderDialog = true" :size="isMobile ? 'small' : 'default'">
                <span v-if="isMobile">预约</span>
                <span v-else>预约</span>
              </el-button>
            </div>
          </template>
          
          <!-- 周计划表 -->
          <WeeklySchedule
            :weekDays="weekDays"
            :timeSlots="timeSlots"
            :weeklyReservations="weeklyReservations"
            :unavailableTimes="unavailableTimes"
            :loading="loading"
            :weekRange="weekRange"
            :isMobile="isMobile"
            @reservation-click="showReservationDetail"
          />
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="24" :md="8" :lg="8" class="sidebar-col">
        <!-- 钥匙管理员 -->
        <KeyManagers :keyManagers="keyManagers" style="margin-bottom: 12px" />
        
        <!-- 已领取钥匙 -->
        <KeyPickups :activeKeyPickups="activeKeyPickups" />
      </el-col>
    </el-row>

    <!-- 预约对话框 -->
    <ReservationDialog
      v-model:showReminderDialog="showReminderDialog"
      v-model:showReserveDialog="showReserveDialog"
      :isMobile="isMobile"
      :userWeeklyHours="userWeeklyHours"
      :dailyReservations="dailyReservations"
      :dailyUnavailableTimes="dailyUnavailableTimes"
      :reserving="reserving"
      @acknowledge="handleAcknowledgeReminder"
      @reserve="handleReserveSubmit"
      @close="showReserveDialog = false"
      @date-change="loadDailySchedule"
    />
  </div>
</template>

<script>
import { ref, onMounted, computed, onUnmounted, watch } from 'vue'
import { reservationService, keyService, adminService } from '@/services/api'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import CampusSelector from '@/components/home/CampusSelector.vue'
import WeeklySchedule from '@/components/home/WeeklySchedule.vue'
import KeyManagers from '@/components/home/KeyManagers.vue'
import KeyPickups from '@/components/home/KeyPickups.vue'
import ReservationDialog from '@/components/home/ReservationDialog.vue'

export default {
  name: 'Home',
  components: {
    CampusSelector,
    WeeklySchedule,
    KeyManagers,
    KeyPickups,
    ReservationDialog
  },
  setup() {
    const authStore = useAuthStore()
    const campuses = ref([])
    const selectedCampusId = ref(null)
    const weeklyReservations = ref([])
    const unavailableTimes = ref([])
    const myReservations = ref([])
    const keyManagers = ref([])
    const keyPickups = ref([])
    const loading = ref(false)
    const showReminderDialog = ref(false)
    const showReserveDialog = ref(false)
    const reserving = ref(false)
    const weekRange = ref('')
    const isMobile = ref(false)
    const userWeeklyHours = ref(null)

    // 当天的预约和不可预约时间（用于预约对话框）
    const dailyReservations = ref([])
    const dailyUnavailableTimes = ref([])

    const timeSlots = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]

    // 检测屏幕尺寸
    const checkMobile = () => {
      isMobile.value = window.innerWidth <= 768
    }

    // 计算本周的日期（周日22:00后显示下周）
    const weekDays = computed(() => {
      const days = []
      const now = new Date()
      const currentHour = now.getHours()
      const dayOfWeek = now.getDay() // 0=周日, 1=周一, ..., 6=周六
      
      // 如果是周日22:00之后，显示下周
      let baseDate = new Date(now)
      if (dayOfWeek === 0 && currentHour >= 22) {
        // 周日22:00后，跳到下周一
        baseDate.setDate(now.getDate() + 1)
      }
      
      // 计算周一的日期
      const adjustedDayOfWeek = baseDate.getDay() || 7 // 将周日(0)转为7
      const monday = new Date(baseDate)
      monday.setDate(baseDate.getDate() - adjustedDayOfWeek + 1)

      const dayNames = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
      
      for (let i = 0; i < 7; i++) {
        const date = new Date(monday)
        date.setDate(monday.getDate() + i)
        // 使用本地时区格式化日期，避免UTC偏差
        const year = date.getFullYear()
        const month = String(date.getMonth() + 1).padStart(2, '0')
        const day = String(date.getDate()).padStart(2, '0')
        const dateStr = `${year}-${month}-${day}`
        
        days.push({
          date: dateStr,
          dayName: dayNames[i],
          dateText: `${date.getMonth() + 1}/${date.getDate()}`
        })
      }
      return days
    })

    // 计算本周配额类型（用于标签颜色）
    const weeklyQuotaType = computed(() => {
      if (userWeeklyHours.value === null) return 'info'
      if (userWeeklyHours.value >= 6) return 'danger'
      if (userWeeklyHours.value >= 4) return 'warning'
      return 'success'
    })

    // 过滤已领取但未归还的钥匙
    const activeKeyPickups = computed(() => {
      return keyPickups.value.filter(pickup => 
        pickup.key_picked_up && !pickup.key_returned
      )
    })

    // 显示预约详情
    const showReservationDetail = (reservation) => {
      let keyStatus = '✗ 未领取钥匙'
      if (reservation.key_returned) {
        keyStatus = '✓ 已归还钥匙'
      } else if (reservation.key_picked_up) {
        keyStatus = '✓ 已领取钥匙'
      }
      
      ElMessage.info({
        message: `${reservation.user_name} (${reservation.student_id})\n${reservation.start_hour}:00-${reservation.end_hour}:00\n${keyStatus}`,
        duration: 3000
      })
    }

    const loadCampuses = async () => {
      try {
        campuses.value = await reservationService.getCampuses()
        if (campuses.value.length > 0) {
          // 优先使用用户设置的默认校区
          const preferredCampusId = authStore.user?.preferred_campus_id
          if (preferredCampusId && campuses.value.find(c => c.id === preferredCampusId)) {
            selectedCampusId.value = preferredCampusId
          } else {
            selectedCampusId.value = campuses.value[0].id
          }
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
        weekRange.value = `${data.start_date} ~ ${data.end_date}`
      } catch (error) {
        console.error('Failed to load reservations:', error)
      } finally {
        loading.value = false
      }
    }

    const loadUnavailableTimes = async () => {
      if (!selectedCampusId.value) return
      
      try {
        const data = await adminService.getUnavailableTimes(selectedCampusId.value)
        unavailableTimes.value = data
      } catch (error) {
        console.error('Failed to load unavailable times:', error)
      }
    }

    const loadMyWeeklyHours = async () => {
      // 只有登录用户才加载
      if (!authStore.isAuthenticated) {
        userWeeklyHours.value = null
        return
      }
      
      try {
        const reservations = await reservationService.getMyReservations()
        
        // 计算本周的日期范围（与weekDays计算逻辑一致）
        const now = new Date()
        const currentHour = now.getHours()
        const dayOfWeek = now.getDay()
        
        let baseDate = new Date(now)
        if (dayOfWeek === 0 && currentHour >= 22) {
          baseDate.setDate(now.getDate() + 1)
        }
        
        const adjustedDayOfWeek = baseDate.getDay() || 7
        const monday = new Date(baseDate)
        monday.setDate(baseDate.getDate() - adjustedDayOfWeek + 1)
        monday.setHours(0, 0, 0, 0)
        
        const sunday = new Date(monday)
        sunday.setDate(monday.getDate() + 6)
        sunday.setHours(23, 59, 59, 999)
        
        // 筛选本周的预约并计算总时长
        const weeklyReservations = reservations.filter(r => {
          const reservationDate = new Date(r.date)
          return reservationDate >= monday && reservationDate <= sunday && r.status === 'active'
        })
        
        const totalHours = weeklyReservations.reduce((sum, r) => {
          return sum + (r.end_hour - r.start_hour)
        }, 0)
        
        userWeeklyHours.value = totalHours
      } catch (error) {
        console.error('Failed to load my weekly hours:', error)
        userWeeklyHours.value = null
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
      loadUnavailableTimes()
      loadKeyManagers()
      loadKeyPickups()
      loadMyWeeklyHours()
    }

    const handleAcknowledgeReminder = () => {
      showReminderDialog.value = false
      showReserveDialog.value = true
    }

    const loadDailySchedule = async (date) => {
      if (!date || !selectedCampusId.value) return

      try {
        const targetDate = new Date(date)
        const year = targetDate.getFullYear()
        const month = String(targetDate.getMonth() + 1).padStart(2, '0')
        const day = String(targetDate.getDate()).padStart(2, '0')
        const dateStr = `${year}-${month}-${day}`

        // 加载当天的预约
        const reservations = await reservationService.getReservationsByDate(selectedCampusId.value, dateStr)
        dailyReservations.value = reservations.filter(r => r.status === 'active')

        // 过滤出当天的不可预约时间
        const dayOfWeek = targetDate.getDay()
        dailyUnavailableTimes.value = unavailableTimes.value.filter(ut => {
          if (ut.date === dateStr) return true
          if (!ut.date) {
            // 如果day_of_week为空，表示每天都不可预约
            if (ut.day_of_week === null || ut.day_of_week === undefined) return true
            // 否则检查是否匹配当天
            return Number(ut.day_of_week) === dayOfWeek
          }
          return false
        })
      } catch (error) {
        console.error('Failed to load daily schedule:', error)
      }
    }

    const handleReserveSubmit = async (formData) => {
      if (!formData.date) {
        ElMessage.warning('请选择日期')
        return
      }

      let startHour = formData.start_hour
      let endHour = formData.end_hour

      if (startHour === null || endHour === null) {
        ElMessage.warning('请选择时间段')
        return
      }

      if (startHour >= endHour) {
        ElMessage.warning('结束时间必须大于开始时间')
        return
      }

      reserving.value = true
      try {
        const date = new Date(formData.date)
        // 使用本地时区格式化日期，避免UTC偏差
        const year = date.getFullYear()
        const month = String(date.getMonth() + 1).padStart(2, '0')
        const day = String(date.getDate()).padStart(2, '0')
        const dateStr = `${year}-${month}-${day}`

        await reservationService.createReservation({
          campus_id: selectedCampusId.value,
          date: dateStr,
          start_hour: startHour,
          end_hour: endHour
        })

        ElMessage.success('预约成功')
        showReserveDialog.value = false
        dailyReservations.value = []
        dailyUnavailableTimes.value = []
        loadWeeklyReservations()
        loadMyWeeklyHours()  // 重新加载本周预约统计
      } catch (error) {
        console.error('Reservation failed:', error)
      } finally {
        reserving.value = false
      }
    }

    onMounted(() => {
      checkMobile()
      window.addEventListener('resize', checkMobile)
      loadCampuses()
      loadMyWeeklyHours()  // 加载用户本周预约统计
    })

    onUnmounted(() => {
      window.removeEventListener('resize', checkMobile)
    })

    return {
      // 数据
      campuses,
      selectedCampusId,
      weeklyReservations,
      unavailableTimes,
      keyManagers,
      keyPickups,
      loading,
      showReminderDialog,
      showReserveDialog,
      reserving,
      dailyReservations,
      dailyUnavailableTimes,
      weekRange,
      timeSlots,
      weekDays,
      isMobile,
      userWeeklyHours,
      
      // 计算属性
      weeklyQuotaType,
      activeKeyPickups,
      
      // 方法
      handleCampusChange,
      handleAcknowledgeReminder,
      loadDailySchedule,
      handleReserveSubmit,
      showReservationDetail
    }
  }
}
</script>

<style scoped>
/* 移动优先设计 */
.home {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
}

.card-header > div {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.weekly-quota {
  font-size: 12px;
  font-weight: normal;
}

.manager-item {
  padding: 8px 0;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.manager-item:last-child {
  border-bottom: none;
}

.manager-item strong {
  font-size: 14px;
  color: #303133;
}

.manager-contact {
  font-size: 13px;
  color: #606266;
  white-space: nowrap;
}

.manager-item p {
  margin: 5px 0;
  font-size: 14px;
}

/* 侧边栏在移动端的间距 */
.sidebar-col {
  margin-top: 12px;
}

/* 校区卡片 */
.campus-card :deep(.el-radio-group) {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.schedule-container {
  width: 100%;
  font-size: 10px;
  position: relative;
}

/* 表头 */
.schedule-header {
  display: flex;
  background-color: #f5f7fa;
  position: sticky;
  top: 0;
  z-index: 10;
}

.header-corner {
  width: 35px;
  flex-shrink: 0;
  border-right: 1px solid #dcdfe6;
}

.header-days {
  display: flex;
  flex: 1;
}

.header-day {
  flex: 1;
  padding: 6px 2px;
  text-align: center;
  border-right: 1px solid #dcdfe6;
  min-width: 0;
}

.header-day:last-child {
  border-right: none;
}

.day-name {
  font-weight: 600;
  font-size: 11px;
  color: #303133;
  white-space: nowrap;
}

.day-date {
  font-size: 9px;
  color: #909399;
  margin-top: 2px;
}

/* 时间表主体 */
.schedule-body {
  position: relative;
  padding-top: 10px; /* 为第一个时间标签留空间 */
}

.time-row {
  position: relative;
  display: flex;
}

/* 第一个时间标签 - 在表格顶部 */
.first-time-label {
  position: absolute;
  left: 0;
  top: 0;
  width: 35px;
  background-color: #f5f7fa;
  color: #606266;
  font-size: 9px;
  text-align: center;
  font-weight: 500;
  padding: 2px 0;
  z-index: 5;
  border-radius: 3px;
}

/* 时间标签 - 放在边框上 */
.time-label {
  position: absolute;
  left: 0;
  top: -8px;
  width: 35px;
  background-color: #f5f7fa;
  color: #606266;
  font-size: 9px;
  text-align: center;
  font-weight: 500;
  padding: 2px 0;
  z-index: 5;
  border-radius: 3px;
}

/* 最后一个时间标签 - 在表格底部 */
.last-time-label {
  position: relative;
  left: 0;
  width: 35px;
  background-color: #f5f7fa;
  color: #606266;
  font-size: 9px;
  text-align: center;
  font-weight: 500;
  padding: 2px 0;
  margin-top: -8px;
  z-index: 5;
  border-radius: 3px;
}

/* 行单元格容器 */
.row-cells {
  display: flex;
  width: 100%;
  padding-left: 35px;
  border-top: 1px solid #e4e7ed;
}

.unavailable-block {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: help;
  z-index: 1;
}

.unavailable-content {
  text-align: center;
  color: #f56c6c;
  font-size: 10px;
  padding: 2px;
}

.unavailable-icon {
  font-size: 14px;
  margin-bottom: 2px;
}

.unavailable-reason {
  font-size: 9px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

/* 预约块 */
.reservation-block {
  color: white;
  border-radius: 3px;
  font-size: 9px;
  overflow: hidden;
  cursor: pointer;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.reservation-block:active {
  transform: scale(0.98);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15);
}

.reservation-content {
  text-align: center;
  padding: 2px;
  width: 100%;
}

.user-name {
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 9px;
  line-height: 1.2;
}

.time-info {
  font-size: 8px;
  opacity: 0.9;
  margin-top: 1px;
  white-space: nowrap;
}

/* 平板适配 */
@media (min-width: 769px) {
  .card-header {
    font-size: 16px;
  }
  
  .sidebar-col {
    margin-top: 0;
  }
  
  .schedule-container {
    font-size: 12px;
  }
  
  .schedule-body {
    padding-top: 12px;
  }
  
  .header-corner {
    width: 50px;
  }
  
  .header-day {
    padding: 8px 4px;
  }
  
  .day-name {
    font-size: 13px;
  }
  
  .day-date {
    font-size: 11px;
  }
  
  .first-time-label,
  .time-label,
  .last-time-label {
    width: 50px;
    font-size: 11px;
  }
  
  .time-label {
    top: -9px;
  }
  
  .last-time-label {
    margin-top: -9px;
  }
  
  .row-cells {
    padding-left: 50px;
  }
  
  .reservation-block {
    font-size: 11px;
  }
  
  .user-name {
    font-size: 11px;
  }
  
  .time-info {
    font-size: 9px;
  }
  
  .unavailable-icon {
    font-size: 16px;
  }
  
  .unavailable-reason {
    font-size: 10px;
  }
  
  .manager-item strong {
    font-size: 15px;
  }
  
  .manager-contact {
    font-size: 14px;
  }
  
  .manager-item p {
    font-size: 15px;
  }
}

/* 桌面端适配 */
@media (min-width: 1200px) {
  .schedule-container {
    font-size: 13px;
  }
  
  .schedule-body {
    padding-top: 14px;
  }
  
  .header-corner {
    width: 60px;
  }
  
  .header-day {
    padding: 10px 6px;
  }
  
  .day-name {
    font-size: 14px;
  }
  
  .day-date {
    font-size: 12px;
  }
  
  .first-time-label,
  .time-label,
  .last-time-label {
    width: 60px;
    font-size: 12px;
  }
  
  .time-label {
    top: -10px;
  }
  
  .last-time-label {
    margin-top: -10px;
  }
  
  .row-cells {
    padding-left: 60px;
  }
  
  .reservation-block {
    font-size: 12px;
  }
  
  .user-name {
    font-size: 12px;
  }
  
  .time-info {
    font-size: 10px;
  }
  
  .unavailable-icon {
    font-size: 18px;
  }
  
  .unavailable-reason {
    font-size: 11px;
  }
}

/* 小屏手机优化 */
@media (max-width: 375px) {
  .card-header {
    font-size: 14px;
  }
  
  .schedule-container {
    font-size: 9px;
  }
  
  .schedule-body {
    padding-top: 9px;
  }
  
  .header-corner {
    width: 30px;
  }
  
  .header-day {
    padding: 5px 1px;
  }
  
  .day-name {
    font-size: 10px;
  }
  
  .day-date {
    font-size: 8px;
  }
  
  .first-time-label,
  .time-label,
  .last-time-label {
    width: 30px;
    font-size: 8px;
  }
  
  .time-label {
    top: -7px;
  }
  
  .last-time-label {
    margin-top: -7px;
  }
  
  .row-cells {
    padding-left: 30px;
  }
  
  .reservation-block {
    font-size: 8px;
  }
  
  .user-name {
    font-size: 8px;
  }
  
  .time-info {
    font-size: 7px;
  }
}

/* 时间块选择样式 */
</style>
