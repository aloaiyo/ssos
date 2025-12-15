<template>
  <v-container>
    <!-- 페이지 헤더 -->
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-2">동호회 찾기</h1>
        <p class="text-body-1 text-medium-emphasis mb-6">원하는 동호회를 찾아 가입해보세요</p>
      </v-col>
    </v-row>

    <!-- 검색 바 -->
    <v-row>
      <v-col cols="12">
        <v-text-field v-model="searchQuery" label="동호회 검색" prepend-inner-icon="mdi-magnify" variant="outlined" clearable
          hide-details @update:model-value="handleSearch"></v-text-field>
      </v-col>
    </v-row>

    <!-- 로딩 -->
    <v-row v-if="isLoading">
      <v-col cols="12" class="text-center py-12">
        <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
      </v-col>
    </v-row>

    <!-- 동호회 카드 목록 -->
    <v-row v-else class="mt-4">
      <v-col v-for="club in clubs" :key="club.id" cols="12" md="6">
        <v-card>
          <v-card-title>{{ club.name }}</v-card-title>
          <v-card-text>
            <p class="text-body-2">{{ club.description || '설명이 없습니다.' }}</p>
            <p class="text-caption text-medium-emphasis">생성일: {{ new Date(club.created_at).toLocaleDateString() }}</p>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn v-if="isJoined(club.id)" color="grey" variant="flat" disabled>
              가입됨
            </v-btn>
            <v-btn v-else color="#009630" variant="flat" class="text-white" :loading="joiningClubId === club.id"
              @click="handleJoin(club)">
              가입 요청
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>

      <!-- 검색 결과 없음 -->
      <v-col v-if="clubs.length === 0" cols="12">
        <v-card class="text-center py-12" variant="outlined" style="border-style: dashed;">
          <v-icon icon="mdi-tennis-ball" size="64" color="grey-lighten-1" class="mb-4"></v-icon>
          <h3 class="text-h6 text-grey-darken-1 mb-2">검색 결과가 없습니다</h3>
          <p class="text-body-2 text-grey mb-6">원하는 동호회가 없다면 직접 만들어보세요!</p>
          <v-btn :to="{ name: 'club-create' }" color="#009630" variant="flat" class="text-white">
            동호회 생성하기
          </v-btn>
        </v-card>
      </v-col>
    </v-row>

    <!-- 알림 스낵바 -->
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000">
      {{ snackbar.text }}
      <template v-slot:actions>
        <v-btn variant="text" @click="snackbar.show = false">닫기</v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useClubStore } from '@/stores/club'
import { debounce } from 'lodash'
import apiClient from '@/api'

const clubStore = useClubStore()

const clubs = ref([])
const isLoading = ref(false)
const searchQuery = ref('')
const joiningClubId = ref(null)
const myClubIds = ref([])
const snackbar = ref({
  show: false,
  text: '',
  color: 'success'
})

// 가입 여부 확인
function isJoined(clubId) {
  return myClubIds.value.includes(clubId)
}

// 전체 동호회 검색
async function loadClubs(search = null) {
  isLoading.value = true
  try {
    clubs.value = await clubStore.searchClubs(search)
  } catch (error) {
    console.error('동호회 목록 로드 실패:', error)
  } finally {
    isLoading.value = false
  }
}

// 검색 핸들러 (디바운스 적용)
const handleSearch = debounce(async (value) => {
  await loadClubs(value)
}, 300)

// 내가 가입한 동호회 가져오기
async function loadMyClubs() {
  try {
    const response = await apiClient.get('/users/me/clubs')
    myClubIds.value = response.data.map(club => club.id)
  } catch (error) {
    console.error('내 동호회 로드 실패:', error)
  }
}

// 가입 요청 핸들러
async function handleJoin(club) {
  joiningClubId.value = club.id
  try {
    await clubStore.joinClub(club.id)
    showSnackbar('가입 요청이 전송되었습니다.', 'success')
    await loadMyClubs() // 목록 갱신
  } catch (error) {
    showSnackbar(error.response?.data?.detail || '가입 요청 실패', 'error')
  } finally {
    joiningClubId.value = null
  }
}

function showSnackbar(text, color) {
  snackbar.value = {
    show: true,
    text,
    color
  }
}

onMounted(async () => {
  await loadMyClubs()
  await loadClubs()
})
</script>
