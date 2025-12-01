<template>
  <div class="home">
    <el-row :gutter="isMobile ? 10 : 20">
      <el-col :span="24">
        <el-card class="campus-card">
          <el-radio-group v-model="selectedCampusId" @change="handleCampusChange" :size="isMobile ? 'small' : 'default'">
            <el-radio-button v-for="campus in campuses" :key="campus.id" :label="campus.id">
              {{ campus.name }}
            </el-radio-button>
          </el-radio-group>
        </el-card>
      </el-col>
    </el-row>

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
          <div class="schedule-table-wrapper" v-loading="loading">
            <div class="schedule-container">
              <!-- 表头 -->
              <div class="schedule-header">
                <div class="header-corner"></div>
                <div class="header-days">
                  <div v-for="day in weekDays" :key="day.date" class="header-day">
                    <div class="day-name">{{ day.dayName }}</div>
                    <div class="day-date">{{ day.dateText }}</div>
                  </div>
                </div>
              </div>
              
              <!-- 时间行 -->
              <div class="schedule-body">
                <!-- 第一个时间标签 - 在表格开始前 -->
                <div class="first-time-label">{{ timeSlots[0] }}:00</div>
                
                <div v-for="(hour, index) in timeSlots" :key="hour" class="time-row">
                  <!-- 时间标签 - 放在框线上（除了第一个） -->
                  <div class="time-label" v-if="index > 0 && index < timeSlots.length">
                    {{ hour }}:00
                  </div>
                  
                  <!-- 内容单元格 -->
                  <div class="row-cells">
                    <div 
                      v-for="day in weekDays" 
                      :key="day.date" 
                      class="schedule-cell"
                      :class="{ 
                        'last-row': index === timeSlots.length - 1,
                        'break-time': hour === 12 || hour === 18,
                        'unavailable-cell': getUnavailableForCell(day.date, hour)
                      }"
                    >
                      <!-- 不可预约时间段标记 -->
                      <div 
                        v-if="getUnavailableForCell(day.date, hour)"
                        class="unavailable-block"
                        :title="getUnavailableForCell(day.date, hour).reason || '不可预约'"
                      >
                        <div class="unavailable-content">
                          <!-- <div class="unavailable-icon">🚫</div> -->
                          <div class="unavailable-reason" v-if="!isMobile">
                            {{ getUnavailableForCell(day.date, hour).reason || '不可预约' }}
                          </div>
                        </div>
                      </div>
                      
                      <!-- 预约信息块 -->
                      <div 
                        v-for="reservation in getReservationsForCell(day.date, hour)" 
                        :key="reservation.id"
                        class="reservation-block"
                        :style="getReservationStyle(reservation, hour)"
                        @click="showReservationDetail(reservation)"
                      >
                        <div class="reservation-content">
                          <div class="user-name">{{ reservation.user_name }}</div>
                          <div class="time-info" v-if="!isMobile">{{ reservation.start_hour }}-{{ reservation.end_hour }}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- 最后的时间标签 - 在表格结束后 -->
                <div class="last-time-label">{{ timeSlots[timeSlots.length - 1] + 1 }}:00</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="24" :md="8" :lg="8" class="sidebar-col">
        <el-card class="manager-card" style="margin-bottom: 12px">
          <template #header>
            <div class="card-header">
              <span>钥匙管理员</span>
            </div>
          </template>
          <div v-if="keyManagers.length > 0">
            <div v-for="manager in keyManagers" :key="manager.id" class="manager-item">
              <strong>{{ manager.name }}</strong>
              <span class="manager-contact">{{ manager.contact }}</span>
            </div>
          </div>
          <el-empty v-else description="暂无钥匙管理员" :image-size="60" />
        </el-card>

        <el-card class="pickup-card">
          <template #header>
            <div class="card-header">
              <span>已领取钥匙</span>
            </div>
          </template>
          <el-timeline v-if="activeKeyPickups.length > 0">
            <el-timeline-item
              v-for="pickup in activeKeyPickups"
              :key="pickup.id"
              :timestamp="formatTime(pickup.key_pickup_time)"
            >
              {{ pickup.user_name }} - {{ pickup.date }} {{ pickup.start_hour }}:00-{{ pickup.end_hour }}:00
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else description="暂无已领取钥匙" :image-size="60" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 预约提示对话框 -->
    <el-dialog 
      v-model="showReminderDialog" 
      title="预约须知" 
      :width="isMobile ? '90%' : '400px'"
      :fullscreen="isMobile"
      center
    >
      <div style="text-align: center; padding: 20px 0;">
        <el-icon :size="60" color="#E6A23C" style="margin-bottom: 20px;">
          <WarningFilled />
        </el-icon>
        <p style="font-size: 16px; line-height: 1.8; color: #606266;">
          请维护好排练室内卫生，使用完毕<b style="color:red">物归原位</b><br/>
          把琴房的中间部分空出来，线材理顺<br/>
          使用设备请联系物主，损坏设备会查监控要求照价赔偿<br/>
          门口有扫把拖把垃圾袋垃圾桶，请<b style="color:red">自觉清理并带走垃圾</b><br/>
          违反规则可能会得到“特别关照”
        </p>
      </div>
      <template #footer>
        <el-button type="primary" @click="handleAcknowledgeReminder" size="large" style="width: 100%;">
          我已知晓
        </el-button>
      </template>
    </el-dialog>

    <!-- 新建预约对话框 -->
    <el-dialog 
      v-model="showReserveDialog" 
      title="新建预约" 
      :width="isMobile ? '90%' : '500px'"
      :fullscreen="isMobile"
    >
      <el-alert 
        v-if="userWeeklyHours !== null"
        :title="`本周已预约 ${userWeeklyHours} 小时，还可预约 ${6 - userWeeklyHours} 小时`"
        :type="weeklyQuotaType"
        :closable="false"
        style="margin-bottom: 15px"
      />
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
        <!-- <el-form-item label="时间段">
          <el-select v-model="reserveForm.timeSlot" placeholder="请选择时间段" style="width: 100%">
            <el-option label="上午 8:00-12:00" value="morning" />
            <el-option label="下午 13:00-18:00" value="afternoon" />
            <el-option label="晚上 19:00-22:00" value="evening" />
          </el-select>
        </el-form-item> -->
        <el-form-item label="时间段">
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
import { ref, onMounted, computed, onUnmounted, watch } from 'vue'
import { reservationService, keyService, adminService } from '@/services/api'
import { ElMessage } from 'element-plus'
import { WarningFilled } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'Home',
  components: {
    WarningFilled
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

    const reserveForm = ref({
      date: null,
      timeSlot: '',
      start_hour: 8,
      end_hour: 12
    })

    const timeSlots = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
    
    const predefinedTimeSlots = {
      morning: { start: 8, end: 12 },
      afternoon: { start: 13, end: 18 },
      evening: { start: 19, end: 22 }
    }

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

    // 获取某个单元格的预约信息
    const getReservationsForCell = (date, hour) => {
      return weeklyReservations.value.filter(reservation => {
        return reservation.date === date && 
               reservation.start_hour <= hour && 
               reservation.end_hour > hour
      })
    }

    // 检查某个单元格是否为不可预约时间段
    const getUnavailableForCell = (date, hour) => {
      // 将日期字符串转为Date对象
      const dateObj = new Date(date)
      const dayOfWeek = (dateObj.getDay()) // 0=周日, 1=周一, ..., 6=周六
      
      // 查找匹配的不可预约时间段
      return unavailableTimes.value.find(ut => {
        // 检查时间是否在范围内
        const inTimeRange = ut.start_hour <= hour && ut.end_hour > hour
        if (!inTimeRange) return false
        
        // 检查日期条件
        if (ut.date) {
          // 特定日期
          return ut.date === date
        } else if (ut.day_of_week !== null) {
          // 固定周几
          return ut.day_of_week === dayOfWeek
        } else {
          // 所有日期
          return true
        }
      })
    }

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

    // 根据用户名生成一致的颜色
    const getUserColor = (userName) => {
      // 简单的字符串哈希函数
      let hash = 0
      for (let i = 0; i < userName.length; i++) {
        hash = userName.charCodeAt(i) + ((hash << 5) - hash)
        hash = hash & hash // 转换为32位整数
      }
      
      // 预定义的纯色方案（柔和且易区分）
      const colors = [
        // '#7c7cde', // 紫色
        // '#f279a1', // 粉红
        '#4eb8fe', // 蓝色
        // '#3ee8a9', // 青绿
        // '#f5a071', // 橙色
        // '#5099d0', // 青蓝
        // '#b9e5e8', // 薄荷
        // '#ff8476', // 橙粉
        // '#c7b5ec', // 淡紫
        // '#f4daf0', // 淡粉
        // '#b6d8fc', // 淡蓝
        // '#ffd5b8', // 橙黄
        // '#d3a5c8', // 紫粉
        // '#b8d8fc', // 蓝紫
        // '#f68389', // 红粉
        // '#e4a8bc', // 玫粉
      ]
      
      // 使用哈希值选择颜色
      const index = Math.abs(hash) % colors.length
      return colors[index]
    }

    // 计算预约块的样式
    const getReservationStyle = (reservation, hour) => {
      if (reservation.start_hour === hour) {
        const duration = reservation.end_hour - reservation.start_hour
        // 根据屏幕尺寸动态计算单元格高度（与CSS一致）
        let cellHeight = 35 // 移动端默认
        if (window.innerWidth <= 375) {
          cellHeight = 30 // 小屏手机
        } else if (window.innerWidth >= 1200) {
          cellHeight = 35 // 桌面端
        } else if (window.innerWidth >= 769) {
          cellHeight = 40 // 平板端
        }
        
        // 获取用户专属颜色
        let background
        if (reservation.key_returned) {
          background = '#9e9e9e' // 已归还钥匙：灰色
        } else if (reservation.key_picked_up) {
          background = '#2ac98d' // 已取钥匙：绿色
        } else {
          background = getUserColor(reservation.user_name) // 用户专属颜色
        }
        
        return {
          height: `${duration * cellHeight}px`,
          background: background,
          position: 'absolute',
          top: '0',
          left: '2px',
          right: '2px',
          zIndex: 1
        }
      }
      return { display: 'none' }
    }

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

    const disabledDate = (time) => {
      const now = new Date()
      const currentHour = now.getHours()
      const dayOfWeek = now.getDay() // 0=周日, 1=周一, ..., 6=周六
      
      // 计算上周日22:00
      let lastSunday = new Date(now)
      const daysToLastSunday = dayOfWeek === 0 ? 7 : dayOfWeek
      lastSunday.setDate(now.getDate() - daysToLastSunday)
      lastSunday.setHours(22, 0, 0, 0)
      
      // 如果当前是周日22:00之后，则上周日应该是今天
      if (dayOfWeek === 0 && currentHour >= 22) {
        lastSunday = new Date(now)
        lastSunday.setHours(22, 0, 0, 0)
      }
      
      // 计算本周日22:00
      let thisSunday = new Date(now)
      const daysToThisSunday = dayOfWeek === 0 ? 0 : 7 - dayOfWeek
      thisSunday.setDate(now.getDate() + daysToThisSunday)
      thisSunday.setHours(22, 0, 0, 0)
      
      // 如果当前是周日22:00之后，本周日应该是下周日
      if (dayOfWeek === 0 && currentHour >= 22) {
        thisSunday.setDate(thisSunday.getDate() + 7)
      }
      
      // 禁用上周日22:00之前和本周日22:00之后的日期
      const timeValue = time.getTime()
      return timeValue < lastSunday.getTime() || timeValue > thisSunday.getTime()
    }

    const formatTime = (timeStr) => {
      return new Date(timeStr).toLocaleString('zh-CN')
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

    const handleReserve = async () => {
      if (!reserveForm.value.date) {
        ElMessage.warning('请选择日期')
        return
      }

      let startHour = reserveForm.value.start_hour
      let endHour = reserveForm.value.end_hour

      if (reserveForm.value.timeSlot) {
        const slot = predefinedTimeSlots[reserveForm.value.timeSlot]
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
        reserveForm.value = {
          date: null,
          timeSlot: '',
          start_hour: 8,
          end_hour: 12
        }
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
      campuses,
      selectedCampusId,
      weeklyReservations,
      keyManagers,
      keyPickups,
      loading,
      showReminderDialog,
      showReserveDialog,
      reserving,
      reserveForm,
      weekRange,
      timeSlots,
      weekDays,
      isMobile,
      userWeeklyHours,
      weeklyQuotaType,
      activeKeyPickups,
      disabledDate,
      formatTime,
      handleCampusChange,
      handleAcknowledgeReminder,
      handleReserve,
      getReservationsForCell,
      getUnavailableForCell,
      getReservationStyle,
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

/* 课程表样式 - 重新设计 */
.schedule-table-wrapper {
  overflow-x: hidden;
  overflow-y: auto;
  max-height: 700px;
  -webkit-overflow-scrolling: touch;
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

/* 单个时间格 */
.schedule-cell {
  flex: 1;
  height: 35px;
  border-right: 1px solid #e4e7ed;
  position: relative;
  background-color: #fff;
  min-width: 0;
}

.schedule-cell:last-child {
  border-right: none;
}

.schedule-cell.last-row {
  border-bottom: 1px solid #e4e7ed;
}

/* 休息时间段（12:00-13:00, 18:00-19:00）变灰 */
.schedule-cell.break-time {
  background-color: #f5f7fa;
}

/* 不可预约时间段 */
.schedule-cell.unavailable-cell {
  background-color: #fef0f0;
  position: relative;
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
  
  .schedule-cell {
    height: 40px;
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
  
  .schedule-cell {
    height: 35px;
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
  
  .schedule-table-wrapper {
    max-height: 800px;
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
  
  .schedule-cell {
    height: 30px;
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
</style>
