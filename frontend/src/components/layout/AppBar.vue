<template>
  <v-app-bar
    color="primary"
    prominent
    elevation="2"
  >
    <v-app-bar-nav-icon
      variant="text"
      @click.stop="toggleDrawer"
    ></v-app-bar-nav-icon>

    <v-app-bar-title>
      <span class="text-h5 font-weight-bold">테니스 동호회</span>
    </v-app-bar-title>

    <v-spacer></v-spacer>

    <!-- 동호회 선택 -->
    <v-select
      v-if="clubs.length > 0"
      v-model="selectedClubId"
      :items="clubItems"
      item-title="name"
      item-value="id"
      label="동호회 선택"
      density="compact"
      variant="outlined"
      hide-details
      class="mr-4"
      style="max-width: 250px;"
      @update:model-value="handleClubChange"
    ></v-select>

    <!-- 사용자 메뉴 -->
    <v-menu>
      <template v-slot:activator="{ props }">
        <v-btn
          v-bind="props"
          icon="mdi-account-circle"
          size="large"
        ></v-btn>
      </template>
      <v-list>
        <v-list-item>
          <v-list-item-title class="font-weight-bold">
            {{ user?.full_name || user?.username }}
          </v-list-item-title>
          <v-list-item-subtitle>
            {{ user?.email }}
          </v-list-item-subtitle>
        </v-list-item>
        <v-divider></v-divider>
        <v-list-item
          prepend-icon="mdi-account"
          title="프로필"
          @click="goToProfile"
        ></v-list-item>
        <v-list-item
          prepend-icon="mdi-cog"
          title="설정"
          @click="goToSettings"
        ></v-list-item>
        <v-divider></v-divider>
        <v-list-item
          prepend-icon="mdi-logout"
          title="로그아웃"
          @click="handleLogout"
        ></v-list-item>
      </v-list>
    </v-menu>
  </v-app-bar>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { useClubStore } from '@/stores/club'

const router = useRouter()
const authStore = useAuthStore()
const clubStore = useClubStore()

const { user } = storeToRefs(authStore)
const { clubs, selectedClubId } = storeToRefs(clubStore)

const emit = defineEmits(['toggle-drawer'])

// 동호회 목록 아이템
const clubItems = computed(() => {
  return clubs.value.map(club => ({
    id: club.id,
    name: club.name,
  }))
})

// 네비게이션 드로어 토글
function toggleDrawer() {
  emit('toggle-drawer')
}

// 동호회 변경
function handleClubChange(clubId) {
  clubStore.selectClub(clubId)
  // 홈으로 이동
  router.push({ name: 'home' })
}

// 프로필 페이지로 이동
function goToProfile() {
  // TODO: Phase 2에서 구현
  console.log('프로필 페이지')
}

// 설정 페이지로 이동
function goToSettings() {
  // TODO: Phase 2에서 구현
  console.log('설정 페이지')
}

// 로그아웃
function handleLogout() {
  authStore.logout()
}

// 컴포넌트 마운트 시 동호회 목록 로드
onMounted(async () => {
  if (clubs.value.length === 0) {
    await clubStore.fetchClubs()
  }
})
</script>

<style scoped>
.v-app-bar-title {
  cursor: pointer;
}
</style>
