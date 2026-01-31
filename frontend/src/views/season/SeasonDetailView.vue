<template>
  <div class="season-detail-page">
    <!-- 로딩 -->
    <div v-if="isLoading" class="loading-container">
      <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
    </div>

    <template v-else-if="season">
      <!-- 시즌 정보 헤더 -->
      <div class="season-header">
        <div class="header-content">
          <v-btn icon variant="text" @click="goBack" class="back-btn">
            <v-icon>mdi-arrow-left</v-icon>
          </v-btn>
          <div class="season-info">
            <div class="season-title-row">
              <h1 class="season-title">{{ season.name }}</h1>
              <v-chip :color="getStatusColor(season.status)" size="small" variant="tonal">
                {{ getStatusLabel(season.status) }}
              </v-chip>
            </div>
            <p v-if="season.description" class="season-description">{{ season.description }}</p>
            <div class="season-meta">
              <span class="meta-item">
                <v-icon size="16">mdi-calendar-range</v-icon>
                {{ formatDate(season.start_date) }} ~ {{ formatDate(season.end_date) }}
              </span>
              <span class="meta-item">
                <v-icon size="16">mdi-calendar-check</v-icon>
                {{ sessions.length }}개 세션
              </span>
            </div>
          </div>
          <v-btn icon variant="text" @click="openEditDialog">
            <v-icon>mdi-pencil</v-icon>
          </v-btn>
        </div>
      </div>

      <!-- 탭 메뉴 -->
      <v-tabs v-model="activeTab" color="primary" class="season-tabs">
        <v-tab value="sessions">세션</v-tab>
        <v-tab value="rankings">랭킹</v-tab>
      </v-tabs>

      <v-window v-model="activeTab" class="tab-content">
        <!-- 세션 탭 -->
        <v-window-item value="sessions">
          <div class="tab-header">
            <h2 class="section-title">세션 목록</h2>
            <v-btn color="primary" variant="flat" size="small" @click="showSessionDialog = true">
              <v-icon start size="18">mdi-plus</v-icon>
              세션 추가
            </v-btn>
          </div>

          <div v-if="sessions.length === 0" class="empty-state">
            <v-icon size="48" color="grey-lighten-1">mdi-calendar-blank</v-icon>
            <p class="text-grey mt-3">등록된 세션이 없습니다</p>
            <v-btn color="primary" variant="flat" class="mt-3" @click="showSessionDialog = true">
              첫 세션 생성하기
            </v-btn>
          </div>

          <div v-else class="session-list">
            <v-card
              v-for="session in sessions"
              :key="session.id"
              class="session-card"
              variant="flat"
              @click="goToSession(session)"
            >
              <div class="session-card-content">
                <div class="session-info">
                  <div class="session-header">
                    <h3 class="session-name">{{ session.title || `세션 #${session.id}` }}</h3>
                    <v-chip :color="getSessionTypeColor(session.session_type)" size="x-small" variant="tonal">
                      {{ getSessionTypeLabel(session.session_type) }}
                    </v-chip>
                  </div>
                  <div class="session-meta">
                    <span v-if="session.date" class="meta-item">
                      <v-icon size="14">mdi-calendar</v-icon>
                      {{ formatDate(session.date) }} {{ session.start_time ? session.start_time.substring(0, 5) : '' }}
                    </span>
                    <span v-if="session.location" class="meta-item">
                      <v-icon size="14">mdi-map-marker</v-icon>
                      {{ session.location }}
                    </span>
                  </div>
                  <div class="session-stats">
                    <span><v-icon size="14">mdi-account-group</v-icon> {{ session.participant_count || 0 }}명 참가</span>
                    <span class="ml-3"><v-icon size="14">mdi-tennis</v-icon> {{ session.match_count || 0 }}경기</span>
                  </div>
                </div>
                <v-icon color="grey-lighten-1">mdi-chevron-right</v-icon>
              </div>
            </v-card>
          </div>
        </v-window-item>

        <!-- 랭킹 탭 -->
        <v-window-item value="rankings">
          <div class="tab-header">
            <h2 class="section-title">시즌 랭킹</h2>
            <v-btn
              color="primary"
              variant="outlined"
              size="small"
              @click="calculateRankings"
              :loading="isCalculating"
            >
              <v-icon start size="18">mdi-refresh</v-icon>
              랭킹 갱신
            </v-btn>
          </div>

          <div v-if="rankings.length === 0" class="empty-state">
            <v-icon size="48" color="grey-lighten-1">mdi-podium</v-icon>
            <p class="text-grey mt-3">아직 랭킹 데이터가 없습니다</p>
            <p class="text-grey-lighten-1 text-caption">경기 결과가 입력되면 랭킹이 계산됩니다</p>
          </div>

          <v-table v-else class="ranking-table">
            <thead>
              <tr>
                <th class="text-center">순위</th>
                <th>이름</th>
                <th class="text-center">경기</th>
                <th class="text-center">승</th>
                <th class="text-center">무</th>
                <th class="text-center">패</th>
                <th class="text-center">승점</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="ranking in rankings" :key="ranking.id">
                <td class="text-center">
                  <span :class="getRankClass(ranking.rank)">{{ ranking.rank || '-' }}</span>
                </td>
                <td>{{ ranking.member_name || '알 수 없음' }}</td>
                <td class="text-center">{{ ranking.total_matches }}</td>
                <td class="text-center text-success">{{ ranking.wins }}</td>
                <td class="text-center text-grey">{{ ranking.draws }}</td>
                <td class="text-center text-error">{{ ranking.losses }}</td>
                <td class="text-center font-weight-bold">{{ ranking.points }}</td>
              </tr>
            </tbody>
          </v-table>
        </v-window-item>
      </v-window>
    </template>

    <!-- 시즌 수정 다이얼로그 -->
    <v-dialog v-model="showEditDialog" max-width="500">
      <v-card>
        <v-card-title>시즌 수정</v-card-title>
        <v-card-text>
          <v-form ref="formRef" v-model="formValid">
            <v-text-field
              v-model="editForm.name"
              label="시즌 이름"
              :rules="[v => !!v || '시즌 이름을 입력해주세요']"
              required
            ></v-text-field>
            <v-textarea
              v-model="editForm.description"
              label="설명 (선택)"
              rows="2"
            ></v-textarea>
            <v-row>
              <v-col cols="6">
                <v-text-field
                  v-model="editForm.start_date"
                  label="시작일"
                  type="date"
                  :rules="[v => !!v || '시작일을 선택해주세요']"
                  required
                ></v-text-field>
              </v-col>
              <v-col cols="6">
                <v-text-field
                  v-model="editForm.end_date"
                  label="종료일"
                  type="date"
                  :rules="[
                    v => !!v || '종료일을 선택해주세요',
                    v => !editForm.start_date || v > editForm.start_date || '종료일은 시작일 이후여야 합니다'
                  ]"
                  required
                ></v-text-field>
              </v-col>
            </v-row>
            <v-select
              v-model="editForm.status"
              label="상태"
              :items="statusOptions"
              item-title="label"
              item-value="value"
            ></v-select>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-btn color="error" variant="text" @click="confirmDeleteSeason">삭제</v-btn>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="showEditDialog = false">취소</v-btn>
          <v-btn
            color="primary"
            variant="flat"
            :loading="isSaving"
            :disabled="!formValid"
            @click="saveSeason"
          >
            수정
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 시즌 삭제 확인 다이얼로그 -->
    <v-dialog v-model="showDeleteDialog" max-width="400">
      <v-card>
        <v-card-title>시즌 삭제</v-card-title>
        <v-card-text>
          <strong>{{ season?.name }}</strong> 시즌을 삭제하시겠습니까?
          <br /><br />
          <span class="text-error">이 시즌에 속한 모든 세션과 경기 기록도 함께 삭제됩니다. 이 작업은 되돌릴 수 없습니다.</span>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="showDeleteDialog = false">취소</v-btn>
          <v-btn color="error" variant="flat" :loading="isDeleting" @click="deleteSeason">삭제</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 세션 생성 다이얼로그 -->
    <v-dialog v-model="showSessionDialog" max-width="500">
      <v-card>
        <v-card-title>세션 생성</v-card-title>
        <v-card-text>
          <v-form ref="sessionFormRef" v-model="sessionFormValid">
            <v-text-field
              v-model="sessionForm.title"
              label="세션 제목"
              placeholder="예: 1주차 리그전"
            ></v-text-field>

            <!-- 날짜 선택 -->
            <v-menu
              v-model="showDatePicker"
              :close-on-content-click="false"
              location="bottom"
            >
              <template v-slot:activator="{ props }">
                <v-text-field
                  v-bind="props"
                  :model-value="formatDateDisplay(sessionForm.date)"
                  label="날짜"
                  prepend-inner-icon="mdi-calendar"
                  readonly
                  :rules="[v => !!sessionForm.date || '날짜를 선택해주세요']"
                ></v-text-field>
              </template>
              <v-date-picker
                v-model="sessionForm.date"
                @update:model-value="showDatePicker = false"
                color="primary"
              ></v-date-picker>
            </v-menu>

            <!-- 시작 시간 선택 -->
            <div class="time-section">
              <label class="time-label">시작 시간</label>
              <v-chip-group
                v-model="sessionForm.start_time"
                selected-class="bg-primary text-white"
                mandatory
                column
              >
                <v-chip
                  v-for="time in timeOptions"
                  :key="time.value"
                  :value="time.value"
                  variant="outlined"
                  size="small"
                  class="time-chip"
                >
                  {{ time.label }}
                </v-chip>
              </v-chip-group>
            </div>

            <!-- 종료 시간 선택 -->
            <div class="time-section">
              <label class="time-label">종료 시간</label>
              <v-chip-group
                v-model="sessionForm.end_time"
                selected-class="bg-primary text-white"
                mandatory
                column
              >
                <v-chip
                  v-for="time in endTimeOptions"
                  :key="time.value"
                  :value="time.value"
                  variant="outlined"
                  size="small"
                  class="time-chip"
                >
                  {{ time.label }}
                </v-chip>
              </v-chip-group>
            </div>

            <v-text-field
              v-model="sessionForm.location"
              label="장소"
              placeholder="예: 올림픽공원 테니스장"
              prepend-inner-icon="mdi-map-marker"
              class="mt-2"
            ></v-text-field>

            <v-row>
              <v-col cols="6">
                <v-select
                  v-model="sessionForm.session_type"
                  label="유형"
                  :items="sessionTypeOptions"
                  item-title="label"
                  item-value="value"
                ></v-select>
              </v-col>
              <v-col cols="6">
                <v-text-field
                  v-model.number="sessionForm.num_courts"
                  label="코트 수"
                  type="number"
                  min="1"
                  max="20"
                ></v-text-field>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="closeSessionDialog">취소</v-btn>
          <v-btn
            color="primary"
            variant="flat"
            :loading="isCreatingSession"
            :disabled="!sessionFormValid || !sessionForm.date"
            @click="createSession"
          >
            생성
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useClubStore } from '@/stores/club'
import { useSeasonStore } from '@/stores/season'
import sessionsApi from '@/api/sessions'

const route = useRoute()
const router = useRouter()
const clubStore = useClubStore()
const seasonStore = useSeasonStore()

const selectedClub = computed(() => clubStore.selectedClub)
const season = computed(() => seasonStore.currentSeason)
const rankings = computed(() => seasonStore.seasonRankings)
const isLoading = computed(() => seasonStore.isLoading)

const activeTab = ref('sessions')
const sessions = ref([])
const isCalculating = ref(false)

// 시즌 수정
const showEditDialog = ref(false)
const formRef = ref(null)
const formValid = ref(false)
const isSaving = ref(false)
const editForm = ref({
  name: '',
  description: '',
  start_date: '',
  end_date: '',
  status: 'upcoming'
})

// 시즌 삭제
const showDeleteDialog = ref(false)
const isDeleting = ref(false)

// 세션 생성
const showSessionDialog = ref(false)
const showDatePicker = ref(false)
const sessionFormRef = ref(null)
const sessionFormValid = ref(false)
const isCreatingSession = ref(false)

// 오늘 날짜를 기본값으로
function getDefaultDate() {
  const today = new Date()
  return today
}

const sessionForm = ref({
  title: '',
  date: getDefaultDate(),
  start_time: '09:00',
  end_time: '12:00',
  location: '',
  session_type: 'league',
  num_courts: 4
})

// 시간 옵션 (06:00 ~ 22:00)
const timeOptions = [
  { value: '06:00', label: '06:00' },
  { value: '07:00', label: '07:00' },
  { value: '08:00', label: '08:00' },
  { value: '09:00', label: '09:00' },
  { value: '10:00', label: '10:00' },
  { value: '11:00', label: '11:00' },
  { value: '12:00', label: '12:00' },
  { value: '13:00', label: '13:00' },
  { value: '14:00', label: '14:00' },
  { value: '15:00', label: '15:00' },
  { value: '16:00', label: '16:00' },
  { value: '17:00', label: '17:00' },
  { value: '18:00', label: '18:00' },
  { value: '19:00', label: '19:00' },
  { value: '20:00', label: '20:00' },
  { value: '21:00', label: '21:00' },
  { value: '22:00', label: '22:00' },
]

// 종료 시간 옵션 (시작 시간 이후만)
const endTimeOptions = computed(() => {
  const startIdx = timeOptions.findIndex(t => t.value === sessionForm.value.start_time)
  return timeOptions.slice(startIdx + 1)
})

const statusOptions = [
  { value: 'upcoming', label: '예정' },
  { value: 'active', label: '진행 중' },
  { value: 'completed', label: '완료' }
]

const sessionTypeOptions = [
  { value: 'league', label: '리그전' },
  { value: 'tournament', label: '토너먼트' }
]

function getStatusColor(status) {
  const colors = { upcoming: 'info', active: 'success', completed: 'grey' }
  return colors[status] || 'grey'
}

function getStatusLabel(status) {
  const labels = { upcoming: '예정', active: '진행 중', completed: '완료' }
  return labels[status] || status
}

function getSessionTypeColor(type) {
  return type === 'tournament' ? 'warning' : 'primary'
}

function getSessionTypeLabel(type) {
  return type === 'tournament' ? '토너먼트' : '리그'
}

function getRankClass(rank) {
  if (rank === 1) return 'rank-gold'
  if (rank === 2) return 'rank-silver'
  if (rank === 3) return 'rank-bronze'
  return ''
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}`
}

function formatDateDisplay(date) {
  if (!date) return ''
  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const weekdays = ['일', '월', '화', '수', '목', '금', '토']
  const weekday = weekdays[d.getDay()]
  return `${year}.${month}.${day} (${weekday})`
}

function formatDateTime(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const dateFormatted = formatDate(dateStr)
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${dateFormatted} ${hours}:${minutes}`
}

function goBack() {
  router.push({ name: 'season-list' })
}

function goToSession(session) {
  router.push({ name: 'session-detail', params: { sessionId: session.id } })
}

function openEditDialog() {
  if (season.value) {
    editForm.value = {
      name: season.value.name,
      description: season.value.description || '',
      start_date: season.value.start_date,
      end_date: season.value.end_date,
      status: season.value.status
    }
    showEditDialog.value = true
  }
}

async function saveSeason() {
  if (!selectedClub.value?.id || !season.value?.id) return

  isSaving.value = true
  try {
    await seasonStore.updateSeason(selectedClub.value.id, season.value.id, editForm.value)
    showEditDialog.value = false
  } catch (error) {
    console.error('시즌 수정 실패:', error)
  } finally {
    isSaving.value = false
  }
}

function confirmDeleteSeason() {
  showEditDialog.value = false
  showDeleteDialog.value = true
}

async function deleteSeason() {
  if (!selectedClub.value?.id || !season.value?.id) return

  isDeleting.value = true
  try {
    await seasonStore.deleteSeason(selectedClub.value.id, season.value.id)
    showDeleteDialog.value = false
    router.push({ name: 'season-list' })
  } catch (error) {
    console.error('시즌 삭제 실패:', error)
    alert(error.response?.data?.detail || '시즌 삭제에 실패했습니다')
  } finally {
    isDeleting.value = false
  }
}

function closeSessionDialog() {
  showSessionDialog.value = false
  sessionForm.value = {
    title: '',
    date: getDefaultDate(),
    start_time: '09:00',
    end_time: '12:00',
    location: '',
    session_type: 'league',
    num_courts: 4
  }
}

async function createSession() {
  if (!selectedClub.value?.id || !season.value?.id) return

  isCreatingSession.value = true
  try {
    // Date 객체에서 YYYY-MM-DD 형식 추출
    const d = new Date(sessionForm.value.date)
    const datePart = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`

    await sessionsApi.createSession(selectedClub.value.id, {
      title: sessionForm.value.title,
      date: datePart,
      start_time: sessionForm.value.start_time + ':00',  // HH:MM:SS 형식
      end_time: sessionForm.value.end_time + ':00',
      location: sessionForm.value.location,
      session_type: sessionForm.value.session_type,
      num_courts: sessionForm.value.num_courts,
      season_id: season.value.id
    })
    closeSessionDialog()
    await loadSessions()
  } catch (error) {
    console.error('세션 생성 실패:', error)
  } finally {
    isCreatingSession.value = false
  }
}

async function calculateRankings() {
  if (!selectedClub.value?.id || !season.value?.id) return

  isCalculating.value = true
  try {
    await seasonStore.calculateRankings(selectedClub.value.id, season.value.id)
  } catch (error) {
    console.error('랭킹 계산 실패:', error)
  } finally {
    isCalculating.value = false
  }
}

async function loadSeason() {
  if (!selectedClub.value?.id) return
  const seasonId = route.params.seasonId
  if (seasonId) {
    await seasonStore.fetchSeason(selectedClub.value.id, seasonId)
    await loadSessions()
    await seasonStore.fetchSeasonRankings(selectedClub.value.id, seasonId)
  }
}

async function loadSessions() {
  if (!selectedClub.value?.id || !season.value?.id) return
  try {
    const response = await sessionsApi.getSessions(selectedClub.value.id, { season_id: season.value.id })
    sessions.value = Array.isArray(response.data) ? response.data : []
  } catch (error) {
    console.error('세션 목록 조회 실패:', error)
    sessions.value = []
  }
}

watch(selectedClub, () => {
  loadSeason()
})

onMounted(() => {
  loadSeason()
})
</script>

<style scoped>
.season-detail-page {
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

.season-header {
  background: white;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 16px;
  border: 1px solid #E2E8F0;
}

.header-content {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.back-btn {
  margin-top: -4px;
}

.season-info {
  flex: 1;
}

.season-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.season-title {
  font-size: 1.4rem;
  font-weight: 600;
  color: #1E293B;
}

.season-description {
  font-size: 0.9rem;
  color: #64748B;
  margin-bottom: 8px;
}

.season-meta {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.85rem;
  color: #64748B;
}

.season-tabs {
  margin-bottom: 16px;
}

.tab-content {
  min-height: 300px;
}

.tab-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1E293B;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  text-align: center;
}

.session-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.session-card {
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.session-card:hover {
  border-color: #059669;
  box-shadow: 0 2px 8px rgba(5, 150, 105, 0.1);
}

.session-card-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.session-info {
  flex: 1;
}

.session-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.session-name {
  font-size: 1rem;
  font-weight: 600;
  color: #1E293B;
}

.session-meta {
  display: flex;
  gap: 12px;
  margin-bottom: 6px;
  flex-wrap: wrap;
}

.session-meta .meta-item {
  font-size: 0.8rem;
}

.session-stats {
  font-size: 0.75rem;
  color: #94A3B8;
  display: flex;
  align-items: center;
}

.session-stats span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.ranking-table {
  border-radius: 12px;
  overflow: hidden;
}

.rank-gold {
  color: #F59E0B;
  font-weight: 700;
}

.rank-silver {
  color: #9CA3AF;
  font-weight: 600;
}

.rank-bronze {
  color: #D97706;
  font-weight: 600;
}

/* 시간 선택 스타일 */
.time-section {
  margin: 16px 0;
}

.time-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #64748B;
  margin-bottom: 8px;
}

.time-chip {
  min-width: 60px;
  justify-content: center;
}
</style>
