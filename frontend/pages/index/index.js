const app = getApp()

Page({
  data: {
    campuses: [],
    selectedCampusId: null,
    date: '',
    startDate: '',
    endDate: '',
    timeSlots: [],
    selectedSlot: null,
    reservations: [],
    unavailableTimes: []
  },

  onLoad() {
    const now = new Date()
    const dateStr = now.toISOString().split('T')[0]
    
    // Calculate end date (e.g., 2 weeks from now)
    const end = new Date()
    end.setDate(end.getDate() + 14)
    const endDateStr = end.toISOString().split('T')[0]

    this.setData({
      date: dateStr,
      startDate: dateStr,
      endDate: endDateStr
    })

    this.fetchCampuses()
  },

  onShow() {
    if (this.data.selectedCampusId) {
      this.loadData()
    }
  },

  fetchCampuses() {
    wx.cloud.callFunction({
      name: 'api',
      data: { $url: 'reservation/campuses' },
      success: res => {
        this.setData({ campuses: res.result })
        if (res.result.length > 0) {
          this.setData({ selectedCampusId: res.result[0].id })
          this.loadData()
        }
      }
    })
  },

  selectCampus(e) {
    const id = e.currentTarget.dataset.id
    this.setData({ selectedCampusId: id, selectedSlot: null })
    this.loadData()
  },

  bindDateChange(e) {
    this.setData({ date: e.detail.value, selectedSlot: null })
    this.loadData()
  },

  loadData() {
    wx.showLoading({ title: '加载中...' })
    const { selectedCampusId, date } = this.data
    
    // Fetch reservations and unavailable times in parallel
    const p1 = wx.cloud.callFunction({
      name: 'api',
      data: { 
        $url: 'reservation/date',
        campus_id: selectedCampusId,
        date: date
      }
    })

    const p2 = wx.cloud.callFunction({
      name: 'api',
      data: {
        $url: 'admin/unavailable-times',
        campus_id: selectedCampusId
      }
    })

    Promise.all([p1, p2]).then(([res1, res2]) => {
      wx.hideLoading()
      this.setData({
        reservations: res1.result,
        unavailableTimes: res2.result
      })
      this.processSlots()
    }).catch(err => {
      wx.hideLoading()
      console.error(err)
      wx.showToast({ title: '加载失败', icon: 'none' })
    })
  },

  processSlots() {
    const { reservations, unavailableTimes, date } = this.data
    const slots = []
    const currentHour = new Date().getHours()
    const isToday = date === new Date().toISOString().split('T')[0]
    const dayOfWeek = new Date(date).getDay() // 0-6

    for (let h = 8; h < 22; h++) {
      let status = 'available'
      let statusText = '可预约'

      // Check past time
      if (isToday && h <= currentHour) {
        status = 'disabled'
        statusText = '已过期'
      }

      // Check reservations
      const isReserved = reservations.some(r => r.start_hour <= h && r.end_hour > h)
      if (isReserved) {
        status = 'reserved'
        statusText = '已预约'
      }

      // Check unavailable times
      const isUnavailable = unavailableTimes.some(u => {
        // Check date specific
        if (u.date && u.date === date) {
          return u.start_hour <= h && u.end_hour > h
        }
        // Check day of week specific
        if (u.day_of_week !== null && u.day_of_week !== undefined) {
           // Cloud function uses JS getDay() (0-6)
           return u.day_of_week === dayOfWeek && u.start_hour <= h && u.end_hour > h
        }
        // Check all dates (if no date and no day_of_week)
        if (!u.date && (u.day_of_week === null || u.day_of_week === undefined)) {
           return u.start_hour <= h && u.end_hour > h
        }
        return false
      })

      if (isUnavailable) {
        status = 'unavailable'
        statusText = '不可用'
      }

      slots.push({
        hour: h,
        status,
        statusText
      })
    }

    this.setData({ timeSlots: slots })
  },

  selectSlot(e) {
    const hour = e.currentTarget.dataset.hour
    const slot = this.data.timeSlots.find(s => s.hour === hour)
    
    if (slot.status !== 'available') {
      return
    }

    this.setData({ selectedSlot: hour })
  },

  confirmBooking() {
    const { selectedCampusId, date, selectedSlot } = this.data
    if (selectedSlot === null) return

    wx.showModal({
      title: '确认预约',
      content: `确定预约 ${date} ${selectedSlot}:00 - ${selectedSlot+1}:00 吗？`,
      success: (res) => {
        if (res.confirm) {
          this.doBooking()
        }
      }
    })
  },

  doBooking() {
    wx.showLoading({ title: '提交中...' })
    const { selectedCampusId, date, selectedSlot } = this.data
    const userInfo = app.globalData.userInfo

    wx.cloud.callFunction({
      name: 'api',
      data: {
        $url: 'reservation/create',
        campus_id: selectedCampusId,
        date: date,
        start_hour: selectedSlot,
        end_hour: selectedSlot + 1,
        student_id: userInfo.student_id,
        name: userInfo.name,
        contact: userInfo.phone
      },
      success: res => {
        wx.hideLoading()
        if (res.result.error) {
          wx.showToast({ title: res.result.error, icon: 'none' })
        } else {
          wx.showToast({ title: '预约成功', icon: 'success' })
          this.setData({ selectedSlot: null })
          this.loadData()
        }
      },
      fail: err => {
        wx.hideLoading()
        console.error(err)
        wx.showToast({ title: '预约失败', icon: 'none' })
      }
    })
  }
})
