<template>
  <div class="equipment-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>设备列表</span>
          <el-button 
            type="primary" 
            @click="goToRegister" 
            :size="isMobile ? 'small' : 'default'"
          >
            <span v-if="isMobile">登记设备</span>
            <span v-else>登记设备</span>
          </el-button>
        </div>
      </template>

      <!-- 过滤条件 -->
      <div class="filter-section">
        <el-row :gutter="isMobile ? 10 : 20">
          <el-col :xs="24" :sm="12" :md="8">
            <el-select 
              v-model="filterCampusId" 
              placeholder="选择校区" 
              clearable
              @change="loadEquipment"
              :size="isMobile ? 'default' : 'default'"
            >
              <el-option label="全部校区" :value="null" />
              <el-option v-for="campus in campuses" :key="campus.id" :label="campus.name" :value="campus.id" />
            </el-select>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8">
            <el-select 
              v-model="filterType" 
              placeholder="设备类型" 
              clearable
              @change="loadEquipment"
              :size="isMobile ? 'default' : 'default'"
            >
              <el-option label="全部类型" :value="null" />
              <el-option v-for="type in equipmentTypes" :key="type" :label="type" :value="type" />
            </el-select>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8">
            <el-input 
              v-model="searchKeyword" 
              placeholder="搜索设备名称" 
              clearable
              @input="handleSearch"
              :size="isMobile ? 'default' : 'default'"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-col>
        </el-row>
        <el-row :gutter="10" style="margin-top: 10px;">
          <el-col :xs="12" :sm="8" :md="6">
            <el-checkbox v-model="filterShared" @change="loadEquipment">仅显示共享设备</el-checkbox>
          </el-col>
        </el-row>
      </div>

      <!-- 设备列表 - 移动端卡片布局 / 桌面端表格布局 -->
      <div v-if="isMobile" class="mobile-equipment-list">
        <div v-if="filteredEquipment.length === 0" class="empty-state">
          <el-empty description="暂无设备" />
        </div>
        <div v-else>
          <div 
            v-for="equipment in filteredEquipment" 
            :key="equipment.id" 
            class="equipment-card"
            @click="showEquipmentDetail(equipment)"
          >
            <div class="equipment-header">
              <span class="equipment-name">{{ equipment.equipment_name }}</span>
              <el-tag :type="equipment.is_shared ? 'success' : 'info'" size="small">
                {{ equipment.is_shared ? '共享' : '私有' }}
              </el-tag>
            </div>
            <div class="equipment-info">
              <div class="info-row">
                <span class="label">类型：</span>
                <span class="value">{{ equipment.equipment_type }}</span>
              </div>
              <div class="info-row">
                <span class="label">位置：</span>
                <span class="value">{{ equipment.location }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 桌面端表格 -->
      <el-table 
        v-else 
        :data="filteredEquipment" 
        style="width: 100%; margin-top: 20px;" 
        v-loading="loading"
        @row-click="showEquipmentDetail"
        :row-style="{ cursor: 'pointer' }"
      >
        <el-table-column prop="campus_name" label="校区" width="100" />
        <el-table-column prop="equipment_type" label="类型" width="120" />
        <el-table-column prop="equipment_name" label="设备名称" min-width="180" />
        <el-table-column prop="location" label="位置" width="150" />
        <el-table-column prop="is_shared" label="共享" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_shared ? 'success' : 'info'" size="small">
              {{ row.is_shared ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 设备详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="设备详情"
      :width="isMobile ? '90%' : '500px'"
      :fullscreen="isMobile"
    >
      <div v-if="selectedEquipment" class="detail-content">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="设备名称">
            {{ selectedEquipment.equipment_name }}
          </el-descriptions-item>
          <el-descriptions-item label="设备类型">
            {{ selectedEquipment.equipment_type }}
          </el-descriptions-item>
          <el-descriptions-item label="校区">
            {{ selectedEquipment.campus_name }}
          </el-descriptions-item>
          <el-descriptions-item label="位置">
            {{ selectedEquipment.location }}
          </el-descriptions-item>
          <el-descriptions-item label="所有者">
            {{ selectedEquipment.owner_name }}
          </el-descriptions-item>
          <el-descriptions-item label="联系方式">
            {{ selectedEquipment.contact }}
          </el-descriptions-item>
          <el-descriptions-item label="共享状态">
            <el-tag :type="selectedEquipment.is_shared ? 'success' : 'info'">
              {{ selectedEquipment.is_shared ? '共享' : '私有' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="登记时间">
            {{ formatDate(selectedEquipment.placed_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="备注" v-if="selectedEquipment.notes">
            {{ selectedEquipment.notes }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <el-button 
          v-if="selectedEquipment?.is_shared" 
          type="primary" 
          @click="handleBorrowFromDetail"
        >
          借用设备
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { equipmentService, reservationService } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { Search } from '@element-plus/icons-vue'

export default {
  name: 'EquipmentList',
  components: {
    Search
  },
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const allEquipment = ref([])
    const campuses = ref([])
    const loading = ref(false)
    const filterCampusId = ref(null)
    const filterType = ref(null)
    const filterShared = ref(false)
    const searchKeyword = ref('')
    const isMobile = ref(false)
    const showDetailDialog = ref(false)
    const selectedEquipment = ref(null)

    // 检测移动端
    const checkMobile = () => {
      isMobile.value = window.innerWidth <= 768
    }

    // 获取所有唯一的设备类型
    const equipmentTypes = computed(() => {
      const types = new Set()
      allEquipment.value.forEach(eq => {
        if (eq.equipment_type) {
          types.add(eq.equipment_type)
        }
      })
      return Array.from(types).sort()
    })

    // 过滤后的设备列表
    const filteredEquipment = computed(() => {
      let result = allEquipment.value

      // 校区过滤
      if (filterCampusId.value) {
        result = result.filter(eq => eq.campus_id === filterCampusId.value)
      }

      // 类型过滤
      if (filterType.value) {
        result = result.filter(eq => eq.equipment_type === filterType.value)
      }

      // 共享过滤
      if (filterShared.value) {
        result = result.filter(eq => eq.is_shared)
      }

      // 关键词搜索
      if (searchKeyword.value) {
        const keyword = searchKeyword.value.toLowerCase()
        result = result.filter(eq => 
          eq.equipment_name?.toLowerCase().includes(keyword) ||
          eq.location?.toLowerCase().includes(keyword) ||
          eq.owner_name?.toLowerCase().includes(keyword)
        )
      }

      return result
    })

    const loadCampuses = async () => {
      try {
        campuses.value = await reservationService.getCampuses()
        // 如果用户设置了默认校区，使用默认校区作为筛选条件
        const preferredCampusId = authStore.user?.preferred_campus_id
        if (preferredCampusId && campuses.value.find(c => c.id === preferredCampusId)) {
          filterCampusId.value = preferredCampusId
        }
      } catch (error) {
        console.error('Failed to load campuses:', error)
      }
    }

    const loadEquipment = async () => {
      loading.value = true
      try {
        const params = {}
        if (filterCampusId.value) {
          params.campus_id = filterCampusId.value
        }
        if (filterShared.value) {
          params.is_shared = true
        }
        allEquipment.value = await equipmentService.getEquipmentList(params)
      } catch (error) {
        console.error('Failed to load equipment:', error)
      } finally {
        loading.value = false
      }
    }

    const handleSearch = () => {
      // 搜索已通过computed属性自动处理
    }

    const showEquipmentDetail = (equipment) => {
      selectedEquipment.value = equipment
      showDetailDialog.value = true
    }

    const formatDate = (dateStr) => {
      return new Date(dateStr).toLocaleDateString('zh-CN')
    }

    const handleBorrowFromDetail = () => {
      // 关闭详情对话框
      showDetailDialog.value = false
      
      // 跳转到借用页面，并传递设备信息
      router.push({
        name: 'EquipmentBorrow',
        query: {
          equipment_name: selectedEquipment.value.equipment_name,
          equipment_type: selectedEquipment.value.equipment_type,
          owner_name: selectedEquipment.value.owner_name
        }
      })
    }

    const goToRegister = () => {
      router.push({ name: 'EquipmentRegister' })
    }

    onMounted(() => {
      checkMobile()
      window.addEventListener('resize', checkMobile)
      loadCampuses()
      loadEquipment()
    })

    onUnmounted(() => {
      window.removeEventListener('resize', checkMobile)
    })

    return {
      allEquipment,
      campuses,
      loading,
      filterCampusId,
      filterType,
      filterShared,
      searchKeyword,
      isMobile,
      showDetailDialog,
      selectedEquipment,
      equipmentTypes,
      filteredEquipment,
      loadEquipment,
      handleSearch,
      showEquipmentDetail,
      formatDate,
      handleBorrowFromDetail,
      goToRegister
    }
  }
}
</script>

<style scoped>
.equipment-list {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
}

.filter-section {
  margin-bottom: 20px;
}

.filter-section .el-select,
.filter-section .el-input {
  width: 100%;
}

/* 移动端卡片样式 */
.mobile-equipment-list {
  margin-top: 15px;
}

.equipment-card {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.equipment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid #f0f0f0;
}

.equipment-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  flex: 1;
  margin-right: 10px;
}

.equipment-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-row {
  display: flex;
  font-size: 14px;
  line-height: 1.5;
}

.info-row .label {
  color: #909399;
  min-width: 70px;
  flex-shrink: 0;
}

.info-row .value {
  color: #606266;
  flex: 1;
  word-break: break-word;
}

.empty-state {
  padding: 40px 0;
  text-align: center;
}

/* 移动端过滤区域优化 */
@media (max-width: 768px) {
  .card-header {
    font-size: 16px;
  }

  .filter-section :deep(.el-col) {
    margin-bottom: 10px;
  }

  .filter-section :deep(.el-col):last-child {
    margin-bottom: 0;
  }
}

/* 桌面端优化 */
@media (min-width: 769px) {
  .filter-section {
    background: #f5f7fa;
    padding: 15px;
    border-radius: 8px;
  }
}
</style>
