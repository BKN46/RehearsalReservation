const app = getApp()

Page({
  data: {
    name: '',
    student_id: '',
    phone: '',
    loading: false,
    isRegistering: true,
    hasLogo: false
  },

  onLoad() {
    if (app.globalData.userInfo) {
      const { name, student_id, phone } = app.globalData.userInfo
      this.setData({
        name,
        student_id,
        phone,
        isRegistering: false
      })
    }
  },

  handleLogin() {
    const { name, student_id, phone } = this.data
    if (!name || !student_id || !phone) {
      wx.showToast({ title: '请填写完整信息', icon: 'none' })
      return
    }

    this.setData({ loading: true })
    
    wx.cloud.callFunction({
      name: 'api',
      data: {
        $url: 'auth/register',
        name,
        student_id,
        phone
      },
      success: res => {
        this.setData({ loading: false })
        if (res.result.error) {
          wx.showToast({ title: res.result.error, icon: 'none' })
        } else {
          app.globalData.userInfo = res.result.user
          app.globalData.isLoggedIn = true
          
          wx.showToast({ title: '登录成功', icon: 'success' })
          
          setTimeout(() => {
            wx.switchTab({ url: '/pages/index/index' })
          }, 1500)
        }
      },
      fail: err => {
        this.setData({ loading: false })
        console.error(err)
        wx.showToast({ title: '登录失败', icon: 'none' })
      }
    })
  }
})
