<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <!-- 환영 메시지 -->
        <v-card elevation="2" class="mb-6">
          <v-card-title class="text-h4 py-6">
            <v-icon icon="mdi-hand-wave" size="large" class="mr-3"></v-icon>
            환영합니다, {{ user?.full_name || user?.username }}님!
          </v-card-title>
          <v-card-subtitle class="text-h6 pb-6">
            {{ selectedClub ? selectedClub.name : '동호회를 선택해주세요' }}
          </v-card-subtitle>
        </v-card>
      </v-col>

      <!-- 통계 카드들 -->
      <v-col v-if="selectedClub" cols="12" sm="6" md="3">
        <v-card color="primary" dark>
          <v-card-text>
            <div class="text-h6">총 회원</div>
            <div class="text-h3">{{ stats.totalMembers }}</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col v-if="selectedClub" cols="12" sm="6" md="3">
        <v-card color="success" dark>
          <v-card-text>
            <div class="text-h6">진행된 세션</div>
            <div class="text-h3">{{ stats.totalSessions }}</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col v-if="selectedClub" cols="12" sm="6" md="3">
        <v-card color="accent" dark>
          <v-card-text>
            <div class="text-h6">총 경기</div>
            <div class="text-h3">{{ stats.totalMatches }}</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col v-if="selectedClub" cols="12" sm="6" md="3">
        <v-card color="info" dark>
          <v-card-text>
            <div class="text-h6">내 순위</div>
            <div class="text-h3">{{ stats.myRanking || '-' }}</div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- 빠른 링크 -->
      <v-col cols="12">
        <v-card>
          <v-card-title class="text-h5">빠른 링크</v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" sm="6" md="4">
                <v-btn
                  :to="{ name: 'club-list' }"
                  color="primary"
                  variant="outlined"
                  size="large"
                  block
                  prepend-icon="mdi-account-group"
                >
                  동호회 목록
                </v-btn>
              </v-col>
              <v-col cols="12" sm="6" md="4">
                <v-btn
                  :to="{ name: 'member-list' }"
                  color="primary"
                  variant="outlined"
                  size="large"
                  block
                  prepend-icon="mdi-account-multiple"
                >
                  회원 목록
                </v-btn>
              </v-col>
              <v-col v-if="isAdmin" cols="12" sm="6" md="4">
                <v-btn
                  :to="{ name: 'club-manage' }"
                  color="primary"
                  variant="outlined"
                  size="large"
                  block
                  prepend-icon="mdi-cog"
                >
                  동호회 관리
                </v-btn>
              </v-col>
              <v-col v-if="isAdmin" cols="12" sm="6" md="4">
                <v-btn
                  :to="{ name: 'member-manage' }"
                  color="primary"
                  variant="outlined"
                  size="large"
                  block
                  prepend-icon="mdi-account-cog"
                >
                  회원 관리
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Phase 2 예정 기능 -->
      <v-col cols="12">
        <v-card color="grey-lighten-3">
          <v-card-title class="text-h5">Phase 2 예정 기능</v-card-title>
          <v-card-text>
            <v-chip-group>
              <v-chip prepend-icon="mdi-calendar">세션 관리</v-chip>
              <v-chip prepend-icon="mdi-tennis">자동 매칭</v-chip>
              <v-chip prepend-icon="mdi-clipboard-text">결과 입력</v-chip>
              <v-chip prepend-icon="mdi-trophy">랭킹 시스템</v-chip>
            </v-chip-group>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { useClubStore } from '@/stores/club'
import { useMemberStore } from '@/stores/member'

const authStore = useAuthStore()
const clubStore = useClubStore()
const memberStore = useMemberStore()

const { user, isAdmin } = storeToRefs(authStore)
const { selectedClub } = storeToRefs(clubStore)

// 통계 데이터 (Phase 2에서 실제 API 연동)
const stats = ref({
  totalMembers: 0,
  totalSessions: 0,
  totalMatches: 0,
  myRanking: null,
})

// 컴포넌트 마운트 시 데이터 로드
onMounted(async () => {
  if (selectedClub.value) {
    try {
      // 회원 수 조회
      await memberStore.fetchMembers(selectedClub.value.id)
      stats.value.totalMembers = memberStore.members.length
    } catch (error) {
      console.error('데이터 로드 실패:', error)
    }
  }
})
</script>

<style scoped>
.v-card {
  transition: transform 0.3s ease;
}

.v-card:hover {
  transform: translateY(-4px);
}
</style>
