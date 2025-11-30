import api from '@/utils/request'

export const reservationService = {
  // 获取校区列表
  getCampuses() {
    return api.get('/reservation/campuses')
  },

  // 创建预约
  createReservation(data) {
    return api.post('/reservation/create', data)
  },

  // 获取我的预约
  getMyReservations() {
    return api.get('/reservation/my-reservations')
  },

  // 获取本周预约
  getWeeklyReservations(campusId) {
    return api.get('/reservation/weekly', { params: { campus_id: campusId } })
  },

  // 获取指定日期预约
  getReservationsByDate(campusId, date) {
    return api.get(`/reservation/date/${date}`, { params: { campus_id: campusId } })
  },

  // 取消预约
  cancelReservation(reservationId) {
    return api.delete(`/reservation/${reservationId}`)
  }
}

export const keyService = {
  // 登记取钥匙
  pickupKey(reservationId) {
    return api.post(`/key/pickup/${reservationId}`)
  },

  // 获取钥匙领取情况
  getKeyPickups(campusId) {
    return api.get('/key/pickups', { params: { campus_id: campusId } })
  },

  // 获取钥匙管理员
  getKeyManagers(campusId) {
    return api.get(`/key/managers/${campusId}`)
  }
}

export const equipmentService = {
  // 借用设备
  borrowEquipment(data) {
    return api.post('/equipment/borrow', data)
  },

  // 归还设备
  returnEquipment(borrowId) {
    return api.post(`/equipment/borrow/${borrowId}/return`)
  },

  // 获取借用记录
  getBorrows(status = 'borrowed') {
    return api.get('/equipment/borrows', { params: { status } })
  },

  // 获取我的借用记录
  getMyBorrows() {
    return api.get('/equipment/my-borrows')
  },

  // 登记设备
  registerEquipment(data) {
    return api.post('/equipment/register', data)
  },

  // 获取设备列表
  getEquipmentList(params) {
    return api.get('/equipment/list', { params })
  },

  // 获取我的设备
  getMyEquipment() {
    return api.get('/equipment/my-equipment')
  },

  // 更新设备
  updateEquipment(equipmentId, data) {
    return api.put(`/equipment/${equipmentId}`, data)
  },

  // 删除设备
  deleteEquipment(equipmentId) {
    return api.delete(`/equipment/${equipmentId}`)
  },

  // 获取设备类型
  getEquipmentTypes() {
    return api.get('/equipment/types')
  }
}

export const adminService = {
  // 获取不可预约时间段
  getUnavailableTimes(campusId) {
    return api.get('/admin/unavailable-times', { params: campusId ? { campus_id: campusId } : {} })
  },

  // 创建不可预约时间段
  createUnavailableTime(data) {
    return api.post('/admin/unavailable-times', data)
  },

  // 删除不可预约时间段
  deleteUnavailableTime(id) {
    return api.delete(`/admin/unavailable-times/${id}`)
  },

  // 获取钥匙管理员
  getKeyManagers(campusId) {
    return api.get('/admin/key-managers', { params: campusId ? { campus_id: campusId } : {} })
  },

  // 创建钥匙管理员
  createKeyManager(data) {
    return api.post('/admin/key-managers', data)
  },

  // 更新钥匙管理员
  updateKeyManager(id, data) {
    return api.put(`/admin/key-managers/${id}`, data)
  },

  // 删除钥匙管理员
  deleteKeyManager(id) {
    return api.delete(`/admin/key-managers/${id}`)
  },

  // 获取所有用户
  getAllUsers() {
    return api.get('/admin/users')
  },

  // 启用/禁用用户
  toggleUserActive(userId) {
    return api.put(`/admin/users/${userId}/toggle-active`)
  }
}
