Page({
  data: {
    campuses: [{id: 1, name: '学院路校区'}, {id: 2, name: '沙河校区'}],
    campusIndex: 0,
    list: [],
    name: '',
    contact: ''
  },

  onLoad() {
    this.fetchList()
  },

  fetchList() {
    wx.cloud.callFunction({
      name: 'api',
      data: { $url: 'admin/key-managers' },
      success: res => {
        this.setData({ list: res.result })
      }
    })
  },

  bindCampusChange(e) { this.setData({ campusIndex: e.detail.value }) },
  inputChange(e) { this.setData({ [e.currentTarget.dataset.field]: e.detail.value }) },

  add() {
    const { campusIndex, name, contact, campuses } = this.data
    if (!name || !contact) return

    wx.cloud.callFunction({
      name: 'api',
      data: {
        $url: 'admin/key-managers',
        httpMethod: 'POST',
        campus_id: campuses[campusIndex].id,
        name,
        contact
      },
      success: res => {
        wx.showToast({ title: '添加成功' })
        this.setData({ name: '', contact: '' })
        this.fetchList()
      }
    })
  },

  remove(e) {
    const id = e.currentTarget.dataset.id
    wx.cloud.callFunction({
      name: 'api',
      data: {
        $url: 'admin/key-managers',
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
