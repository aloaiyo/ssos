<template>
  <div class="ranking-page">
    <!-- 헤더 -->
    <div class="page-header">
      <h1 class="page-title">랭킹</h1>
    </div>

    <!-- 시즌 선택 -->
    <div class="season-selector">
      <v-select
        v-model="selectedSeasonId"
        :items="seasonOptions"
        item-title="label"
        item-value="value"
        label="시즌 선택"
        variant="outlined"
        density="compact"
        hide-details
        :loading="isLoadingSeasons"
        @update:model-value="loadRankings"
      ></v-select>
    </div>

    <!-- 로딩 -->
    <div v-if="isLoading" class="loading-container">
      <v-progress-circular indeterminate color="primary" size="48"></v-progress-circular>
    </div>

    <!-- 랭킹 테이블 -->
    <div v-else-if="rankings.length > 0" class="ranking-section">
      <!-- 시즌 정보 -->
      <div v-if="seasonInfo" class="season-info">
        <v-chip :color="getSeasonStatusColor(seasonInfo.status)" size="small" variant="tonal">
          {{ getSeasonStatusLabel(seasonInfo.status) }}
        </v-chip>
        <span class="season-name">{{ seasonInfo.name }}</span>
      </div>

      <!-- 포인트 안내 -->
      <div class="points-info">
        <v-chip size="x-small" color="success" variant="tonal">승 3점</v-chip>
        <v-chip size="x-small" color="warning" variant="tonal">무 1점</v-chip>
        <v-chip size="x-small" color="error" variant="tonal">패 0점</v-chip>
      </div>

      <!-- 랭킹 리스트 -->
      <div class="ranking-list">
        <div
          v-for="player in rankings"
          :key="player.member_id"
          class="ranking-card"
          :class="{ 'top-three': player.rank <= 3, [`rank-${player.rank}`]: player.rank <= 3 }"
        >
          <!-- 순위 -->
          <div class="rank-badge" :class="`rank-${player.rank}`">
            <template v-if="player.rank <= 3">
              <v-icon v-if="player.rank === 1" color="amber-darken-2">mdi-trophy</v-icon>
              <v-icon v-else-if="player.rank === 2" color="grey">mdi-trophy</v-icon>
              <v-icon v-else color="brown">mdi-trophy</v-icon>
            </template>
            <span v-else class="rank-number">{{ player.rank }}</span>
          </div>

          <!-- 선수 정보 -->
          <div class="player-info">
            <span class="player-name">{{ player.member_name }}</span>
            <span class="player-stats">
              {{ player.total_matches }}경기 |
              <span class="wins">{{ player.wins }}승</span>
              <span class="draws">{{ player.draws }}무</span>
              <span class="losses">{{ player.losses }}패</span>
            </span>
          </div>

          <!-- 포인트 -->
          <div class="points-badge">
            <span class="points-value">{{ player.points }}</span>
            <span class="points-label">점</span>
          </div>

          <!-- 승률 -->
          <div class="win-rate">
            <span class="win-rate-value">{{ player.win_rate?.toFixed(0) || 0 }}%</span>
            <span class="win-rate-label">승률</span>
          </div>
        </div>
      </div>

      <!-- 관리자 기능 -->
      <div v-if="isManager" class="admin-actions">
        <v-btn
          variant="outlined"
          color="primary"
          size="small"
          :loading="isCalculating"
          @click="calculateRankings"
        >
          <v-icon start>mdi-refresh</v-icon>
          랭킹 재계산
        </v-btn>
      </div>
    </div>

    <!-- 빈 상태 -->
    <v-card v-else-if="!isLoading && selectedSeasonId" class="empty-card" variant="flat">
      <v-card-text class="text-center py-12">
        <v-icon size="64" color="grey-lighten-1">mdi-trophy-outline</v-icon>
        <h3 class="text-h6 mt-4 text-grey">랭킹 데이터가 없습니다</h3>
        <p class="text-grey mt-2">경기 결과를 입력하면 랭킹이 자동으로 계산됩니다</p>
        <v-btn
          v-if="isManager"
          color="primary"
          variant="flat"
          class="mt-4"
          :loading="isCalculating"
          @click="calculateRankings"
        >
          <v-icon start>mdi-calculator</v-icon>
          랭킹 계산하기
        </v-btn>
      </v-card-text>
    </v-card>

    <!-- 시즌 없음 -->
    <v-card v-else-if="!isLoading && seasons.length === 0" class="empty-card" variant="flat">
      <v-card-text class="text-center py-12">
        <v-icon size="64" color="grey-lighten-1">mdi-calendar-blank</v-icon>
        <h3 class="text-h6 mt-4 text-grey">시즌이 없습니다</h3>
        <p class="text-grey mt-2">시즌을 먼저 생성해주세요</p>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useClubStore } from '@/stores/club'
import seasonsApi from '@/api/seasons'
import rankingsApi from '@/api/rankings'
import { getSeasonStatusColor, getSeasonStatusLabel } from '@/utils/constants'

const clubStore = useClubStore()

const selectedClub = computed(() => clubStore.selectedClub)
const isManager = computed(() => clubStore.isManagerOfSelectedClub)

const isLoading = ref(false)
const isLoadingSeasons = ref(false)
const isCalculating = ref(false)

const seasons = ref([])
const selectedSeasonId = ref(null)
const seasonInfo = ref(null)
const rankings = ref([])

const seasonOptions = computed(() => {
  return seasons.value.map(s => ({
    label: `${s.name} (${getSeasonStatusLabel(s.status)})`,
    value: s.id
  }))
})

async function loadSeasons() {
  if (!selectedClub.value?.id) return

  isLoadingSeasons.value = true
  try {
    const response = await seasonsApi.getSeasons(selectedClub.value.id)
    seasons.value = response.data || []

    // 활성 시즌이 있으면 선택, 없으면 첫 번째 시즌 선택
    const activeSeason = seasons.value.find(s => s.status === 'active')
    if (activeSeason) {
      selectedSeasonId.value = activeSeason.id
    } else if (seasons.value.length > 0) {
      selectedSeasonId.value = seasons.value[0].id
    }

    if (selectedSeasonId.value) {
      await loadRankings()
    }
  } catch (error) {
    console.error('시즌 목록 로드 실패:', error)
  } finally {
    isLoadingSeasons.value = false
  }
}

async function loadRankings() {
  if (!selectedClub.value?.id || !selectedSeasonId.value) return

  isLoading.value = true
  try {
    const response = await rankingsApi.getSeasonRankings(selectedClub.value.id, selectedSeasonId.value)
    seasonInfo.value = response.data.season
    rankings.value = response.data.rankings || []
  } catch (error) {
    console.error('랭킹 로드 실패:', error)
    rankings.value = []
  } finally {
    isLoading.value = false
  }
}

async function calculateRankings() {
  if (!selectedClub.value?.id || !selectedSeasonId.value) return

  isCalculating.value = true
  try {
    await rankingsApi.calculateSeasonRankings(selectedClub.value.id, selectedSeasonId.value)
    await loadRankings()
  } catch (error) {
    console.error('랭킹 계산 실패:', error)
    alert(error.response?.data?.detail || '랭킹 계산에 실패했습니다')
  } finally {
    isCalculating.value = false
  }
}

watch(selectedClub, () => {
  loadSeasons()
})

onMounted(() => {
  loadSeasons()
})
</script>

<style scoped>
.ranking-page {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 20px;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1E293B;
}

.season-selector {
  margin-bottom: 20px;
}

.loading-container {
  display: flex;
  justify-content: center;
  padding: 48px;
}

.ranking-section {
  background: white;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  padding: 20px;
}

.season-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #E2E8F0;
}

.season-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1E293B;
}

.points-info {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ranking-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #F8FAFC;
  border-radius: 12px;
  transition: all 0.2s;
}

.ranking-card:hover {
  background: #F1F5F9;
}

.ranking-card.top-three {
  border: 2px solid transparent;
}

.ranking-card.rank-1 {
  background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
  border-color: #F59E0B;
}

.ranking-card.rank-2 {
  background: linear-gradient(135deg, #F3F4F6 0%, #E5E7EB 100%);
  border-color: #9CA3AF;
}

.ranking-card.rank-3 {
  background: linear-gradient(135deg, #FED7AA 0%, #FDBA74 100%);
  border-color: #C2410C;
}

.rank-badge {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.rank-number {
  font-size: 1.2rem;
  font-weight: 700;
  color: #64748B;
}

.player-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.player-name {
  font-size: 1rem;
  font-weight: 600;
  color: #1E293B;
}

.player-stats {
  font-size: 0.85rem;
  color: #64748B;
}

.player-stats .wins {
  color: #059669;
}

.player-stats .draws {
  color: #D97706;
  margin-left: 4px;
}

.player-stats .losses {
  color: #DC2626;
  margin-left: 4px;
}

.points-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: #059669;
  color: white;
  padding: 8px 16px;
  border-radius: 12px;
  min-width: 60px;
}

.points-value {
  font-size: 1.3rem;
  font-weight: 700;
}

.points-label {
  font-size: 0.7rem;
  opacity: 0.9;
}

.win-rate {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 50px;
}

.win-rate-value {
  font-size: 1rem;
  font-weight: 600;
  color: #1E293B;
}

.win-rate-label {
  font-size: 0.7rem;
  color: #64748B;
}

.admin-actions {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #E2E8F0;
  display: flex;
  justify-content: center;
}

.empty-card {
  border: 1px solid #E2E8F0;
  border-radius: 16px;
}

@media (max-width: 600px) {
  .ranking-page {
    padding: 12px;
  }

  .ranking-card {
    flex-wrap: wrap;
    gap: 12px;
  }

  .rank-badge {
    width: 40px;
    height: 40px;
  }

  .player-info {
    flex: 1 1 calc(100% - 60px);
    order: 1;
  }

  .points-badge,
  .win-rate {
    order: 2;
  }

  .points-badge {
    padding: 6px 12px;
    min-width: 50px;
  }

  .points-value {
    font-size: 1.1rem;
  }
}
</style>
