<template>
  <div class="trend-page">
    <!-- 顶部导航栏 -->
    <van-nav-bar title="趋势" class="top-bar" :border="false">
      <template #right>
        <span class="logout-btn" @click="handleLogout">退出</span>
      </template>
    </van-nav-bar>

    <div class="content">
      <!-- 时间范围选择 -->
      <div class="range-card">
        <div
          v-for="r in ranges"
          :key="r.key"
          class="range-tab"
          :class="{ 'range-active': activeRange === r.key }"
          @click="selectRange(r.key)"
        >{{ r.label }}</div>
      </div>

      <!-- 自定义日期范围 -->
      <div class="date-range-card">
        <van-field
          v-model="customStart"
          label="开始"
          readonly
          is-link
          class="date-field"
          @click="showStartPicker = true"
        />
        <van-field
          v-model="customEnd"
          label="结束"
          readonly
          is-link
          class="date-field"
          @click="showEndPicker = true"
        />
      </div>

      <!-- 开始日期选择器 -->
      <van-popup v-model:show="showStartPicker" position="bottom" round>
        <van-date-picker
          v-model="startPickerVal"
          title="选择开始日期"
          :max-date="new Date(customEnd)"
          @confirm="onStartConfirm"
          @cancel="showStartPicker = false"
        />
      </van-popup>

      <!-- 结束日期选择器 -->
      <van-popup v-model:show="showEndPicker" position="bottom" round>
        <van-date-picker
          v-model="endPickerVal"
          title="选择结束日期"
          :min-date="new Date(customStart)"
          :max-date="new Date()"
          @confirm="onEndConfirm"
          @cancel="showEndPicker = false"
        />
      </van-popup>

      <!-- 统计概要 -->
      <div class="summary-row">
        <div class="summary-item">
          <div class="summary-val">{{ stats.maxWeight ?? '–' }}</div>
          <div class="summary-label">最高体重(kg)</div>
        </div>
        <div class="summary-divider"></div>
        <div class="summary-item">
          <div class="summary-val">{{ stats.minWeight ?? '–' }}</div>
          <div class="summary-label">最低体重(kg)</div>
        </div>
        <div class="summary-divider"></div>
        <div class="summary-item">
          <div class="summary-val">{{ stats.totalExercise ?? '–' }}</div>
          <div class="summary-label">运动总时长(min)</div>
        </div>
        <div class="summary-divider"></div>
        <div class="summary-item">
          <div class="summary-val">{{ stats.exerciseDays ?? '–' }}</div>
          <div class="summary-label">运动天数</div>
        </div>
      </div>

      <!-- 体重趋势图 -->
      <div class="chart-card">
        <div class="chart-header">
          <van-icon name="chart-trending-o" class="chart-icon chart-icon-flip" />
          <span class="chart-title">体重</span>
        </div>
        <div v-if="loading" class="chart-loading">
          <van-loading color="#764ba2" />
        </div>
        <div v-else-if="weightPoints.length === 0" class="chart-empty">
          <van-empty description="暂无体重记录" image-size="80" />
        </div>
        <div v-else ref="weightChartEl" class="chart-canvas"></div>
      </div>

      <!-- 运动时长图 -->
      <div class="chart-card">
        <div class="chart-header">
          <van-icon name="fire-o" class="chart-icon chart-icon-orange" />
          <span class="chart-title">运动时长(min)</span>
        </div>
        <div v-if="loading" class="chart-loading">
          <van-loading color="#764ba2" />
        </div>
        <div v-else-if="exercisePoints.length === 0" class="chart-empty">
          <van-empty description="暂无运动记录" image-size="80" />
        </div>
        <div v-else ref="exerciseChartEl" class="chart-canvas"></div>
      </div>
    </div>

    <!-- 底部导航 -->
    <van-tabbar v-model="tabActive" class="bottom-nav" active-color="#764ba2" inactive-color="#aaa">
      <van-tabbar-item name="dashboard" icon="calendar-o" @click="$router.push('/dashboard')">仪表盘</van-tabbar-item>
      <van-tabbar-item name="trend" icon="chart-trending-o">趋势</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { showConfirmDialog } from 'vant'
import * as echarts from 'echarts/core'
import { LineChart, BarChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  DataZoomComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { useAuthStore } from '@/stores/auth'
import { weightApi } from '@/api/weight'
import { exerciseApi } from '@/api/exercise'

echarts.use([LineChart, BarChart, GridComponent, TooltipComponent, DataZoomComponent, CanvasRenderer])

const router = useRouter()
const auth = useAuthStore()

// ─── 持久化 ───
const STORAGE_KEY = 'trend_range'
function loadSaved() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) return JSON.parse(saved)
  } catch {}
  return null
}
function savePref(range, start, end) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({ range, start, end }))
}

// ─── 时间范围 ───
const ranges = [
  { key: '7d', label: '一周' },
  { key: '1m', label: '一月' },
  { key: '3m', label: '三月' },
  { key: '6m', label: '半年' },
  { key: '1y', label: '一年' },
]

const _pad = n => String(n).padStart(2, '0')
function getTodayStr() {
  const now = new Date()
  return `${now.getFullYear()}-${_pad(now.getMonth() + 1)}-${_pad(now.getDate())}`
}
function getRangeStart(key) {
  const now = new Date()
  const d = new Date(now)
  if (key === '7d') d.setDate(d.getDate() - 6)
  else if (key === '1m') d.setMonth(d.getMonth() - 1)
  else if (key === '3m') d.setMonth(d.getMonth() - 3)
  else if (key === '6m') d.setMonth(d.getMonth() - 6)
  else if (key === '1y') d.setFullYear(d.getFullYear() - 1)
  return `${d.getFullYear()}-${_pad(d.getMonth() + 1)}-${_pad(d.getDate())}`
}

const saved = loadSaved()
const activeRange = ref(saved?.range ?? '1m')
const customStart = ref(saved?.start ?? getRangeStart(activeRange.value))
const customEnd = ref(saved?.end ?? getTodayStr())

const showStartPicker = ref(false)
const showEndPicker = ref(false)

// van-date-picker v-model 格式: ['YYYY', 'MM', 'DD']
function dateStrToArr(str) {
  return str.split('-')
}
const startPickerVal = ref(dateStrToArr(customStart.value))
const endPickerVal = ref(dateStrToArr(customEnd.value))

function onStartConfirm({ selectedValues }) {
  customStart.value = selectedValues.join('-')
  startPickerVal.value = selectedValues
  showStartPicker.value = false
  activeRange.value = 'custom'
  savePref('custom', customStart.value, customEnd.value)
  loadData()
}
function onEndConfirm({ selectedValues }) {
  customEnd.value = selectedValues.join('-')
  endPickerVal.value = selectedValues
  showEndPicker.value = false
  activeRange.value = 'custom'
  savePref('custom', customStart.value, customEnd.value)
  loadData()
}

const tabActive = ref('trend')

// ─── 数据 ───
const loading = ref(false)
const weightPoints = ref([])   // [{ date, value }]
const exercisePoints = ref([]) // [{ date, value }]

// ─── 图表实例 ───
const weightChartEl = ref(null)
const exerciseChartEl = ref(null)
let weightChart = null
let exerciseChart = null

// ─── 统计概要 ───
const stats = computed(() => {
  if (weightPoints.value.length === 0 && exercisePoints.value.length === 0) {
    return { avgWeight: null, minWeight: null, totalExercise: null, exerciseDays: null }
  }
  const vals = weightPoints.value.map(p => p.value)
  const maxWeight = vals.length ? Math.max(...vals).toFixed(1) : null
  const minWeight = vals.length ? Math.min(...vals).toFixed(1) : null
  const totalExercise = exercisePoints.value.reduce((a, p) => a + p.value, 0) || null
  const exerciseDays = exercisePoints.value.filter(p => p.value > 0).length || null
  return { maxWeight, minWeight, totalExercise, exerciseDays }
})

// ─── 日期工具 ───
// 生成日期范围内所有天的列表
function genDateRange(startStr, endStr) {
  const result = []
  const cur = new Date(startStr)
  const end = new Date(endStr)
  while (cur <= end) {
    result.push(`${cur.getFullYear()}-${_pad(cur.getMonth() + 1)}-${_pad(cur.getDate())}`)
    cur.setDate(cur.getDate() + 1)
  }
  return result
}

// ─── 加载数据 ───
async function loadData() {
  loading.value = true
  const startDate = activeRange.value === 'custom' ? customStart.value : getRangeStart(activeRange.value)
  const endDate = activeRange.value === 'custom' ? customEnd.value : getTodayStr()
  try {
    const [wRes, eRes] = await Promise.all([
      weightApi.list({ start: `${startDate}T00:00:00`, end: `${endDate}T23:59:59` }),
      exerciseApi.list({ start: `${startDate}T00:00:00`, end: `${endDate}T23:59:59` }),
    ])

    // 体重：按天平均
    const wMap = new Map()
    for (const r of wRes.data.data) {
      const d = r.recorded_at.substring(0, 10)
      if (!wMap.has(d)) wMap.set(d, [])
      wMap.get(d).push(r.weight_kg)
    }
    const allDates = genDateRange(startDate, endDate)
    weightPoints.value = allDates
      .filter(d => wMap.has(d))
      .map(d => {
        const arr = wMap.get(d)
        return { date: d, value: parseFloat((arr.reduce((a, b) => a + b, 0) / arr.length).toFixed(2)) }
      })

    // 运动：按天合计时长（所有有数据的天）
    const eMap = new Map()
    for (const r of eRes.data.data) {
      const d = r.exercised_at.substring(0, 10)
      eMap.set(d, (eMap.get(d) || 0) + (r.duration_minutes || 0))
    }
    exercisePoints.value = allDates
      .filter(d => eMap.has(d))
      .map(d => ({ date: d, value: eMap.get(d) }))
  } finally {
    loading.value = false
    await nextTick()
    renderCharts()
  }
}

// ─── 渲染图表 ───
const PURPLE = '#764ba2'
const PURPLE_LIGHT = 'rgba(118,75,162,0.15)'
const ORANGE = '#ff9f0a'
const ORANGE_LIGHT = 'rgba(255,159,10,0.18)'
const GRID_COLOR = '#f0f0f5'
const LABEL_COLOR = '#8e8e93'

function buildTimeAxis() {
  return {
    type: 'time',
    axisLine: { lineStyle: { color: GRID_COLOR } },
    axisTick: { show: false },
    axisLabel: {
      color: LABEL_COLOR,
      fontSize: 10,
      formatter: (val) => {
        const d = new Date(val)
        return `${d.getMonth() + 1}/${d.getDate()}`
      },
    },
    splitLine: { show: false },
  }
}

function buildYAxis() {
  return {
    type: 'value',
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: { color: LABEL_COLOR, fontSize: 10 },
    splitLine: { lineStyle: { color: GRID_COLOR, type: 'dashed' } },
  }
}

function renderWeightChart() {
  if (!weightChartEl.value || weightPoints.value.length === 0) return
  if (weightChart) {
    weightChart.dispose()
    weightChart = null
  }
  weightChart = echarts.init(weightChartEl.value)
  const data = weightPoints.value.map(p => [p.date, p.value])
  const values = weightPoints.value.map(p => p.value)
  const min = Math.min(...values)
  const max = Math.max(...values)
  const padding = Math.max((max - min) * 0.3, 1)

  weightChart.setOption({
    grid: { top: 16, right: 12, bottom: 36, left: 46 },
    xAxis: buildTimeAxis(),
    yAxis: {
      ...buildYAxis(),
      min: parseFloat((min - padding).toFixed(1)),
      max: parseFloat((max + padding).toFixed(1)),
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#fff',
      borderColor: '#e8e0f5',
      borderWidth: 1,
      textStyle: { color: '#333', fontSize: 12 },
      formatter: params => {
        const d = new Date(params[0].value[0])
        const label = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
        return `${label}<br/><b style="color:${PURPLE}">${params[0].value[1]} kg</b>`
      },
    },
    series: [{
      type: 'line',
      data,
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: { color: PURPLE, width: 2.5 },
      itemStyle: { color: PURPLE, borderColor: '#fff', borderWidth: 2 },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(118,75,162,0.25)' },
          { offset: 1, color: 'rgba(118,75,162,0.02)' },
        ]),
      },
    }],
  })
}

function renderExerciseChart() {
  if (!exerciseChartEl.value || exercisePoints.value.length === 0) return
  if (exerciseChart) {
    exerciseChart.dispose()
    exerciseChart = null
  }
  exerciseChart = echarts.init(exerciseChartEl.value)
  const data = exercisePoints.value.map(p => [p.date, p.value])

  exerciseChart.setOption({
    grid: { top: 16, right: 12, bottom: 36, left: 46 },
    xAxis: buildTimeAxis(),
    yAxis: buildYAxis(),
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#fff',
      borderColor: '#fde8c0',
      borderWidth: 1,
      textStyle: { color: '#333', fontSize: 12 },
      formatter: params => {
        const d = new Date(params[0].value[0])
        const label = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
        return `${label}<br/><b style="color:${ORANGE}">${params[0].value[1]} min</b>`
      },
    },
    series: [{
      type: 'bar',
      data,
      barMaxWidth: 28,
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#ffb347' },
          { offset: 1, color: ORANGE },
        ]),
        borderRadius: [6, 6, 0, 0],
      },
    }],
  })
}

function renderCharts() {
  renderWeightChart()
  renderExerciseChart()
}

// ─── 响应窗口变化 ───
function onResize() {
  weightChart?.resize()
  exerciseChart?.resize()
}

// ─── 事件 ───
function selectRange(key) {
  activeRange.value = key
  customStart.value = getRangeStart(key)
  customEnd.value = getTodayStr()
  savePref(key, customStart.value, customEnd.value)
}

async function handleLogout() {
  try {
    await showConfirmDialog({
      title: '退出登录',
      message: '确定要退出吗？',
      confirmButtonText: '退出',
      cancelButtonText: '取消',
      confirmButtonColor: '#764ba2',
    })
    auth.logout()
    router.push({ name: 'Login' })
  } catch { /* 取消 */ }
}

watch(activeRange, () => {
  if (activeRange.value !== 'custom') loadData()
})
onMounted(() => {
  loadData()
  window.addEventListener('resize', onResize)
})
onUnmounted(() => {
  window.removeEventListener('resize', onResize)
  weightChart?.dispose()
  exerciseChart?.dispose()
})
</script>

<style scoped>
.trend-page {
  min-height: 100vh;
  background: #f2f2f7;
  padding-bottom: 72px;
}

/* ─── 顶部导航 ─── */
.top-bar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
}

:deep(.van-nav-bar__title) {
  color: #fff !important;
  font-weight: 700;
  font-size: 17px;
}

:deep(.van-nav-bar) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.logout-btn {
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  cursor: pointer;
}

.content {
  padding: 12px 12px 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* ─── 时间范围 ─── */
.range-card {
  display: flex;
  background: #fff;
  border-radius: 16px;
  padding: 4px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  gap: 2px;
}

.range-tab {
  flex: 1;
  text-align: center;
  padding: 8px 0;
  font-size: 13px;
  font-weight: 500;
  color: #8e8e93;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  -webkit-tap-highlight-color: transparent;
}

.range-active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  font-weight: 700;
  box-shadow: 0 3px 10px rgba(118, 75, 162, 0.3);
}

/* ─── 自定义日期范围 ─── */
.date-range-card {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.date-field {
  background: transparent;
}

:deep(.date-field .van-field__label) {
  color: #764ba2;
  font-weight: 600;
  width: 2.5em;
}

:deep(.date-field.van-cell::after) {
  left: 16px;
  right: 16px;
}

/* ─── 统计概要 ─── */
.summary-row {
  display: flex;
  background: #fff;
  border-radius: 16px;
  padding: 16px 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  align-items: center;
}

.summary-item {
  flex: 1;
  text-align: center;
}

.summary-val {
  font-size: 18px;
  font-weight: 700;
  color: #1a1a2e;
  line-height: 1.2;
}

.summary-label {
  font-size: 10px;
  color: #8e8e93;
  margin-top: 4px;
  line-height: 1.3;
}

.summary-divider {
  width: 1px;
  height: 32px;
  background: #f0f0f5;
}

/* ─── 图表卡片 ─── */
.chart-card {
  background: #fff;
  border-radius: 20px;
  padding: 16px 12px 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.chart-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 12px;
}

.chart-icon {
  font-size: 18px;
  color: #764ba2;
}

.chart-icon-flip {
  transform: scaleY(-1);
  display: inline-block;
}

.chart-icon-orange {
  color: #ff9f0a;
}

.chart-title {
  font-size: 15px;
  font-weight: 700;
  color: #1a1a2e;
}

.chart-canvas {
  width: 100%;
  height: 200px;
}

.chart-loading {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-empty {
  height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ─── 底部导航 ─── */
.bottom-nav {
  border-top: 1px solid #f0f0f5 !important;
}

:deep(.van-tabbar) {
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.06);
}
</style>
