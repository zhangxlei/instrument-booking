import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/auth/LoginView.vue'),
      meta: { guest: true },
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('../views/auth/RegisterView.vue'),
      meta: { guest: true },
    },
    {
      path: '/',
      component: () => import('../components/layout/AppLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', name: 'Home', redirect: '/instruments' },
        {
          path: 'instruments',
          name: 'Instruments',
          component: () => import('../views/instruments/InstrumentListView.vue'),
        },
        {
          path: 'instruments/:id',
          name: 'InstrumentDetail',
          component: () => import('../views/instruments/InstrumentDetailView.vue'),
        },
        {
          path: 'bookings',
          name: 'MyBookings',
          component: () => import('../views/bookings/MyBookingsView.vue'),
        },
        {
          path: 'bookings/:id',
          name: 'BookingDetail',
          component: () => import('../views/bookings/BookingDetailView.vue'),
        },
      ],
    },
    {
      path: '/admin',
      component: () => import('../components/layout/AdminLayout.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
      children: [
        { path: '', name: 'AdminDashboard', component: () => import('../views/admin/AdminDashboardView.vue') },
        {
          path: 'instruments',
          name: 'AdminInstruments',
          component: () => import('../views/admin/AdminInstrumentsView.vue'),
        },
        {
          path: 'instruments/new',
          name: 'AdminInstrumentCreate',
          component: () => import('../views/admin/AdminInstrumentFormView.vue'),
        },
        {
          path: 'instruments/:id/edit',
          name: 'AdminInstrumentEdit',
          component: () => import('../views/admin/AdminInstrumentFormView.vue'),
        },
        {
          path: 'bookings',
          name: 'AdminBookings',
          component: () => import('../views/admin/AdminBookingsView.vue'),
        },
        {
          path: 'users',
          name: 'AdminUsers',
          component: () => import('../views/admin/AdminUsersView.vue'),
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('../views/auth/RegisterView.vue'),
      meta: { guest: true },
    },
  ],
})

router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()
  const loggedIn = authStore.isLoggedIn()

  if (to.meta.requiresAuth && !loggedIn) {
    next('/login')
  } else if (to.meta.guest && loggedIn) {
    next('/')
  } else if (to.meta.requiresAdmin) {
    if (!authStore.user) {
      try {
        const { getMe } = await import('../api/auth')
        const user = await getMe()
        authStore.setUser({
          id: user.id,
          username: user.username,
          full_name: user.full_name,
          role: user.role,
        })
      } catch {
        authStore.logout()
        next('/login')
        return
      }
    }
    if (!authStore.isAdmin()) {
      next('/')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
