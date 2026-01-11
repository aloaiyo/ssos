import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  // 랜딩 페이지 (비로그인)
  {
    path: '/',
    name: 'landing',
    component: () => import('@/views/LandingView.vue'),
    meta: { isLanding: true },
  },
  // 대시보드 (로그인 후 홈)
  {
    path: '/dashboard',
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
  {
    path: '/auth/verify',
    name: 'verify-email',
    component: () => import('@/views/auth/VerifyEmailView.vue'),
    meta: { requiresGuest: true },
  },
  {
    path: '/auth/callback',
    name: 'auth-callback',
    component: () => import('@/views/auth/CallbackView.vue'),
  },
  {
    path: '/auth/complete-profile',
    name: 'profile-completion',
    component: () => import('@/views/auth/ProfileCompletionView.vue'),
    meta: { requiresAuth: true },
  },
  // 동호회
  {
    path: '/clubs',
    name: 'club-list',
    component: () => import('@/views/club/ClubListView.vue'),
    meta: { requiresAuth: true },
  },
  {
    // 주의: /clubs/create가 /clubs/:id보다 먼저 정의되어야 함
    path: '/clubs/create',
    name: 'club-create',
    component: () => import('@/views/club/ClubCreateView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/clubs/:id',
    name: 'club-detail',
    component: () => import('@/views/club/ClubDetailView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/clubs/:id/manage',
    name: 'club-manage',
    component: () => import('@/views/club/ClubManageView.vue'),
    meta: { requiresAuth: true },
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
  // 시즌
  {
    path: '/seasons',
    name: 'season-list',
    component: () => import('@/views/season/SeasonListView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/seasons/:seasonId',
    name: 'season-detail',
    component: () => import('@/views/season/SeasonDetailView.vue'),
    meta: { requiresAuth: true },
  },
  // 세션
  {
    path: '/sessions',
    name: 'session-list',
    component: () => import('@/views/session/SessionListView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/sessions/:sessionId',
    name: 'session-detail',
    component: () => import('@/views/session/SessionDetailView.vue'),
    meta: { requiresAuth: true },
  },
  // 경기
  {
    path: '/matches',
    name: 'match-list',
    component: () => import('@/views/match/MatchScheduleView.vue'),
    meta: { requiresAuth: true },
  },
  // 랭킹
  {
    path: '/rankings',
    name: 'ranking-list',
    component: () => import('@/views/ranking/RankingView.vue'),
    meta: { requiresAuth: true },
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

  // 404 페이지는 바로 통과
  if (to.name === 'not-found') {
    return next()
  }

  // 인증 상태 확인 (쿠키 기반)
  if (!authStore.user) {
    try {
      await authStore.checkAuth()
    } catch (error) {
      console.error('인증 상태 확인 실패:', error)
    }
  }

  // 랜딩 페이지: 로그인된 사용자는 대시보드로 리다이렉트
  if (to.meta.isLanding && authStore.isAuthenticated) {
    return next({ name: 'home' })
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

  // 프로필 완성 체크 (인증된 사용자만)
  if (authStore.isAuthenticated && authStore.user) {
    const isProfileComplete = authStore.user.gender && authStore.user.birth_date
    const isProfilePage = to.name === 'profile-completion'

    // 프로필 미완성이고 프로필 페이지가 아니면 리다이렉트
    if (!isProfileComplete && !isProfilePage && to.meta.requiresAuth) {
      return next({ name: 'profile-completion' })
    }

    // 프로필 완성했는데 프로필 페이지로 가려고 하면 홈으로
    if (isProfileComplete && isProfilePage) {
      return next({ name: 'home' })
    }
  }

  next()
})

export default router
