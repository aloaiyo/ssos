<template>
  <div class="auth-page">
    <v-container class="fill-height" fluid>
      <v-row align="center" justify="center">
        <v-col cols="12" sm="8" md="5" lg="4">
          <v-card class="auth-card" elevation="16" rounded="xl">
            <!-- 로고 & 제목 -->
            <v-card-title class="text-center pa-8 pb-4">
              <div class="w-100">
                <div class="email-icon-wrapper mb-4">
                  <v-icon size="48" color="primary">mdi-email-check-outline</v-icon>
                </div>
                <h1 class="text-h5 font-weight-bold text-primary mb-1">이메일 인증</h1>
                <p class="text-body-2 text-medium-emphasis">
                  {{ email }}로 발송된<br />
                  6자리 인증번호를 입력해주세요
                </p>
              </div>
            </v-card-title>

            <v-card-text class="px-8 pb-8">
              <v-form ref="verifyForm" v-model="valid" @submit.prevent="handleVerify">
                <!-- 인증번호 입력 -->
                <div class="otp-container mb-6">
                  <v-otp-input
                    v-model="code"
                    length="6"
                    type="number"
                    :disabled="authStore.isLoading"
                    @finish="handleVerify"
                  />
                </div>

                <!-- 에러 메시지 -->
                <v-alert
                  v-if="authStore.error"
                  type="error"
                  variant="tonal"
                  class="mb-4"
                  closable
                  @click:close="authStore.clearError()"
                >
                  {{ authStore.error }}
                </v-alert>

                <!-- 성공 메시지 -->
                <v-alert
                  v-if="resendSuccess"
                  type="success"
                  variant="tonal"
                  class="mb-4"
                  closable
                  @click:close="resendSuccess = false"
                >
                  인증번호가 재발송되었습니다.
                </v-alert>

                <!-- 인증 버튼 -->
                <v-btn
                  :loading="authStore.isLoading"
                  :disabled="code.length !== 6"
                  type="submit"
                  color="primary"
                  size="large"
                  block
                  rounded="lg"
                  class="mb-4 font-weight-bold"
                >
                  <v-icon start>mdi-check-circle</v-icon>
                  인증 완료
                </v-btn>

                <!-- 재발송 -->
                <div class="text-center">
                  <span class="text-body-2 text-medium-emphasis">
                    인증번호를 받지 못하셨나요?
                  </span>
                  <v-btn
                    variant="text"
                    color="primary"
                    size="small"
                    :loading="resendLoading"
                    :disabled="resendCooldown > 0"
                    @click="handleResend"
                  >
                    {{ resendCooldown > 0 ? `${resendCooldown}초 후 재발송` : '재발송' }}
                  </v-btn>
                </div>
              </v-form>
            </v-card-text>
          </v-card>

          <!-- 돌아가기 -->
          <div class="text-center mt-6">
            <router-link :to="{ name: 'register' }" class="text-white text-decoration-none">
              <v-icon size="small" class="mr-1">mdi-arrow-left</v-icon>
              회원가입으로 돌아가기
            </router-link>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const verifyForm = ref(null)
const valid = ref(false)
const code = ref('')
const email = ref('')
const resendLoading = ref(false)
const resendSuccess = ref(false)
const resendCooldown = ref(0)

let cooldownInterval = null

// URL에서 이메일 가져오기
onMounted(() => {
  email.value = route.query.email || authStore.pendingEmail || ''

  if (!email.value) {
    // 이메일이 없으면 회원가입 페이지로 리다이렉트
    router.push({ name: 'register' })
  }
})

onUnmounted(() => {
  if (cooldownInterval) {
    clearInterval(cooldownInterval)
  }
})

// 인증번호 확인
async function handleVerify() {
  if (code.value.length !== 6) return

  try {
    await authStore.verifyEmail(email.value, code.value)

    // 인증 성공 시 대시보드로 이동
    router.push({ name: 'home' })
  } catch (error) {
    console.error('인증 실패:', error)
  }
}

// 인증번호 재발송
async function handleResend() {
  if (resendCooldown.value > 0) return

  resendLoading.value = true
  resendSuccess.value = false

  try {
    await authStore.resendCode(email.value)
    resendSuccess.value = true

    // 60초 쿨다운 시작
    resendCooldown.value = 60
    cooldownInterval = setInterval(() => {
      resendCooldown.value--
      if (resendCooldown.value <= 0) {
        clearInterval(cooldownInterval)
      }
    }, 1000)
  } catch (error) {
    console.error('재발송 실패:', error)
  } finally {
    resendLoading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 50%, #43A047 100%);
}

.fill-height {
  min-height: 100vh;
}

.auth-card {
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
}

.email-icon-wrapper {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}

.otp-container {
  display: flex;
  justify-content: center;
}

.otp-container :deep(.v-otp-input) {
  gap: 8px;
}

.otp-container :deep(.v-otp-input__content) {
  gap: 8px;
}

.otp-container :deep(input) {
  width: 48px !important;
  height: 56px !important;
  font-size: 1.5rem;
  font-weight: 600;
  text-align: center;
  border: 2px solid #E0E0E0;
  border-radius: 12px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.otp-container :deep(input:focus) {
  border-color: #2E7D32;
  box-shadow: 0 0 0 3px rgba(46, 125, 50, 0.15);
}
</style>
