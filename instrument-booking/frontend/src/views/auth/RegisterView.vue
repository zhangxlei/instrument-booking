<template>
  <div class="auth-page">
    <div class="auth-card">
      <h2 class="auth-title">硅光实验室预约管理系统(试运行)</h2>
      <RegisterForm />
    </div>
  </div>
</template>

<script setup lang="ts">
import RegisterForm from '../../components/auth/RegisterForm.vue'
</script>

<style scoped>
.auth-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: #f1f5f9;
}
.auth-card {
  background: white;
  border-radius: 8px;
  padding: 32px;
  width: 380px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}
.auth-title {
  text-align: center;
  margin-bottom: 24px;
  font-size: 22px;
  color: #1e293b;
}
</style>
