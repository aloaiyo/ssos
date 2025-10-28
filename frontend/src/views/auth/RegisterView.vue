<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="10" md="8" lg="6">
        <v-card elevation="8" rounded="lg">
          <v-card-title class="text-h4 text-center pa-6 bg-primary">
            <span class="text-white font-weight-bold">회원가입</span>
          </v-card-title>

          <v-card-text class="pa-8">
            <v-form ref="registerForm" v-model="valid" @submit.prevent="handleSubmit">
              <v-row>
                <!-- 사용자명 -->
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="userData.username"
                    :rules="[required, validateUsername]"
                    label="사용자명 *"
                    prepend-inner-icon="mdi-account"
                    variant="outlined"
                    hint="3-20자의 영문, 숫자, 밑줄만 사용"
                    persistent-hint
                    required
                  ></v-text-field>
                </v-col>

                <!-- 이름 -->
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="userData.full_name"
                    :rules="[required]"
                    label="이름 *"
                    prepend-inner-icon="mdi-account-circle"
                    variant="outlined"
                    required
                  ></v-text-field>
                </v-col>

                <!-- 이메일 -->
                <v-col cols="12">
                  <v-text-field
                    v-model="userData.email"
                    :rules="[required, validateEmail]"
                    label="이메일 *"
                    prepend-inner-icon="mdi-email"
                    variant="outlined"
                    type="email"
                    required
                  ></v-text-field>
                </v-col>

                <!-- 비밀번호 -->
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="userData.password"
                    :rules="[required, validatePassword]"
                    :type="showPassword ? 'text' : 'password'"
                    :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                    label="비밀번호 *"
                    prepend-inner-icon="mdi-lock"
                    variant="outlined"
                    hint="최소 8자, 영문자와 숫자 포함"
                    persistent-hint
                    required
                    @click:append-inner="showPassword = !showPassword"
                  ></v-text-field>
                </v-col>

                <!-- 비밀번호 확인 -->
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="passwordConfirm"
                    :rules="[required, confirmPasswordRule]"
                    :type="showPasswordConfirm ? 'text' : 'password'"
                    :append-inner-icon="showPasswordConfirm ? 'mdi-eye' : 'mdi-eye-off'"
                    label="비밀번호 확인 *"
                    prepend-inner-icon="mdi-lock-check"
                    variant="outlined"
                    required
                    @click:append-inner="showPasswordConfirm = !showPasswordConfirm"
                  ></v-text-field>
                </v-col>
              </v-row>

              <!-- 회원가입 버튼 -->
              <v-btn
                :loading="isLoading"
                :disabled="!valid"
                type="submit"
                color="primary"
                size="large"
                block
                class="mt-6"
              >
                회원가입
              </v-btn>

              <!-- 로그인 링크 -->
              <div class="text-center mt-4">
                <span class="text-body-2">이미 계정이 있으신가요?</span>
                <v-btn
                  :to="{ name: 'login' }"
                  variant="text"
                  color="primary"
                  size="small"
                  class="ml-2"
                >
                  로그인
                </v-btn>
              </div>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { required, validateEmail, validatePassword, validateUsername, confirmPassword } from '@/utils/validators'

const authStore = useAuthStore()
const { isLoading } = storeToRefs(authStore)

const registerForm = ref(null)
const valid = ref(false)
const showPassword = ref(false)
const showPasswordConfirm = ref(false)
const passwordConfirm = ref('')

const userData = ref({
  username: '',
  email: '',
  password: '',
  full_name: '',
})

// 비밀번호 확인 규칙
const confirmPasswordRule = computed(() => {
  return confirmPassword(userData.value.password)
})

// 회원가입 처리
async function handleSubmit() {
  if (!valid.value) return

  try {
    await authStore.register(userData.value)
  } catch (error) {
    console.error('회원가입 실패:', error)
  }
}
</script>

<style scoped>
.fill-height {
  min-height: 100vh;
}

.v-card {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12) !important;
}
</style>
