<template>
  <div class="match-result-page">
    <!-- 로딩 -->
    <div v-if="isLoading" class="loading-container">
      <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
    </div>

    <template v-else>
      <!-- 헤더 -->
      <div class="page-header">
        <v-btn icon variant="text" @click="goBack" class="back-btn">
          <v-icon>mdi-arrow-left</v-icon>
        </v-btn>
        <h1 class="page-title">경기 기록</h1>
      </div>

      <!-- 필터 -->
      <div class="filter-section">
        <v-select
          v-model="selectedSeasonId"
          :items="seasonOptions"
          item-title="name"
          item-value="id"
          label="시즌 선택"
          variant="outlined"
          density="compact"
          clearable
          hide-details
          class="season-filter"
          @update:model-value="loadSessions"
        ></v-select>
      </div>

      <!-- 세션별 경기 기록 -->
      <div v-if="sessions.length === 0" class="empty-state">
        <v-icon size="64" color="grey-lighten-1">mdi-tennis</v-icon>
        <p class="text-grey mt-4">경기 기록이 없습니다</p>
        <p class="text-grey-darken-1 text-body-2">세션에서 경기를 생성해주세요</p>
      </div>

      <div v-else class="session-list">
        <v-expansion-panels variant="accordion">
          <v-expansion-panel
            v-for="session in sessions"
            :key="session.id"
          >
            <v-expansion-panel-title>
              <div class="session-header-content">
                <div class="session-info">
                  <span class="session-date">{{ formatDate(session.date) }}</span>
                  <span class="session-title">{{ session.title || `세션 #${session.id}` }}</span>
                </div>
                <div class="session-stats">
                  <v-chip size="small" color="primary" variant="tonal">
                    {{ session.match_count || 0 }}경기
                  </v-chip>
                </div>
              </div>
            </v-expansion-panel-title>
            <v-expansion-panel-text>
              <div v-if="session.matches && session.matches.length > 0" class="match-list">
                <div
                  v-for="match in session.matches"
                  :key="match.id"
                  class="match-item"
                  :class="{ 'completed': match.status === 'completed' }"
                >
                  <div class="match-header">
                    <v-chip
                      size="x-small"
                      :color="getMatchTypeColor(match.match_type)"
                      variant="tonal"
                    >
                      {{ getMatchTypeLabel(match.match_type) }}
                    </v-chip>
                    <span class="court-info">코트 {{ match.court_number }}</span>
                  </div>
                  <div class="match-teams">
                    <div class="team team-a" :class="{ 'winner': match.winner_team === 'A' }">
                      <div class="team-players">
                        <span v-for="(player, idx) in match.team_a" :key="idx" class="player-name">
                          {{ player.name }}
                        </span>
                      </div>
                      <span class="team-score">{{ match.score?.team_a ?? '-' }}</span>
                    </div>
                    <div class="vs-divider">VS</div>
                    <div class="team team-b" :class="{ 'winner': match.winner_team === 'B' }">
                      <span class="team-score">{{ match.score?.team_b ?? '-' }}</span>
                      <div class="team-players">
                        <span v-for="(player, idx) in match.team_b" :key="idx" class="player-name">
                          {{ player.name }}
                        </span>
                      </div>
                    </div>
                  </div>
                  <v-btn
                    v-if="match.status !== 'completed'"
                    size="small"
                    color="primary"
                    variant="tonal"
                    class="mt-2"
                    @click="openScoreDialog(session, match)"
                  >
                    <v-icon start size="16">mdi-pencil</v-icon>
                    점수 입력
                  </v-btn>
                  <v-chip
                    v-else
                    size="small"
                    color="success"
                    variant="tonal"
                    class="mt-2"
                  >
                    <v-icon start size="14">mdi-check</v-icon>
                    완료
                  </v-chip>
                </div>
              </div>
              <div v-else class="no-matches">
                <p class="text-grey">이 세션에 경기가 없습니다</p>
                <v-btn
                  size="small"
                  color="primary"
                  variant="tonal"
                  :to="{ name: 'session-detail', params: { sessionId: session.id } }"
                >
                  세션으로 이동
                </v-btn>
              </div>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
      </div>
    </template>

    <!-- 점수 입력 다이얼로그 -->
    <v-dialog v-model="showScoreDialog" max-width="400">
      <v-card>
        <v-card-title>점수 입력</v-card-title>
        <v-card-text>
          <div class="score-teams">
            <div class="score-team">
              <p class="team-title">팀 A</p>
              <div class="team-members">
                <span v-for="(player, idx) in selectedMatch?.team_a" :key="idx">
                  {{ player.name }}
                </span>
              </div>
            </div>
            <div class="score-team">
              <p class="team-title">팀 B</p>
              <div class="team-members">
                <span v-for="(player, idx) in selectedMatch?.team_b" :key="idx">
                  {{ player.name }}
                </span>
              </div>
            </div>
          </div>
          <div class="score-inputs">
            <v-text-field
              v-model.number="scoreForm.score_a"
              type="number"
              min="0"
              label="팀 A 점수"
              variant="outlined"
              density="compact"
            ></v-text-field>
            <span class="score-divider">:</span>
            <v-text-field
              v-model.number="scoreForm.score_b"
              type="number"
              min="0"
              label="팀 B 점수"
              variant="outlined"
              density="compact"
            ></v-text-field>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="showScoreDialog = false">취소</v-btn>
          <v-btn color="primary" variant="flat" :loading="isSaving" @click="saveScore">저장</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useClubStore } from '@/stores/club'
import sessionsApi from '@/api/sessions'
import seasonsApi from '@/api/seasons'

const router = useRouter()
const clubStore = useClubStore()

const selectedClub = computed(() => clubStore.selectedClub)

const isLoading = ref(true)
const sessions = ref([])
const seasons = ref([])
const selectedSeasonId = ref(null)

const showScoreDialog = ref(false)
const selectedSession = ref(null)
const selectedMatch = ref(null)
const scoreForm = ref({ score_a: 0, score_b: 0 })
const isSaving = ref(false)

const seasonOptions = computed(() => {
  return [{ id: null, name: '전체 시즌' }, ...seasons.value]
})

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const month = d.getMonth() + 1
  const day = d.getDate()
  const weekdays = ['일', '월', '화', '수', '목', '금', '토']
  const weekday = weekdays[d.getDay()]
  return `${month}/${day} (${weekday})`
}

function getMatchTypeColor(type) {
  const colors = {
    mens_doubles: 'blue',
    mixed_doubles: 'purple',
    singles: 'green'
  }
  return colors[type] || 'grey'
}

function getMatchTypeLabel(type) {
  const labels = {
    mens_doubles: '남복',
    mixed_doubles: '혼복',
    singles: '단식'
  }
  return labels[type] || type
}

function goBack() {
  router.back()
}

async function loadSeasons() {
  if (!selectedClub.value?.id) return
  try {
    const response = await seasonsApi.getSeasons(selectedClub.value.id)
    seasons.value = response.data || []
  } catch (error) {
    console.error('시즌 목록 조회 실패:', error)
  }
}

async function loadSessions() {
  if (!selectedClub.value?.id) return

  isLoading.value = true
  try {
    const params = {}
    if (selectedSeasonId.value) {
      params.season_id = selectedSeasonId.value
    }
    const response = await sessionsApi.getSessions(selectedClub.value.id, params)
    const sessionList = response.data || []

    // 각 세션의 경기 목록 로드
    const sessionsWithMatches = await Promise.all(
      sessionList.map(async (session) => {
        try {
          const matchResponse = await sessionsApi.getSession(selectedClub.value.id, session.id)
          const sessionData = matchResponse.data
          return {
            ...session,
            matches: sessionData.matches || [],
            match_count: sessionData.matches?.length || 0
          }
        } catch {
          return { ...session, matches: [], match_count: 0 }
        }
      })
    )

    sessions.value = sessionsWithMatches.filter(s => s.matches.length > 0)
  } catch (error) {
    console.error('세션 목록 조회 실패:', error)
  } finally {
    isLoading.value = false
  }
}

function openScoreDialog(session, match) {
  selectedSession.value = session
  selectedMatch.value = match
  scoreForm.value = {
    score_a: match.score?.team_a || 0,
    score_b: match.score?.team_b || 0
  }
  showScoreDialog.value = true
}

async function saveScore() {
  if (!selectedClub.value?.id || !selectedSession.value?.id || !selectedMatch.value?.id) return

  isSaving.value = true
  try {
    await sessionsApi.updateMatch(
      selectedClub.value.id,
      selectedSession.value.id,
      selectedMatch.value.id,
      {
        team_a_score: scoreForm.value.score_a,
        team_b_score: scoreForm.value.score_b
      }
    )
    showScoreDialog.value = false
    // 세션 목록 새로고침
    await loadSessions()
  } catch (error) {
    console.error('점수 저장 실패:', error)
    alert(error.response?.data?.detail || '점수 저장에 실패했습니다')
  } finally {
    isSaving.value = false
  }
}

onMounted(async () => {
  await loadSeasons()
  await loadSessions()
})
</script>

<style scoped>
.match-result-page {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
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

.filter-section {
  margin-bottom: 20px;
}

.season-filter {
  max-width: 300px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  text-align: center;
}

.session-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.session-header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding-right: 16px;
}

.session-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.session-date {
  font-size: 0.85rem;
  color: #64748B;
}

.session-title {
  font-weight: 500;
  color: #1E293B;
}

.match-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.match-item {
  background: #F8FAFC;
  border-radius: 12px;
  padding: 16px;
  border: 1px solid #E2E8F0;
}

.match-item.completed {
  background: #F0FDF4;
  border-color: #BBF7D0;
}

.match-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.court-info {
  font-size: 0.85rem;
  color: #64748B;
}

.match-teams {
  display: flex;
  align-items: center;
  gap: 16px;
}

.team {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
}

.team-a {
  justify-content: flex-end;
}

.team-b {
  justify-content: flex-start;
}

.team.winner .team-score {
  color: #059669;
  font-weight: 700;
}

.team-players {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.team-a .team-players {
  text-align: right;
}

.player-name {
  font-size: 0.9rem;
  color: #334155;
}

.team-score {
  font-size: 1.5rem;
  font-weight: 600;
  color: #64748B;
  min-width: 30px;
  text-align: center;
}

.vs-divider {
  font-size: 0.75rem;
  font-weight: 600;
  color: #94A3B8;
  padding: 0 8px;
}

.no-matches {
  text-align: center;
  padding: 24px;
}

/* 점수 입력 다이얼로그 */
.score-teams {
  display: flex;
  gap: 24px;
  margin-bottom: 24px;
}

.score-team {
  flex: 1;
  text-align: center;
}

.team-title {
  font-weight: 600;
  color: #1E293B;
  margin-bottom: 8px;
}

.team-members {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 0.9rem;
  color: #64748B;
}

.score-inputs {
  display: flex;
  align-items: center;
  gap: 16px;
}

.score-inputs .v-text-field {
  flex: 1;
}

.score-divider {
  font-size: 1.5rem;
  font-weight: 600;
  color: #94A3B8;
}
</style>
