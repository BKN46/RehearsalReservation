const app = getApp()

Page({
  data: {
    loading: true,
    showRegisterForm: false,
    name: '',
    studentId: '',
    phone: ''
  },

  onLoad() {
    this.checkLogin()
  },

  checkLogin() {
    this.setData({ loading: true })
    wx.cloud.callFunction({
      name: 'api',
      data: { $url: 'user/login' },
      success: res => {
        this.setData({ loading: false })
        if (res.result.user) {
          app.globalData.userInfo = res.result.user
          app.globalData.is_admin = res.result.user.is_admin
          wx.switchTab({ url: '/pages/index/index' })
        } else {
          this.setData({ showRegisterForm: true })
        }
      },
      fail: err => {
        this.setData({ loading: false })
        console.error(err)
        wx.showToast({ title: '登录失败，请重试', icon: 'none' })
      }
    })
  },

  onNameInput(e) { this.setData({ name: e.detail.value }) },
  onStudentIdInput(e) { this.setData({ studentId: e.detail.value }) },
  onPhoneInput(e) { this.setData({ phone: e.detail.value }) },

  register() {
    if (!this.data.name || !this.data.studentId) {
      wx.showToast({ title: '请填写完整信息', icon: 'none' })
      return
    }
    
    wx.showLoading({ title: '注册中...' })
    wx.cloud.callFunction({
      name: 'api',
      data: {
        $url: 'user/register',
        name: this.data.name,
        student_id: this.data.studentId,
        phone: this.data.phone
      },
      success: res => {
        wx.hideLoading()
        if (res.result.error) {
          wx.showToast({ title: res.result.error, icon: 'none' })
        } else {
          wx.showToast({ title: '注册成功', icon: 'success' })
          this.checkLogin()
        }
      },
      fail: err => {
        wx.hideLoading()
        console.error(err)
        wx.showToast({ title: '注册失败', icon: 'none' })
      }
    })
  }
})
