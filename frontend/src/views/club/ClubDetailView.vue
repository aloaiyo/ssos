<template>
  <v-container>
    <!-- 로딩 -->
    <v-row v-if="isLoading">
      <v-col cols="12" class="text-center">
        <v-progress-circular
          indeterminate
          color="primary"
          size="64"
        ></v-progress-circular>
      </v-col>
    </v-row>

    <!-- 동호회 정보 -->
    <v-row v-else-if="currentClub">
      <v-col cols="12">
        <!-- 헤더 -->
        <div class="d-flex justify-space-between align-center mb-4">
          <div>
            <h1 class="text-h4 font-weight-bold">{{ currentClub.name }}</h1>
            <p class="text-subtitle-1 text-grey mt-2">
              <v-icon icon="mdi-map-marker" size="small"></v-icon>
              {{ currentClub.location || '위치 정보 없음' }}
            </p>
          </div>
          <div>
            <v-btn
              :to="{ name: 'club-list' }"
              variant="outlined"
              class="mr-2"
            >
              목록으로
            </v-btn>
            <v-btn
              v-if="isAdmin"
              :to="{ name: 'club-manage' }"
              color="primary"
              prepend-icon="mdi-pencil"
            >
              수정
            </v-btn>
          </div>
        </div>
      </v-col>

      <!-- 동호회 정보 카드 -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="text-h6">동호회 정보</v-card-title>
          <v-divider></v-divider>
          <v-card-text>
            <v-list>
              <v-list-item>
                <template v-slot:prepend>
                  <v-icon icon="mdi-account-group"></v-icon>
                </template>
                <v-list-item-title>동호회명</v-list-item-title>
                <v-list-item-subtitle>{{ currentClub.name }}</v-list-item-subtitle>
              </v-list-item>

              <v-list-item>
                <template v-slot:prepend>
                  <v-icon icon="mdi-text"></v-icon>
                </template>
                <v-list-item-title>설명</v-list-item-title>
                <v-list-item-subtitle>
                  {{ currentClub.description || '설명 없음' }}
                </v-list-item-subtitle>
              </v-list-item>

              <v-list-item>
                <template v-slot:prepend>
                  <v-icon icon="mdi-map-marker"></v-icon>
                </template>
                <v-list-item-title>위치</v-list-item-title>
                <v-list-item-subtitle>
                  {{ currentClub.location || '위치 정보 없음' }}
                </v-list-item-subtitle>
              </v-list-item>

              <v-list-item>
                <template v-slot:prepend>
                  <v-icon icon="mdi-calendar"></v-icon>
                </template>
                <v-list-item-title>생성일</v-list-item-title>
                <v-list-item-subtitle>
                  {{ formatDate(currentClub.created_at) }}
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- 통계 카드 -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="text-h6">통계</v-card-title>
          <v-divider></v-divider>
          <v-card-text>
            <v-row>
              <v-col cols="6">
                <div class="text-center pa-4">
                  <v-icon icon="mdi-account-multiple" size="48" color="primary"></v-icon>
                  <div class="text-h4 mt-2">{{ members.length }}</div>
                  <div class="text-body-2 text-grey">총 회원</div>
                </div>
              </v-col>
              <v-col cols="6">
                <div class="text-center pa-4">
                  <v-icon icon="mdi-calendar-check" size="48" color="success"></v-icon>
                  <div class="text-h4 mt-2">0</div>
                  <div class="text-body-2 text-grey">진행된 세션</div>
                </div>
              </v-col>
              <v-col cols="6">
                <div class="text-center pa-4">
                  <v-icon icon="mdi-tennis" size="48" color="accent"></v-icon>
                  <div class="text-h4 mt-2">0</div>
                  <div class="text-body-2 text-grey">총 경기</div>
                </div>
              </v-col>
              <v-col cols="6">
                <div class="text-center pa-4">
                  <v-icon icon="mdi-trophy" size="48" color="warning"></v-icon>
                  <div class="text-h4 mt-2">0</div>
                  <div class="text-body-2 text-grey">랭킹 참여자</div>
                </div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- 회원 목록 미리보기 -->
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center">
            <span class="text-h6">회원 목록</span>
            <v-btn
              :to="{ name: 'member-list' }"
              variant="text"
              color="primary"
            >
              전체보기
            </v-btn>
          </v-card-title>
          <v-divider></v-divider>
          <v-card-text>
            <v-list v-if="members.length > 0">
              <v-list-item
                v-for="member in members.slice(0, 5)"
                :key="member.id"
              >
                <template v-slot:prepend>
                  <v-avatar color="primary">
                    <span class="text-white">
                      {{ member.user?.full_name?.[0] || member.user?.username?.[0] }}
                    </span>
                  </v-avatar>
                </template>
                <v-list-item-title>
                  {{ member.user?.full_name || member.user?.username }}
                </v-list-item-title>
                <v-list-item-subtitle>
                  {{ member.gender === 'male' ? '남성' : '여성' }} |
                  {{ member.preferred_type === 'singles' ? '단식' : member.preferred_type === 'doubles' ? '복식' : '무관' }}
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
            <div v-else class="text-center pa-4 text-grey">
              등록된 회원이 없습니다.
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 동호회 없음 -->
    <v-row v-else>
      <v-col cols="12">
        <v-card>
          <v-card-text class="text-center pa-8">
            <v-icon icon="mdi-alert-circle" size="64" color="warning"></v-icon>
            <p class="text-h6 mt-4">동호회를 찾을 수 없습니다.</p>
            <v-btn
              :to="{ name: 'club-list' }"
              color="primary"
              class="mt-4"
            >
              목록으로 돌아가기
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { useClubStore } from '@/stores/club'
import { useMemberStore } from '@/stores/member'
import { formatDate } from '@/utils/date'

const route = useRoute()
const authStore = useAuthStore()
const clubStore = useClubStore()
const memberStore = useMemberStore()

const { isAdmin } = storeToRefs(authStore)
const { currentClub, isLoading } = storeToRefs(clubStore)
const { members } = storeToRefs(memberStore)

// 컴포넌트 마운트 시 동호회 정보 로드
onMounted(async () => {
  const clubId = parseInt(route.params.id)
  await clubStore.fetchClub(clubId)
  await memberStore.fetchMembers(clubId)
})
</script>

<style scoped>
.v-card {
  height: 100%;
}
</style>
