<template>
  <div class="schedule-table" v-loading="loading">
      <!-- 周几表头 -->
      <div class="schedule-header">
        <div class="time-column-header"></div>
        <div class="days-header">
          <div v-for="day in weekDays" :key="day.date" class="header-day">
            <div class="day-name">{{ day.dayName }}</div>
            <div class="day-date">{{ day.dateText }}</div>
          </div>
        </div>
      </div>
      
      <!-- 时间行 -->
      <div class="schedule-body">
        <!-- 第一个时间标签 -->
        <div class="first-time-label">{{ timeSlots[0] }}:00</div>
        
        <div v-for="(hour, index) in timeSlots" :key="hour" class="time-row">
          <!-- 时间标签 -->
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
                @click="$emit('reservation-click', reservation)"
              >
                <div class="reservation-content">
                  <div class="user-name">{{ reservation.user_name }}</div>
                  <div class="time-info" v-if="!isMobile">{{ reservation.start_hour }}-{{ reservation.end_hour }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 最后的时间标签 -->
        <div class="last-time-label">{{ timeSlots[timeSlots.length - 1] + 1 }}:00</div>
      </div>
  </div>
</template>

<script>
export default {
  name: 'WeeklySchedule',
  props: {
    weekDays: {
      type: Array,
      default: () => []
    },
    timeSlots: {
      type: Array,
      default: () => [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
    },
    weeklyReservations: {
      type: Array,
      default: () => []
    },
    unavailableTimes: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    },
    weekRange: {
      type: String,
      default: ''
    },
    isMobile: {
      type: Boolean,
      default: false
    }
  },
  emits: ['reservation-click'],
  methods: {
    getReservationsForCell(date, hour) {
      return this.weeklyReservations.filter(r => 
        r.date === date && 
        r.start_hour === hour
      )
    },
    
    getUnavailableForCell(date, hour) {
      const dateObj = new Date(date)
      const dayOfWeek = dateObj.getDay()
      
      return this.unavailableTimes.find(ut => {
        const inTimeRange = ut.start_hour <= hour && ut.end_hour > hour
        if (!inTimeRange) return false
        
        if (ut.date) {
          return ut.date === date
        } else if (ut.day_of_week !== null) {
          return ut.day_of_week === dayOfWeek
        } else {
          return true
        }
      })
    },
    
    getReservationStyle(reservation, currentHour) {
      const duration = reservation.end_hour - reservation.start_hour
      const cellHeight = 26 // 与CSS中.schedule-cell的height一致
      
      let backgroundColor = '#4eb8fe' // 默认蓝色
      if (reservation.key_returned) {
        backgroundColor = '#909399' // 已归还：灰色
      } else if (reservation.key_picked_up) {
        backgroundColor = '#67c23a' // 已领取：绿色
      }

      return {
        height: `${duration * cellHeight}px`,
        zIndex: 10,
        backgroundColor
      }
    }
  }
}
</script>

<style scoped>
.schedule-table {
  overflow-x: auto;
  overflow-y: hidden;
  padding-bottom: 5px; /* Ensure space for scrollbar if needed */
}

.schedule-header {
  display: flex;
  position: sticky;
  top: 0;
  background: white;
  z-index: 100;
  border-bottom: 1px solid #e4e7ed;
}

.time-column-header {
  width: 50px;
  flex-shrink: 0;
}

.days-header {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  background: #e4e7ed;
}

.header-day {
  background: white;
  padding: 10px;
  text-align: center;
}

.day-name {
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.day-date {
  font-size: 12px;
  color: #909399;
}

.schedule-body {
  position: relative;
  margin-top: 10px;
  margin-bottom: 15px;
  overflow: visible;
}

.first-time-label,
.last-time-label {
  position: absolute;
  left: 0;
  width: 50px;
  text-align: right;
  padding-right: 8px;
  font-size: 12px;
  color: #606266;
  font-weight: 500;
}

.first-time-label {
  top: 0;
  transform: translateY(-50%);
}

.last-time-label {
  bottom: 0;
  transform: translateY(50%);
}

.time-row {
  position: relative;
  display: flex;
  border-top: 1px solid #e4e7ed;
}

.time-label {
  position: absolute;
  left: 0;
  top: 0;
  transform: translateY(-50%);
  width: 50px;
  text-align: right;
  padding-right: 8px;
  font-size: 12px;
  color: #606266;
  background: white;
  z-index: 50;
  font-weight: 500;
}

.row-cells {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  background: #e4e7ed;
  margin-left: 50px;
}

.schedule-cell {
  background: white;
  height: 25px;
  position: relative;
  transition: background-color 0.2s;
}

.schedule-cell:hover {
  background: #f5f7fa;
}

.schedule-cell.last-row {
  border-bottom: 1px solid #e4e7ed;
}

.schedule-cell.break-time {
  background: #fef0f0;
}

.schedule-cell.unavailable-cell {
  background: repeating-linear-gradient(
    45deg,
    #f5f7fa,
    #f5f7fa 10px,
    #e4e7ed 10px,
    #e4e7ed 20px
  );
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
  /* border: 1px dashed #c0c4cc; */
  background: repeating-linear-gradient(
    45deg,
    #f5f7fa,
    #f5f7fa 10px,
    #e4e7ed 10px,
    #e4e7ed 20px
  );
  z-index: 5;
}

.unavailable-content {
  text-align: center;
  padding: 4px;
}

.unavailable-reason {
  font-size: 11px;
  color: #909399;
  font-weight: 500;
}

.reservation-block {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  background: #4eb8fe;
  color: white;
  padding: 4px 6px;
  cursor: pointer;
  transition: all 0.2s;
  overflow: hidden;
  border-radius: 2px;
}

.reservation-block:hover {
  transform: translateX(-2px);
  box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.2);
  z-index: 20 !important;
}

.reservation-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.user-name {
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.time-info {
  font-size: 10px;
  opacity: 0.9;
  margin-top: 2px;
}

@media (max-width: 768px) {
  .time-column-header,
  .first-time-label,
  .last-time-label,
  .time-label {
    width: 35px;
    font-size: 10px;
    padding-right: 4px;
  }

  .row-cells {
    margin-left: 35px;
  }

  .header-day {
    padding: 6px 2px;
  }

  .day-name {
    font-size: 12px;
  }

  .day-date {
    font-size: 10px;
  }

  .schedule-cell {
    height: 25px;
  }

  .user-name {
    font-size: 10px;
  }

  .time-info {
    font-size: 9px;
  }

  .unavailable-reason {
    font-size: 9px;
  }
}
</style>
