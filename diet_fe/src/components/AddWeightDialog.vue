<template>
  <el-dialog
    v-model="visible"
    title="记录体重"
    width="min(420px, 94vw)"
    draggable
    @closed="resetForm"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
      <el-form-item label="日期时间" prop="date">
        <el-date-picker
          v-model="form.date"
          type="datetime"
          placeholder="选择日期时间"
          style="width: 100%"
          size="large"
          :disabled-date="disabledFuture"
          format="YYYY-MM-DD HH:mm:ss"
          value-format="x"
        />
      </el-form-item>
      <el-form-item label="体重 (kg)" prop="weight_kg">
        <el-input-number
          v-model="form.weight_kg"
          :min="10"
          :max="500"
          :precision="1"
          :step="0.1"
          style="width: 100%"
          size="large"
          controls-position="right"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <div class="footer-right">
          <el-button @click="visible = false">取消</el-button>
          <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
        </div>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useWeightStore } from '@/stores/weight'
import dayjs from 'dayjs'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  defaultDate: { type: String, default: null }, // 'YYYY-MM-DD'
})

const emit = defineEmits(['update:modelValue', 'saved'])

const weightStore = useWeightStore()

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})

const formRef = ref(null)
const saving = ref(false)

const form = reactive({
  date: null,
  weight_kg: 60.0,
})

const rules = {
  date: [{ required: true, message: '请选择日期', trigger: 'change' }],
  weight_kg: [{ required: true, message: '请输入体重', trigger: 'blur' }],
}

watch(
  () => props.modelValue,
  (open) => {
    if (!open) return
    if (props.defaultDate) {
      const now = dayjs()
      form.date = dayjs(props.defaultDate)
        .hour(now.hour()).minute(now.minute()).second(now.second())
        .valueOf()
    } else {
      form.date = dayjs().valueOf()
    }
    form.weight_kg = 60.0
  },
)

function resetForm() {
  formRef.value?.resetFields()
}

function disabledFuture(date) {
  return date > new Date()
}

async function handleSave() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  const payload = {
    weight_kg: form.weight_kg,
    recorded_at: dayjs(form.date).toISOString(),
  }

  saving.value = true
  try {
    await weightStore.addRecord(payload)
    ElMessage.success('记录成功')
    visible.value = false
    emit('saved')
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '操作失败，请重试')
  } finally {
    saving.value = false
  }
}

</script>

<style scoped>
.dialog-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.footer-right {
  display: flex;
  gap: 8px;
}
</style>
