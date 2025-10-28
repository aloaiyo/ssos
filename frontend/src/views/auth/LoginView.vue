<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card elevation="8" rounded="lg">
          <v-card-title class="text-h4 text-center pa-6 bg-primary">
            <span class="text-white font-weight-bold">로그인</span>
          </v-card-title>

          <v-card-text class="pa-8">
            <v-form ref="loginForm" v-model="valid" @submit.prevent="handleSubmit">
              <!-- 사용자명 -->
              <v-text-field
                v-model="credentials.username"
                :rules="[required, validateUsername]"
                label="사용자명"
                prepend-inner-icon="mdi-account"
                variant="outlined"
                required
                autofocus
              ></v-text-field>

              <!-- 비밀번호 -->
              <v-text-field
                v-model="credentials.password"
                :rules="[required]"
                :type="showPassword ? 'text' : 'password'"
                :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                label="비밀번호"
                prepend-inner-icon="mdi-lock"
                variant="outlined"
                required
                @click:append-inner="showPassword = !showPassword"
              ></v-text-field>

              <!-- 로그인 버튼 -->
              <v-btn
                :loading="isLoading"
                :disabled="!valid"
                type="submit"
                color="primary"
                size="large"
                block
                class="mt-4"
              >
                로그인
              </v-btn>

              <!-- 회원가입 링크 -->
              <div class="text-center mt-4">
                <span class="text-body-2">계정이 없으신가요?</span>
                <v-btn
                  :to="{ name: 'register' }"
                  variant="text"
                  color="primary"
                  size="small"
                  class="ml-2"
                >
                  회원가입
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
import { ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { required, validateUsername } from '@/utils/validators'

const authStore = useAuthStore()
const { isLoading } = storeToRefs(authStore)

const loginForm = ref(null)
const valid = ref(false)
const showPassword = ref(false)

const credentials = ref({
  username: '',
  password: '',
})

// 로그인 처리
async function handleSubmit() {
  if (!valid.value) return

  try {
    await authStore.login(credentials.value)
  } catch (error) {
    console.error('로그인 실패:', error)
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
