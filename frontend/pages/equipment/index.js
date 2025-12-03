Page({
  data: {
    equipmentList: []
  },

  onShow() {
    this.fetchEquipment()
  },

  fetchEquipment() {
    wx.showLoading({ title: '加载中...' })
    wx.cloud.callFunction({
      name: 'api',
      data: { $url: 'equipment/list' },
      success: res => {
        wx.hideLoading()
        this.setData({ equipmentList: res.result })
      },
      fail: err => {
        wx.hideLoading()
        console.error(err)
        wx.showToast({ title: '加载失败', icon: 'none' })
      }
    })
  },

  reportIssue(e) {
    const item = e.currentTarget.dataset.item
    wx.showModal({
      title: '器材报修',
      content: `确定要报修 ${item.name} 吗？`,
      editable: true,
      placeholderText: '请简述故障情况',
      success: (res) => {
        if (res.confirm) {
          const description = res.content || '用户报修'
          this.doReport(item._id, description)
        }
      }
    })
  },

  doReport(id, description) {
    wx.showLoading({ title: '提交中...' })
    wx.cloud.callFunction({
      name: 'api',
      data: {
        $url: 'equipment/report',
        id: id,
        description: description
      },
      success: res => {
        wx.hideLoading()
        if (res.result.error) {
          wx.showToast({ title: res.result.error, icon: 'none' })
        } else {
          wx.showToast({ title: '报修成功', icon: 'success' })
          this.fetchEquipment()
        }
      },
      fail: err => {
        wx.hideLoading()
        console.error(err)
        wx.showToast({ title: '提交失败', icon: 'none' })
      }
    })
  }
})
