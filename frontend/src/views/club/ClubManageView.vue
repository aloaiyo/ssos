<template>
  <div class="club-manage">
    <!-- 헤더 -->
    <header class="page-header">
      <div class="header-content">
        <div class="header-info">
          <v-btn
            icon
            variant="text"
            size="small"
            class="mr-2"
            @click="router.back()"
          >
            <v-icon>mdi-arrow-left</v-icon>
          </v-btn>
          <div>
            <h1 class="page-title">{{ club?.name || '동호회 관리' }}</h1>
            <p class="page-subtitle">동호회 설정 및 관리</p>
          </div>
        </div>
        <div class="header-actions">
          <v-chip
            v-if="myRole === 'manager'"
            color="primary"
            variant="tonal"
            size="small"
          >
            매니저
          </v-chip>
        </div>
      </div>
    </header>

    <!-- 탭 네비게이션 -->
    <v-tabs
      v-model="currentTab"
      color="primary"
      class="tab-navigation"
      show-arrows
    >
      <v-tab
        v-for="tab in tabs"
        :key="tab.value"
        :value="tab.value"
        :prepend-icon="tab.icon"
      >
        {{ tab.title }}
      </v-tab>
    </v-tabs>

    <!-- 탭 컨텐츠 -->
    <v-window v-model="currentTab" class="tab-content">
      <!-- 기본 정보 -->
      <v-window-item value="info">
        <ClubInfoTab :club="club" @update="handleClubUpdate" />
      </v-window-item>

      <!-- 회원 관리 -->
      <v-window-item value="members">
        <MemberManagementTab :club-id="clubId" />
      </v-window-item>

      <!-- 일정 관리 -->
      <v-window-item value="sessions">
        <SessionManagementTab :club-id="clubId" :club="club" />
      </v-window-item>

      <!-- 공지사항 -->
      <v-window-item value="announcements">
        <AnnouncementTab :club-id="clubId" />
      </v-window-item>

      <!-- 회비 관리 -->
      <v-window-item value="fees">
        <FeeManagementTab :club-id="clubId" />
      </v-window-item>

      <!-- 통계 -->
      <v-window-item value="stats">
        <ClubStatsTab :club-id="clubId" />
      </v-window-item>
    </v-window>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useClubStore } from '@/stores/club'
import apiClient from '@/api'
import MemberManagementTab from './components/MemberManagementTab.vue'
import SessionManagementTab from './components/SessionManagementTab.vue'
import ClubInfoTab from './components/ClubInfoTab.vue'
import AnnouncementTab from './components/AnnouncementTab.vue'
import FeeManagementTab from './components/FeeManagementTab.vue'
import ClubStatsTab from './components/ClubStatsTab.vue'

const route = useRoute()
const router = useRouter()
const clubStore = useClubStore()

const { selectedClub } = storeToRefs(clubStore)

const clubId = ref(parseInt(route.params.id))
const club = ref(null)
const currentTab = ref('info')

const tabs = [
  { value: 'info', title: '기본 정보', icon: 'mdi-information-outline' },
  { value: 'members', title: '회원 관리', icon: 'mdi-account-multiple-outline' },
  { value: 'sessions', title: '일정 관리', icon: 'mdi-calendar-outline' },
  { value: 'announcements', title: '공지사항', icon: 'mdi-bullhorn-outline' },
  { value: 'fees', title: '회비 관리', icon: 'mdi-cash-multiple' },
  { value: 'stats', title: '통계', icon: 'mdi-chart-bar' },
]

const myRole = computed(() => {
  return club.value?.my_role || selectedClub.value?.my_role
})

async function loadClub() {
  try {
    const response = await apiClient.get(`/clubs/${clubId.value}`)
    club.value = response.data
  } catch (error) {
    console.error('동호회 정보 로드 실패:', error)
  }
}

function handleClubUpdate(updatedClub) {
  club.value = updatedClub
}

onMounted(() => {
  loadClub()

  // URL 쿼리에서 탭 설정
  if (route.query.tab) {
    currentTab.value = route.query.tab
  }
})
</script>

<style scoped>
.club-manage {
  background: #F8FAFC;
  min-height: calc(100vh - 64px);
}

.page-header {
  background: white;
  border-bottom: 1px solid #E2E8F0;
  padding: 20px 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
}

.header-info {
  display: flex;
  align-items: center;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1E293B;
  margin: 0;
}

.page-subtitle {
  font-size: 0.875rem;
  color: #64748B;
  margin: 0;
}

.tab-navigation {
  background: white;
  border-bottom: 1px solid #E2E8F0;
}

.tab-navigation :deep(.v-tabs) {
  max-width: 1400px;
  margin: 0 auto;
}

.tab-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}
</style>
