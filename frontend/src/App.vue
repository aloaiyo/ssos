<template>
  <v-app>
    <!-- 대시보드 레이아웃 (로그인 후) -->
    <template v-if="showDashboardLayout">
      <app-bar @toggle-drawer="drawerOpen = !drawerOpen" />
      <navigation-drawer v-model="drawerOpen" />
    </template>

    <!-- 메인 콘텐츠 -->
    <v-main :class="{ 'landing-main': isLandingPage }">
      <v-container v-if="!isLandingPage" :fluid="isAuthPage">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </v-container>
      <!-- 랜딩 페이지는 컨테이너 없이 전체 화면 -->
      <router-view v-else v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </v-main>

    <!-- 전역 로딩 스피너 -->
    <loading-spinner v-if="isLoading" />

    <!-- 전역 에러 알림 -->
    <error-alert />
  </v-app>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import AppBar from '@/components/layout/AppBar.vue'
import NavigationDrawer from '@/components/layout/NavigationDrawer.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import ErrorAlert from '@/components/common/ErrorAlert.vue'

const route = useRoute()
const authStore = useAuthStore()
const { isLoading } = storeToRefs(authStore)

// 네비게이션 드로어 상태 (데스크톱에서 기본 열림)
const drawerOpen = ref(true)

// 랜딩 페이지 여부
const isLandingPage = computed(() => {
  return route.meta.isLanding === true
})

// 인증 페이지 여부 확인
const isAuthPage = computed(() => {
  return route.path.startsWith('/auth')
})

// 대시보드 레이아웃 표시 여부
const showDashboardLayout = computed(() => {
  return !isAuthPage.value && !isLandingPage.value
})
</script>

<style scoped>
.landing-main {
  padding: 0 !important;
}
</style>
