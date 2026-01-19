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

      <!-- 기본 프로필 수정 -->
      <v-card class="edit-card" variant="flat">
        <v-card-title class="edit-title">기본 프로필</v-card-title>
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

      <!-- 클럽별 프로필 -->
      <v-card class="club-profiles-card" variant="flat">
        <v-card-title class="edit-title">
          <v-icon size="20" class="mr-2">mdi-account-group</v-icon>
          클럽별 프로필
        </v-card-title>
        <v-card-subtitle class="px-4 pb-2">
          각 클럽에서 사용할 이름을 개별적으로 설정할 수 있습니다
        </v-card-subtitle>
        <v-card-text>
          <!-- 멤버십 로딩 -->
          <div v-if="isLoadingMemberships" class="text-center py-4">
            <v-progress-circular indeterminate color="primary" size="32"></v-progress-circular>
          </div>

          <!-- 멤버십 없음 -->
          <div v-else-if="memberships.length === 0" class="empty-memberships">
            <v-icon size="48" color="grey-lighten-1">mdi-tennis</v-icon>
            <p class="text-grey mt-2">가입된 동호회가 없습니다</p>
            <v-btn
              color="primary"
              variant="tonal"
              size="small"
              class="mt-2"
              @click="$router.push({ name: 'club-list' })"
            >
              동호회 찾기
            </v-btn>
          </div>

          <!-- 멤버십 목록 -->
          <div v-else class="membership-list">
            <div
              v-for="membership in memberships"
              :key="membership.id"
              class="membership-item"
            >
              <div class="membership-header">
                <div class="club-info">
                  <v-icon size="20" color="primary" class="mr-2">mdi-tennis</v-icon>
                  <span class="club-name">{{ membership.club_name }}</span>
                  <v-chip
                    v-if="membership.role === 'manager'"
                    size="x-small"
                    color="primary"
                    variant="tonal"
                    class="ml-2"
                  >
                    매니저
                  </v-chip>
                </div>
                <v-btn
                  icon
                  size="small"
                  variant="text"
                  @click="openEditMembershipDialog(membership)"
                >
                  <v-icon size="18">mdi-pencil</v-icon>
                </v-btn>
              </div>
              <div class="membership-details">
                <div class="detail-item">
                  <span class="detail-label">닉네임</span>
                  <span class="detail-value">{{ membership.nickname || user?.name || '-' }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">성별</span>
                  <span class="detail-value">{{ membership.gender === 'male' ? '남성' : '여성' }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">전적</span>
                  <span class="detail-value">{{ membership.wins }}승 {{ membership.losses }}패 ({{ membership.win_rate }}%)</span>
                </div>
              </div>
            </div>
          </div>
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

    <!-- 클럽 프로필 수정 다이얼로그 -->
    <v-dialog v-model="showEditMembershipDialog" max-width="400">
      <v-card>
        <v-card-title>
          <v-icon size="20" class="mr-2">mdi-tennis</v-icon>
          {{ editingMembership?.club_name }} 프로필 수정
        </v-card-title>
        <v-card-text>
          <v-form @submit.prevent="saveMembership">
            <v-text-field
              v-model="membershipForm.nickname"
              label="닉네임"
              variant="outlined"
              :placeholder="user?.name || ''"
              hint="이 클럽에서 사용할 이름입니다. 비워두면 기본 이름이 사용됩니다."
              persistent-hint
              class="mb-3"
            ></v-text-field>

            <v-select
              v-model="membershipForm.gender"
              label="성별"
              :items="genderOptions"
              item-title="label"
              item-value="value"
              variant="outlined"
              class="mb-3"
            ></v-select>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="showEditMembershipDialog = false">취소</v-btn>
          <v-btn
            color="primary"
            variant="flat"
            :loading="isSavingMembership"
            @click="saveMembership"
          >
            저장
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

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
import authApi from '@/api/auth'

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

// 클럽 멤버십 관련
const memberships = ref([])
const isLoadingMemberships = ref(false)
const showEditMembershipDialog = ref(false)
const editingMembership = ref(null)
const isSavingMembership = ref(false)
const membershipForm = ref({
  nickname: '',
  gender: ''
})

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

async function loadMemberships() {
  isLoadingMemberships.value = true
  try {
    const response = await authApi.getMyMemberships()
    memberships.value = response.data || []
  } catch (error) {
    console.error('멤버십 로드 실패:', error)
  } finally {
    isLoadingMemberships.value = false
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

function openEditMembershipDialog(membership) {
  editingMembership.value = membership
  membershipForm.value = {
    nickname: membership.nickname || '',
    gender: membership.gender
  }
  showEditMembershipDialog.value = true
}

async function saveMembership() {
  if (!editingMembership.value) return

  isSavingMembership.value = true
  try {
    const response = await authApi.updateMyMembershipInClub(
      editingMembership.value.club_id,
      {
        nickname: membershipForm.value.nickname || null,
        gender: membershipForm.value.gender
      }
    )

    // 목록 업데이트
    const index = memberships.value.findIndex(m => m.id === editingMembership.value.id)
    if (index !== -1) {
      memberships.value[index] = response.data
    }

    showEditMembershipDialog.value = false
    snackbarMessage.value = '클럽 프로필이 저장되었습니다'
    snackbarColor.value = 'success'
    showSnackbar.value = true
  } catch (error) {
    console.error('클럽 프로필 저장 실패:', error)
    snackbarMessage.value = error.response?.data?.detail || '클럽 프로필 저장에 실패했습니다'
    snackbarColor.value = 'error'
    showSnackbar.value = true
  } finally {
    isSavingMembership.value = false
  }
}

onMounted(() => {
  loadProfile()
  loadMemberships()
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
.account-card,
.club-profiles-card {
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
  display: flex;
  align-items: center;
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

/* 클럽 멤버십 스타일 */
.empty-memberships {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  text-align: center;
}

.membership-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.membership-item {
  background: #F8FAFC;
  border-radius: 12px;
  padding: 16px;
  border: 1px solid #E2E8F0;
}

.membership-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.club-info {
  display: flex;
  align-items: center;
}

.club-name {
  font-weight: 600;
  color: #1E293B;
}

.membership-details {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.detail-label {
  font-size: 0.75rem;
  color: #94A3B8;
  text-transform: uppercase;
}

.detail-value {
  font-size: 0.85rem;
  color: #1E293B;
  font-weight: 500;
}

@media (max-width: 480px) {
  .membership-details {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
