<template>
  <div class="app-layout">
    <!-- Header -->
    <header class="app-header">
      <div class="header-brand">
        <span class="brand-icon">⚖️</span>
        <span class="brand-name">体重记录</span>
      </div>
      <div class="header-user">
        <span class="username">{{ user?.username }}</span>
        <el-button link class="logout-btn" @click="handleLogout">
          <el-icon><SwitchButton /></el-icon>
          <span class="logout-text">退出</span>
        </el-button>
      </div>
    </header>

    <!-- Summary bar -->
    <div class="summary-bar">
      <div class="stat-item">
        <span class="stat-label">最新体重</span>
        <span class="stat-value">
          {{ latestRecord ? `${latestRecord.weight_kg} kg` : '—' }}
        </span>
      </div>
      <div class="stat-divider" />
      <div class="stat-item">
        <span class="stat-label">本月记录</span>
        <span class="stat-value">{{ calendarRecords.length }} 条</span>
      </div>
    </div>

    <!-- Main content -->
    <main class="app-main">
      <!-- Controls row -->
      <div class="controls-row">
        <el-segmented v-model="activeView" :options="viewOptions" />
        <el-button type="primary" :icon="Plus" round @click="openAddDialog()">
          记录体重
        </el-button>
      </div>

      <!-- Chart date range picker -->
      <transition name="fade">
        <div v-if="activeView === 'chart'" class="range-row">
          <el-date-picker
            v-model="chartRange"
            type="daterange"
            unlink-panels
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            :shortcuts="rangeShortcuts"
            style="max-width: 340px; width: 100%"
            @change="fetchChartData"
          />
        </div>
      </transition>

      <!-- Views -->
      <weight-calendar
        v-show="activeView === 'calendar'"
        :records="calendarRecords"
        @month-change="onMonthChange"
        @day-click="handleDayClick"
      />

      <weight-chart
        v-show="activeView === 'chart'"
        :records="chartRecords"
        :loading="weightStore.loading"
      />
    </main>

    <!-- Add Dialog -->
    <add-weight-dialog
      v-model="dialogVisible"
      :default-date="dialogDefaultDate"
      @saved="onSaved"
    />

    <!-- Day Records Dialog -->
    <day-records-dialog
      v-model="dayRecordsVisible"
      :date-str="dayRecordsDate"
      :records="dayRecordsRecords"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, SwitchButton } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

import { useAuthStore } from '@/stores/auth'
import { useWeightStore } from '@/stores/weight'
import WeightCalendar from '@/components/WeightCalendar.vue'
import WeightChart from '@/components/WeightChart.vue'
import AddWeightDialog from '@/components/AddWeightDialog.vue'
import DayRecordsDialog from '@/components/DayRecordsDialog.vue'

const router = useRouter()
const authStore = useAuthStore()
const weightStore = useWeightStore()

const user = computed(() => authStore.user)

// View toggle
const activeView = ref('calendar')
const viewOptions = [
  { label: '📅 日历', value: 'calendar' },
  { label: '📈 折线图', value: 'chart' },
]

// Calendar data
const calendarRecords = ref([])
let currentYM = dayjs().format('YYYY-MM')

async function fetchCalendarMonth(ym) {
  currentYM = ym
  const start = dayjs(ym).startOf('month').toISOString()
  const end = dayjs(ym).endOf('month').toISOString()
  try {
    const res = await weightStore.fetchRecords({ start, end })
    calendarRecords.value = res.data
  } catch {
    ElMessage.error('获取记录失败')
  }
}

function onMonthChange(ym) {
  fetchCalendarMonth(ym)
}

// Chart data
const chartRecords = ref([])
const chartRange = ref([
  dayjs().subtract(29, 'day').toDate(),
  dayjs().toDate(),
])

async function fetchChartData() {
  if (!chartRange.value || !chartRange.value[0]) return
  const start = dayjs(chartRange.value[0]).startOf('day').toISOString()
  const end = dayjs(chartRange.value[1]).endOf('day').toISOString()
  try {
    const res = await weightStore.fetchRecords({ start, end })
    chartRecords.value = res.data
  } catch {
    ElMessage.error('获取记录失败')
  }
}

const rangeShortcuts = [
  {
    text: '近7天',
    value: () => [dayjs().subtract(6, 'day').toDate(), dayjs().toDate()],
  },
  {
    text: '近30天',
    value: () => [dayjs().subtract(29, 'day').toDate(), dayjs().toDate()],
  },
  {
    text: '近90天',
    value: () => [dayjs().subtract(89, 'day').toDate(), dayjs().toDate()],
  },
  {
    text: '近半年',
    value: () => [dayjs().subtract(179, 'day').toDate(), dayjs().toDate()],
  },
]

// Summary stats
const latestRecord = computed(() => {
  if (!calendarRecords.value.length) return null
  return [...calendarRecords.value].sort(
    (a, b) => dayjs(b.recorded_at).valueOf() - dayjs(a.recorded_at).valueOf(),
  )[0]
})

// Dialog
const dialogVisible = ref(false)
const dialogDefaultDate = ref(null)

// Day records dialog
const dayRecordsVisible = ref(false)
const dayRecordsDate = ref('')
const dayRecordsRecords = ref([])

function openAddDialog(dateStr = null) {
  dialogDefaultDate.value = dateStr
  dialogVisible.value = true
}

function handleDayClick({ dateStr, records }) {
  if (records.length > 0) {
    dayRecordsDate.value = dateStr
    dayRecordsRecords.value = records
    dayRecordsVisible.value = true
  }
}

async function onSaved() {
  // Refresh both views
  await fetchCalendarMonth(currentYM)
  await fetchChartData()
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

onMounted(() => {
  fetchChartData()
})
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  background: #f0f2f5;
  display: flex;
  flex-direction: column;
}

/* Header */
.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 56px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.header-brand {
  display: flex;
  align-items: center;
  gap: 8px;
}

.brand-icon {
  font-size: 22px;
}

.brand-name {
  font-size: 18px;
  font-weight: 700;
  color: #303133;
}

.header-user {
  display: flex;
  align-items: center;
  gap: 8px;
}

.username {
  font-size: 14px;
  color: #606266;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.logout-btn {
  color: #909399 !important;
  font-size: 14px;
}

.logout-btn:hover {
  color: var(--el-color-danger) !important;
}

/* Summary bar */
.summary-bar {
  display: flex;
  align-items: center;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  padding: 12px 24px;
  gap: 0;
}

.stat-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.stat-label {
  font-size: 12px;
  color: #909399;
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.stat-divider {
  width: 1px;
  height: 32px;
  background: #f0f0f0;
}

/* Main */
.app-main {
  flex: 1;
  max-width: 900px;
  width: 100%;
  margin: 0 auto;
  padding: 20px 16px 32px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.controls-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}

.range-row {
  display: flex;
  align-items: center;
}

/* Transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 600px) {
  .app-header {
    padding: 0 16px;
  }

  .logout-text {
    display: none;
  }

  .summary-bar {
    padding: 10px 16px;
  }

  .stat-value {
    font-size: 14px;
  }

  .app-main {
    padding: 14px 12px 24px;
  }
}
</style>
