<template>
  <div class="dashboard">
    <var-app-bar title="Diet" title-position="center" color="#764ba2">
      <template #right>
        <var-button text @click="handleLogout">
          <var-icon name="logout" color="#fff" />
        </var-button>
      </template>
    </var-app-bar>

    <div class="content">
      <var-paper :elevation="1" class="welcome-card">
        <div class="welcome-icon">🥗</div>
        <div class="welcome-text">
          <h3>你好，{{ auth.user?.username }}</h3>
          <p>今天也要好好记录饮食哦</p>
        </div>
      </var-paper>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { Dialog } from '@varlet/ui'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

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
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: #f5f5f5;
}

.content {
  padding: 16px;
}

.welcome-card {
  border-radius: 16px !important;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  background: #fff;
}

.welcome-icon {
  font-size: 40px;
}

.welcome-text h3 {
  font-size: 18px;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 4px;
}

.welcome-text p {
  font-size: 13px;
  color: #999;
}
</style>
