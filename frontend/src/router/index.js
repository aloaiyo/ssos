import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  // 홈
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
    meta: { requiresAuth: true },
  },
  // 인증
  {
    path: '/auth/login',
    name: 'login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { requiresGuest: true },
  },
  {
    path: '/auth/register',
    name: 'register',
    component: () => import('@/views/auth/RegisterView.vue'),
    meta: { requiresGuest: true },
  },
  // 동호회
  {
    path: '/clubs',
    name: 'club-list',
    component: () => import('@/views/club/ClubListView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/clubs/:id',
    name: 'club-detail',
    component: () => import('@/views/club/ClubDetailView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/clubs/manage',
    name: 'club-manage',
    component: () => import('@/views/club/ClubManageView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  // 회원
  {
    path: '/members',
    name: 'member-list',
    component: () => import('@/views/member/MemberListView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/members/manage',
    name: 'member-manage',
    component: () => import('@/views/member/MemberManageView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  // 404
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// 네비게이션 가드
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // 토큰이 있으면 사용자 정보 로드
  if (authStore.token && !authStore.user) {
    try {
      await authStore.loadUser()
    } catch (error) {
      console.error('사용자 정보 로드 실패:', error)
      authStore.logout()
    }
  }

  // 인증이 필요한 페이지
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next({ name: 'login', query: { redirect: to.fullPath } })
  }

  // 게스트만 접근 가능한 페이지 (로그인, 회원가입)
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    return next({ name: 'home' })
  }

  // 관리자 권한이 필요한 페이지
  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    return next({ name: 'home' })
  }

  next()
})

export default router
