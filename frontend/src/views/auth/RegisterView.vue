<template>
  <div class="auth-page">
    <v-container class="fill-height" fluid>
      <v-row align="center" justify="center">
        <v-col cols="12" sm="8" md="6" lg="5">
          <v-card class="auth-card" elevation="16" rounded="xl">
            <!-- 로고 & 제목 -->
            <v-card-title class="text-center pa-8 pb-4">
              <div class="w-100">
                <router-link to="/" class="logo-link">
                  <v-icon size="56" color="primary" class="mb-3">mdi-tennis</v-icon>
                </router-link>
                <h1 class="text-h5 font-weight-bold text-primary mb-1">회원가입</h1>
                <p class="text-body-2 text-medium-emphasis">테니스 동호회 관리를 시작하세요</p>
              </div>
            </v-card-title>

            <v-card-text class="px-8 pb-8">
              <v-form ref="registerForm" v-model="valid" @submit.prevent="handleRegister">
                <!-- 이름 -->
                <v-text-field
                  v-model="name"
                  :rules="[rules.required, rules.minLength(2)]"
                  label="이름"
                  prepend-inner-icon="mdi-account-outline"
                  autocomplete="name"
                  class="mb-2"
                />

                <!-- 이메일 -->
                <v-text-field
                  v-model="email"
                  :rules="[rules.required, rules.email]"
                  label="이메일"
                  prepend-inner-icon="mdi-email-outline"
                  type="email"
                  autocomplete="email"
                  class="mb-2"
                />

                <!-- 비밀번호 -->
                <v-text-field
                  v-model="password"
                  :rules="[rules.required, rules.password]"
                  :type="showPassword ? 'text' : 'password'"
                  :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                  label="비밀번호"
                  prepend-inner-icon="mdi-lock-outline"
                  autocomplete="new-password"
                  class="mb-2"
                  @click:append-inner="showPassword = !showPassword"
                />

                <!-- 비밀번호 요구사항 -->
                <div class="password-requirements mb-4">
                  <div class="text-caption text-medium-emphasis mb-2">비밀번호 요구사항:</div>
                  <div class="requirements-grid">
                    <div :class="['requirement', { 'met': passwordChecks.length }]">
                      <v-icon size="14" :color="passwordChecks.length ? 'success' : 'grey'">
                        {{ passwordChecks.length ? 'mdi-check-circle' : 'mdi-circle-outline' }}
                      </v-icon>
                      <span>8자 이상</span>
                    </div>
                    <div :class="['requirement', { 'met': passwordChecks.number }]">
                      <v-icon size="14" :color="passwordChecks.number ? 'success' : 'grey'">
                        {{ passwordChecks.number ? 'mdi-check-circle' : 'mdi-circle-outline' }}
                      </v-icon>
                      <span>숫자 포함</span>
                    </div>
                    <div :class="['requirement', { 'met': passwordChecks.uppercase }]">
                      <v-icon size="14" :color="passwordChecks.uppercase ? 'success' : 'grey'">
                        {{ passwordChecks.uppercase ? 'mdi-check-circle' : 'mdi-circle-outline' }}
                      </v-icon>
                      <span>대문자 포함</span>
                    </div>
                    <div :class="['requirement', { 'met': passwordChecks.special }]">
                      <v-icon size="14" :color="passwordChecks.special ? 'success' : 'grey'">
                        {{ passwordChecks.special ? 'mdi-check-circle' : 'mdi-circle-outline' }}
                      </v-icon>
                      <span>특수문자 포함</span>
                    </div>
                  </div>
                </div>

                <!-- 비밀번호 확인 -->
                <v-text-field
                  v-model="passwordConfirm"
                  :rules="[rules.required, rules.match]"
                  :type="showPasswordConfirm ? 'text' : 'password'"
                  :append-inner-icon="showPasswordConfirm ? 'mdi-eye' : 'mdi-eye-off'"
                  label="비밀번호 확인"
                  prepend-inner-icon="mdi-lock-check-outline"
                  autocomplete="new-password"
                  class="mb-4"
                  @click:append-inner="showPasswordConfirm = !showPasswordConfirm"
                />

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

                <!-- 회원가입 버튼 -->
                <v-btn
                  :loading="authStore.isLoading"
                  :disabled="!valid || !allPasswordChecksMet"
                  type="submit"
                  color="primary"
                  size="large"
                  block
                  rounded="lg"
                  class="mb-4 font-weight-bold"
                >
                  <v-icon start>mdi-account-plus</v-icon>
                  회원가입
                </v-btn>

                <!-- 구분선 -->
                <div class="divider-container mb-4">
                  <v-divider />
                  <span class="divider-text text-medium-emphasis">이미 계정이 있으신가요?</span>
                  <v-divider />
                </div>

                <!-- 로그인 링크 -->
                <v-btn
                  :to="{ name: 'login' }"
                  variant="outlined"
                  color="primary"
                  size="large"
                  block
                  rounded="lg"
                >
                  로그인
                </v-btn>
              </v-form>
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
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const registerForm = ref(null)
const valid = ref(false)
const name = ref('')
const email = ref('')
const password = ref('')
const passwordConfirm = ref('')
const showPassword = ref(false)
const showPasswordConfirm = ref(false)

// 비밀번호 체크
const passwordChecks = computed(() => ({
  length: password.value.length >= 8,
  number: /[0-9]/.test(password.value),
  uppercase: /[A-Z]/.test(password.value),
  special: /[!@#$%^&*(),.?":{}|<>]/.test(password.value),
}))

const allPasswordChecksMet = computed(() => {
  return passwordChecks.value.length &&
    passwordChecks.value.number &&
    passwordChecks.value.uppercase &&
    passwordChecks.value.special
})

// 유효성 검사 규칙
const rules = {
  required: (v) => !!v || '필수 입력 항목입니다',
  email: (v) => /.+@.+\..+/.test(v) || '올바른 이메일 형식이 아닙니다',
  minLength: (min) => (v) => (v && v.length >= min) || `최소 ${min}자 이상 입력해주세요`,
  password: (v) => {
    if (!v) return '필수 입력 항목입니다'
    if (v.length < 8) return '8자 이상 입력해주세요'
    if (!/[0-9]/.test(v)) return '숫자를 포함해주세요'
    if (!/[A-Z]/.test(v)) return '대문자를 포함해주세요'
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(v)) return '특수문자를 포함해주세요'
    return true
  },
  match: (v) => v === password.value || '비밀번호가 일치하지 않습니다',
}

// 회원가입 처리
async function handleRegister() {
  if (!valid.value || !allPasswordChecksMet.value) return

  try {
    const result = await authStore.register(email.value, password.value, name.value)

    if (result.success) {
      // 이메일 인증 페이지로 이동
      router.push({
        name: 'verify-email',
        query: { email: result.email }
      })
    }
  } catch (error) {
    console.error('회원가입 실패:', error)
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
  font-size: 0.875rem;
  white-space: nowrap;
}

.password-requirements {
  background: #F5F5F5;
  border-radius: 8px;
  padding: 12px 16px;
}

.requirements-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.requirement {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.75rem;
  color: #757575;
  transition: color 0.2s;
}

.requirement.met {
  color: #10B981;
}
</style>
