<template>
  <view class="container">
    <view class="header-bar">
      <text class="page-title">器材管理</text>
    </view>

    <view class="equipment-list">
      <view v-for="item in equipmentList" :key="item._id" class="equipment-card card">
        <view class="equip-info">
          <view class="equip-name">{{ item.name }}</view>
          <view class="equip-status" :class="{ 'status-bad': item.status !== 'normal' }">
            {{ item.status === 'normal' ? '状态良好' : '需维修' }}
          </view>
        </view>
        
        <view class="equip-actions">
          <button 
            class="btn-report" 
            size="mini" 
            @click="reportIssue(item)"
            :disabled="item.status !== 'normal'"
          >
            {{ item.status === 'normal' ? '报修' : '已报修' }}
          </button>
        </view>
      </view>
    </view>

    <view v-if="equipmentList.length === 0" class="empty-state">
      <text>暂无器材信息</text>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'

const equipmentList = ref([])

const fetchEquipment = () => {
  uni.showLoading({ title: '加载中...' })
  wx.cloud.callFunction({
    name: 'api',
    data: { $url: 'equipment/list' },
    success: res => {
      uni.hideLoading()
      equipmentList.value = res.result
    },
    fail: err => {
      uni.hideLoading()
      console.error(err)
      uni.showToast({ title: '加载失败', icon: 'none' })
    }
  })
}

const reportIssue = (item) => {
  uni.showModal({
    title: '器材报修',
    content: `确定要报修 ${item.name} 吗？`,
    editable: true,
    placeholderText: '请简述故障情况',
    success: (res) => {
      if (res.confirm) {
        const description = res.content || '用户报修'
        doReport(item._id, description)
      }
    }
  })
}

const doReport = (id, description) => {
  uni.showToast({ title: '请直接联系管理员报修', icon: 'none' })
  return
  /* Backend support pending
  uni.showLoading({ title: '提交中...' })
  wx.cloud.callFunction({
    name: 'api',
    data: {
      $url: 'equipment/report',
      id: id,
      description: description
    },
    success: res => {
      uni.hideLoading()
      if (res.result.error) {
        uni.showToast({ title: res.result.error, icon: 'none' })
      } else {
        uni.showToast({ title: '报修成功', icon: 'success' })
        fetchEquipment()
      }
    },
    fail: err => {
      uni.hideLoading()
      console.error(err)
      uni.showToast({ title: '提交失败', icon: 'none' })
    }
  })
  */
}

onShow(() => {
  fetchEquipment()
})
</script>

<style lang="scss">
.header-bar {
  padding: 30rpx 0;
  margin-bottom: 20rpx;
}

.page-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
  padding-left: 20rpx;
  border-left: 8rpx solid #333;
}

.equipment-list {
  padding-bottom: 40rpx;
}

.equipment-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx;
  margin-bottom: 20rpx;
}

.equip-info {
  flex: 1;
}

.equip-name {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 10rpx;
}

.equip-status {
  font-size: 24rpx;
  color: #67c23a; /* Green for good */
  
  &.status-bad {
    color: #f56c6c; /* Red for bad */
  }
}

.equip-actions {
  margin-left: 20rpx;
}

.btn-report {
  background-color: #fff;
  color: #333;
  border: 1rpx solid #ccc;
  font-size: 24rpx;
  padding: 0 30rpx;
  line-height: 50rpx;
  
  &[disabled] {
    background-color: #f5f5f5;
    color: #999;
    border-color: #eee;
  }
}

.empty-state {
  text-align: center;
  padding: 100rpx 0;
  color: #999;
  font-size: 28rpx;
}
</style>
