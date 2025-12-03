<template>
  <el-card class="campus-card">
    <el-radio-group 
      :model-value="selectedCampusId" 
      @update:model-value="$emit('update:selectedCampusId', $event)"
      @change="$emit('change', $event)" 
      :size="isMobile ? 'small' : 'default'"
    >
      <el-radio-button v-for="campus in campuses" :key="campus.id" :label="campus.id">
        {{ campus.name }}
      </el-radio-button>
    </el-radio-group>
  </el-card>
</template>

<script>
export default {
  name: 'CampusSelector',
  props: {
    campuses: {
      type: Array,
      default: () => []
    },
    selectedCampusId: {
      type: Number,
      default: null
    },
    isMobile: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:selectedCampusId', 'change']
}
</script>

<style scoped>
.campus-card {
  /* 样式可以在这里定义或继承自父组件 */
}
</style>
