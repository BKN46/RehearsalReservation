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

    <view class="manager-list">
      <view v-for="item in managers" :key="item._id" class="manager-card card">
        <view class="info">
          <view class="name">{{ item.name }}</view>
          <view class="contact">{{ item.contact }}</view>
        </view>
        <button class="btn-delete" size="mini" @click="deleteManager(item._id)">删除</button>
      </view>
      
      <view v-if="managers.length === 0" class="empty-state">
        <text>暂无管理员</text>
      </view>
    </view>

    <button class="btn-add" @click="showAddModal = true">+</button>

    <!-- Add Modal (Simple overlay implementation) -->
    <view class="modal-overlay" v-if="showAddModal" @click="showAddModal = false">
      <view class="modal-content" @click.stop>
        <view class="modal-title">添加管理员</view>
        <input class="modal-input" v-model="newManager.name" placeholder="姓名" />
        <input class="modal-input" v-model="newManager.contact" placeholder="联系方式" />
        <view class="modal-actions">
          <button class="btn-cancel" @click="showAddModal = false">取消</button>
          <button class="btn-confirm" @click="addManager">确定</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const campuses = ref([])
const selectedCampusId = ref(null)
const managers = ref([])
const showAddModal = ref(false)
const newManager = ref({ name: '', contact: '' })

const fetchCampuses = () => {
  wx.cloud.callFunction({
    name: 'api',
    data: { $url: 'reservation/campuses' },
    success: res => {
      campuses.value = res.result
      if (res.result.length > 0) {
        selectedCampusId.value = res.result[0].id
        fetchManagers()
      }
    }
  })
}

const selectCampus = (id) => {
  selectedCampusId.value = id
  fetchManagers()
}

const fetchManagers = () => {
  if (!selectedCampusId.value) return
  
  uni.showLoading({ title: '加载中...' })
  wx.cloud.callFunction({
    name: 'api',
    data: {
      $url: 'admin/key-managers',
      campus_id: selectedCampusId.value
    },
    success: res => {
      uni.hideLoading()
      managers.value = res.result
    },
    fail: err => {
      uni.hideLoading()
      console.error(err)
    }
  })
}

const addManager = () => {
  if (!newManager.value.name || !newManager.value.contact) {
    uni.showToast({ title: '请填写完整', icon: 'none' })
    return
  }

  uni.showLoading({ title: '添加中...' })
  wx.cloud.callFunction({
    name: 'api',
    data: {
      $url: 'admin/key-managers',
      httpMethod: 'POST',
      campus_id: selectedCampusId.value,
      name: newManager.value.name,
      contact: newManager.value.contact
    },
    success: res => {
      uni.hideLoading()
      if (res.result.error) {
        uni.showToast({ title: res.result.error, icon: 'none' })
      } else {
        uni.showToast({ title: '添加成功', icon: 'success' })
        showAddModal.value = false
        newManager.value = { name: '', contact: '' }
        fetchManagers()
      }
    },
    fail: err => {
      uni.hideLoading()
      console.error(err)
      uni.showToast({ title: '添加失败', icon: 'none' })
    }
  })
}

const deleteManager = (id) => {
  uni.showModal({
    title: '确认删除',
    content: '确定要删除该管理员吗？',
    success: (res) => {
      if (res.confirm) {
        uni.showLoading({ title: '删除中...' })
        wx.cloud.callFunction({
          name: 'api',
          data: {
            $url: 'admin/key-managers',
            httpMethod: 'DELETE',
            id: id
          },
          success: res => {
            uni.hideLoading()
            uni.showToast({ title: '删除成功', icon: 'success' })
            fetchManagers()
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

.manager-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx;
  margin-bottom: 20rpx;
}

.name {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.contact {
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

.modal-input {
  border: 1rpx solid #eee;
  height: 80rpx;
  padding: 0 20rpx;
  margin-bottom: 20rpx;
  border-radius: 8rpx;
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
