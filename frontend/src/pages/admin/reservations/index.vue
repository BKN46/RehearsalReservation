<template>
  <view class="container">
    <view class="header-bar">
      <text class="page-title">预约管理</text>
    </view>

    <view class="filter-bar">
      <picker :range="campuses" range-key="name" @change="handleCampusChange">
        <view class="picker-item">
          {{ selectedCampus ? selectedCampus.name : '所有校区' }} ▼
        </view>
      </picker>
      <picker mode="date" @change="handleDateChange">
        <view class="picker-item">
          {{ selectedDate || '所有日期' }} ▼
        </view>
      </picker>
    </view>

    <view class="list">
      <view v-for="item in list" :key="item._id" class="res-card card">
        <view class="res-header">
          <text class="res-date">{{ item.date }}</text>
          <text class="res-status" :class="getStatusClass(item)">{{ getStatusText(item) }}</text>
        </view>
        <view class="res-body">
          <view class="res-row">
            <text class="label">时间:</text>
            <text class="value">{{ item.start_hour }}:00 - {{ item.end_hour }}:00</text>
          </view>
          <view class="res-row">
            <text class="label">用户:</text>
            <text class="value">{{ item.user_name }} ({{ item.student_id }})</text>
          </view>
          <view class="res-row">
            <text class="label">联系:</text>
            <text class="value">{{ item.contact }}</text>
          </view>
        </view>
        <view class="res-footer">
          <button class="btn-action" size="mini" v-if="item.status === 'active' && !item.key_picked_up" @click="updateStatus(item, 'pickup')">领取钥匙</button>
          <button class="btn-action" size="mini" v-if="item.key_picked_up && !item.key_returned" @click="updateStatus(item, 'return')">归还钥匙</button>
        </view>
      </view>
      
      <view v-if="list.length === 0" class="empty-state">
        <text>暂无预约记录</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const campuses = ref([])
const selectedCampus = ref(null)
const selectedDate = ref('')
const list = ref([])

const fetchCampuses = () => {
  wx.cloud.callFunction({
    name: 'api',
    data: { $url: 'reservation/campuses' },
    success: res => {
      campuses.value = [{ id: null, name: '所有校区' }, ...res.result]
    }
  })
}

const loadData = () => {
  uni.showLoading({ title: '加载中...' })
  wx.cloud.callFunction({
    name: 'api',
    data: {
      $url: 'admin/reservations', // Need to ensure backend has this
      campus_id: selectedCampus.value?.id,
      date: selectedDate.value
    },
    success: res => {
      uni.hideLoading()
      list.value = res.result || []
    },
    fail: err => {
      uni.hideLoading()
      // Fallback mock if backend not ready
      console.log('Backend API might be missing, showing empty list')
      list.value = []
    }
  })
}

const handleCampusChange = (e) => {
  selectedCampus.value = campuses.value[e.detail.value]
  loadData()
}

const handleDateChange = (e) => {
  selectedDate.value = e.detail.value
  loadData()
}

const getStatusText = (item) => {
  if (item.status === 'cancelled') return '已取消'
  if (item.key_returned) return '已归还'
  if (item.key_picked_up) return '使用中'
  return '待使用'
}

const getStatusClass = (item) => {
  if (item.status === 'cancelled') return 'status-grey'
  if (item.key_returned) return 'status-grey'
  if (item.key_picked_up) return 'status-green'
  return 'status-blue'
}

const updateStatus = (item, action) => {
  // Implement status update logic
  uni.showToast({ title: '功能开发中', icon: 'none' })
}

onMounted(() => {
  fetchCampuses()
  loadData()
})
</script>

<style lang="scss">
.header-bar { padding: 30rpx 0; margin-bottom: 20rpx; }
.page-title { font-size: 36rpx; font-weight: bold; color: #333; padding-left: 20rpx; border-left: 8rpx solid #333; }

.filter-bar {
  display: flex;
  background: #fff;
  padding: 20rpx;
  margin-bottom: 20rpx;
}

.picker-item {
  padding: 10rpx 30rpx;
  background: #f5f5f5;
  border-radius: 30rpx;
  font-size: 26rpx;
  color: #333;
  margin-right: 20rpx;
}

.res-card { padding: 30rpx; margin-bottom: 20rpx; }
.res-header { display: flex; justify-content: space-between; margin-bottom: 20rpx; padding-bottom: 15rpx; border-bottom: 1rpx solid #f5f5f5; }
.res-date { font-weight: bold; font-size: 30rpx; }
.res-status { font-size: 26rpx; }
.status-blue { color: #4eb8fe; }
.status-green { color: #67c23a; }
.status-grey { color: #999; }

.res-row { display: flex; margin-bottom: 10rpx; font-size: 28rpx; }
.label { color: #999; width: 100rpx; }
.value { color: #333; flex: 1; }

.res-footer { display: flex; justify-content: flex-end; margin-top: 20rpx; padding-top: 20rpx; border-top: 1rpx solid #f5f5f5; }
.btn-action { margin-left: 20rpx; background: #fff; border: 1rpx solid #ccc; color: #333; font-size: 24rpx; }

.empty-state { text-align: center; padding: 100rpx 0; color: #999; }
</style>
