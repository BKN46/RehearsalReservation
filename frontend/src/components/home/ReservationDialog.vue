<template>
  <div>
    <!-- 预约提示对话框 -->
    <el-dialog 
      v-model="showReminder" 
      title="预约前须知" 
      :width="isMobile ? '90%' : '450px'"
      :fullscreen="isMobile"
    >
      <div style="text-align: center;">
        <el-icon :size="60" color="#e6a23c" style="margin-bottom: 15px;">
          <WarningFilled />
        </el-icon>
        <p style="font-size: 16px; line-height: 1.8; color: #606266;">
          请维护好排练室内卫生，使用完毕<b style="color:red">物归原位</b><br/>
          把琴房的中间部分空出来，线材理顺<br/>
          使用设备请联系物主，损坏设备会查监控要求照价赔偿<br/>
          门口有扫把拖把垃圾袋垃圾桶，请<b style="color:red">自觉清理并带走垃圾</b><br/>
          违反规则可能会得到"特别关照"
        </p>
      </div>
      <template #footer>
        <el-button type="primary" @click="handleAcknowledge" size="large" style="width: 100%;">
          我已知晓
        </el-button>
      </template>
    </el-dialog>

    <!-- 新建预约对话框 -->
    <el-dialog 
      v-model="showDialog" 
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
        <el-form-item label="选择时间段" v-if="reserveForm.date">
          <TimeBlockSelector
            v-model:startHour="reserveForm.start_hour"
            v-model:endHour="reserveForm.end_hour"
            :date="reserveForm.date"
            :dailyReservations="dailyReservations"
            :dailyUnavailableTimes="dailyUnavailableTimes"
            @select="handleTimeSelect"
            @clear="clearTimeSelection"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="handleClose">取消</el-button>
        <el-button 
          v-if="reserveForm.date" 
          type="primary" 
          @click="handleReserve" 
          :loading="reserving"
        >
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { WarningFilled } from '@element-plus/icons-vue'
import TimeBlockSelector from './TimeBlockSelector.vue'

export default {
  name: 'ReservationDialog',
  components: {
    WarningFilled,
    TimeBlockSelector
  },
  props: {
    showReminderDialog: {
      type: Boolean,
      default: false
    },
    showReserveDialog: {
      type: Boolean,
      default: false
    },
    isMobile: {
      type: Boolean,
      default: false
    },
    userWeeklyHours: {
      type: Number,
      default: null
    },
    dailyReservations: {
      type: Array,
      default: () => []
    },
    dailyUnavailableTimes: {
      type: Array,
      default: () => []
    },
    reserving: {
      type: Boolean,
      default: false
    }
  },
  emits: [
    'update:showReminderDialog',
    'update:showReserveDialog',
    'acknowledge',
    'reserve',
    'close',
    'date-change'
  ],
  setup(props, { emit }) {
    const showReminder = computed({
      get: () => props.showReminderDialog,
      set: (val) => emit('update:showReminderDialog', val)
    })

    const showDialog = computed({
      get: () => props.showReserveDialog,
      set: (val) => emit('update:showReserveDialog', val)
    })

    const reserveForm = ref({
      date: null,
      timeSlot: '',
      start_hour: null,
      end_hour: null
    })

    const selectingStart = ref(true)

    const weeklyQuotaType = computed(() => {
      if (props.userWeeklyHours === null) return 'info'
      if (props.userWeeklyHours >= 6) return 'danger'
      if (props.userWeeklyHours >= 4) return 'warning'
      return 'success'
    })

    const disabledDate = (time) => {
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      const maxDate = new Date(today)
      maxDate.setDate(today.getDate() + 7)
      return time.getTime() < today.getTime() || time.getTime() > maxDate.getTime()
    }

    const handleAcknowledge = () => {
      emit('acknowledge')
    }

    const handleTimeSelect = (hour) => {
      if (selectingStart.value) {
        // 选择起始时间
        reserveForm.value.start_hour = hour
        reserveForm.value.end_hour = hour + 1 // 默认选择1小时
        selectingStart.value = false
      } else {
        // 选择结束时间
        if (hour < reserveForm.value.start_hour) {
          // 如果选择的时间小于起始时间，重新选择起始时间
          reserveForm.value.start_hour = hour
          reserveForm.value.end_hour = hour + 1
          selectingStart.value = false
        } else if (hour === reserveForm.value.start_hour) {
          // 如果点击同一个时间块，选择1小时
          reserveForm.value.end_hour = hour + 1
          selectingStart.value = true
        } else {
          // 选择结束时间（包含当前小时）
          reserveForm.value.end_hour = hour + 1
          selectingStart.value = true
        }
      }
    }

    const clearTimeSelection = () => {
      reserveForm.value.start_hour = null
      reserveForm.value.end_hour = null
      selectingStart.value = true
    }

    const handleReserve = () => {
      emit('reserve', { ...reserveForm.value })
    }

    const handleClose = () => {
      clearTimeSelection()
      emit('close')
    }

    // 监听日期变化，清空时间选择并通知父组件加载数据
    watch(() => reserveForm.value.date, (newDate) => {
      clearTimeSelection()
      if (newDate) {
        emit('date-change', newDate)
      }
    })

    // 监听对话框关闭，重置表单
    watch(showDialog, (val) => {
      if (!val) {
        reserveForm.value = {
          date: null,
          timeSlot: '',
          start_hour: null,
          end_hour: null
        }
        selectingStart.value = true
      }
    })

    return {
      showReminder,
      showDialog,
      reserveForm,
      weeklyQuotaType,
      disabledDate,
      handleAcknowledge,
      handleTimeSelect,
      clearTimeSelection,
      handleReserve,
      handleClose
    }
  }
}
</script>

<style scoped>
.selected-time-display {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 15px;
  padding: 10px;
  background: #f0f9ff;
  border-radius: 8px;
}

@media (max-width: 768px) {
  .selected-time-display {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
}
</style>
