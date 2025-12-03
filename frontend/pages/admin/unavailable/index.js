Page({
  data: {
    campuses: [],
    selectedCampusId: null,
    rules: [],
    showAddModal: false,
    addType: 'weekly',
    weekDays: [
      { id: 1, name: '周一' },
      { id: 2, name: '周二' },
      { id: 3, name: '周三' },
      { id: 4, name: '周四' },
      { id: 5, name: '周五' },
      { id: 6, name: '周六' },
      { id: 0, name: '周日' }
    ],
    selectedDay: null,
    selectedDate: '',
    startHour: '',
    endHour: ''
  },

  onLoad() {
    this.fetchCampuses()
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
          this.fetchRules()
        }
      }
    })
  },

  selectCampus(e) {
    const id = e.currentTarget.dataset.id
    this.setData({ selectedCampusId: id })
    this.fetchRules()
  },

  fetchRules() {
    if (!this.data.selectedCampusId) return
    
    wx.showLoading({ title: '加载中...' })
    wx.cloud.callFunction({
      name: 'api',
      data: {
        $url: 'admin/unavailable-times',
        campus_id: this.data.selectedCampusId
      },
      success: res => {
        wx.hideLoading()
        const rules = res.result.map(item => {
          let displayText = '未知规则'
          if (item.date) {
            displayText = `日期: ${item.date}`
          } else if (item.day_of_week !== null) {
            const day = this.data.weekDays.find(d => d.id === item.day_of_week)
            displayText = `每周: ${day ? day.name : '未知'}`
          }
          return { ...item, displayText }
        })
        this.setData({ rules })
      },
      fail: err => {
        wx.hideLoading()
        console.error(err)
      }
    })
  },

  showAddModal() {
    this.setData({ showAddModal: true })
  },

  hideAddModal() {
    this.setData({ showAddModal: false })
  },

  preventBubble() {},

  handleTypeChange(e) {
    this.setData({ addType: e.detail.value })
  },

  handleDayChange(e) {
    this.setData({ selectedDay: e.detail.value })
  },

  handleDateChange(e) {
    this.setData({ selectedDate: e.detail.value })
  },

  addRule() {
    const { startHour, endHour, addType, selectedDay, selectedDate, selectedCampusId, weekDays } = this.data

    if (!startHour || !endHour) {
      wx.showToast({ title: '请填写时间', icon: 'none' })
      return
    }

    const data = {
      $url: 'admin/unavailable-times/add',
      campus_id: selectedCampusId,
      start_hour: parseInt(startHour),
      end_hour: parseInt(endHour)
    }

    if (addType === 'weekly') {
      if (selectedDay === null) {
        wx.showToast({ title: '请选择星期', icon: 'none' })
        return
      }
      data.day_of_week = weekDays[selectedDay].id
    } else {
      if (!selectedDate) {
        wx.showToast({ title: '请选择日期', icon: 'none' })
        return
      }
      data.date = selectedDate
    }

    wx.showLoading({ title: '添加中...' })
    wx.cloud.callFunction({
      name: 'api',
      data: data,
      success: res => {
        wx.hideLoading()
        if (res.result.error) {
          wx.showToast({ title: res.result.error, icon: 'none' })
        } else {
          wx.showToast({ title: '添加成功', icon: 'success' })
          this.setData({
            showAddModal: false,
            startHour: '',
            endHour: '',
            selectedDay: null,
            selectedDate: ''
          })
          this.fetchRules()
        }
      },
      fail: err => {
        wx.hideLoading()
        console.error(err)
        wx.showToast({ title: '添加失败', icon: 'none' })
      }
    })
  },

  deleteRule(e) {
    const id = e.currentTarget.dataset.id
    wx.showModal({
      title: '确认删除',
      content: '确定要删除该规则吗？',
      success: (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '删除中...' })
          wx.cloud.callFunction({
            name: 'api',
            data: {
              $url: 'admin/unavailable-times/delete',
              id: id
            },
            success: res => {
              wx.hideLoading()
              wx.showToast({ title: '删除成功', icon: 'success' })
              this.fetchRules()
            },
            fail: err => {
              wx.hideLoading()
              console.error(err)
              wx.showToast({ title: '删除失败', icon: 'none' })
            }
          })
        }
      }
    })
  }
})
