<template>
  <div class="dashboard">
    <var-app-bar title="健康日历" title-position="center" color="#764ba2">
      <template #right>
        <var-button text @click="handleLogout">
          <var-icon name="logout" color="#fff" />
        </var-button>
      </template>
    </var-app-bar>

    <div class="content">
      <!-- 月份导航 -->
      <div class="month-nav">
        <var-button round text @click="prevMonth">
          <var-icon name="chevron-left" />
        </var-button>
        <span class="month-title">{{ currentYear }}年{{ currentMonth + 1 }}月</span>
        <var-button round text @click="nextMonth">
          <var-icon name="chevron-right" />
        </var-button>
      </div>

      <!-- 日历 -->
      <div class="calendar-container">
        <div class="cal-grid">
          <div v-for="d in weekDays" :key="d" class="cal-head">{{ d }}</div>
          <div
            v-for="(cell, i) in calendarCells"
            :key="i"
            class="cal-cell"
            :class="{
              'cell-empty': !cell.date,
              'cell-exercise': cell.hasExercise,
              'cell-selected': selectedDate === cell.dateStr,
            }"
            @click="cell.date && selectDate(cell.dateStr)"
          >
            <template v-if="cell.date">
              <div class="day-num" :class="{ 'num-today': cell.isToday }">{{ cell.date }}</div>
              <div class="day-weight" v-if="cell.avgWeight !== null">{{ cell.avgWeight }}</div>
              <div v-else class="day-weight-placeholder"></div>
              <div class="day-dots">
                <span class="dot" :class="getMealDotClass(cell.dateStr, 'breakfast')"></span>
                <span class="dot" :class="getMealDotClass(cell.dateStr, 'lunch')"></span>
                <span class="dot" :class="getMealDotClass(cell.dateStr, 'dinner')"></span>
              </div>
            </template>
          </div>
        </div>
        <!-- 图例 -->
        <div class="legend">
          <div class="legend-item"><span class="dot dot-green"></span>节食</div>
          <div class="legend-item"><span class="dot dot-yellow"></span>正常</div>
          <div class="legend-item"><span class="dot dot-red"></span>大吃</div>
          <div class="legend-item"><span class="dot dot-empty"></span>未记录</div>
          <div class="legend-item"><span class="exercise-badge"></span>有运动</div>
        </div>
      </div>

      <!-- 操作区 -->
      <div class="action-section">
        <div class="action-header">
          <span class="action-date">{{ formatDisplayDate(activeDate) }}</span>
          <span v-if="activeDate === todayStr" class="today-badge">今天</span>
        </div>
        <div class="action-row">
          <var-button class="action-btn" color="#764ba2" text-color="#fff" @click="openWeightDialog">
            ⚖️ 记录体重
          </var-button>
          <var-button class="action-btn" color="#764ba2" text-color="#fff" @click="openExerciseDialog">
            🏃 记录锻炼
          </var-button>
        </div>
        <div class="meal-section">
          <div class="meal-label">🍽️ 记录饮食</div>
          <div class="meal-row">
            <button
              v-for="m in mealTypes"
              :key="m.type"
              class="meal-btn"
              :class="{ 'meal-btn-done': isMealRecorded(activeDate, m.type) }"
              :disabled="isMealRecorded(activeDate, m.type)"
              @click="openMealDialog(m.type)"
            >{{ m.label }}</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 记录体重弹窗 -->
    <var-dialog v-model:show="showWeightDialog" title="记录体重">
      <var-input
        v-model="weightForm.weight_kg"
        type="number"
        placeholder="请输入体重 (kg)"
        clearable
      />
      <template #actions>
        <var-button text @click="showWeightDialog = false">取消</var-button>
        <var-button text color="#764ba2" @click="submitWeight" :loading="submitting">确定</var-button>
      </template>
    </var-dialog>

    <!-- 记录锻炼弹窗 -->
    <var-dialog v-model:show="showExerciseDialog" title="记录锻炼">
      <var-space direction="column" size="12">
        <var-input v-model="exerciseForm.content" placeholder="锻炼内容（如：跑步5公里）" clearable />
        <var-input v-model="exerciseForm.duration_minutes" type="number" placeholder="时长（分钟）" clearable />
      </var-space>
      <template #actions>
        <var-button text @click="showExerciseDialog = false">取消</var-button>
        <var-button text color="#764ba2" @click="submitExercise" :loading="submitting">确定</var-button>
      </template>
    </var-dialog>

    <!-- 记录饮食弹窗 -->
    <var-dialog v-model:show="showMealDialog" :title="mealDialogTitle">
      <div class="intake-section">
        <div class="intake-label">饮食状态</div>
        <div class="intake-options">
          <div
            v-for="opt in intakeOptions"
            :key="opt.value"
            class="intake-opt"
            :class="[opt.colorClass, { 'intake-selected': mealForm.intake_level === opt.value }]"
            @click="mealForm.intake_level = opt.value"
          >{{ opt.label }}</div>
        </div>
      </div>
      <var-input v-model="mealForm.note" placeholder="备注（可选）" clearable style="margin-top:12px" />
      <template #actions>
        <var-button text @click="showMealDialog = false">取消</var-button>
        <var-button text color="#764ba2" @click="submitMeal" :loading="submitting">确定</var-button>
      </template>
    </var-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Dialog, Snackbar } from '@varlet/ui'
import { useAuthStore } from '@/stores/auth'
import { weightApi } from '@/api/weight'
import { mealApi } from '@/api/meal'
import { exerciseApi } from '@/api/exercise'

const router = useRouter()
const auth = useAuthStore()

// ─── 日期工具 ───
const _today = new Date()
const _pad = (n) => String(n).padStart(2, '0')
const todayStr = `${_today.getFullYear()}-${_pad(_today.getMonth() + 1)}-${_pad(_today.getDate())}`

// ─── 日历状态 ───
const currentYear = ref(_today.getFullYear())
const currentMonth = ref(_today.getMonth()) // 0-indexed
const selectedDate = ref(todayStr)
const activeDate = computed(() => selectedDate.value || todayStr)

// ─── 数据存储 ───
const weightData = ref(new Map())    // dateStr -> number[]
const mealData = ref(new Map())      // dateStr -> { breakfast?, lunch?, dinner? }
const exerciseDates = ref(new Set()) // Set<dateStr>
const loading = ref(false)
const submitting = ref(false)

// ─── 弹窗状态 ───
const showWeightDialog = ref(false)
const showExerciseDialog = ref(false)
const showMealDialog = ref(false)
const currentMealType = ref('')

// ─── 表单 ───
const weightForm = reactive({ weight_kg: '' })
const exerciseForm = reactive({ content: '', duration_minutes: '' })
const mealForm = reactive({ intake_level: 'normal', note: '' })

// ─── 静态配置 ───
const weekDays = ['日', '一', '二', '三', '四', '五', '六']
const mealTypes = [
  { type: 'breakfast', label: '早饭' },
  { type: 'lunch', label: '午饭' },
  { type: 'dinner', label: '晚饭' },
]
const intakeOptions = [
  { value: 'fast', label: '节食', colorClass: 'opt-green' },
  { value: 'normal', label: '正常', colorClass: 'opt-yellow' },
  { value: 'feast', label: '大吃', colorClass: 'opt-red' },
]

// ─── 计算属性 ───
const mealDialogTitle = computed(() => {
  const map = { breakfast: '记录早饭', lunch: '记录午饭', dinner: '记录晚饭' }
  return map[currentMealType.value] || '记录饮食'
})

const calendarCells = computed(() => {
  const year = currentYear.value
  const month = currentMonth.value
  const firstWeekday = new Date(year, month, 1).getDay()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const cells = []
  for (let i = 0; i < firstWeekday; i++) {
    cells.push({ date: null, dateStr: null })
  }
  for (let d = 1; d <= daysInMonth; d++) {
    const dateStr = `${year}-${_pad(month + 1)}-${_pad(d)}`
    const weights = weightData.value.get(dateStr) || []
    const avgWeight =
      weights.length > 0
        ? (weights.reduce((a, b) => a + b, 0) / weights.length).toFixed(2)
        : null
    cells.push({
      date: d,
      dateStr,
      isToday: dateStr === todayStr,
      hasExercise: exerciseDates.value.has(dateStr),
      avgWeight,
    })
  }
  return cells
})

// ─── 方法 ───
function getMealDotClass(dateStr, mealType) {
  const meals = mealData.value.get(dateStr)
  if (!meals || !meals[mealType]) return 'dot-empty'
  return { fast: 'dot-green', normal: 'dot-yellow', feast: 'dot-red' }[meals[mealType]] || 'dot-empty'
}

function isMealRecorded(dateStr, mealType) {
  const meals = mealData.value.get(dateStr)
  return !!(meals && meals[mealType])
}

function selectDate(dateStr) {
  selectedDate.value = dateStr
}

function formatDisplayDate(dateStr) {
  if (!dateStr) return ''
  const [, m, d] = dateStr.split('-')
  return `${parseInt(m)}月${parseInt(d)}日`
}

function prevMonth() {
  if (currentMonth.value === 0) {
    currentYear.value--
    currentMonth.value = 11
  } else {
    currentMonth.value--
  }
}

function nextMonth() {
  if (currentMonth.value === 11) {
    currentYear.value++
    currentMonth.value = 0
  } else {
    currentMonth.value++
  }
}

async function loadMonthData() {
  loading.value = true
  const year = currentYear.value
  const month = currentMonth.value
  const mm = _pad(month + 1)
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const startDate = `${year}-${mm}-01`
  const endDate = `${year}-${mm}-${_pad(daysInMonth)}`
  try {
    const [weightRes, mealRes, exerciseRes] = await Promise.all([
      weightApi.list({ start: `${startDate}T00:00:00`, end: `${endDate}T23:59:59` }),
      mealApi.list({ start: startDate, end: endDate }),
      exerciseApi.list({ start: `${startDate}T00:00:00`, end: `${endDate}T23:59:59` }),
    ])
    const wMap = new Map()
    for (const r of weightRes.data.data) {
      const ds = r.recorded_at.substring(0, 10)
      if (!wMap.has(ds)) wMap.set(ds, [])
      wMap.get(ds).push(r.weight_kg)
    }
    weightData.value = wMap

    const mMap = new Map()
    for (const r of mealRes.data.data) {
      if (!mMap.has(r.date)) mMap.set(r.date, {})
      mMap.get(r.date)[r.meal_type] = r.intake_level
    }
    mealData.value = mMap

    const eSet = new Set()
    for (const r of exerciseRes.data.data) {
      eSet.add(r.exercised_at.substring(0, 10))
    }
    exerciseDates.value = eSet
  } catch (e) {
    console.error('loadMonthData failed:', e)
  } finally {
    loading.value = false
  }
}

function openWeightDialog() {
  weightForm.weight_kg = ''
  showWeightDialog.value = true
}

function openExerciseDialog() {
  exerciseForm.content = ''
  exerciseForm.duration_minutes = ''
  showExerciseDialog.value = true
}

function openMealDialog(mealType) {
  currentMealType.value = mealType
  mealForm.intake_level = 'normal'
  mealForm.note = ''
  showMealDialog.value = true
}

function getRecordedAt(dateStr) {
  const now = new Date()
  const nowDate = now.toISOString().substring(0, 10)
  if (dateStr === nowDate) {
    return `${dateStr}T${_pad(now.getHours())}:${_pad(now.getMinutes())}:00`
  }
  return `${dateStr}T12:00:00`
}

async function submitWeight() {
  const weight = parseFloat(weightForm.weight_kg)
  if (isNaN(weight) || weight <= 0) {
    Snackbar.warning('请输入有效体重')
    return
  }
  submitting.value = true
  try {
    await weightApi.create({ weight_kg: weight, recorded_at: getRecordedAt(activeDate.value) })
    Snackbar.success('体重记录成功')
    showWeightDialog.value = false
    await loadMonthData()
  } catch {
    Snackbar.error('记录失败，请重试')
  } finally {
    submitting.value = false
  }
}

async function submitExercise() {
  if (!exerciseForm.content.trim()) {
    Snackbar.warning('请输入锻炼内容')
    return
  }
  const duration = parseInt(exerciseForm.duration_minutes)
  if (isNaN(duration) || duration <= 0) {
    Snackbar.warning('请输入有效时长')
    return
  }
  submitting.value = true
  try {
    await exerciseApi.create({
      content: exerciseForm.content.trim(),
      exercised_at: getRecordedAt(activeDate.value),
      duration_minutes: duration,
    })
    Snackbar.success('锻炼记录成功')
    showExerciseDialog.value = false
    await loadMonthData()
  } catch {
    Snackbar.error('记录失败，请重试')
  } finally {
    submitting.value = false
  }
}

async function submitMeal() {
  submitting.value = true
  try {
    await mealApi.create({
      date: activeDate.value,
      meal_type: currentMealType.value,
      intake_level: mealForm.intake_level,
      note: mealForm.note || undefined,
    })
    Snackbar.success('饮食记录成功')
    showMealDialog.value = false
    await loadMonthData()
  } catch (e) {
    if (e.response?.status === 409) {
      Snackbar.warning('该餐次已记录')
    } else {
      Snackbar.error('记录失败，请重试')
    }
  } finally {
    submitting.value = false
  }
}

async function handleLogout() {
  const action = await Dialog({
    title: '退出登录',
    message: '确定要退出吗？',
    confirmButton: true,
    cancelButton: true,
    confirmButtonText: '退出',
    cancelButtonText: '取消',
  })
  if (action === 'confirm') {
    auth.logout()
    router.push({ name: 'Login' })
  }
}

watch([currentYear, currentMonth], loadMonthData)
onMounted(loadMonthData)
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: #f5f5f5;
}

.content {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* ─── 月份导航 ─── */
.month-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.month-title {
  font-size: 17px;
  font-weight: 700;
  color: #1a1a2e;
  min-width: 110px;
  text-align: center;
}

/* ─── 日历容器 ─── */
.calendar-container {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  padding: 8px 6px 10px;
}

.cal-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
}

.cal-head {
  text-align: center;
  font-size: 12px;
  color: #aaa;
  padding: 4px 0 6px;
  font-weight: 600;
}

.cal-cell {
  min-height: 62px;
  padding: 4px 2px 3px;
  display: flex;
  flex-direction: column;
  align-items: center;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.12s;
  overflow: hidden;
}

.cal-cell:not(.cell-empty):active {
  background: #ede7f6;
}

.cell-empty {
  cursor: default;
}

.cell-exercise {
  background: #e3f2fd;
}

.cell-selected {
  outline: 2px solid #764ba2;
  outline-offset: -2px;
}

/* 日期数字 */
.day-num {
  font-size: 13px;
  font-weight: 600;
  color: #333;
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border-radius: 50%;
}

.num-today {
  background: #764ba2;
  color: #fff;
}

/* 体重均值 */
.day-weight {
  font-size: 9px;
  color: #764ba2;
  font-weight: 600;
  line-height: 1;
  margin-top: 2px;
  height: 11px;
}

.day-weight-placeholder {
  height: 11px;
  margin-top: 2px;
}

/* 三餐彩点 */
.day-dots {
  display: flex;
  gap: 2px;
  margin-top: 3px;
}

.dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

.dot-empty {
  border: 1.5px solid #ccc;
  background: transparent;
}

.dot-green {
  background: #4caf50;
}

.dot-yellow {
  background: #ffc107;
}

.dot-red {
  background: #f44336;
}

/* 图例 */
.legend {
  display: flex;
  gap: 10px;
  padding: 8px 4px 0;
  flex-wrap: wrap;
  border-top: 1px solid #f0f0f0;
  margin-top: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #888;
}

.exercise-badge {
  display: inline-block;
  width: 14px;
  height: 10px;
  background: #e3f2fd;
  border: 1px solid #90caf9;
  border-radius: 2px;
}

/* ─── 操作区 ─── */
.action-section {
  background: #fff;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-date {
  font-size: 16px;
  font-weight: 700;
  color: #1a1a2e;
}

.today-badge {
  font-size: 11px;
  background: #764ba2;
  color: #fff;
  border-radius: 10px;
  padding: 2px 8px;
}

.action-row {
  display: flex;
  gap: 10px;
}

.action-btn {
  flex: 1;
  font-size: 14px !important;
}

/* 饮食按钮组 */
.meal-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.meal-label {
  font-size: 14px;
  font-weight: 600;
  color: #444;
}

.meal-row {
  display: flex;
  gap: 8px;
}

.meal-btn {
  flex: 1;
  padding: 10px 0;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  background: #764ba2;
  color: #fff;
  cursor: pointer;
  transition: opacity 0.15s;
}

.meal-btn:active {
  opacity: 0.8;
}

.meal-btn-done {
  background: #e0e0e0;
  color: #999;
  cursor: not-allowed;
}

/* ─── 饮食状态选择 ─── */
.intake-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.intake-label {
  font-size: 13px;
  color: #666;
}

.intake-options {
  display: flex;
  gap: 10px;
}

.intake-opt {
  flex: 1;
  padding: 10px 0;
  border-radius: 8px;
  text-align: center;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  border: 2px solid transparent;
  transition: border-color 0.15s;
}

.intake-selected {
  border-color: #764ba2 !important;
}

.opt-green {
  background: #e8f5e9;
  color: #2e7d32;
}

.opt-yellow {
  background: #fff8e1;
  color: #f57f17;
}

.opt-red {
  background: #ffebee;
  color: #c62828;
}
</style>
