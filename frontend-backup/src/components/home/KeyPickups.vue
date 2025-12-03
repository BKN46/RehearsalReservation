<template>
  <el-card class="pickup-card">
    <template #header>
      <div class="card-header">
        <span>已领取钥匙</span>
      </div>
    </template>
    <el-timeline v-if="activeKeyPickups.length > 0">
      <el-timeline-item
        v-for="pickup in activeKeyPickups"
        :key="pickup.id"
        :timestamp="formatTime(pickup.key_pickup_time)"
      >
        {{ pickup.user_name }} - {{ pickup.date }} {{ pickup.start_hour }}:00-{{ pickup.end_hour }}:00
      </el-timeline-item>
    </el-timeline>
    <el-empty v-else description="暂无已领取钥匙" :image-size="60" />
  </el-card>
</template>

<script>
export default {
  name: 'KeyPickups',
  props: {
    activeKeyPickups: {
      type: Array,
      default: () => []
    }
  },
  methods: {
    formatTime(timeStr) {
      return new Date(timeStr).toLocaleString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  }
}
</script>
