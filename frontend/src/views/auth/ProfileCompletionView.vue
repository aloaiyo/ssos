<template>
  <v-app>
    <v-container class="fill-height" fluid>
      <v-row align="center" justify="center">
        <v-col cols="12" sm="8" md="6" lg="4">
          <v-card class="profile-card" elevation="16" rounded="xl">
            <v-card-title class="text-center pa-8 pb-4">
              <h1 class="text-h4 font-weight-bold mb-2">추가 정보 입력</h1>
              <p class="text-body-1 text-medium-emphasis">
                서비스 이용을 위해 추가 정보를 입력해주세요
              </p>
            </v-card-title>

            <v-card-text class="px-8 pb-8">
              <v-form ref="form" v-model="valid" @submit.prevent="handleSubmit">
                <!-- 이름 -->
                <v-text-field v-model="name" label="이름" variant="outlined" :rules="[v => !!v || '이름을 입력해주세요']" required
                  class="mb-2"></v-text-field>

                <!-- 성별 -->
                <v-radio-group v-model="gender" inline label="성별" :rules="[v => !!v || '성별을 선택해주세요']" class="mb-2">
                  <v-radio label="남성" value="M"></v-radio>
                  <v-radio label="여성" value="F"></v-radio>
                </v-radio-group>

                <!-- 생년월일 -->
                <v-text-field v-model="birthDate" label="생년월일 (YYYY-MM-DD)" type="date" variant="outlined"
                  :rules="[v => !!v || '생년월일을 입력해주세요']" required class="mb-6"></v-text-field>

                <!-- 에러 메시지 -->
                <v-alert v-if="error" type="error" variant="tonal" class="mb-6" closable @click:close="error = ''">
                  {{ error }}
                </v-alert>

                <!-- 저장 버튼 -->
                <v-btn type="submit" color="primary" size="x-large" block :loading="isLoading" :disabled="!valid">
                  시작!
                </v-btn>
              </v-form>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </v-app>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref(null)
const valid = ref(false)
const name = ref('')
const gender = ref(null)
const birthDate = ref(null)
const error = ref('')
const isLoading = ref(false)

onMounted(async () => {
  // 현재 사용자 정보 로드
  if (authStore.user) {
    name.value = authStore.user.name || ''
    gender.value = authStore.user.gender || null
    // 기존 값이 있을 때만 설정 (기본값 없음 - 필수 입력)
    birthDate.value = authStore.user.birth_date ? authStore.user.birth_date.split('T')[0] : null
  } else {
    try {
      await authStore.loadUser()
      name.value = authStore.user.name || ''
      gender.value = authStore.user.gender || null
      birthDate.value = authStore.user.birth_date ? authStore.user.birth_date.split('T')[0] : null
    } catch (e) {
      router.push({ name: 'login' })
    }
  }
})

async function handleSubmit() {
  const { valid: isValid } = await form.value.validate()

  if (!isValid) return

  isLoading.value = true
  error.value = ''

  try {
    await authStore.updateProfile({
      name: name.value,
      gender: gender.value,
      birth_date: birthDate.value
    })

    // 홈으로 이동
    router.push({ name: 'home' })
  } catch (e) {
    error.value = e.response?.data?.detail || '프로필 저장에 실패했습니다.'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.fill-height {
  min-height: 100vh;
  /* 테니스 코트 색상 그라디언트 (#009630 기준) */
  background: linear-gradient(135deg, #009630 0%, #006420 100%);
}

.profile-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1) !important;
  border: 1px solid rgba(255, 255, 255, 0.18);
}

/* 테니스 테마 버튼 스타일 */
:deep(.v-btn.bg-primary) {
  background-color: #009630 !important;
  color: #FFFFFF !important;
  /* 어두운 배경이므로 흰색 텍스트 */
  font-weight: bold;
  box-shadow: 0 4px 14px 0 rgba(0, 150, 48, 0.4);
}
</style>
