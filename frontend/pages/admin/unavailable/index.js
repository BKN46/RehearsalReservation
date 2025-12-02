Page({
  data: {
    campuses: [{id: 1, name: '学院路校区'}, {id: 2, name: '沙河校区'}],
    campusIndex: 0,
    days: ['周日', '周一', '周二', '周三', '周四', '周五', '周六'],
    dayIndex: -1,
    list: [],
    startHour: '',
    endHour: '',
    reason: '',
    date: ''
  },

  onLoad() {
    this.fetchList()
  },

  fetchList() {
    wx.cloud.callFunction({
      name: 'api',
      data: { $url: 'admin/unavailable-times' },
      success: res => {
        this.setData({ list: res.result })
      }
    })
  },

  bindCampusChange(e) { this.setData({ campusIndex: e.detail.value }) },
  bindDateChange(e) { this.setData({ date: e.detail.value, dayIndex: -1 }) },
  bindDayChange(e) { this.setData({ dayIndex: e.detail.value, date: '' }) },
  inputChange(e) { this.setData({ [e.currentTarget.dataset.field]: e.detail.value }) },

  add() {
    const { campusIndex, startHour, endHour, reason, date, dayIndex, campuses } = this.data
    if (!startHour || !endHour) return

    const data = {
      $url: 'admin/unavailable-times',
      httpMethod: 'POST',
      campus_id: campuses[campusIndex].id,
      start_hour: parseInt(startHour),
      end_hour: parseInt(endHour),
      reason
    }

    if (date) data.date = date
    if (dayIndex >= 0) data.day_of_week = parseInt(dayIndex)

    wx.cloud.callFunction({
      name: 'api',
      data: data,
      success: res => {
        wx.showToast({ title: '添加成功' })
        this.fetchList()
      }
    })
  },

  remove(e) {
    const id = e.currentTarget.dataset.id
    wx.cloud.callFunction({
      name: 'api',
      data: {
        $url: 'admin/unavailable-times',
        httpMethod: 'DELETE',
        id
      },
      success: res => {
        wx.showToast({ title: '删除成功' })
        this.fetchList()
      }
    })
  }
})
