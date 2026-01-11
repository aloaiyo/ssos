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
        <v-text-field
          v-model="searchQuery"
          label="동호회 이름으로 검색"
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
          clearable
          hide-details
          placeholder="검색어를 입력하세요"
          @update:model-value="handleSearch"
        ></v-text-field>
      </v-col>
    </v-row>

    <!-- 로딩 -->
    <v-row v-if="isLoading">
      <v-col cols="12" class="text-center py-12">
        <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
        <p class="mt-4 text-medium-emphasis">동호회를 불러오는 중...</p>
      </v-col>
    </v-row>

    <!-- 동호회 카드 목록 -->
    <v-row v-else class="mt-4">
      <v-col v-for="club in clubs" :key="club.id" cols="12" md="6">
        <v-card class="h-100">
          <v-card-title class="d-flex align-center">
            <span>{{ club.name }}</span>
            <v-chip
              v-if="club.my_status === 'pending'"
              size="small"
              color="warning"
              class="ml-2"
            >
              승인 대기
            </v-chip>
          </v-card-title>
          <v-card-text>
            <p class="text-body-2 mb-2">{{ club.description || '설명이 없습니다.' }}</p>
            <div class="d-flex flex-wrap gap-2 text-caption text-medium-emphasis">
              <span v-if="club.location">
                <v-icon size="small" class="mr-1">mdi-map-marker</v-icon>
                {{ club.location }}
              </span>
              <span>
                <v-icon size="small" class="mr-1">mdi-account-group</v-icon>
                회원 {{ club.member_count }}명
              </span>
              <span>
                <v-icon size="small" class="mr-1">mdi-calendar</v-icon>
                {{ formatDate(club.created_at) }}
              </span>
            </div>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <!-- 가입됨 (active) -->
            <v-btn
              v-if="club.my_status === 'active'"
              color="grey"
              variant="flat"
              disabled
            >
              <v-icon start>mdi-check</v-icon>
              가입됨
            </v-btn>
            <!-- 승인 대기 중 (pending) -->
            <v-btn
              v-else-if="club.my_status === 'pending'"
              color="warning"
              variant="outlined"
              disabled
            >
              <v-icon start>mdi-clock-outline</v-icon>
              승인 대기 중
            </v-btn>
            <!-- 추방됨 (banned) -->
            <v-btn
              v-else-if="club.my_status === 'banned'"
              color="error"
              variant="outlined"
              disabled
            >
              <v-icon start>mdi-cancel</v-icon>
              가입 불가
            </v-btn>
            <!-- 가입 불가 (is_join_allowed = false) -->
            <v-btn
              v-else-if="!club.is_join_allowed"
              color="grey"
              variant="outlined"
              disabled
            >
              <v-icon start>mdi-account-off</v-icon>
              가입 불가
            </v-btn>
            <!-- 가입 가능 (null 또는 left) -->
            <v-btn
              v-else
              color="#009630"
              variant="flat"
              class="text-white"
              :loading="joiningClubId === club.id"
              @click="handleJoin(club)"
            >
              <v-icon start>mdi-plus</v-icon>
              {{ club.requires_approval ? '가입 신청' : '가입하기' }}
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>

      <!-- 검색 결과 없음 -->
      <v-col v-if="clubs.length === 0" cols="12">
        <v-card class="text-center py-12" variant="outlined" style="border-style: dashed;">
          <v-icon icon="mdi-tennis-ball" size="64" color="grey-lighten-1" class="mb-4"></v-icon>
          <h3 class="text-h6 text-grey-darken-1 mb-2">
            {{ searchQuery ? '검색 결과가 없습니다' : '등록된 동호회가 없습니다' }}
          </h3>
          <p class="text-body-2 text-grey mb-6">원하는 동호회가 없다면 직접 만들어보세요!</p>
          <v-btn :to="{ name: 'club-create' }" color="#009630" variant="flat" class="text-white">
            <v-icon start>mdi-plus</v-icon>
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

const clubStore = useClubStore()

const clubs = ref([])
const isLoading = ref(false)
const searchQuery = ref('')
const joiningClubId = ref(null)
const snackbar = ref({
  show: false,
  text: '',
  color: 'success'
})

// 날짜 포맷팅
function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

// 전체 동호회 검색
async function loadClubs(search = null) {
  isLoading.value = true
  try {
    clubs.value = await clubStore.searchClubs(search)
  } catch (error) {
    console.error('동호회 목록 로드 실패:', error)
    showSnackbar('동호회 목록을 불러오는데 실패했습니다.', 'error')
  } finally {
    isLoading.value = false
  }
}

// 검색 핸들러 (디바운스 적용)
const handleSearch = debounce(async (value) => {
  await loadClubs(value)
}, 300)

// 가입 요청 핸들러
async function handleJoin(club) {
  joiningClubId.value = club.id
  try {
    await clubStore.joinClub(club.id)
    showSnackbar('가입이 완료되었습니다!', 'success')
    // 목록 갱신하여 상태 업데이트
    await loadClubs(searchQuery.value || null)
  } catch (error) {
    showSnackbar(error.response?.data?.detail || '가입 요청에 실패했습니다.', 'error')
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
  await loadClubs()
})
</script>

<style scoped>
.gap-2 {
  gap: 12px;
}
</style>
