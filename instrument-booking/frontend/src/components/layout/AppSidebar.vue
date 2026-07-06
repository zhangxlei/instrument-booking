<template>
  <aside class="sidebar">
    <router-link to="/admin" class="sidebar-item" active-class="active">
      仪表盘
    </router-link>
    <router-link to="/admin/instruments" class="sidebar-item" active-class="active">
      仪器管理
    </router-link>
    <router-link to="/admin/booking-overview" class="sidebar-item" active-class="active">
      预约总览
    </router-link>
    <router-link to="/admin/bookings" class="sidebar-item" active-class="active">
      预约管理
    </router-link>
    <router-link to="/admin/users" class="sidebar-item" active-class="active">
      用户管理
    </router-link>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 200px;
  background: white;
  border-right: 1px solid #e2e8f0;
  padding: 12px 0;
  min-height: calc(100vh - 56px);
}
.sidebar-item {
  display: block;
  padding: 10px 20px;
  font-size: 14px;
  color: #475569;
  text-decoration: none;
  transition: background 0.1s;
}
.sidebar-item:hover {
  background: #f1f5f9;
}
.sidebar-item.active {
  background: #eff6ff;
  color: #3b82f6;
  font-weight: 500;
}
</style>
