<template>
  <div class="match-history-page">
    <!-- 헤더 -->
    <div class="page-header">
      <h1 class="page-title">경기 기록</h1>
    </div>

    <!-- 세션 목록 -->
    <div v-if="sessionsWithMatches.length > 0" class="sessions-list">
      <div
        v-for="session in sessionsWithMatches"
        :key="session.id"
        class="session-card"
      >
        <!-- 세션 헤더 -->
        <div class="session-header" @click="toggleSession(session.id)">
          <div class="session-date">
            <span class="date-badge">{{ formatDate(session.date) }}</span>
            <span class="time-badge">{{ session.start_time?.substring(0, 5) }} - {{ session.end_time?.substring(0, 5) }}</span>
          </div>
          <div class="session-meta">
            <v-chip size="small" :color="getStatusColor(session.status)" variant="tonal">
              {{ getStatusLabel(session.status) }}
            </v-chip>
            <v-icon>
              {{ expandedSessions.includes(session.id) ? 'mdi-chevron-up' : 'mdi-chevron-down' }}
            </v-icon>
          </div>
        </div>

        <!-- 경기 목록 -->
        <v-expand-transition>
          <div v-if="expandedSessions.includes(session.id)" class="matches-list">
            <div v-if="session.matches && session.matches.length > 0">
              <div
                v-for="match in session.matches"
                :key="match.id"
                class="match-card"
                :class="{ 'my-match': isMyMatch(match) }"
              >
                <div class="match-header">
                  <v-chip size="x-small" color="grey" variant="tonal">
                    {{ match.court_number }}코트
                  </v-chip>
                  <v-chip size="x-small" :color="getMatchTypeColor(match.match_type)" variant="tonal">
                    {{ getMatchTypeLabel(match.match_type) }}
                  </v-chip>
                  <v-chip v-if="isMyMatch(match)" size="x-small" color="primary" variant="flat">
                    내 경기
                  </v-chip>
                </div>

                <div class="match-teams">
                  <!-- Team A -->
                  <div class="team" :class="{ winner: match.score && match.score.team_a > match.score.team_b }">
                    <div class="team-players">
                      <span
                        v-for="(player, i) in match.team_a"
                        :key="i"
                        class="player-name"
                        :class="{ 'is-me': isMe(player) }"
                      >
                        {{ player.name }}
                      </span>
                    </div>
                    <span v-if="match.score" class="team-score">{{ match.score.team_a }}</span>
                  </div>

                  <div class="vs-divider">VS</div>

                  <!-- Team B -->
                  <div class="team" :class="{ winner: match.score && match.score.team_b > match.score.team_a }">
                    <div class="team-players">
                      <span
                        v-for="(player, i) in match.team_b"
                        :key="i"
                        class="player-name"
                        :class="{ 'is-me': isMe(player) }"
                      >
                        {{ player.name }}
                      </span>
                    </div>
                    <span v-if="match.score" class="team-score">{{ match.score.team_b }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="no-matches">
              <p>아직 생성된 경기가 없습니다</p>
            </div>
          </div>
        </v-expand-transition>
      </div>
    </div>

    <!-- 빈 상태 -->
    <v-card v-else-if="!isLoading" class="empty-card" variant="flat">
      <v-card-text class="text-center py-12">
        <v-icon size="64" color="grey-lighten-1">mdi-tennis</v-icon>
        <h3 class="text-h6 mt-4 text-grey">경기 기록이 없습니다</h3>
        <p class="text-grey mt-2">세션을 생성하고 경기를 진행해보세요</p>
      </v-card-text>
    </v-card>

    <!-- 로딩 -->
    <div v-if="isLoading" class="loading-container">
      <v-progress-circular indeterminate color="primary" size="48"></v-progress-circular>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useClubStore } from '@/stores/club'
import { useAuthStore } from '@/stores/auth'
import apiClient from '@/api'

const clubStore = useClubStore()
const authStore = useAuthStore()

const selectedClub = computed(() => clubStore.selectedClub)
const currentUser = computed(() => authStore.user)

const isLoading = ref(false)
const sessions = ref([])
const expandedSessions = ref([])

const sessionsWithMatches = computed(() => {
  return sessions.value
    .filter(s => s.status === 'completed' || s.matches?.length > 0)
    .sort((a, b) => new Date(b.date) - new Date(a.date))
})

function formatDate(dateStr) {
  const date = new Date(dateStr)
  const month = date.getMonth() + 1
  const day = date.getDate()
  const weekdays = ['일', '월', '화', '수', '목', '금', '토']
  const weekday = weekdays[date.getDay()]
  return `${month}/${day} (${weekday})`
}

function toggleSession(sessionId) {
  const index = expandedSessions.value.indexOf(sessionId)
  if (index >= 0) {
    expandedSessions.value.splice(index, 1)
  } else {
    expandedSessions.value.push(sessionId)
    loadSessionDetail(sessionId)
  }
}

function getStatusColor(status) {
  const colors = {
    scheduled: 'primary',
    in_progress: 'warning',
    completed: 'success',
    cancelled: 'grey'
  }
  return colors[status] || 'grey'
}

function getStatusLabel(status) {
  const labels = {
    scheduled: '예정',
    in_progress: '진행중',
    completed: '완료',
    cancelled: '취소'
  }
  return labels[status] || status
}

function getMatchTypeColor(type) {
  const colors = {
    mens_doubles: 'blue',
    mixed_doubles: 'purple',
    singles: 'orange'
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

function isMyMatch(match) {
  if (!currentUser.value?.id) return false
  const allPlayers = [...(match.team_a || []), ...(match.team_b || [])]
  return allPlayers.some(p => isMe(p))
}

function isMe(player) {
  if (!currentUser.value?.id) return false
  return player.user_id === currentUser.value.id
}

async function loadSessions() {
  if (!selectedClub.value?.id) return

  isLoading.value = true
  try {
    const response = await apiClient.get(`/clubs/${selectedClub.value.id}/sessions`)
    sessions.value = response.data

    // 가장 최근 세션 자동 확장
    if (sessions.value.length > 0) {
      const sortedSessions = [...sessions.value].sort((a, b) => new Date(b.date) - new Date(a.date))
      if (sortedSessions[0]) {
        expandedSessions.value = [sortedSessions[0].id]
        await loadSessionDetail(sortedSessions[0].id)
      }
    }
  } catch (error) {
    console.error('세션 목록 로드 실패:', error)
  } finally {
    isLoading.value = false
  }
}

async function loadSessionDetail(sessionId) {
  if (!selectedClub.value?.id) return

  try {
    const response = await apiClient.get(`/clubs/${selectedClub.value.id}/sessions/${sessionId}`)
    const index = sessions.value.findIndex(s => s.id === sessionId)
    if (index >= 0) {
      sessions.value[index] = { ...sessions.value[index], ...response.data }
    }
  } catch (error) {
    console.error('세션 상세 로드 실패:', error)
  }
}

watch(selectedClub, () => {
  loadSessions()
})

onMounted(() => {
  loadSessions()
})
</script>

<style scoped>
.match-history-page {
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

.sessions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.session-card {
  background: white;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  overflow: hidden;
}

.session-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  cursor: pointer;
  transition: background 0.2s;
}

.session-header:hover {
  background: #F8FAFC;
}

.session-date {
  display: flex;
  align-items: center;
  gap: 12px;
}

.date-badge {
  font-size: 1rem;
  font-weight: 600;
  color: #1E293B;
}

.time-badge {
  font-size: 0.85rem;
  color: #64748B;
}

.session-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.matches-list {
  border-top: 1px solid #E2E8F0;
  padding: 16px;
  background: #F8FAFC;
}

.match-card {
  background: white;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
  transition: all 0.2s;
}

.match-card:last-child {
  margin-bottom: 0;
}

.match-card.my-match {
  border-color: #059669;
  background: #F0FDF4;
  box-shadow: 0 0 0 1px #059669;
}

.match-header {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.match-teams {
  display: flex;
  align-items: center;
  gap: 16px;
}

.team {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #F8FAFC;
  border-radius: 8px;
}

.team.winner {
  background: #D1FAE5;
}

.team-players {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.player-name {
  font-size: 0.9rem;
  color: #1E293B;
}

.player-name.is-me {
  font-weight: 600;
  color: #059669;
}

.team-score {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1E293B;
}

.team.winner .team-score {
  color: #059669;
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
  color: #64748B;
}

.empty-card {
  border: 1px solid #E2E8F0;
  border-radius: 16px;
}

.loading-container {
  display: flex;
  justify-content: center;
  padding: 48px;
}

@media (max-width: 600px) {
  .match-history-page {
    padding: 12px;
  }

  .match-teams {
    flex-direction: column;
    gap: 8px;
  }

  .team {
    width: 100%;
  }

  .vs-divider {
    padding: 4px 0;
  }
}
</style>
