const app = getApp()

Page({
  data: {
    campuses: [],
    selectedCampusId: null,
    weekDays: [],
    timeSlots: [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21],
    weeklyReservations: [],
    unavailableTimes: [],
    keyManagers: [],
    keyPickups: [],
    userWeeklyHours: null,
    selectedSlot: null
  },

  onLoad() {
    this.calculateWeekDays()
    this.fetchCampuses()
  },

  onShow() {
    if (this.data.selectedCampusId) {
      this.loadData()
      this.loadMyWeeklyHours()
    }
  },

  calculateWeekDays() {
    const now = new Date()
    const currentHour = now.getHours()
    const dayOfWeek = now.getDay() // 0=Sun
    
    let baseDate = new Date(now)
    if (dayOfWeek === 0 && currentHour >= 22) {
      baseDate.setDate(now.getDate() + 1)
    }
    
    const adjustedDayOfWeek = baseDate.getDay() || 7
    const monday = new Date(baseDate)
    monday.setDate(baseDate.getDate() - adjustedDayOfWeek + 1)

    const days = []
    const dayNames = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    
    for (let i = 0; i < 7; i++) {
      const d = new Date(monday)
      d.setDate(monday.getDate() + i)
      const year = d.getFullYear()
      const month = String(d.getMonth() + 1).padStart(2, '0')
      const day = String(d.getDate()).padStart(2, '0')
      days.push({
        date: `${year}-${month}-${day}`,
        dayName: dayNames[i],
        dateText: `${d.getMonth() + 1}/${d.getDate()}`,
        reservations: {}, // Map hour -> reservation
        unavailable: {} // Map hour -> boolean
      })
    }
    this.setData({ weekDays: days })
  },

  fetchCampuses() {
    wx.cloud.callFunction({
      name: 'api',
      data: { $url: 'reservation/campuses' },
      success: res => {
        const campuses = res.result
        this.setData({ campuses })
        if (campuses.length > 0) {
          this.setData({ selectedCampusId: campuses[0].id })
          this.loadData()
          this.loadMyWeeklyHours()
        }
      }
    })
  },

  loadData() {
    if (!this.data.selectedCampusId) return
    
    wx.showLoading({ title: '加载中...' })
    
    const p1 = wx.cloud.callFunction({
      name: 'api',
      data: { 
        $url: 'reservation/weekly',
        campus_id: this.data.selectedCampusId
      }
    })

    const p2 = wx.cloud.callFunction({
      name: 'api',
      data: {
        $url: 'admin/unavailable-times',
        campus_id: this.data.selectedCampusId
      }
    })

    const p3 = wx.cloud.callFunction({
      name: 'api',
      data: {
        $url: 'admin/key-managers',
        campus_id: this.data.selectedCampusId
      }
    })

    const p4 = wx.cloud.callFunction({
      name: 'api',
      data: {
        $url: 'key/pickups',
        campus_id: this.data.selectedCampusId
      }
    })

    Promise.all([p1, p2, p3, p4]).then(([res1, res2, res3, res4]) => {
      wx.hideLoading()
      const reservations = res1.result.reservations
      const unavailable = res2.result
      
      this.processScheduleData(reservations, unavailable)
      
      this.setData({
        weeklyReservations: reservations,
        unavailableTimes: unavailable,
        keyManagers: res3.result,
        keyPickups: res4.result
      })
    }).catch(err => {
      wx.hideLoading()
      console.error(err)
      wx.showToast({ title: '加载失败', icon: 'none' })
    })
  },

  processScheduleData(reservations, unavailable) {
    const weekDays = this.data.weekDays.map(day => {
      const dayRes = {}
      const dayUnavail = {}
      const dayOfWeek = new Date(day.date).getDay()

      // Process Unavailable
      unavailable.forEach(u => {
        let match = false
        if (u.date) {
          match = u.date === day.date
        } else if (u.day_of_week !== null && u.day_of_week !== undefined) {
          match = u.day_of_week === dayOfWeek
        } else {
          match = true
        }

        if (match) {
          for (let h = u.start_hour; h < u.end_hour; h++) {
            dayUnavail[h] = true
          }
        }
      })

      // Process Reservations
      reservations.forEach(r => {
        if (r.date === day.date && r.status === 'active') {
          dayRes[r.start_hour] = r
        }
      })

      return {
        ...day,
        reservations: dayRes,
        unavailable: dayUnavail
      }
    })

    this.setData({ weekDays })
  },

  loadMyWeeklyHours() {
    wx.cloud.callFunction({
      name: 'api',
      data: { $url: 'reservation/my-reservations' },
      success: res => {
        const reservations = res.result
        const now = new Date()
        const dayOfWeek = now.getDay()
        const diff = now.getDate() - dayOfWeek + (dayOfWeek == 0 ? -6 : 1)
        const monday = new Date(now)
        monday.setDate(diff)
        monday.setHours(0,0,0,0)
        
        const sunday = new Date(monday)
        sunday.setDate(monday.getDate() + 6)
        sunday.setHours(23,59,59,999)

        const weeklyRes = reservations.filter(r => {
          const d = new Date(r.date)
          return d >= monday && d <= sunday && r.status === 'active'
        })

        let total = 0
        weeklyRes.forEach(r => total += (r.end_hour - r.start_hour))
        this.setData({ userWeeklyHours: total })
      }
    })
  },

  selectCampus(e) {
    const id = e.currentTarget.dataset.id
    this.setData({ 
      selectedCampusId: id,
      selectedSlot: null
    })
    this.loadData()
  },

  selectSlot(e) {
    const { date, hour } = e.currentTarget.dataset
    const dayData = this.data.weekDays.find(d => d.date === date)
    
    const now = new Date()
    const slotDate = new Date(date)
    slotDate.setHours(hour)
    if (slotDate < now) return

    if (dayData.unavailable[hour]) return

    const res = dayData.reservations[hour]
    if (res) {
      let keyStatus = '未领取钥匙'
      if (res.key_returned) keyStatus = '已归还钥匙'
      else if (res.key_picked_up) keyStatus = '已领取钥匙'
      
      wx.showModal({
        title: '预约详情',
        content: `${res.user_name}\n${res.start_hour}:00-${res.end_hour}:00\n${keyStatus}`,
        showCancel: false
      })
      return
    }

    this.setData({
      selectedSlot: { date, hour }
    })
  },

  confirmBooking() {
    if (!this.data.selectedSlot) return

    wx.showModal({
      title: '确认预约',
      content: `确定预约 ${this.data.selectedSlot.date} ${this.data.selectedSlot.hour}:00 - ${this.data.selectedSlot.hour + 1}:00 吗？`,
      success: (res) => {
        if (res.confirm) {
          this.doBooking()
        }
      }
    })
  },

  doBooking() {
    wx.showLoading({ title: '提交中...' })
    const userInfo = app.globalData.userInfo

    wx.cloud.callFunction({
      name: 'api',
      data: {
        $url: 'reservation/create',
        campus_id: this.data.selectedCampusId,
        date: this.data.selectedSlot.date,
        start_hour: this.data.selectedSlot.hour,
        end_hour: this.data.selectedSlot.hour + 1,
        student_id: userInfo?.student_id || 'anonymous',
        name: userInfo?.name || 'Anonymous',
        contact: userInfo?.phone || ''
      },
      success: res => {
        wx.hideLoading()
        if (res.result.error) {
          wx.showToast({ title: res.result.error, icon: 'none' })
        } else {
          wx.showToast({ title: '预约成功', icon: 'success' })
          this.setData({ selectedSlot: null })
          this.loadData()
          this.loadMyWeeklyHours()
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
