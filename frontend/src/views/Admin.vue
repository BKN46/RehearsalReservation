<template>
  <div class="admin">
    <el-tabs v-model="activeTab">
      <!-- 用户管理 -->
      <el-tab-pane label="用户管理" name="users">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>用户管理</span>
              <div class="filter-section">
                <el-select 
                  v-model="userFilters.is_active" 
                  placeholder="状态" 
                  clearable
                  @change="loadUsers"
                  style="width: 120px; margin-right: 10px"
                >
                  <el-option label="启用" value="true" />
                  <el-option label="禁用" value="false" />
                </el-select>
                
                <el-select 
                  v-model="userFilters.year" 
                  placeholder="入学年份" 
                  clearable
                  @change="loadUsers"
                  style="width: 120px; margin-right: 10px"
                >
                  <el-option 
                    v-for="year in enrollmentYears" 
                    :key="year" 
                    :label="`${year}级`" 
                    :value="year" 
                  />
                </el-select>
                
                <el-input 
                  v-model="userFilters.search" 
                  placeholder="搜索姓名" 
                  clearable
                  @input="handleSearchUsers"
                  style="width: 200px; margin-right: 10px"
                  @keyup.enter="loadUsers"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>

                <el-button type="primary" @click="loadUsers" style="margin-right: 10px">搜索</el-button>
                <el-button type="danger" @click="handleAnnualReset">年度重置</el-button>
              </div>
            </div>
          </template>

          <el-table :data="users" style="width: 100%" v-loading="loadingUsers">
            <el-table-column label="操作" width="80">
              <template #default="{ row }">
                <el-button
                  :type="row.is_active ? 'danger' : 'success'"
                  size="small"
                  @click="handleToggleUserActive(row.id)"
                  :disabled="row.is_admin"
                >
                  {{ row.is_active ? '禁用' : '启用' }}
                </el-button>
              </template>
            </el-table-column>
            <el-table-column prop="is_active" label="状态" width="70">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
                  {{ row.is_active ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="name" label="姓名" width="100" />
            <el-table-column prop="student_id" label="学号" width="120" />
            <el-table-column prop="phone" label="手机号" width="120" />
            <el-table-column prop="email" label="邮箱" width="200" />
            <el-table-column prop="is_admin" label="管理员" width="80">
              <template #default="{ row }">
                <el-tag :type="row.is_admin ? 'danger' : 'info'" size="small">
                  {{ row.is_admin ? '是' : '否' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="注册时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.created_at) }}
              </template>
            </el-table-column>
            
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 不可预约时间段 -->
      <el-tab-pane label="不可预约时间" name="unavailable">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>不可预约时间段管理</span>
              <el-button type="primary" @click="showUnavailableDialog = true">添加</el-button>
            </div>
          </template>

          <el-table :data="unavailableTimes" style="width: 100%" v-loading="loadingUnavailable">
            <el-table-column prop="campus_name" label="校区" width="120" />
            <el-table-column label="适用时间" width="150">
              <template #default="{ row }">
                <span v-if="row.day_of_week !== null">
                  {{ getDayOfWeekText(row.day_of_week) }}
                </span>
                <span v-else-if="row.date">
                  {{ row.date }}
                </span>
                <span v-else>
                  所有日期
                </span>
              </template>
            </el-table-column>
            <el-table-column label="时间段" width="180">
              <template #default="{ row }">
                {{ row.start_hour }}:00 - {{ row.end_hour }}:00
              </template>
            </el-table-column>
            <el-table-column prop="reason" label="原因" />
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button type="danger" size="small" @click="handleDeleteUnavailable(row.id)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 钥匙管理员 -->
      <el-tab-pane label="钥匙管理员" name="keyManagers">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>钥匙管理员</span>
              <el-button type="primary" @click="showKeyManagerDialog = true">添加</el-button>
            </div>
          </template>

          <el-table :data="keyManagers" style="width: 100%" v-loading="loadingKeyManagers">
            <el-table-column prop="campus_name" label="校区" width="120" />
            <el-table-column prop="name" label="姓名" width="150" />
            <el-table-column prop="contact" label="联系方式" />
            <el-table-column prop="is_active" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
                  {{ row.is_active ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="handleEditKeyManager(row)">
                  编辑
                </el-button>
                <el-button type="danger" size="small" @click="handleDeleteKeyManager(row.id)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 历史预约记录 -->
      <el-tab-pane label="历史预约记录" name="reservationHistory">
        <el-card>
          <div class="filter-section" style="margin-bottom: 20px;">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-input
                  v-model="reservationFilters.userName"
                  placeholder="搜索预约人"
                  clearable
                  @input="loadReservationHistory"
                />
              </el-col>
              <el-col :span="6">
                <el-select
                  v-model="reservationFilters.campusId"
                  placeholder="选择校区"
                  clearable
                  @change="loadReservationHistory"
                  style="width: 100%"
                >
                  <el-option label="全部校区" :value="null" />
                  <el-option
                    v-for="campus in campuses"
                    :key="campus.id"
                    :label="campus.name"
                    :value="campus.id"
                  />
                </el-select>
              </el-col>
              <el-col :span="12">
                <el-date-picker
                  v-model="reservationFilters.dateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  @change="loadReservationHistory"
                  style="width: 100%"
                />
              </el-col>
            </el-row>
          </div>

          <el-table
            :data="reservationHistory"
            v-loading="loadingReservations"
            stripe
            style="width: 100%"
          >
            <el-table-column prop="user_name" label="预约人" width="120" />
            <el-table-column prop="campus_name" label="校区" width="100" />
            <el-table-column prop="date" label="日期" width="120" />
            <el-table-column label="时间段" width="150">
              <template #default="scope">
                {{ scope.row.start_hour }}:00 - {{ scope.row.end_hour }}:00
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="scope">
                <el-tag v-if="scope.row.status === 'active'" type="success">有效</el-tag>
                <el-tag v-else-if="scope.row.status === 'cancelled'" type="info">已取消</el-tag>
                <el-tag v-else type="warning">{{ scope.row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="钥匙状态" width="120">
              <template #default="scope">
                <el-tag v-if="scope.row.key_returned" type="info">已归还</el-tag>
                <el-tag v-else-if="scope.row.key_picked_up" type="success">已领取</el-tag>
                <el-tag v-else type="warning">未领取</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="scope">
                {{ formatDateTime(scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column prop="notes" label="备注" show-overflow-tooltip />
          </el-table>

          <el-pagination
            :current-page="reservationPagination.page"
            :page-size="reservationPagination.pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="reservationPagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleReservationPageSizeChange"
            @current-change="handleReservationPageChange"
            style="margin-top: 20px; justify-content: center;"
          />
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 不可预约时间对话框 -->
    <el-dialog v-model="showUnavailableDialog" title="添加不可预约时间" width="500px">
      <el-form :model="unavailableForm" label-width="120px">
        <el-form-item label="校区">
          <el-select v-model="unavailableForm.campus_id" placeholder="请选择校区" style="width: 100%">
            <el-option v-for="campus in campuses" :key="campus.id" :label="campus.name" :value="campus.id" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="时间规则类型">
          <el-radio-group v-model="unavailableForm.rule_type">
            <el-radio label="weekday">固定周几</el-radio>
            <el-radio label="all">所有日期</el-radio>
            <el-radio label="specific">特定日期</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="周几" v-if="unavailableForm.rule_type === 'weekday'">
          <el-select v-model="unavailableForm.day_of_week" placeholder="请选择周几" style="width: 100%">
            <el-option label="周一" :value="1" />
            <el-option label="周二" :value="2" />
            <el-option label="周三" :value="3" />
            <el-option label="周四" :value="4" />
            <el-option label="周五" :value="5" />
            <el-option label="周六" :value="6" />
            <el-option label="周日" :value="0" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="特定日期" v-if="unavailableForm.rule_type === 'specific'">
          <el-date-picker
            v-model="unavailableForm.date"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="开始时间">
          <el-input-number v-model="unavailableForm.start_hour" :min="0" :max="23" />
          <span style="margin-left: 8px">:00</span>
        </el-form-item>
        
        <el-form-item label="结束时间">
          <el-input-number v-model="unavailableForm.end_hour" :min="1" :max="24" />
          <span style="margin-left: 8px">:00</span>
        </el-form-item>
        
        <el-form-item label="原因">
          <el-input 
            v-model="unavailableForm.reason" 
            placeholder="例如：周一维护时间、每日休息时间等"
            type="textarea"
            :rows="2"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUnavailableDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAddUnavailable">确定</el-button>
      </template>
    </el-dialog>

    <!-- 钥匙管理员对话框 -->
    <el-dialog v-model="showKeyManagerDialog" :title="editingKeyManager ? '编辑钥匙管理员' : '添加钥匙管理员'" width="500px">
      <el-form :model="keyManagerForm" label-width="100px">
        <el-form-item label="校区">
          <el-select v-model="keyManagerForm.campus_id" placeholder="请选择校区" style="width: 100%">
            <el-option v-for="campus in campuses" :key="campus.id" :label="campus.name" :value="campus.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="keyManagerForm.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="联系方式">
          <el-input v-model="keyManagerForm.contact" placeholder="请输入联系方式" />
        </el-form-item>
        <el-form-item v-if="editingKeyManager" label="状态">
          <el-switch v-model="keyManagerForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showKeyManagerDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitKeyManager">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { adminService, reservationService } from '@/services/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

export default {
  name: 'Admin',
  components: {
    Search
  },
  setup() {
    const activeTab = ref('users')
    const users = ref([])
    const unavailableTimes = ref([])
    const keyManagers = ref([])
    const campuses = ref([])
    const loadingUsers = ref(false)
    const loadingUnavailable = ref(false)
    const loadingKeyManagers = ref(false)
    const loadingReservations = ref(false)
    const showUnavailableDialog = ref(false)
    const showKeyManagerDialog = ref(false)
    const editingKeyManager = ref(false)

    // 历史预约记录
    const reservationHistory = ref([])
    const reservationFilters = ref({
      userName: '',
      campusId: null,
      dateRange: null
    })
    const reservationPagination = ref({
      page: 1,
      pageSize: 20,
      total: 0
    })

    // 用户筛选条件
    const userFilters = ref({
      is_active: null,  // 'true' | 'false' | null
      year: null,       // 入学年份
      search: ''        // 搜索关键词
    })

    // 生成入学年份选项（最近10年）
    const enrollmentYears = computed(() => {
      const currentYear = new Date().getFullYear()
      const years = []
      for (let i = 0; i < 10; i++) {
        years.push(currentYear - i)
      }
      return years
    })

    const unavailableForm = ref({
      campus_id: null,
      rule_type: 'weekday', // 'weekday' | 'all' | 'specific'
      day_of_week: null, // 0-6 (0=周日, 1=周一, ..., 6=周六)
      date: null,
      start_hour: 8,
      end_hour: 12,
      reason: ''
    })

    const keyManagerForm = ref({
      id: null,
      campus_id: null,
      name: '',
      contact: '',
      is_active: true
    })

    const formatTime = (timeStr) => {
      return new Date(timeStr).toLocaleString('zh-CN')
    }

    const getDayOfWeekText = (dayOfWeek) => {
      const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
      return days[dayOfWeek] || '未知'
    }

    const loadCampuses = async () => {
      try {
        campuses.value = await reservationService.getCampuses()
      } catch (error) {
        console.error('Failed to load campuses:', error)
      }
    }

    const loadUsers = async () => {
      loadingUsers.value = true
      try {
        // 构建查询参数
        const params = {}
        if (userFilters.value.is_active !== null) {
          params.is_active = userFilters.value.is_active
        }
        if (userFilters.value.year) {
          params.year = userFilters.value.year
        }
        if (userFilters.value.search) {
          params.search = userFilters.value.search
        }
        
        users.value = await adminService.getAllUsers(params)
      } catch (error) {
        console.error('Failed to load users:', error)
      } finally {
        loadingUsers.value = false
      }
    }

    // 搜索防抖
    let searchTimeout = null
    const handleSearchUsers = () => {
      if (searchTimeout) clearTimeout(searchTimeout)
      searchTimeout = setTimeout(() => {
        loadUsers()
      }, 500)
    }

    const loadUnavailableTimes = async () => {
      loadingUnavailable.value = true
      try {
        unavailableTimes.value = await adminService.getUnavailableTimes()
      } catch (error) {
        console.error('Failed to load unavailable times:', error)
      } finally {
        loadingUnavailable.value = false
      }
    }

    const loadKeyManagers = async () => {
      loadingKeyManagers.value = true
      try {
        keyManagers.value = await adminService.getKeyManagers()
      } catch (error) {
        console.error('Failed to load key managers:', error)
      } finally {
        loadingKeyManagers.value = false
      }
    }

    const handleToggleUserActive = async (userId) => {
      try {
        await adminService.toggleUserActive(userId)
        ElMessage.success('操作成功')
        loadUsers()
      } catch (error) {
        console.error('Failed to toggle user active:', error)
      }
    }

    const handleAnnualReset = async () => {
      try {
        await ElMessageBox.confirm(
          '确定要执行年度重置吗？这将禁用所有普通用户账号（管理员除外）。',
          '年度重置确认',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        await adminService.annualResetUsers()
        ElMessage.success('年度重置成功')
        loadUsers()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Failed to reset users:', error)
          ElMessage.error('年度重置失败')
        }
      }
    }

    const handleAddUnavailable = async () => {
      if (!unavailableForm.value.campus_id) {
        ElMessage.warning('请选择校区')
        return
      }

      if (unavailableForm.value.rule_type === 'weekday' && unavailableForm.value.day_of_week === null) {
        ElMessage.warning('请选择周几')
        return
      }

      if (unavailableForm.value.rule_type === 'specific' && !unavailableForm.value.date) {
        ElMessage.warning('请选择日期')
        return
      }

      if (unavailableForm.value.start_hour >= unavailableForm.value.end_hour) {
        ElMessage.warning('结束时间必须大于开始时间')
        return
      }

      try {
        const payload = {
          campus_id: unavailableForm.value.campus_id,
          start_hour: unavailableForm.value.start_hour,
          end_hour: unavailableForm.value.end_hour,
          reason: unavailableForm.value.reason
        }

        // 根据规则类型设置不同的字段
        if (unavailableForm.value.rule_type === 'weekday') {
          payload.day_of_week = unavailableForm.value.day_of_week
        } else if (unavailableForm.value.rule_type === 'specific') {
          const date = new Date(unavailableForm.value.date)
          payload.date = date.toISOString().split('T')[0]
        }
        // 'all' 类型不需要额外字段

        await adminService.createUnavailableTime(payload)
        
        ElMessage.success('添加成功')
        showUnavailableDialog.value = false
        unavailableForm.value = {
          campus_id: null,
          rule_type: 'weekday',
          day_of_week: null,
          date: null,
          start_hour: 8,
          end_hour: 12,
          reason: ''
        }
        loadUnavailableTimes()
      } catch (error) {
        console.error('Failed to add unavailable time:', error)
      }
    }

    const handleDeleteUnavailable = async (id) => {
      try {
        await ElMessageBox.confirm('确定要删除这个不可预约时间段吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        await adminService.deleteUnavailableTime(id)
        ElMessage.success('删除成功')
        loadUnavailableTimes()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Failed to delete unavailable time:', error)
        }
      }
    }

    const handleEditKeyManager = (manager) => {
      editingKeyManager.value = true
      keyManagerForm.value = { ...manager }
      showKeyManagerDialog.value = true
    }

    const handleSubmitKeyManager = async () => {
      if (!keyManagerForm.value.campus_id || !keyManagerForm.value.name || !keyManagerForm.value.contact) {
        ElMessage.warning('请填写所有必填项')
        return
      }

      try {
        if (editingKeyManager.value) {
          await adminService.updateKeyManager(keyManagerForm.value.id, keyManagerForm.value)
          ElMessage.success('更新成功')
        } else {
          await adminService.createKeyManager(keyManagerForm.value)
          ElMessage.success('添加成功')
        }
        
        showKeyManagerDialog.value = false
        editingKeyManager.value = false
        keyManagerForm.value = {
          id: null,
          campus_id: null,
          name: '',
          contact: '',
          is_active: true
        }
        loadKeyManagers()
      } catch (error) {
        console.error('Failed to submit key manager:', error)
      }
    }

    const handleDeleteKeyManager = async (id) => {
      try {
        await ElMessageBox.confirm('确定要删除这个钥匙管理员吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        await adminService.deleteKeyManager(id)
        ElMessage.success('删除成功')
        loadKeyManagers()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Failed to delete key manager:', error)
        }
      }
    }

    // 加载历史预约记录
    const loadReservationHistory = async () => {
      loadingReservations.value = true
      try {
        const params = {
          page: reservationPagination.value.page,
          page_size: reservationPagination.value.pageSize
        }
        
        // 添加筛选条件
        if (reservationFilters.value.userName) {
          params.user_name = reservationFilters.value.userName
        }
        if (reservationFilters.value.campusId) {
          params.campus_id = reservationFilters.value.campusId
        }
        if (reservationFilters.value.dateRange && reservationFilters.value.dateRange.length === 2) {
          const [startDate, endDate] = reservationFilters.value.dateRange
          params.start_date = startDate.toISOString().split('T')[0]
          params.end_date = endDate.toISOString().split('T')[0]
        }

        const response = await adminService.getReservationHistory(params)
        reservationHistory.value = response.data
        reservationPagination.value.total = response.total
      } catch (error) {
        console.error('Failed to load reservation history:', error)
        ElMessage.error('加载预约记录失败')
      } finally {
        loadingReservations.value = false
      }
    }

    const handleReservationPageChange = (page) => {
      reservationPagination.value.page = page
      loadReservationHistory()
    }

    const handleReservationPageSizeChange = (pageSize) => {
      reservationPagination.value.pageSize = pageSize
      reservationPagination.value.page = 1
      loadReservationHistory()
    }

    const formatDateTime = (dateTimeStr) => {
      if (!dateTimeStr) return '-'
      return new Date(dateTimeStr).toLocaleString('zh-CN')
    }

    onMounted(() => {
      loadCampuses()
      loadUsers()
      loadUnavailableTimes()
      loadKeyManagers()
      loadReservationHistory()
    })

    return {
      activeTab,
      users,
      unavailableTimes,
      keyManagers,
      campuses,
      loadingUsers,
      loadingUnavailable,
      loadingKeyManagers,
      loadingReservations,
      showUnavailableDialog,
      showKeyManagerDialog,
      editingKeyManager,
      unavailableForm,
      keyManagerForm,
      userFilters,
      enrollmentYears,
      reservationHistory,
      reservationFilters,
      reservationPagination,
      formatTime,
      getDayOfWeekText,
      formatDateTime,
      loadUsers,
      handleToggleUserActive,
      handleAnnualReset,
      handleSearchUsers,
      handleAddUnavailable,
      handleDeleteUnavailable,
      handleEditKeyManager,
      handleSubmitKeyManager,
      handleDeleteKeyManager,
      loadReservationHistory,
      handleReservationPageChange,
      handleReservationPageSizeChange
    }
  }
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.filter-section {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .card-header {
    font-size: 16px;
  }
  
  :deep(.el-table) {
    font-size: 12px;
  }
  
  :deep(.el-button) {
    padding: 5px 10px;
    font-size: 12px;
  }
  
  :deep(.el-tabs__item) {
    padding: 0 10px;
    font-size: 14px;
  }
}
</style>
