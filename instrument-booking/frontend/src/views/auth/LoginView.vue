<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-header">
        <div class="auth-logo">
          <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M12 2L2 7l10 5 10-5-10-5z" />
            <path d="M2 17l10 5 10-5" />
            <path d="M2 12l10 5 10-5" />
          </svg>
        </div>
        <h2 class="auth-title">仪表预约系统</h2>
        <p class="auth-subtitle">上海光电科技创新中心硅光实验室</p>
      </div>
      <LoginForm />
    </div>
    <div class="auth-footer">
      <p>© 2024 上海光电科技创新中心</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import LoginForm from '../../components/auth/LoginForm.vue'
</script>

<style scoped>
.auth-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, var(--color-primary-50) 0%, var(--color-bg) 100%);
  padding: var(--space-lg);
}

.auth-card {
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  padding: var(--space-2xl);
  width: 100%;
  max-width: 420px;
  box-shadow: var(--shadow-xl);
  animation: fadeIn var(--transition-slow) ease;
}

.auth-header {
  text-align: center;
  margin-bottom: var(--space-xl);
}

.auth-logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  background: var(--color-primary-50);
  border-radius: var(--radius-xl);
  color: var(--color-primary);
  margin-bottom: var(--space-md);
}

.auth-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text);
  margin: 0 0 var(--space-sm);
}

.auth-subtitle {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin: 0;
}

.auth-footer {
  margin-top: var(--space-xl);
  text-align: center;
}

.auth-footer p {
  font-size: 12px;
  color: var(--color-text-muted);
  margin: 0;
}
</style>
