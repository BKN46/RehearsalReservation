<template>
  <view class="container">
    <view class="form-card card">
      <view class="form-item">
        <text class="label">姓名</text>
        <input class="input" v-model="formData.name" placeholder="姓名" />
      </view>
      <view class="form-item">
        <text class="label">学号</text>
        <input class="input" v-model="formData.student_id" placeholder="学号" />
      </view>
      <view class="form-item">
        <text class="label">联系方式</text>
        <input class="input" v-model="formData.phone" placeholder="联系方式" />
      </view>
      <button class="btn-submit" @click="saveProfile">保存</button>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'

const formData = ref({
  name: '',
  student_id: '',
  phone: ''
})

onLoad(() => {
  const app = getApp()
  if (app.globalData.userInfo) {
    formData.value = { ...app.globalData.userInfo }
  }
})

const saveProfile = () => {
  uni.showLoading({ title: '保存中...' })
  wx.cloud.callFunction({
    name: 'api',
    data: {
      $url: 'auth/register', // Re-use register for update
      ...formData.value
    },
    success: res => {
      uni.hideLoading()
      if (res.result.error) {
        uni.showToast({ title: res.result.error, icon: 'none' })
      } else {
        const app = getApp()
        app.globalData.userInfo = { ...app.globalData.userInfo, ...formData.value }
        uni.showToast({ title: '保存成功', icon: 'success' })
        setTimeout(() => uni.navigateBack(), 1500)
      }
    },
    fail: err => {
      uni.hideLoading()
      uni.showToast({ title: '保存失败', icon: 'none' })
    }
  })
}
</script>

<style lang="scss">
.form-card { padding: 40rpx; }
.form-item { margin-bottom: 30rpx; }
.label { display: block; margin-bottom: 10rpx; color: #666; font-size: 28rpx; }
.input { background: #f9f9f9; height: 80rpx; padding: 0 20rpx; border-radius: 8rpx; font-size: 30rpx; }
.btn-submit { background: #333; color: #fff; margin-top: 40rpx; font-size: 30rpx; }
</style>
