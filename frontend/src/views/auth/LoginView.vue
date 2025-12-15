<template>
  <div class="auth-page">
    <v-container class="fill-height" fluid>
      <v-row align="center" justify="center">
        <v-col cols="12" sm="8" md="5" lg="4">
          <v-card class="auth-card" elevation="16" rounded="xl">
            <!-- 로고 & 제목 -->
            <v-card-title class="text-center pa-8 pb-4">
              <div class="w-100">
                <router-link to="/" class="logo-link">
                  <v-icon size="56" color="primary" class="mb-3">mdi-tennis</v-icon>
                </router-link>
                <h1 class="text-h5 font-weight-bold text-primary mb-1">로그인</h1>
                <p class="text-body-2 text-medium-emphasis">테니스 동호회 관리 서비스</p>
              </div>
            </v-card-title>

            <v-card-text class="px-8 pb-8">
              <!-- 에러 메시지 (URL 쿼리 또는 스토어) -->
              <v-alert
                v-if="errorMessage"
                type="error"
                variant="tonal"
                class="mb-4"
                closable
                @click:close="clearError"
              >
                {{ errorMessage }}
              </v-alert>

              <!-- 구글 로그인 버튼 (메인) -->
              <v-btn
                :loading="isGoogleLoading"
                color="white"
                size="x-large"
                block
                rounded="lg"
                class="mb-4 google-btn"
                elevation="2"
                @click="handleGoogleLogin"
              >
                <img
                  src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg"
                  alt="Google"
                  class="google-icon mr-3"
                />
                <span class="text-body-1 font-weight-medium">Google로 계속하기</span>
              </v-btn>

              <p class="text-center text-caption text-medium-emphasis mb-4">
                구글 계정으로 간편하게 시작하세요
              </p>

              <!-- 구분선 -->
              <div class="divider-container mb-4">
                <v-divider />
                <span class="divider-text text-medium-emphasis">또는 이메일로 로그인</span>
                <v-divider />
              </div>

              <!-- 이메일 로그인 토글 -->
              <v-expand-transition>
                <div v-if="showEmailLogin">
                  <v-form ref="loginForm" v-model="valid" @submit.prevent="handleLogin">
                    <!-- 이메일 -->
                    <v-text-field
                      v-model="email"
                      :rules="[rules.required, rules.email]"
                      label="이메일"
                      prepend-inner-icon="mdi-email-outline"
                      type="email"
                      autocomplete="email"
                      variant="outlined"
                      density="comfortable"
                      class="mb-2"
                    />

                    <!-- 비밀번호 -->
                    <v-text-field
                      v-model="password"
                      :rules="[rules.required]"
                      :type="showPassword ? 'text' : 'password'"
                      :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                      label="비밀번호"
                      prepend-inner-icon="mdi-lock-outline"
                      autocomplete="current-password"
                      variant="outlined"
                      density="comfortable"
                      class="mb-4"
                      @click:append-inner="showPassword = !showPassword"
                    />

                    <!-- 로그인 버튼 -->
                    <v-btn
                      :loading="authStore.isLoading"
                      :disabled="!valid"
                      type="submit"
                      color="primary"
                      size="large"
                      block
                      rounded="lg"
                      class="mb-4"
                    >
                      로그인
                    </v-btn>
                  </v-form>
                </div>
              </v-expand-transition>

              <!-- 이메일 로그인 토글 버튼 -->
              <v-btn
                v-if="!showEmailLogin"
                variant="text"
                color="primary"
                size="small"
                block
                class="mb-4"
                @click="showEmailLogin = true"
              >
                <v-icon size="small" class="mr-1">mdi-email-outline</v-icon>
                이메일로 로그인하기
              </v-btn>

              <!-- 구분선 -->
              <v-divider class="mb-4" />

              <!-- 회원가입 링크 -->
              <div class="text-center">
                <span class="text-body-2 text-medium-emphasis">계정이 없으신가요?</span>
                <router-link
                  :to="{ name: 'register' }"
                  class="text-primary text-decoration-none font-weight-medium ml-1"
                >
                  회원가입
                </router-link>
              </div>
            </v-card-text>
          </v-card>

          <!-- 홈으로 돌아가기 -->
          <div class="text-center mt-6">
            <router-link to="/" class="text-white text-decoration-none">
              <v-icon size="small" class="mr-1">mdi-arrow-left</v-icon>
              홈으로 돌아가기
            </router-link>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getGoogleLoginUrl } from '@/api/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const loginForm = ref(null)
const valid = ref(false)
const email = ref('')
const password = ref('')
const showPassword = ref(false)
const showEmailLogin = ref(false)
const isGoogleLoading = ref(false)

// 에러 메시지 (URL 쿼리 파라미터 또는 스토어)
const errorMessage = computed(() => {
  return route.query.error || authStore.error
})

// 에러 초기화
function clearError() {
  authStore.clearError()
  // URL 쿼리에서 error 제거
  if (route.query.error) {
    router.replace({ query: { ...route.query, error: undefined } })
  }
}

// URL에 에러 쿼리가 있으면 표시
onMounted(() => {
  if (route.query.error) {
    console.error('로그인 에러:', route.query.error)
  }
})

// 유효성 검사 규칙
const rules = {
  required: (v) => !!v || '필수 입력 항목입니다',
  email: (v) => /.+@.+\..+/.test(v) || '올바른 이메일 형식이 아닙니다',
}

// 구글 로그인 처리
function handleGoogleLogin() {
  isGoogleLoading.value = true
  const googleUrl = getGoogleLoginUrl()
  window.location.href = googleUrl
}

// 이메일 로그인 처리
async function handleLogin() {
  if (!valid.value) return

  try {
    await authStore.login(email.value, password.value)

    // 리다이렉트 처리
    const redirect = route.query.redirect || '/dashboard'
    router.push(redirect)
  } catch (error) {
    console.error('로그인 실패:', error)
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #059669 0%, #10B981 50%, #34D399 100%);
}

.fill-height {
  min-height: 100vh;
}

.auth-card {
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
}

.logo-link {
  text-decoration: none;
  display: inline-block;
  transition: transform 0.2s;
}

.logo-link:hover {
  transform: scale(1.05);
}

.divider-container {
  display: flex;
  align-items: center;
  gap: 16px;
}

.divider-text {
  font-size: 0.75rem;
  white-space: nowrap;
}

.google-btn {
  border: 1px solid #dadce0;
  text-transform: none;
  letter-spacing: 0;
}

.google-btn:hover {
  background-color: #f8f9fa !important;
  border-color: #dadce0;
}

.google-icon {
  width: 20px;
  height: 20px;
}
</style>
