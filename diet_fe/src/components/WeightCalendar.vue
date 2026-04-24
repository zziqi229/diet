<template>
  <div class="calendar-wrap">
    <div class="calendar-nav">
      <el-button :icon="ArrowLeft" circle size="small" @click="prevMonth" />
      <span class="month-label">{{ currentMonthLabel }}</span>
      <el-button :icon="ArrowRight" circle size="small" @click="nextMonth" />
    </div>

    <el-calendar v-model="internalDate" class="weight-calendar">
      <template #header>
        <!-- suppress default header -->
        <span />
      </template>
      <template #date-cell="{ data }">
        <div
          class="cell"
          :class="{
            'is-current': data.type === 'current-month',
            'has-record': !!recordMap[data.day],
            'is-today': data.day === todayStr,
          }"
          @click="handleCellClick(data)"
        >
          <span class="cell-day">{{ data.day.split('-')[2] }}</span>
          <span v-if="recordMap[data.day]" class="cell-weight">
            {{ recordMap[data.day].avgWeight }} kg
          </span>
        </div>
      </template>
    </el-calendar>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

const props = defineProps({
  records: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['month-change', 'day-click'])

const internalDate = ref(new Date())
const todayStr = dayjs().format('YYYY-MM-DD')

const currentMonthLabel = computed(() => dayjs(internalDate.value).format('YYYY年MM月'))

// Build date → { records, avgWeight } map
const recordMap = computed(() => {
  const map = {}
  for (const r of props.records) {
    const dateKey = dayjs(r.recorded_at).format('YYYY-MM-DD')
    if (!map[dateKey]) map[dateKey] = { records: [], avgWeight: 0 }
    map[dateKey].records.push(r)
  }
  for (const key in map) {
    const records = map[key].records
    const sum = records.reduce((s, r) => s + r.weight_kg, 0)
    map[key].avgWeight = +(sum / records.length).toFixed(1)
  }
  return map
})

function prevMonth() {
  internalDate.value = dayjs(internalDate.value).subtract(1, 'month').toDate()
}

function nextMonth() {
  internalDate.value = dayjs(internalDate.value).add(1, 'month').toDate()
}

watch(
  () => dayjs(internalDate.value).format('YYYY-MM'),
  (ym) => {
    emit('month-change', ym)
  },
  { immediate: true },
)

function handleCellClick(data) {
  if (data.type !== 'current-month') return
  const dayData = recordMap.value[data.day]
  const records = dayData ? dayData.records : []
  emit('day-click', { dateStr: data.day, records })
}
</script>

<style scoped>
.calendar-wrap {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.calendar-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
}

.month-label {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

/* override el-calendar default header spacing */
:deep(.el-calendar__header) {
  display: none;
}

:deep(.el-calendar__body) {
  padding: 0;
}

:deep(.el-calendar-table) {
  border-collapse: collapse;
}

:deep(.el-calendar-table thead th) {
  padding: 8px 0;
  font-size: 12px;
  color: #909399;
  font-weight: 500;
  background: #fafafa;
  text-align: center;
}

:deep(.el-calendar-table .el-calendar-day) {
  padding: 0;
  height: auto;
  min-height: 64px;
}

.cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  height: 64px;
  padding: 6px 4px 4px;
  cursor: pointer;
  transition: background 0.15s;
  color: #c0c4cc;
  user-select: none;
}

.cell:hover {
  background: #f5f7fa;
}

.cell.is-current {
  color: #303133;
}

.cell.is-today .cell-day {
  background: var(--el-color-primary);
  color: #fff;
  border-radius: 50%;
  width: 26px;
  height: 26px;
  line-height: 26px;
  text-align: center;
}

.cell.has-record {
  background: #f0f9eb;
}

.cell.has-record:hover {
  background: #e1f3d8;
}

.cell-day {
  font-size: 13px;
  font-weight: 500;
  line-height: 26px;
  min-width: 26px;
  text-align: center;
}

.cell-weight {
  font-size: 11px;
  color: var(--el-color-success);
  font-weight: 600;
  margin-top: 2px;
  white-space: nowrap;
}

@media (max-width: 600px) {
  :deep(.el-calendar-table .el-calendar-day) {
    min-height: 52px;
  }

  .cell {
    height: 52px;
    padding: 4px 2px;
  }

  .cell-day {
    font-size: 12px;
  }

  .cell-weight {
    font-size: 10px;
  }
}
</style>
