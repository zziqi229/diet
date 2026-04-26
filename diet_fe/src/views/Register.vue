<template>
  <div class="auth-page">
    <div class="auth-container">
      <!-- Logo -->
      <div class="brand">
        <div class="brand-icon">🥗</div>
        <h1 class="brand-name">Diet</h1>
        <p class="brand-desc">开始你的健康之旅</p>
      </div>

      <!-- Form Card -->
      <var-paper :elevation="2" class="form-card">
        <h2 class="form-title">创建账号</h2>

        <var-form ref="formRef" class="form-body">
          <var-input
            v-model="form.username"
            placeholder="用户名"
            :rules="[
              v => !!v || '请输入用户名',
              v => v.length >= 2 || '用户名至少 2 个字符',
            ]"
            size="large"
            class="form-field"
            clearable
          >
            <template #prepend-icon>
              <var-icon name="account-circle-outline" />
            </template>
          </var-input>

          <var-input
            v-model="form.password"
            placeholder="密码（至少 8 位）"
            :rules="[
              v => !!v || '请输入密码',
              v => v.length >= 8 || '密码至少 8 个字符',
            ]"
            type="password"
            size="large"
            class="form-field"
          >
            <template #prepend-icon>
              <var-icon name="lock-outline" />
            </template>
          </var-input>

          <var-input
            v-model="form.confirmPassword"
            placeholder="确认密码"
            :rules="[
              v => !!v || '请再次输入密码',
              v => v === form.password || '两次密码不一致',
            ]"
            type="password"
            size="large"
            class="form-field"
          >
            <template #prepend-icon>
              <var-icon name="lock-check-outline" />
            </template>
          </var-input>

          <var-button
            type="primary"
            size="large"
            block
            :loading="loading"
            class="submit-btn"
            @click="handleRegister"
          >
            注册
          </var-button>
        </var-form>

        <div class="form-footer">
          <span class="footer-text">已有账号？</span>
          <router-link to="/login" class="footer-link">立即登录</router-link>
        </div>
      </var-paper>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { Snackbar } from '@varlet/ui'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
  confirmPassword: '',
})

async function handleRegister() {
  const valid = await formRef.value?.validate()
  if (!valid) return

  loading.value = true
  try {
    await auth.register({ username: form.username, password: form.password })
    Snackbar.success('注册成功，欢迎加入！')
    router.push({ name: 'Dashboard' })
  } catch (err) {
    const msg = err.response?.data?.message || '注册失败，请稍后重试'
    Snackbar.error(msg)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  padding: 24px 16px;
}

.auth-container {
  width: 100%;
  max-width: 400px;
}

.brand {
  text-align: center;
  margin-bottom: 32px;
}

.brand-icon {
  font-size: 56px;
  line-height: 1;
  margin-bottom: 12px;
}

.brand-name {
  font-size: 36px;
  font-weight: 800;
  color: #fff;
  letter-spacing: 2px;
  margin-bottom: 6px;
}

.brand-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.85);
}

.form-card {
  border-radius: 20px !important;
  padding: 32px 24px 24px;
  background: #fff;
}

.form-title {
  font-size: 22px;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 24px;
  text-align: center;
}

.form-body {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-field {
  margin-bottom: 8px;
}

.submit-btn {
  margin-top: 16px;
  height: 48px !important;
  border-radius: 12px !important;
  font-size: 16px !important;
  font-weight: 600 !important;
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%) !important;
}

.form-footer {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
}

.footer-text {
  color: #999;
}

.footer-link {
  color: #11998e;
  font-weight: 600;
  text-decoration: none;
  margin-left: 4px;
}

.footer-link:hover {
  text-decoration: underline;
}
</style>
