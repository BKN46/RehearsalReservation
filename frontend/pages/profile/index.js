const app = getApp()

Page({
  data: {
    userInfo: null,
    isAdmin: false
  },

  onShow() {
    this.checkLogin()
  },

  checkLogin() {
    const userInfo = app.globalData.userInfo
    this.setData({ userInfo })
    
    if (userInfo) {
      // Check admin status
      wx.cloud.callFunction({
        name: 'api',
        data: { $url: 'auth/check_admin' },
        success: res => {
          this.setData({ isAdmin: res.result.isAdmin })
        }
      })
    } else {
      this.setData({ isAdmin: false })
    }
  },

  goToLogin() {
    wx.navigateTo({ url: '/pages/login/index' })
  },

  navigateTo(e) {
    const url = e.currentTarget.dataset.url
    if (!this.data.userInfo) {
      this.goToLogin()
      return
    }
    wx.navigateTo({ url })
  },

  handleLogout() {
    wx.showModal({
      title: '提示',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          app.globalData.userInfo = null
          app.globalData.isLoggedIn = false
          this.setData({
            userInfo: null,
            isAdmin: false
          })
          wx.showToast({ title: '已退出', icon: 'none' })
        }
      }
    })
  }
})
