<template>
  <div class="dashboard">
    <!-- 顶部导航栏 -->
    <van-nav-bar
      title="仪表盘"
      class="top-bar"
      :border="false"
    >
      <template #right>
        <span class="logout-btn" @click="handleLogout">退出</span>
      </template>
    </van-nav-bar>

    <div class="content">
      <!-- 月份导航 -->
      <div class="month-nav">
        <button class="nav-arrow" @click="prevMonth">‹</button>
        <span class="month-title">{{ currentYear }}年{{ currentMonth + 1 }}月</span>
        <button class="nav-arrow" @click="nextMonth">›</button>
      </div>

      <!-- 日历 -->
      <div class="calendar-card">
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
          <div class="legend-item"><span class="exercise-dot"></span>有运动</div>
        </div>
      </div>

      <!-- 操作区 -->
      <div class="action-card">
        <div class="action-header">
          <span class="action-date">{{ formatDisplayDate(activeDate) }}</span>
          <van-tag v-if="activeDate === todayStr" color="#764ba2" text-color="#fff" class="today-tag">今天</van-tag>
        </div>

        <!-- 体重 & 运动 -->
        <div class="btn-row">
          <button class="action-btn btn-purple" @click="openWeightDialog">
            <span class="btn-emoji">🪄</span>
            <span>记录体重</span>
          </button>
          <button class="action-btn btn-purple" @click="openExerciseDialog">
            <span class="btn-emoji">🔥</span>
            <span>记录锻炼</span>
          </button>
        </div>

        <!-- 三餐 -->
        <div class="meal-section">
          <div class="meal-label">🍽️ 记录饮食</div>
          <div class="meal-row">
            <button
              v-for="m in mealTypes"
              :key="m.type"
              class="meal-btn"
              :class="{
                'meal-btn-done': isMealRecorded(activeDate, m.type) && !isFutureDate(activeDate),
                'meal-btn-future': isFutureDate(activeDate),
              }"
              :disabled="isFutureDate(activeDate)"
              @click="openMealDialog(m.type)"
            >{{ m.label }}</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 记录体重弹窗 -->
    <van-popup
      v-model:show="showWeightDialog"
      position="bottom"
      round
      class="bottom-popup"
      :style="popupKeyboardStyle"
      @opened="weightFieldRef?.focus()"
    >
      <div class="popup-header">
        <span class="popup-title">⚖️ 记录体重</span>
        <span class="popup-close" @click="showWeightDialog = false">✕</span>
      </div>
      <div class="popup-body">
        <van-field
          ref="weightFieldRef"
          v-model="weightForm.weight_kg"
          type="number"
          placeholder="请输入体重 (kg)"
          class="popup-field"
          clearable
        />
        <van-button
          block
          round
          color="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
          :loading="submitting"
          @click="submitWeight"
        >确认</van-button>
      </div>
    </van-popup>

    <!-- 记录锻炼弹窗 -->
    <van-popup
      v-model:show="showExerciseDialog"
      position="bottom"
      round
      class="bottom-popup"
      :style="popupKeyboardStyle"
      @opened="exerciseFieldRef?.focus()"
    >
      <div class="popup-header">
        <span class="popup-title">🏃 记录锻炼</span>
        <span class="popup-close" @click="showExerciseDialog = false">✕</span>
      </div>
      <div class="popup-body">
        <van-field
          ref="exerciseFieldRef"
          v-model="exerciseForm.content"
          placeholder="锻炼内容"
          class="popup-field"
          clearable
        />
        <van-field
          v-model="exerciseForm.duration_minutes"
          type="number"
          placeholder="时长（min）"
          class="popup-field"
          clearable
        />
        <van-button
          block
          round
          color="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
          :loading="submitting"
          @click="submitExercise"
        >确认</van-button>
      </div>
    </van-popup>

    <!-- 记录饮食弹窗 -->
    <van-popup
      v-model:show="showMealDialog"
      position="bottom"
      round
      class="bottom-popup"
      :style="popupKeyboardStyle"
    >
      <div class="popup-header">
        <span class="popup-title">{{ mealDialogTitle }}</span>
        <span class="popup-close" @click="showMealDialog = false">✕</span>
      </div>
      <div class="popup-body">
        <div class="intake-label">饮食状态</div>
        <div class="intake-options">
          <div
            v-for="opt in intakeOptions"
            :key="opt.value"
            class="intake-opt"
            :class="[opt.colorClass, { 'intake-selected': mealForm.intake_level === opt.value }]"
            @click="mealForm.intake_level = opt.value"
          >
            <span class="intake-emoji">{{ opt.emoji }}</span>
            <span>{{ opt.label }}</span>
          </div>
        </div>
        <van-field
          v-model="mealForm.note"
          placeholder="备注（可选）"
          class="popup-field"
          clearable
        />
        <van-button
          block
          round
          color="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
          :loading="submitting"
          @click="submitMeal"
        >确认</van-button>
      </div>
    </van-popup>

    <!-- 底部导航 -->
    <van-tabbar v-model="tabActive" class="bottom-nav" active-color="#764ba2" inactive-color="#aaa">
      <van-tabbar-item name="dashboard" icon="calendar-o">仪表盘</van-tabbar-item>
      <van-tabbar-item name="trend" icon="chart-trending-o" @click="$router.push('/trend')">趋势</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showConfirmDialog, showSuccessToast, showFailToast, showToast } from 'vant'
import { useAuthStore } from '@/stores/auth'
import { weightApi } from '@/api/weight'
import { mealApi } from '@/api/meal'
import { exerciseApi } from '@/api/exercise'

const router = useRouter()
const auth = useAuthStore()
const tabActive = ref('dashboard')
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
const weightFieldRef = ref(null)
const exerciseFieldRef = ref(null)
const editingMealId = ref(null)
const showMealDialog = ref(false)
const currentMealType = ref('')

// ─── 表单 ───
const weightForm = reactive({ weight_kg: '' })
const exerciseForm = reactive({ content: '', duration_minutes: '' })
const mealForm = reactive({ intake_level: 'normal', note: '' })

// ─── 静态配置 ───
const weekDays = ['一', '二', '三', '四', '五', '六', '日']
const mealTypes = [
  { type: 'breakfast', label: '早饭' },
  { type: 'lunch', label: '午饭' },
  { type: 'dinner', label: '晚饭' },
]
const intakeOptions = [
  { value: 'fast', label: '节食', colorClass: 'opt-green', emoji: '🥗' },
  { value: 'normal', label: '正常', colorClass: 'opt-yellow', emoji: '🍱' },
  { value: 'feast', label: '大吃', colorClass: 'opt-red', emoji: '🍔' },
]

// ─── 计算属性 ───
const mealDialogTitle = computed(() => {
  const map = { breakfast: '记录早饭', lunch: '记录午饭', dinner: '记录晚饭' }
  return map[currentMealType.value] || '记录饮食'
})

const calendarCells = computed(() => {
  const year = currentYear.value
  const month = currentMonth.value
  const firstWeekday = (new Date(year, month, 1).getDay() + 6) % 7
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
  return { fast: 'dot-green', normal: 'dot-yellow', feast: 'dot-red' }[meals[mealType].intake_level] || 'dot-empty'
}

function isFutureDate(dateStr) {
  return dateStr > todayStr
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
      mMap.get(r.date)[r.meal_type] = { id: r.id, intake_level: r.intake_level, note: r.note || '' }
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
  const existing = mealData.value.get(activeDate.value)?.[mealType]
  if (existing) {
    editingMealId.value = existing.id
    mealForm.intake_level = existing.intake_level
    mealForm.note = existing.note || ''
  } else {
    editingMealId.value = null
    mealForm.intake_level = 'normal'
    mealForm.note = ''
  }
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
    showToast('请输入有效体重')
    return
  }
  submitting.value = true
  try {
    await weightApi.create({ weight_kg: weight, recorded_at: getRecordedAt(activeDate.value) })
    showSuccessToast('体重记录成功')
    showWeightDialog.value = false
    await loadMonthData()
  } catch {
    showFailToast('记录失败，请重试')
  } finally {
    submitting.value = false
  }
}

async function submitExercise() {
  if (!exerciseForm.content.trim()) {
    showToast('请输入锻炼内容')
    return
  }
  const duration = parseInt(exerciseForm.duration_minutes)
  if (isNaN(duration) || duration <= 0) {
    showToast('请输入有效时长')
    return
  }
  submitting.value = true
  try {
    await exerciseApi.create({
      content: exerciseForm.content.trim(),
      exercised_at: getRecordedAt(activeDate.value),
      duration_minutes: duration,
    })
    showSuccessToast('锻炼记录成功')
    showExerciseDialog.value = false
    await loadMonthData()
  } catch {
    showFailToast('记录失败，请重试')
  } finally {
    submitting.value = false
  }
}

async function submitMeal() {
  submitting.value = true
  try {
    if (editingMealId.value) {
      await mealApi.update(editingMealId.value, {
        intake_level: mealForm.intake_level,
        note: mealForm.note || undefined,
      })
      showSuccessToast('修改成功')
    } else {
      await mealApi.create({
        date: activeDate.value,
        meal_type: currentMealType.value,
        intake_level: mealForm.intake_level,
        note: mealForm.note || undefined,
      })
      showSuccessToast('饮食记录成功')
    }
    showMealDialog.value = false
    await loadMonthData()
  } catch (e) {
    if (e.response?.status === 409) {
      showToast('该餐次已记录')
    } else {
      showFailToast('记录失败，请重试')
    }
  } finally {
    submitting.value = false
  }
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
  } catch {
    // 用户取消
  }
}

watch([currentYear, currentMonth], loadMonthData)
onMounted(loadMonthData)

// ─── 键盘遮挡修复 ───
const keyboardOffset = ref(0)

function onViewportResize() {
  if (!window.visualViewport) return
  const offset = window.innerHeight - window.visualViewport.offsetTop - window.visualViewport.height
  keyboardOffset.value = Math.max(0, offset)
}

const popupKeyboardStyle = computed(() =>
  keyboardOffset.value > 0
    ? { transform: `translateY(-${keyboardOffset.value}px)`, transition: 'transform 0.1s' }
    : {}
)

watch([showWeightDialog, showExerciseDialog, showMealDialog], ([w, e, m]) => {
  if (w || e || m) {
    window.visualViewport?.addEventListener('resize', onViewportResize)
    window.visualViewport?.addEventListener('scroll', onViewportResize)
  } else {
    window.visualViewport?.removeEventListener('resize', onViewportResize)
    window.visualViewport?.removeEventListener('scroll', onViewportResize)
    keyboardOffset.value = 0
  }
})
</script>

<style scoped>
.dashboard {
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
  padding: 4px 0;
}

/* ─── 底部导航 ─── */
:deep(.van-tabbar) {
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.06);
  border-top: 1px solid #f0f0f5;
}

.content {
  padding: 12px 12px 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* ─── 月份导航 ─── */
.month-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 4px 0;
}

.nav-arrow {
  width: 36px;
  height: 36px;
  border: none;
  background: #fff;
  border-radius: 50%;
  font-size: 22px;
  color: #764ba2;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  transition: background 0.15s;
}
.nav-arrow:active {
  background: #ede7f6;
}

.month-title {
  font-size: 17px;
  font-weight: 700;
  color: #1a1a2e;
  min-width: 110px;
  text-align: center;
}

/* ─── 日历卡片 ─── */
.calendar-card {
  background: #fff;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  padding: 10px 8px 12px;
}

.cal-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
}

.cal-head {
  text-align: center;
  font-size: 11px;
  color: #aaa;
  padding: 4px 0 8px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.cal-cell {
  min-height: 64px;
  padding: 4px 2px 3px;
  display: flex;
  flex-direction: column;
  align-items: center;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.12s;
  overflow: hidden;
  -webkit-tap-highlight-color: transparent;
}

.cal-cell:not(.cell-empty):active {
  background: #ede7f6;
}

.cell-empty {
  cursor: default;
}

.cell-exercise {
  background: linear-gradient(135deg, rgba(100, 181, 246, 0.35), rgba(100, 181, 246, 0.22));
}

.cell-selected {
  outline: 2.5px solid #764ba2;
  outline-offset: -2px;
}

.cell-selected:not(.cell-exercise) {
  background: rgba(118, 75, 162, 0.06);
}

.day-num {
  font-size: 13px;
  font-weight: 600;
  color: #333;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border-radius: 50%;
}

.num-today {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  box-shadow: 0 2px 6px rgba(118, 75, 162, 0.4);
}

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
  border: 1.5px solid #ddd;
  background: transparent;
}

.dot-green  { background: #34c759; }
.dot-yellow { background: #ff9f0a; }
.dot-red    { background: #ff3b30; }

.legend {
  display: flex;
  gap: 10px;
  padding: 10px 4px 0;
  flex-wrap: wrap;
  border-top: 1px solid #f0f0f0;
  margin-top: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #8e8e93;
}

.exercise-dot {
  display: inline-block;
  width: 14px;
  height: 10px;
  background: linear-gradient(135deg, rgba(100, 181, 246, 0.3), rgba(100, 181, 246, 0.15));
  border: 1px solid rgba(100, 181, 246, 0.5);
  border-radius: 3px;
}

/* ─── 操作卡片 ─── */
.action-card {
  background: #fff;
  border-radius: 20px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.action-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-date {
  font-size: 17px;
  font-weight: 700;
  color: #1a1a2e;
}

.today-tag {
  border-radius: 10px !important;
  font-size: 11px !important;
  padding: 2px 8px !important;
}

.btn-row {
  display: flex;
  gap: 10px;
}

.action-btn {
  flex: 1;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 14px 8px;
  border: none;
  border-radius: 14px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s, transform 0.1s;
  -webkit-tap-highlight-color: transparent;
}

.btn-purple {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  box-shadow: 0 4px 12px rgba(118, 75, 162, 0.3);
}

.btn-purple:active {
  opacity: 0.85;
  transform: scale(0.98);
}

.btn-emoji {
  font-size: 20px;
}

/* ─── 饮食记录 ─── */
.meal-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
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
  padding: 11px 0;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  cursor: pointer;
  transition: opacity 0.15s, transform 0.1s;
  box-shadow: 0 3px 10px rgba(118, 75, 162, 0.25);
  -webkit-tap-highlight-color: transparent;
}

.meal-btn:active {
  opacity: 0.8;
  transform: scale(0.97);
}

.meal-btn-done {
  background: #e8e0f5;
  color: #764ba2;
  border: 1.5px solid #c8b4e8;
  box-shadow: none;
}

.meal-btn-future {
  background: #f0f0f5;
  color: #bbb;
  cursor: not-allowed;
  box-shadow: none;
}

/* ─── 底部弹窗 ─── */
.bottom-popup {
  padding-bottom: env(safe-area-inset-bottom, 0);
}

.popup-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 20px 8px;
}

.popup-title {
  font-size: 17px;
  font-weight: 700;
  color: #1a1a2e;
}

.popup-close {
  font-size: 18px;
  color: #aaa;
  cursor: pointer;
  padding: 4px;
  line-height: 1;
}

.popup-body {
  padding: 12px 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.popup-field {
  background: #f7f7fb !important;
  border-radius: 12px !important;
  overflow: hidden;
}

:deep(.popup-field .van-cell) {
  background: #f7f7fb;
  border-radius: 12px;
}

:deep(.popup-field .van-cell::after) {
  display: none;
}

:deep(.van-button--round) {
  height: 50px;
  font-size: 15px;
  font-weight: 600;
}

/* ─── 饮食状态选择 ─── */
.intake-label {
  font-size: 13px;
  color: #8e8e93;
  margin-bottom: -4px;
}

.intake-options {
  display: flex;
  gap: 10px;
}

.intake-opt {
  flex: 1;
  padding: 12px 0;
  border-radius: 12px;
  text-align: center;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  border: 2px solid transparent;
  transition: border-color 0.15s, transform 0.1s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  -webkit-tap-highlight-color: transparent;
}

.intake-opt:active {
  transform: scale(0.97);
}

.intake-emoji {
  font-size: 20px;
}

.intake-selected {
  border-color: #764ba2 !important;
  box-shadow: 0 2px 8px rgba(118, 75, 162, 0.2);
}

.opt-green  { background: #e9f9ee; color: #2e7d32; }
.opt-yellow { background: #fff8e1; color: #e65100; }
.opt-red    { background: #fff0f0; color: #c62828; }
</style>
