<template>
  <el-card class="manager-card" style="margin-bottom: 12px">
    <template #header>
      <div class="card-header">
        <span>钥匙管理员</span>
      </div>
    </template>
    <div v-if="keyManagers.length > 0">
      <div v-for="manager in keyManagers" :key="manager.id" class="manager-item">
        <strong>{{ manager.name }}</strong>
        <span class="manager-contact">{{ manager.contact }}</span>
      </div>
    </div>
    <el-empty v-else description="暂无钥匙管理员" :image-size="60" />
  </el-card>
</template>

<script>
export default {
  name: 'KeyManagers',
  props: {
    keyManagers: {
      type: Array,
      default: () => []
    }
  }
}
</script>

<style scoped>
.manager-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.manager-item:last-child {
  border-bottom: none;
}

.manager-contact {
  color: #409eff;
  font-size: 13px;
}
</style>
