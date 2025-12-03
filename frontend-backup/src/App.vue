<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  width: 100%;
  overflow-x: hidden;
}

#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  min-height: 100vh;
  background-color: #f5f5f5;
  font-size: 14px;
}

/* 移动端优化 */
@media (max-width: 768px) {
  #app {
    font-size: 16px; /* 移动端稍大字体 */
  }
}
</style>
