Page({
  data: {
    campuses: [],
    selectedCampusId: null,
    managers: [],
    showAddModal: false,
    newManagerName: '',
    newManagerContact: ''
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
          this.fetchManagers()
        }
      }
    })
  },

  selectCampus(e) {
    const id = e.currentTarget.dataset.id
    this.setData({ selectedCampusId: id })
    this.fetchManagers()
  },

  fetchManagers() {
    if (!this.data.selectedCampusId) return
    
    wx.showLoading({ title: '加载中...' })
    wx.cloud.callFunction({
      name: 'api',
      data: {
        $url: 'admin/key-managers',
        campus_id: this.data.selectedCampusId
      },
      success: res => {
        wx.hideLoading()
        this.setData({ managers: res.result })
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

  addManager() {
    const { newManagerName, newManagerContact, selectedCampusId } = this.data
    if (!newManagerName || !newManagerContact) {
      wx.showToast({ title: '请填写完整', icon: 'none' })
      return
    }

    wx.showLoading({ title: '添加中...' })
    wx.cloud.callFunction({
      name: 'api',
      data: {
        $url: 'admin/key-managers/add',
        campus_id: selectedCampusId,
        name: newManagerName,
        contact: newManagerContact
      },
      success: res => {
        wx.hideLoading()
        if (res.result.error) {
          wx.showToast({ title: res.result.error, icon: 'none' })
        } else {
          wx.showToast({ title: '添加成功', icon: 'success' })
          this.setData({
            showAddModal: false,
            newManagerName: '',
            newManagerContact: ''
          })
          this.fetchManagers()
        }
      },
      fail: err => {
        wx.hideLoading()
        console.error(err)
        wx.showToast({ title: '添加失败', icon: 'none' })
      }
    })
  },

  deleteManager(e) {
    const id = e.currentTarget.dataset.id
    wx.showModal({
      title: '确认删除',
      content: '确定要删除该管理员吗？',
      success: (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '删除中...' })
          wx.cloud.callFunction({
            name: 'api',
            data: {
              $url: 'admin/key-managers/delete',
              id: id
            },
            success: res => {
              wx.hideLoading()
              wx.showToast({ title: '删除成功', icon: 'success' })
              this.fetchManagers()
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
