<template>
  <v-app>
    <!-- 로그인 페이지가 아닐 때만 네비게이션 표시 -->
    <template v-if="!isAuthPage">
      <app-bar @toggle-drawer="drawerOpen = !drawerOpen" />
      <navigation-drawer v-model="drawerOpen" />
    </template>

    <!-- 메인 콘텐츠 -->
    <v-main>
      <v-container :fluid="isAuthPage">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </v-container>
    </v-main>

    <!-- 푸터 (로그인 페이지가 아닐 때만) -->
    <app-footer v-if="!isAuthPage" />

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
import AppFooter from '@/components/layout/Footer.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import ErrorAlert from '@/components/common/ErrorAlert.vue'

const route = useRoute()
const authStore = useAuthStore()
const { isLoading } = storeToRefs(authStore)

// 네비게이션 드로어 상태
const drawerOpen = ref(false)

// 인증 페이지 여부 확인
const isAuthPage = computed(() => {
  return route.path.startsWith('/auth')
})
</script>

<style scoped>
/* App 레벨 스타일 */
</style>
