<template>
  <el-dialog
    v-model="visible"
    :title="title"
    width="min(400px, 94vw)"
    draggable
  >
    <el-empty v-if="!records.length" description="当天暂无记录" :image-size="60" />
    <div v-else class="records-list">
      <div v-for="r in sortedRecords" :key="r.id" class="record-item">
        <span class="record-time">{{ formatTime(r.recorded_at) }}</span>
        <span class="record-weight">{{ r.weight_kg }} kg</span>
      </div>
      <div class="record-avg">
        <span>平均</span>
        <span class="avg-value">{{ avg }} kg</span>
      </div>
    </div>

    <template #footer>
      <el-button @click="visible = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed } from 'vue'
import dayjs from 'dayjs'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  dateStr: { type: String, default: '' },
  records: { type: Array, default: () => [] },
})

const emit = defineEmits(['update:modelValue'])

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})

const title = computed(() => props.dateStr ? `${props.dateStr} 体重记录` : '体重记录')

const sortedRecords = computed(() =>
  [...props.records].sort((a, b) => dayjs(a.recorded_at).valueOf() - dayjs(b.recorded_at).valueOf()),
)

const avg = computed(() => {
  if (!props.records.length) return '—'
  const sum = props.records.reduce((s, r) => s + r.weight_kg, 0)
  return (sum / props.records.length).toFixed(1)
})

function formatTime(isoStr) {
  return dayjs(isoStr).format('HH:mm:ss')
}
</script>

<style scoped>
.records-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.record-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: #f5f7fa;
  border-radius: 8px;
}

.record-time {
  font-size: 14px;
  color: #606266;
}

.record-weight {
  font-size: 15px;
  font-weight: 600;
  color: var(--el-color-success);
}

.record-avg {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  border-top: 1px solid #e4e7ed;
  margin-top: 4px;
  font-size: 13px;
  color: #909399;
}

.avg-value {
  font-weight: 600;
  color: var(--el-color-primary);
}
</style>
