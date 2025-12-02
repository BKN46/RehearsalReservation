Page({
  data: {
    reservations: []
  },

  onShow() {
    this.fetchReservations()
  },

  fetchReservations() {
    wx.showLoading({ title: '加载中...' })
    wx.cloud.callFunction({
      name: 'api',
      data: { $url: 'reservation/my-reservations' },
      success: res => {
        wx.hideLoading()
        this.setData({ reservations: res.result })
      },
      fail: err => {
        wx.hideLoading()
        console.error(err)
        wx.showToast({ title: '加载失败', icon: 'none' })
      }
    })
  },

  cancelReservation(e) {
    const id = e.currentTarget.dataset.id
    wx.showModal({
      title: '提示',
      content: '确定要取消预约吗？',
      success: (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '取消中...' })
          wx.cloud.callFunction({
            name: 'api',
            data: { 
              $url: 'reservation/cancel',
              reservation_id: id
            },
            success: res => {
              wx.hideLoading()
              if (res.result.error) {
                wx.showToast({ title: res.result.error, icon: 'none' })
              } else {
                wx.showToast({ title: '取消成功', icon: 'success' })
                this.fetchReservations()
              }
            },
            fail: err => {
              wx.hideLoading()
              console.error(err)
              wx.showToast({ title: '取消失败', icon: 'none' })
            }
          })
        }
      }
    })
  },

  pickupKey(e) {
    const id = e.currentTarget.dataset.id
    wx.cloud.callFunction({
      name: 'api',
      data: { $url: 'key/pickup', reservation_id: id },
      success: res => {
        wx.showToast({ title: '登记成功', icon: 'success' })
        this.fetchReservations()
      }
    })
  },

  returnKey(e) {
    const id = e.currentTarget.dataset.id
    wx.cloud.callFunction({
      name: 'api',
      data: { $url: 'key/return', reservation_id: id },
      success: res => {
        wx.showToast({ title: '登记成功', icon: 'success' })
        this.fetchReservations()
      }
    })
  }
})
