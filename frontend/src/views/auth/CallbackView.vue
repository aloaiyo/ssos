<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card>
          <v-card-text class="text-center pa-8">
            <v-progress-circular
              indeterminate
              color="primary"
              size="64"
              class="mb-4"
            ></v-progress-circular>
            <div class="text-h6 mb-2">로그인 처리 중...</div>
            <div class="text-body-2 text-medium-emphasis">
              잠시만 기다려주세요
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

onMounted(async () => {
  try {
    // URL에서 Authorization Code 추출
    const code = route.query.code
    
    if (!code) {
      // 에러가 있는 경우
      const error = route.query.error
      const errorDescription = route.query.error_description
      throw new Error(errorDescription || error || 'Authorization Code를 찾을 수 없습니다')
    }

    // Backend로 Authorization Code 전송하여 로컬 JWT 토큰 받기
    await authStore.handleCallback(code)
    
    // 홈으로 리다이렉트
    router.push({ name: 'home' })
  } catch (error) {
    console.error('콜백 처리 실패:', error)
    // 에러 발생 시 로그인 페이지로 리다이렉트
    router.push({ 
      name: 'login',
      query: { error: error.message || '로그인에 실패했습니다. 다시 시도해주세요.' }
    })
  }
})
</script>

<style scoped>
.fill-height {
  min-height: 100vh;
}
</style>

