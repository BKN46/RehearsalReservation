<template>
  <div class="time-block-selector">
    <div class="selected-time-display" v-if="startHour !== null && endHour !== null">
      <el-tag type="success" size="large">
        已选择：{{ startHour }}:00 - {{ endHour }}:00 
        ({{ endHour - startHour }}小时)
      </el-tag>
      <el-button size="small" @click="$emit('clear')" text>清除选择</el-button>
    </div>
    
    <div class="time-blocks-container">
      <div class="time-blocks-hint">
        <span style="color: #67c23a;">● 可选</span>
        <span style="color: #409eff;">● 已选</span>
        <span style="color: #f56c6c;">● 已被预约</span>
        <span style="color: #909399;">● 不可预约</span>
      </div>
      
      <div class="time-blocks-wrapper">
        <div class="time-labels">
          <div class="time-label-node" v-for="hour in timeLabels" :key="hour">
            {{ hour }}:00
          </div>
        </div>
        
        <div class="time-blocks">
          <div
            v-for="hour in availableHours"
            :key="hour"
            :class="['time-block', getBlockClass(hour)]"
            @click="handleBlockClick(hour)"
          >
            <div class="time-block-status" v-if="getBlockStatus(hour)">
              {{ getBlockStatus(hour) }}
            </div>
          </div>
        </div>
      </div>
      
      <div class="time-selection-tip">
        点击选择起始时间，再点击选择结束时间
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TimeBlockSelector',
  props: {
    startHour: {
      type: Number,
      default: null
    },
    endHour: {
      type: Number,
      default: null
    },
    date: {
      type: [String, Date],
      default: null
    },
    availableHours: {
      type: Array,
      default: () => [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
    },
    dailyReservations: {
      type: Array,
      default: () => []
    },
    dailyUnavailableTimes: {
      type: Array,
      default: () => []
    }
  },
  emits: ['update:startHour', 'update:endHour', 'clear', 'select'],
  computed: {
    timeLabels() {
      if (!this.availableHours.length) return []
      const labels = [...this.availableHours]
      const lastHour = this.availableHours[this.availableHours.length - 1]
      labels.push(lastHour + 1)
      return labels
    }
  },
  methods: {
    isPastTime(hour) {
      if (!this.date) return false
      const now = new Date()
      const targetDate = new Date(this.date)
      
      // 检查是否是今天
      if (targetDate.toDateString() === now.toDateString()) {
        return hour <= now.getHours()
      }
      
      // 检查是否是过去的日子
      if (targetDate < new Date(now.toDateString())) {
        return true
      }
      
      return false
    },

    getBlockStatus(hour) {
      // 检查是否是过去时间
      if (this.isPastTime(hour)) {
        return '已过期'
      }

      // 检查是否被预约
      const hasReservation = this.dailyReservations.some(r => 
        r.start_hour <= hour && r.end_hour > hour
      )
      if (hasReservation) {
        const reservation = this.dailyReservations.find(r => 
          r.start_hour <= hour && r.end_hour > hour
        )
        return reservation.user_name
      }

      // 检查是否不可预约
      const isUnavailable = this.dailyUnavailableTimes.some(ut => 
        ut.start_hour <= hour && ut.end_hour > hour
      )
      if (isUnavailable) {
        const unavailable = this.dailyUnavailableTimes.find(ut => 
          ut.start_hour <= hour && ut.end_hour > hour
        )
        return unavailable.reason || '不可预约'
      }

      return ''
    },
    
    getBlockClass(hour) {
      // 检查是否是过去时间
      if (this.isPastTime(hour)) return 'unavailable'

      // 已选中的时间段
      if (this.startHour !== null && this.endHour !== null) {
        if (hour >= this.startHour && hour < this.endHour) {
          return 'selected'
        }
      }

      // 检查是否被预约
      const hasReservation = this.dailyReservations.some(r => 
        r.start_hour <= hour && r.end_hour > hour
      )
      if (hasReservation) return 'reserved'

      // 检查是否不可预约
      const isUnavailable = this.dailyUnavailableTimes.some(ut => 
        ut.start_hour <= hour && ut.end_hour > hour
      )
      if (isUnavailable) return 'unavailable'

      return 'available'
    },
    
    handleBlockClick(hour) {
      if (this.getBlockClass(hour) === 'unavailable' || this.getBlockClass(hour) === 'reserved') {
        return
      }
      this.$emit('select', hour)
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

.time-blocks-container {
  width: 100%;
}

.time-blocks-hint {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
  font-size: 12px;
  flex-wrap: wrap;
}

.time-blocks-wrapper {
  display: flex;
  gap: 0;
  margin-bottom: 10px;
  padding-top: 10px; /* Space for the first label */
}

.time-labels {
  display: flex;
  flex-direction: column;
  padding-right: 8px;
  border-right: 2px solid #e4e7ed;
}

.time-label-node {
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  font-size: 12px;
  font-weight: 600;
  color: #303133;
  transform: translateY(-50%);
}

/* Ensure the last label is positioned correctly */
.time-label-node:last-child {
  height: 0;
  overflow: visible;
}

.time-blocks {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0; /* Remove gap to make it continuous */
  padding-left: 8px;
}

.time-block {
  padding: 0 12px;
  border: 1px solid #e4e7ed;
  border-top: none; /* Remove double borders */
  cursor: pointer;
  transition: all 0.2s;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 45px;
  box-sizing: border-box;
}

.time-block:first-child {
  border-top: 1px solid #e4e7ed;
}

.time-block-status {
  font-size: 12px;
  color: #606266;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  width: 100%;
  text-align: center;
  font-weight: 500;
}

.time-block.available {
  border-color: #e4e7ed;
  background: #ffffff;
}

.time-block.available:hover {
  background: #f0f9ff;
  z-index: 1;
}

.time-block.selected {
  background: #409eff;
  border-color: #409eff;
  color: white;
  z-index: 2;
}

.time-block.selected .time-block-status {
  color: white;
}

.time-block.reserved {
  background: #fef0f0;
  border-color: #fde2e2;
  cursor: not-allowed;
  opacity: 0.8;
}

.time-block.reserved .time-block-status {
  color: #f56c6c;
  font-weight: 600;
}

.time-block.unavailable {
  background: #f5f7fa;
  border-color: #e4e7ed;
  cursor: not-allowed;
  opacity: 0.7;
}

.time-block.unavailable .time-block-status {
  color: #909399;
  font-weight: 500;
}

.time-selection-tip {
  text-align: center;
  color: #909399;
  font-size: 13px;
  margin-top: 20px;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 4px;
}

@media (max-width: 768px) {
  .time-label-node {
    font-size: 11px;
    height: 30px;
  }
  
  .time-block {
    height: 30px;
  }

  .time-block-status {
    font-size: 11px;
  }

  .selected-time-display {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }

  .time-blocks-hint {
    gap: 10px;
    font-size: 11px;
  }
}
</style>
