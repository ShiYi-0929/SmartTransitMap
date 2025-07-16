<template>
  <div class="card-tech p-6">
    <h2 class="text-xl font-semibold text-white mb-4 flex items-center">
      <Search class="h-5 w-5 mr-2 text-cyan-400" />
      交通数据查询
    </h2>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="space-y-2">
        <label class="text-sm text-blue-200">起始时间</label>
        <input 
          v-model="localQueryParams.startTime"
          type="datetime-local" 
          class="input-tech"
        />
      </div>
      <div class="space-y-2">
        <label class="text-sm text-blue-200">结束时间</label>
        <input 
          v-model="localQueryParams.endTime"
          type="datetime-local" 
          class="input-tech"
        />
      </div>
      <div class="space-y-2">
        <label class="text-sm text-blue-200">车辆标识 (可选)</label>
        <input 
          v-model="localQueryParams.vehicleId"
          type="text" 
          placeholder="输入车辆ID查看轨迹"
          class="input-tech placeholder:text-blue-300"
        />
      </div>
    </div>
    <div class="flex space-x-4 mt-4">
      <button 
        @click="onQueryClick"
        :disabled="loading"
        class="btn-tech flex items-center text-white"
      >
        <Search class="h-4 w-4 mr-2" />
        {{ loading ? '查询中...' : '查询数据' }}
      </button>
      <button 
        @click="onClearClick"
        class="btn-tech-secondary flex items-center text-white"
      >
        <X class="h-4 w-4 mr-2" />
        清除结果
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { Search, X } from 'lucide-vue-next'
const props = defineProps({
  modelValue: Object,
  loading: Boolean
})
const emit = defineEmits(['update:modelValue', 'query', 'clear'])
const localQueryParams = ref({ ...props.modelValue })
watch(() => props.modelValue, (val) => {
  localQueryParams.value = { ...val }
})
const onQueryClick = () => {
  emit('update:modelValue', localQueryParams.value)
  emit('query')
}
const onClearClick = () => emit('clear')
</script>

<style scoped>
.btn-tech,
.btn-tech-secondary {
  color: #fff !important;
}
</style> 