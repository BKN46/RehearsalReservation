const app = getApp()

Page({
  data: {
    userInfo: {},
    isAdmin: false
  },

  onShow() {
    this.setData({
      userInfo: app.globalData.userInfo || {},
      isAdmin: app.globalData.is_admin || false
    })
  }
})
