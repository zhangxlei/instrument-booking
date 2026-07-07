<template>
  <aside class="sidebar">
    <router-link to="/admin" class="sidebar-item" active-class="active">
      仪表盘
    </router-link>
    <router-link to="/admin/instruments" class="sidebar-item" active-class="active">
      仪器管理
    </router-link>
    <router-link to="/admin/booking-overview" class="sidebar-item" active-class="active">
      仪表预约管理
    </router-link>
    <router-link to="/admin/bookings" class="sidebar-item" active-class="active">
      审批管理
    </router-link>
    <router-link to="/admin/documents" class="sidebar-item" active-class="active">
      通知文档
    </router-link>
    <router-link to="/admin/users" class="sidebar-item" active-class="active">
      用户管理
    </router-link>
    <router-link to="/admin/online-status" class="sidebar-item" active-class="active">
      在线用户
    </router-link>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 220px;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  padding: var(--space-md) 0;
  min-height: calc(100vh - 64px);
}

.sidebar-item {
  display: block;
  padding: var(--space-sm) var(--space-lg);
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-secondary);
  text-decoration: none;
  transition: all var(--transition-fast);
  border-left: 3px solid transparent;
}

.sidebar-item:hover {
  background: var(--color-surface-hover);
  color: var(--color-text);
}

.sidebar-item.active {
  background: var(--color-primary-50);
  color: var(--color-primary);
  border-left-color: var(--color-primary);
}
</style>
