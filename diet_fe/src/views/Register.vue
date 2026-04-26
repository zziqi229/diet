<template>
  <div class="auth-page" :style="{ height: pageHeight + 'px' }">
    <!-- 渐变头部 -->
    <div class="auth-header">
      <div class="brand-icon">🥗</div>
      <h1 class="brand-name">Diet</h1>
      <p class="brand-desc">开始你的健康之旅</p>
    </div>

    <!-- 表单卡片 -->
    <div class="auth-card">
      <h2 class="card-title">创建账号</h2>

      <van-form ref="formRef" @submit="handleRegister">
        <div class="fields">
          <van-field
            v-model="form.username"
            name="username"
            placeholder="用户名（至少 2 个字符）"
            :rules="[
              { required: true, message: '请输入用户名' },
              { validator: v => v.length >= 2, message: '用户名至少 2 个字符' },
            ]"
            clearable
            autocomplete="username"
            class="auth-field"
          >
            <template #left-icon>
              <span class="field-icon">👤</span>
            </template>
          </van-field>

          <van-field
            v-model="form.password"
            name="password"
            type="password"
            placeholder="密码（至少 8 位）"
            :rules="[
              { required: true, message: '请输入密码' },
              { validator: v => v.length >= 8, message: '密码至少 8 个字符' },
            ]"
            autocomplete="new-password"
            class="auth-field"
          >
            <template #left-icon>
              <span class="field-icon">🔒</span>
            </template>
          </van-field>

          <van-field
            v-model="form.confirmPassword"
            name="confirmPassword"
            type="password"
            placeholder="确认密码"
            :rules="[
              { required: true, message: '请再次输入密码' },
              { validator: v => v === form.password, message: '两次密码不一致' },
            ]"
            autocomplete="new-password"
            class="auth-field"
          >
            <template #left-icon>
              <span class="field-icon">✅</span>
            </template>
          </van-field>
        </div>

        <van-button
          type="primary"
          size="large"
          block
          round
          native-type="submit"
          :loading="loading"
          class="submit-btn"
        >
          注册
        </van-button>
      </van-form>

      <p class="card-footer">
        已有账号？
        <router-link to="/login" class="footer-link">立即登录</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { showSuccessToast, showFailToast } from 'vant'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const formRef = ref(null)
const loading = ref(false)
const form = reactive({ username: '', password: '', confirmPassword: '' })
const pageHeight = ref(window.visualViewport?.height ?? window.innerHeight)

function onViewportResize() {
  pageHeight.value = window.visualViewport?.height ?? window.innerHeight
}

onMounted(() => window.visualViewport?.addEventListener('resize', onViewportResize))
onUnmounted(() => window.visualViewport?.removeEventListener('resize', onViewportResize))

async function handleRegister() {
  loading.value = true
  try {
    await auth.register({ username: form.username, password: form.password })
    showSuccessToast('注册成功，欢迎加入！')
    router.push({ name: 'Dashboard' })
  } catch (err) {
    showFailToast(err.response?.data?.message || '注册失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* ─── 页面容器 ─── */
.auth-page {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: linear-gradient(160deg, #11998e 0%, #38ef7d 100%);
}

/* ─── 渐变头部 ─── */
.auth-header {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 24px 24px;
  text-align: center;
  overflow: hidden;
}

.brand-icon {
  font-size: 64px;
  line-height: 1;
  margin-bottom: 16px;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.15));
}

.brand-name {
  font-size: 42px;
  font-weight: 800;
  color: #fff;
  letter-spacing: 6px;
  margin-bottom: 10px;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.brand-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.85);
  letter-spacing: 0.5px;
}

/* ─── 表单卡片 ─── */
.auth-card {
  background: #fff;
  border-radius: 28px 28px 0 0;
  padding: 32px 24px 40px;
  box-shadow: 0 -4px 30px rgba(0, 0, 0, 0.08);
}

.card-title {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 28px;
  text-align: center;
}

/* ─── 输入字段 ─── */
.fields {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}

.auth-field {
  border-radius: 14px;
  overflow: hidden;
  background: #f5f5fa;
}

:deep(.auth-field.van-cell) {
  background: #f5f5fa;
  padding: 14px 16px;
}

:deep(.auth-field.van-cell::after) {
  display: none;
}

:deep(.auth-field .van-field__left-icon) {
  margin-right: 10px;
  display: flex;
  align-items: center;
}

.field-icon {
  font-size: 17px;
}

/* ─── 提交按钮 ─── */
.submit-btn {
  height: 52px !important;
  font-size: 16px !important;
  font-weight: 600 !important;
  letter-spacing: 2px;
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%) !important;
  border: none !important;
  box-shadow: 0 8px 24px rgba(17, 153, 142, 0.4);
}

/* ─── 底部导航 ─── */
.card-footer {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: #999;
}

.footer-link {
  color: #11998e;
  font-weight: 600;
  text-decoration: none;
  margin-left: 4px;
}
</style>

