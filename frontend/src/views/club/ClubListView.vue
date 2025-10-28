<template>
  <v-container>
    <!-- 헤더 -->
    <v-row>
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center mb-4">
          <h1 class="text-h4 font-weight-bold">동호회 목록</h1>
          <v-btn
            v-if="isSuperAdmin"
            :to="{ name: 'club-manage' }"
            color="primary"
            prepend-icon="mdi-plus"
          >
            동호회 생성
          </v-btn>
        </div>
      </v-col>
    </v-row>

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

    <!-- 동호회 카드 -->
    <v-row v-else>
      <v-col
        v-for="club in clubs"
        :key="club.id"
        cols="12"
        sm="6"
        md="4"
      >
        <v-card
          :class="{ 'selected-club': selectedClubId === club.id }"
          hover
          @click="selectAndViewClub(club)"
        >
          <v-card-title class="text-h5">
            <v-icon
              v-if="selectedClubId === club.id"
              icon="mdi-check-circle"
              color="success"
              class="mr-2"
            ></v-icon>
            {{ club.name }}
          </v-card-title>

          <v-card-subtitle v-if="club.location">
            <v-icon icon="mdi-map-marker" size="small"></v-icon>
            {{ club.location }}
          </v-card-subtitle>

          <v-card-text>
            <p class="text-body-2">{{ club.description || '설명 없음' }}</p>
          </v-card-text>

          <v-card-actions>
            <v-btn
              variant="text"
              color="primary"
              @click.stop="viewClubDetail(club)"
            >
              상세보기
            </v-btn>
            <v-spacer></v-spacer>
            <v-btn
              v-if="selectedClubId !== club.id"
              variant="outlined"
              color="primary"
              @click.stop="selectClub(club)"
            >
              선택
            </v-btn>
            <v-chip
              v-else
              color="success"
              size="small"
            >
              선택됨
            </v-chip>
          </v-card-actions>
        </v-card>
      </v-col>

      <!-- 동호회 없음 -->
      <v-col v-if="clubs.length === 0" cols="12">
        <v-card>
          <v-card-text class="text-center pa-8">
            <v-icon icon="mdi-account-group-outline" size="64" color="grey"></v-icon>
            <p class="text-h6 mt-4">등록된 동호회가 없습니다.</p>
            <v-btn
              v-if="isSuperAdmin"
              :to="{ name: 'club-manage' }"
              color="primary"
              class="mt-4"
            >
              첫 동호회 만들기
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { useClubStore } from '@/stores/club'

const router = useRouter()
const authStore = useAuthStore()
const clubStore = useClubStore()

const { isSuperAdmin } = storeToRefs(authStore)
const { clubs, selectedClubId, isLoading } = storeToRefs(clubStore)

// 동호회 선택
function selectClub(club) {
  clubStore.selectClub(club.id)
}

// 동호회 선택하고 상세 페이지로 이동
function selectAndViewClub(club) {
  clubStore.selectClub(club.id)
  router.push({ name: 'club-detail', params: { id: club.id } })
}

// 동호회 상세 페이지로 이동
function viewClubDetail(club) {
  router.push({ name: 'club-detail', params: { id: club.id } })
}

// 컴포넌트 마운트 시 동호회 목록 로드
onMounted(async () => {
  await clubStore.fetchClubs()
})
</script>

<style scoped>
.v-card {
  transition: all 0.3s ease;
  cursor: pointer;
}

.v-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15) !important;
}

.selected-club {
  border: 2px solid #4CAF50;
}
</style>
