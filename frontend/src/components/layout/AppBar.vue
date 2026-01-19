<template>
  <v-app-bar flat class="app-bar" height="64">
    <!-- 모바일 메뉴 버튼 -->
    <v-app-bar-nav-icon
      v-if="isMobile"
      class="ml-2"
      @click.stop="toggleDrawer"
    ></v-app-bar-nav-icon>

    <v-spacer></v-spacer>

    <!-- 동호회 선택 -->
    <v-menu v-if="clubs.length > 0" offset-y>
      <template v-slot:activator="{ props }">
        <v-btn
          v-bind="props"
          variant="tonal"
          color="primary"
          rounded="lg"
          class="club-selector mr-3"
        >
          <v-icon start size="18">mdi-tennis</v-icon>
          <span class="club-name-text">{{ selectedClubName }}</span>
          <v-icon end size="18">mdi-chevron-down</v-icon>
        </v-btn>
      </template>
      <v-list rounded="lg" class="pa-2" min-width="240">
        <!-- 내 동호회 목록 -->
        <div class="list-section-label">내 동호회</div>
        <v-list-item
          v-for="club in clubs"
          :key="club.id"
          :active="selectedClubId === club.id"
          :class="{ 'selected-club': selectedClubId === club.id }"
          rounded="lg"
          @click="handleClubChange(club.id)"
        >
          <template v-slot:prepend>
            <v-icon
              v-if="selectedClubId === club.id"
              size="18"
              color="primary"
              class="mr-2"
            >mdi-check-circle</v-icon>
            <v-icon v-else size="18" color="grey" class="mr-2">mdi-circle-outline</v-icon>
          </template>
          <v-list-item-title :class="{ 'text-primary font-weight-bold': selectedClubId === club.id }">
            {{ club.name }}
          </v-list-item-title>
          <template v-slot:append>
            <v-chip
              v-if="isManager(club)"
              size="x-small"
              color="primary"
              variant="tonal"
            >
              매니저
            </v-chip>
          </template>
        </v-list-item>

        <!-- 매니저 메뉴 (매니저인 경우에만 표시) -->
        <template v-if="isManagerOfSelectedClub">
          <v-divider class="my-2"></v-divider>
          <v-list-item
            rounded="lg"
            prepend-icon="mdi-cog-outline"
            @click="router.push({ name: 'club-manage', params: { id: selectedClubId } })"
          >
            <v-list-item-title>동호회 관리</v-list-item-title>
          </v-list-item>
        </template>

        <v-divider class="my-2"></v-divider>
        <v-list-item
          rounded="lg"
          prepend-icon="mdi-format-list-bulleted"
          @click="router.push({ name: 'club-list' })"
        >
          <v-list-item-title>동호회 찾기</v-list-item-title>
        </v-list-item>
        <v-list-item
          rounded="lg"
          prepend-icon="mdi-plus"
          @click="router.push({ name: 'club-create' })"
        >
          <v-list-item-title>새 동호회 만들기</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>

    <!-- 알림 버튼 -->
    <v-btn icon variant="text" class="mr-1">
      <v-icon>mdi-bell-outline</v-icon>
    </v-btn>

    <!-- 사용자 메뉴 -->
    <v-menu offset-y>
      <template v-slot:activator="{ props }">
        <v-btn
          v-bind="props"
          variant="text"
          class="user-menu-btn mr-2"
        >
          <v-avatar size="36" color="primary">
            <span class="text-white font-weight-bold">{{ userInitial }}</span>
          </v-avatar>
        </v-btn>
      </template>
      <v-list rounded="lg" class="pa-2" min-width="220">
        <v-list-item class="user-info-item">
          <template v-slot:prepend>
            <v-avatar size="40" color="primary" class="mr-3">
              <span class="text-white font-weight-bold">{{ userInitial }}</span>
            </v-avatar>
          </template>
          <v-list-item-title class="font-weight-bold">
            {{ user?.name || '사용자' }}
          </v-list-item-title>
          <v-list-item-subtitle class="text-caption">
            {{ user?.email }}
          </v-list-item-subtitle>
        </v-list-item>
        <v-divider class="my-2"></v-divider>
        <v-list-item
          rounded="lg"
          prepend-icon="mdi-account-outline"
          @click="goToProfile"
        >
          <v-list-item-title>프로필</v-list-item-title>
        </v-list-item>
        <v-list-item
          rounded="lg"
          prepend-icon="mdi-cog-outline"
          @click="goToSettings"
        >
          <v-list-item-title>설정</v-list-item-title>
        </v-list-item>
        <v-divider class="my-2"></v-divider>
        <v-list-item
          rounded="lg"
          prepend-icon="mdi-logout"
          class="text-error"
          @click="handleLogout"
        >
          <v-list-item-title>로그아웃</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>
  </v-app-bar>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { useClubStore } from '@/stores/club'

const router = useRouter()
const authStore = useAuthStore()
const clubStore = useClubStore()

const { user } = storeToRefs(authStore)
const { clubs, selectedClubId, isManagerOfSelectedClub } = storeToRefs(clubStore)

const emit = defineEmits(['toggle-drawer'])

const isMobile = ref(false)

// 반응형 체크
function checkMobile() {
  isMobile.value = window.innerWidth < 1024
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)

  if (authStore.isAuthenticated && clubs.value.length === 0) {
    clubStore.fetchClubs()
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})

// 사용자 이니셜
const userInitial = computed(() => {
  const name = user.value?.name || '?'
  return name.charAt(0).toUpperCase()
})

// 선택된 클럽 이름
const selectedClubName = computed(() => {
  if (!selectedClubId.value) return '동호회 선택'
  const club = clubs.value.find(c => c.id === parseInt(selectedClubId.value))
  return club?.name || '동호회 선택'
})

// 해당 동호회에서 매니저인지 확인
function isManager(club) {
  const role = club.my_role || club.role
  return role === 'manager'
}

// 네비게이션 드로어 토글
function toggleDrawer() {
  emit('toggle-drawer')
}

// 동호회 변경
function handleClubChange(clubId) {
  clubStore.selectClub(clubId)
  router.push({ name: 'home' })
}

// 프로필 페이지로 이동
function goToProfile() {
  router.push({ name: 'my-profile' })
}

// 설정 페이지로 이동 (프로필과 동일)
function goToSettings() {
  router.push({ name: 'my-profile' })
}

// 로그아웃
function handleLogout() {
  authStore.logout()
}
</script>

<style scoped>
.app-bar {
  background: rgba(255, 255, 255, 0.8) !important;
  backdrop-filter: blur(20px);
  border-bottom: 1px solid #F1F5F9 !important;
}

.club-selector {
  text-transform: none;
  letter-spacing: 0;
  font-weight: 500;
}

.club-name-text {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-menu-btn {
  padding: 0 4px !important;
  min-width: auto !important;
}

.user-info-item {
  pointer-events: none;
}

.text-error {
  color: #EF4444 !important;
}

.text-error :deep(.v-icon) {
  color: #EF4444 !important;
}

.list-section-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: #94A3B8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 8px 16px 4px;
}

.selected-club {
  background: rgba(16, 185, 129, 0.08) !important;
}

.selected-club:hover {
  background: rgba(16, 185, 129, 0.12) !important;
}
</style>
