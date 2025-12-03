<template>
  <view class="container">
    <view class="campus-tabs">
      <view 
        v-for="item in campuses" 
        :key="item.id" 
        class="tab-item" 
        :class="{ active: selectedCampusId === item.id }"
        @click="selectCampus(item.id)"
      >
        {{ item.name }}
      </view>
    </view>

    <view class="rule-list">
      <view v-for="item in rules" :key="item._id" class="rule-card card">
        <view class="info">
          <view class="rule-time">
            {{ formatRule(item) }}
          </view>
          <view class="rule-hours">
            {{ item.start_hour }}:00 - {{ item.end_hour }}:00
          </view>
        </view>
        <button class="btn-delete" size="mini" @click="deleteRule(item._id)">删除</button>
      </view>
      
      <view v-if="rules.length === 0" class="empty-state">
        <text>暂无不可用设置</text>
      </view>
    </view>

    <button class="btn-add" @click="showAddModal = true">+</button>

    <!-- Add Modal -->
    <view class="modal-overlay" v-if="showAddModal" @click="showAddModal = false">
      <view class="modal-content" @click.stop>
        <view class="modal-title">添加不可用时间</view>
        
        <view class="form-group">
          <text class="label">类型</text>
          <radio-group @change="handleTypeChange" class="radio-group">
            <label class="radio"><radio value="weekly" :checked="addType === 'weekly'" />每周重复</label>
            <label class="radio"><radio value="date" :checked="addType === 'date'" />特定日期</label>
          </radio-group>
        </view>

        <view class="form-group" v-if="addType === 'weekly'">
          <text class="label">星期</text>
          <picker :range="weekDays" range-key="name" @change="handleDayChange">
            <view class="picker-view">
              {{ selectedDay !== null ? weekDays[selectedDay].name : '请选择星期' }}
            </view>
          </picker>
        </view>

        <view class="form-group" v-if="addType === 'date'">
          <text class="label">日期</text>
          <picker mode="date" @change="handleDateChange">
            <view class="picker-view">
              {{ selectedDate || '请选择日期' }}
            </view>
          </picker>
        </view>

        <view class="form-group">
          <text class="label">开始时间</text>
          <input class="input" type="number" v-model="startHour" placeholder="8-21" />
        </view>

        <view class="form-group">
          <text class="label">结束时间</text>
          <input class="input" type="number" v-model="endHour" placeholder="9-22" />
        </view>

        <view class="modal-actions">
          <button class="btn-cancel" @click="showAddModal = false">取消</button>
          <button class="btn-confirm" @click="addRule">确定</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const campuses = ref([])
const selectedCampusId = ref(null)
const rules = ref([])
const showAddModal = ref(false)

const addType = ref('weekly')
const weekDays = [
  { id: 1, name: '周一' },
  { id: 2, name: '周二' },
  { id: 3, name: '周三' },
  { id: 4, name: '周四' },
  { id: 5, name: '周五' },
  { id: 6, name: '周六' },
  { id: 0, name: '周日' }
]
const selectedDay = ref(null)
const selectedDate = ref('')
const startHour = ref('')
const endHour = ref('')

const fetchCampuses = () => {
  wx.cloud.callFunction({
    name: 'api',
    data: { $url: 'reservation/campuses' },
    success: res => {
      campuses.value = res.result
      if (res.result.length > 0) {
        selectedCampusId.value = res.result[0].id
        fetchRules()
      }
    }
  })
}

const selectCampus = (id) => {
  selectedCampusId.value = id
  fetchRules()
}

const fetchRules = () => {
  if (!selectedCampusId.value) return
  
  uni.showLoading({ title: '加载中...' })
  wx.cloud.callFunction({
    name: 'api',
    data: {
      $url: 'admin/unavailable-times',
      campus_id: selectedCampusId.value
    },
    success: res => {
      uni.hideLoading()
      rules.value = res.result
    },
    fail: err => {
      uni.hideLoading()
      console.error(err)
    }
  })
}

const formatRule = (item) => {
  if (item.date) {
    return `日期: ${item.date}`
  } else if (item.day_of_week !== null) {
    const day = weekDays.find(d => d.id === item.day_of_week)
    return `每周: ${day ? day.name : '未知'}`
  }
  return '未知规则'
}

const handleTypeChange = (e) => {
  addType.value = e.detail.value
}

const handleDayChange = (e) => {
  selectedDay.value = e.detail.value
}

const handleDateChange = (e) => {
  selectedDate.value = e.detail.value
}

const addRule = () => {
  if (!startHour.value || !endHour.value) {
    uni.showToast({ title: '请填写时间', icon: 'none' })
    return
  }

  const data = {
    $url: 'admin/unavailable-times',
    httpMethod: 'POST',
    campus_id: selectedCampusId.value,
    start_hour: parseInt(startHour.value),
    end_hour: parseInt(endHour.value)
  }

  if (addType.value === 'weekly') {
    if (selectedDay.value === null) {
      uni.showToast({ title: '请选择星期', icon: 'none' })
      return
    }
    data.day_of_week = weekDays[selectedDay.value].id
  } else {
    if (!selectedDate.value) {
      uni.showToast({ title: '请选择日期', icon: 'none' })
      return
    }
    data.date = selectedDate.value
  }

  uni.showLoading({ title: '添加中...' })
  wx.cloud.callFunction({
    name: 'api',
    data: data,
    success: res => {
      uni.hideLoading()
      if (res.result.error) {
        uni.showToast({ title: res.result.error, icon: 'none' })
      } else {
        uni.showToast({ title: '添加成功', icon: 'success' })
        showAddModal.value = false
        fetchRules()
      }
    },
    fail: err => {
      uni.hideLoading()
      console.error(err)
      uni.showToast({ title: '添加失败', icon: 'none' })
    }
  })
}

const deleteRule = (id) => {
  uni.showModal({
    title: '确认删除',
    content: '确定要删除该规则吗？',
    success: (res) => {
      if (res.confirm) {
        uni.showLoading({ title: '删除中...' })
        wx.cloud.callFunction({
          name: 'api',
          data: {
            $url: 'admin/unavailable-times',
            httpMethod: 'DELETE',
            id: id
          },
          success: res => {
            uni.hideLoading()
            uni.showToast({ title: '删除成功', icon: 'success' })
            fetchRules()
          },
          fail: err => {
            uni.hideLoading()
            console.error(err)
            uni.showToast({ title: '删除失败', icon: 'none' })
          }
        })
      }
    }
  })
}

onMounted(() => {
  fetchCampuses()
})
</script>

<style lang="scss">
.campus-tabs {
  display: flex;
  background: #fff;
  padding: 20rpx;
  margin-bottom: 20rpx;
  border-bottom: 1rpx solid #eee;
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 20rpx;
  font-size: 30rpx;
  color: #666;
  
  &.active {
    color: #333;
    font-weight: bold;
    border-bottom: 4rpx solid #333;
  }
}

.rule-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx;
  margin-bottom: 20rpx;
}

.rule-time {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
}

.rule-hours {
  font-size: 26rpx;
  color: #666;
  margin-top: 10rpx;
}

.btn-delete {
  background: #fff;
  color: #f56c6c;
  border: 1rpx solid #f56c6c;
  font-size: 24rpx;
  margin: 0;
}

.btn-add {
  position: fixed;
  bottom: 60rpx;
  right: 40rpx;
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  background: #333;
  color: #fff;
  font-size: 60rpx;
  line-height: 100rpx;
  text-align: center;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.2);
  padding: 0;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.modal-content {
  width: 600rpx;
  background: #fff;
  border-radius: 12rpx;
  padding: 40rpx;
}

.modal-title {
  font-size: 36rpx;
  font-weight: bold;
  text-align: center;
  margin-bottom: 40rpx;
}

.form-group {
  margin-bottom: 30rpx;
}

.label {
  display: block;
  font-size: 28rpx;
  color: #666;
  margin-bottom: 10rpx;
}

.radio-group {
  display: flex;
  gap: 40rpx;
}

.radio {
  font-size: 28rpx;
}

.picker-view {
  height: 80rpx;
  line-height: 80rpx;
  background: #f9f9f9;
  padding: 0 20rpx;
  border-radius: 8rpx;
  font-size: 30rpx;
  color: #333;
}

.input {
  height: 80rpx;
  background: #f9f9f9;
  padding: 0 20rpx;
  border-radius: 8rpx;
  font-size: 30rpx;
}

.modal-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 40rpx;
}

.btn-cancel, .btn-confirm {
  width: 45%;
  font-size: 28rpx;
}

.btn-confirm {
  background: #333;
  color: #fff;
}

.empty-state {
  text-align: center;
  padding: 100rpx 0;
  color: #999;
}
</style>
