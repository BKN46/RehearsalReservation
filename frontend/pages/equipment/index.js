Page({
  data: {
    currentTab: 0,
    campuses: [{id: 0, name: '全部'}, {id: 1, name: '学院路校区'}, {id: 2, name: '沙河校区'}],
    campusIndex: 0,
    equipmentList: [],
    
    // Register form
    regName: '',
    regType: '',
    regCampusIndex: 0,
    regLocation: '',
    regContact: '',
    regNotes: '',
    regShared: true,

    // Borrow modal
    showBorrowModal: false,
    selectedItem: null,
    borrowNotes: ''
  },

  onLoad() {
    this.fetchEquipment()
  },

  switchTab(e) {
    this.setData({ currentTab: parseInt(e.currentTarget.dataset.idx) })
  },

  bindCampusChange(e) {
    this.setData({ campusIndex: e.detail.value })
    this.fetchEquipment()
  },

  fetchEquipment() {
    const campusId = this.data.campuses[this.data.campusIndex].id
    const data = { $url: 'equipment/list', is_shared: true }
    if (campusId !== 0) {
      data.campus_id = campusId
    }

    wx.cloud.callFunction({
      name: 'api',
      data: data,
      success: res => {
        this.setData({ equipmentList: res.result })
      }
    })
  },

  inputChange(e) {
    const field = e.currentTarget.dataset.field
    this.setData({ [field]: e.detail.value })
  },

  bindRegCampusChange(e) {
    this.setData({ regCampusIndex: e.detail.value })
  },

  switchChange(e) {
    this.setData({ regShared: e.detail.value })
  },

  registerEquipment() {
    const { regName, regType, regCampusIndex, regLocation, regContact, regNotes, regShared, campuses } = this.data
    
    if (!regName || !regType || !regLocation || !regContact) {
      wx.showToast({ title: '请填写必填项', icon: 'none' })
      return
    }

    const campusId = campuses[regCampusIndex].id
    if (campusId === 0) {
       wx.showToast({ title: '请选择校区', icon: 'none' })
       return
    }

    wx.showLoading({ title: '提交中...' })
    wx.cloud.callFunction({
      name: 'api',
      data: {
        $url: 'equipment/register',
        campus_id: campusId,
        equipment_name: regName,
        equipment_type: regType,
        location: regLocation,
        contact: regContact,
        notes: regNotes,
        is_shared: regShared
      },
      success: res => {
        wx.hideLoading()
        wx.showToast({ title: '登记成功', icon: 'success' })
        this.setData({ 
            currentTab: 0,
            regName: '', regType: '', regLocation: '', regContact: '', regNotes: ''
        })
        this.fetchEquipment()
      },
      fail: err => {
        wx.hideLoading()
        console.error(err)
        wx.showToast({ title: '登记失败', icon: 'none' })
      }
    })
  },

  showBorrowDialog(e) {
    this.setData({
      showBorrowModal: true,
      selectedItem: e.currentTarget.dataset.item,
      borrowNotes: ''
    })
  },

  closeBorrowDialog() {
    this.setData({ showBorrowModal: false })
  },

  confirmBorrow() {
    const { selectedItem, borrowNotes } = this.data
    wx.showLoading({ title: '提交中...' })
    wx.cloud.callFunction({
      name: 'api',
      data: {
        $url: 'equipment/borrow',
        equipment_name: selectedItem.equipment_name,
        equipment_type: selectedItem.equipment_type,
        notes: borrowNotes
      },
      success: res => {
        wx.hideLoading()
        wx.showToast({ title: '借用登记成功', icon: 'success' })
        this.closeBorrowDialog()
      },
      fail: err => {
        wx.hideLoading()
        console.error(err)
        wx.showToast({ title: '失败', icon: 'none' })
      }
    })
  }
})
