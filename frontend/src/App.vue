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

    <!-- 전역 스낵바 (alert 대체) -->
    <v-snackbar
      v-model="snackbar"
      :color="snackbarColor"
      :timeout="4000"
      location="top"
    >
      {{ snackbarMessage }}
      <template v-slot:actions>
        <v-btn variant="text" color="white" @click="closeSnackbar">닫기</v-btn>
      </template>
    </v-snackbar>

    <!-- 전역 확인 다이얼로그 (confirm 대체) -->
    <v-dialog v-model="confirmDialog" max-width="400" persistent>
      <v-card>
        <v-card-title>{{ confirmTitle }}</v-card-title>
        <v-card-text>{{ confirmMessage }}</v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="handleCancel">취소</v-btn>
          <v-btn color="primary" variant="flat" @click="handleConfirm">확인</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
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
import { useConfirmDialog } from '@/composables/useConfirmDialog'

const {
  snackbar,
  snackbarMessage,
  snackbarColor,
  closeSnackbar,
  confirmDialog,
  confirmMessage,
  confirmTitle,
  handleConfirm,
  handleCancel,
} = useConfirmDialog()

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
  return authStore.isAuthenticated && !isAuthPage.value && !isLandingPage.value
})
</script>

<style scoped>
.landing-main {
  padding: 0 !important;
}
</style>
