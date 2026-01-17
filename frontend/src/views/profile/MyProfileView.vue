<template>
  <div class="my-profile-page">
    <!-- 헤더 -->
    <div class="page-header">
      <v-btn icon variant="text" @click="goBack" class="back-btn">
        <v-icon>mdi-arrow-left</v-icon>
      </v-btn>
      <h1 class="page-title">내 정보</h1>
    </div>

    <!-- 로딩 -->
    <div v-if="isLoading" class="loading-container">
      <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
    </div>

    <template v-else>
      <!-- 프로필 카드 -->
      <v-card class="profile-card" variant="flat">
        <div class="profile-header">
          <v-avatar size="80" color="primary">
            <span class="text-h4 text-white">{{ userInitial }}</span>
          </v-avatar>
          <div class="profile-info">
            <h2 class="user-name">{{ user?.name || '이름 없음' }}</h2>
            <p class="user-email">{{ user?.email }}</p>
          </div>
        </div>
      </v-card>

      <!-- 정보 수정 폼 -->
      <v-card class="edit-card" variant="flat">
        <v-card-title class="edit-title">프로필 수정</v-card-title>
        <v-card-text>
          <v-form ref="formRef" v-model="formValid" @submit.prevent="saveProfile">
            <v-text-field
              v-model="editForm.name"
              label="이름"
              variant="outlined"
              :rules="[v => !!v || '이름을 입력해주세요']"
              required
              class="mb-3"
            ></v-text-field>

            <v-select
              v-model="editForm.gender"
              label="성별"
              :items="genderOptions"
              item-title="label"
              item-value="value"
              variant="outlined"
              :rules="[v => !!v || '성별을 선택해주세요']"
              required
              class="mb-3"
            ></v-select>

            <v-text-field
              v-model="editForm.birth_date"
              label="생년월일"
              type="date"
              variant="outlined"
              class="mb-3"
            ></v-text-field>

            <v-btn
              type="submit"
              color="primary"
              variant="flat"
              block
              size="large"
              :loading="isSaving"
              :disabled="!formValid"
            >
              저장하기
            </v-btn>
          </v-form>
        </v-card-text>
      </v-card>

      <!-- 계정 정보 -->
      <v-card class="account-card" variant="flat">
        <v-card-title class="edit-title">계정 정보</v-card-title>
        <v-card-text>
          <div class="account-item">
            <span class="account-label">구독 등급</span>
            <v-chip :color="user?.is_premium ? 'warning' : 'grey'" size="small">
              {{ user?.is_premium ? '프리미엄' : '무료' }}
            </v-chip>
          </div>
          <div class="account-item">
            <span class="account-label">가입일</span>
            <span class="account-value">{{ formatDate(user?.created_at) }}</span>
          </div>
        </v-card-text>
      </v-card>
    </template>

    <!-- 성공/에러 스낵바 -->
    <v-snackbar v-model="showSnackbar" :color="snackbarColor" timeout="3000">
      {{ snackbarMessage }}
    </v-snackbar>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const isLoading = ref(true)
const isSaving = ref(false)
const formRef = ref(null)
const formValid = ref(false)

const user = computed(() => authStore.user)
const userInitial = computed(() => user.value?.name?.charAt(0) || '?')

const editForm = ref({
  name: '',
  gender: '',
  birth_date: ''
})

const genderOptions = [
  { value: 'male', label: '남성' },
  { value: 'female', label: '여성' }
]

const showSnackbar = ref(false)
const snackbarMessage = ref('')
const snackbarColor = ref('success')

function goBack() {
  router.back()
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}`
}

async function loadProfile() {
  isLoading.value = true
  try {
    await authStore.loadUser()
    if (user.value) {
      editForm.value = {
        name: user.value.name || '',
        gender: user.value.gender || '',
        birth_date: user.value.birth_date?.split('T')[0] || ''
      }
    }
  } catch (error) {
    console.error('프로필 로드 실패:', error)
  } finally {
    isLoading.value = false
  }
}

async function saveProfile() {
  if (!formValid.value) return

  isSaving.value = true
  try {
    await authStore.updateProfile({
      name: editForm.value.name,
      gender: editForm.value.gender,
      birth_date: editForm.value.birth_date || null
    })
    snackbarMessage.value = '프로필이 저장되었습니다'
    snackbarColor.value = 'success'
    showSnackbar.value = true
  } catch (error) {
    console.error('프로필 저장 실패:', error)
    snackbarMessage.value = error.response?.data?.detail || '프로필 저장에 실패했습니다'
    snackbarColor.value = 'error'
    showSnackbar.value = true
  } finally {
    isSaving.value = false
  }
}

onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.my-profile-page {
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1E293B;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.profile-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 16px;
  border: 1px solid #E2E8F0;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 16px;
}

.profile-info {
  flex: 1;
}

.user-name {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1E293B;
  margin-bottom: 4px;
}

.user-email {
  font-size: 0.9rem;
  color: #64748B;
}

.edit-card,
.account-card {
  background: white;
  border-radius: 16px;
  padding: 8px;
  margin-bottom: 16px;
  border: 1px solid #E2E8F0;
}

.edit-title {
  font-size: 1rem;
  font-weight: 600;
  color: #1E293B;
  padding: 16px 16px 8px;
}

.account-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #F1F5F9;
}

.account-item:last-child {
  border-bottom: none;
}

.account-label {
  font-size: 0.9rem;
  color: #64748B;
}

.account-value {
  font-size: 0.9rem;
  color: #1E293B;
  font-weight: 500;
}
</style>
