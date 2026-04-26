<template>
  <router-view />
</template>

<style>
:root {
  --van-primary-color: #764ba2;
  --van-button-primary-background: #764ba2;
  --van-nav-bar-background: #764ba2;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body,
#app {
  width: 100%;
  height: 100%;
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Helvetica Neue', sans-serif;
  background: #f2f2f7;
  -webkit-font-smoothing: antialiased;
}

/* 全局滚动优化 */
* {
  -webkit-overflow-scrolling: touch;
}

/* Vant Toast 美化 */
.van-toast {
  border-radius: 12px !important;
}
</style>
