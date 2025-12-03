Page({
  data: {
    activeTab: 'active',
    reservations: [],
    displayList: []
  },

  onShow() {
    this.fetchReservations()
  },

  switchTab(e) {
    const tab = e.currentTarget.dataset.tab
    this.setData({ activeTab: tab })
    this.updateDisplayList()
  },

  fetchReservations() {
    wx.showLoading({ title: '加载中...' })
    wx.cloud.callFunction({
      name: 'api',
      data: { $url: 'reservation/my-reservations' },
      success: res => {
        wx.hideLoading()
        const reservations = res.result.sort((a, b) => {
          if (a.date !== b.date) return b.date.localeCompare(a.date)
          return b.start_hour - a.start_hour
        })
        this.setData({ reservations })
        this.updateDisplayList()
      },
      fail: err => {
        wx.hideLoading()
        console.error(err)
        wx.showToast({ title: '加载失败', icon: 'none' })
      }
    })
  },

  updateDisplayList() {
    const now = new Date()
    const today = now.toISOString().split('T')[0]
    const currentHour = now.getHours()
    const { activeTab, reservations } = this.data

    const list = reservations.filter(r => {
      if (activeTab === 'active') {
        if (r.status !== 'active') return false
        if (r.date > today) return true
        if (r.date === today && r.end_hour > currentHour) return true
        return false
      } else {
        if (r.status !== 'active') return true
        if (r.date < today) return true
        if (r.date === today && r.end_hour <= currentHour) return true
        return false
      }
    }).map(item => {
      let statusText = '待使用'
      let statusClass = 'status-blue'

      if (item.status === 'cancelled') {
        statusText = '已取消'
        statusClass = 'status-grey'
      } else if (item.key_returned) {
        statusText = '已完成'
        statusClass = 'status-grey'
      } else if (item.key_picked_up) {
        statusText = '使用中'
        statusClass = 'status-green'
      }

      return {
        ...item,
        statusText,
        statusClass
      }
    })

    this.setData({ displayList: list })
  },

  cancelReservation(e) {
    const item = e.currentTarget.dataset.item
    wx.showModal({
      title: '取消预约',
      content: '确定要取消该预约吗？',
      success: (res) => {
        if (res.confirm) {
          this.doCancel(item._id)
        }
      }
    })
  },

  doCancel(id) {
    wx.showLoading({ title: '处理中...' })
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
          wx.showToast({ title: '已取消', icon: 'success' })
          this.fetchReservations()
        }
      },
      fail: err => {
        wx.hideLoading()
        console.error(err)
        wx.showToast({ title: '操作失败', icon: 'none' })
      }
    })
  }
})
