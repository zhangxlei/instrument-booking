<template>
  <footer class="app-footer">
    <div class="footer-content">
      <span>如有问题请联系管理员</span>
      <span class="footer-contact">
        <a href="mailto:admin@example.com">admin@example.com</a>
        <span class="footer-sep">|</span>
        <a href="tel:021-12345678">021-12345678</a>
        <span class="footer-sep">|</span>
        友情链接：<a href="http://10.201.5.107:8000/" target="_blank">FTP文件库</a>
      </span>
    </div>
  </footer>
</template>

<style scoped>
.app-footer {
  background: var(--color-text);
  color: var(--color-text-muted);
  font-size: 13px;
  padding: var(--space-md) var(--space-lg);
  margin-top: auto;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-contact a {
  color: var(--color-text-muted);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.footer-contact a:hover {
  color: white;
}

.footer-sep {
  margin: 0 var(--space-sm);
  opacity: 0.5;
}
</style>
