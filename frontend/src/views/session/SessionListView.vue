<template>
  <div class="session-calendar-page">
    <!-- 헤더 -->
    <div class="page-header">
      <h1 class="page-title">일정</h1>
      <div class="header-actions">
        <v-btn color="primary" variant="flat" @click="goToToday">
          오늘
        </v-btn>
        <v-btn
          v-if="isManager"
          color="primary"
          variant="flat"
          prepend-icon="mdi-plus"
          @click="openCreateDialog"
        >
          세션 추가
        </v-btn>
      </div>
    </div>

    <!-- 캘린더 네비게이션 -->
    <v-card class="calendar-card" variant="flat">
      <div class="calendar-nav">
        <v-btn icon variant="text" @click="prevMonth">
          <v-icon>mdi-chevron-left</v-icon>
        </v-btn>
        <h2 class="calendar-title">{{ currentYear }}년 {{ currentMonth }}월</h2>
        <v-btn icon variant="text" @click="nextMonth">
          <v-icon>mdi-chevron-right</v-icon>
        </v-btn>
      </div>

      <!-- 요일 헤더 -->
      <div class="calendar-weekdays">
        <div v-for="day in weekdays" :key="day" class="weekday" :class="{ sunday: day === '일', saturday: day === '토' }">
          {{ day }}
        </div>
      </div>

      <!-- 캘린더 그리드 -->
      <div class="calendar-grid">
        <div
          v-for="(day, index) in calendarDays"
          :key="index"
          class="calendar-day"
          :class="{
            'other-month': !day.isCurrentMonth,
            'today': day.isToday,
            'has-session': day.sessions.length > 0,
            'sunday': index % 7 === 0,
            'saturday': index % 7 === 6
          }"
          @click="selectDay(day)"
        >
          <span class="day-number">{{ day.date.getDate() }}</span>
          <div v-if="day.sessions.length > 0" class="session-times">
            <div
              v-for="(session, i) in day.sessions.slice(0, 2)"
              :key="i"
              class="session-time-chip"
              :class="getSessionStatusClass(session)"
              @click.stop="goToSession(session)"
            >
              {{ session.start_time?.substring(0, 5) }}
            </div>
            <div v-if="day.sessions.length > 2" class="more-sessions">
              +{{ day.sessions.length - 2 }}
            </div>
          </div>
        </div>
      </div>
    </v-card>

    <!-- 선택된 날짜의 세션 목록 -->
    <v-card v-if="selectedDay" class="sessions-card" variant="flat">
      <v-card-title class="sessions-title">
        {{ formatSelectedDate(selectedDay.date) }}
        <v-chip v-if="selectedDay.sessions.length > 0" size="small" color="primary" class="ml-2">
          {{ selectedDay.sessions.length }}개 일정
        </v-chip>
      </v-card-title>
      <v-card-text v-if="selectedDay.sessions.length > 0" class="pa-0">
        <v-list>
          <v-list-item
            v-for="session in selectedDay.sessions"
            :key="session.id"
            :to="{ name: 'session-detail', params: { sessionId: session.id } }"
            class="session-item"
          >
            <template v-slot:prepend>
              <div class="session-time-badge" :class="getSessionStatusClass(session)">
                <v-icon size="20">mdi-clock-outline</v-icon>
              </div>
            </template>
            <v-list-item-title class="session-item-title">
              {{ session.start_time?.substring(0, 5) }} - {{ session.end_time?.substring(0, 5) }}
            </v-list-item-title>
            <v-list-item-subtitle>
              <v-icon size="14">mdi-account-group</v-icon>
              {{ session.participant_count }}명 참가
              <v-icon size="14" class="ml-2">mdi-tennis-ball</v-icon>
              {{ session.num_courts }}코트
            </v-list-item-subtitle>
            <template v-slot:append>
              <v-chip :color="getStatusColor(session.status)" size="small" variant="tonal">
                {{ getStatusLabel(session.status) }}
              </v-chip>
            </template>
          </v-list-item>
        </v-list>
      </v-card-text>
      <v-card-text v-else class="text-center py-8">
        <v-icon size="48" color="grey-lighten-1">mdi-calendar-blank</v-icon>
        <p class="text-grey mt-2">이 날짜에 일정이 없습니다</p>
        <v-btn
          v-if="isManager"
          color="primary"
          variant="tonal"
          class="mt-4"
          prepend-icon="mdi-plus"
          @click="openCreateDialogForDate(selectedDay.date)"
        >
          세션 추가
        </v-btn>
      </v-card-text>
    </v-card>

    <!-- 세션 생성 다이얼로그 (과거 날짜: 4단계 스테퍼) -->
    <v-dialog v-model="showCreateDialog" :max-width="dialogMaxWidth" persistent>
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon class="mr-2">mdi-calendar-plus</v-icon>
          새 세션 만들기
        </v-card-title>

        <!-- 과거 날짜인 경우 스테퍼 헤더 -->
        <v-stepper v-if="isPastDate" v-model="currentStep" alt-labels class="stepper elevation-0">
          <v-stepper-header>
            <v-stepper-item :value="1" title="세션 정보" :complete="currentStep > 1" />
            <v-divider />
            <v-stepper-item :value="2" title="참가자" :complete="currentStep > 2" />
            <v-divider />
            <v-stepper-item :value="3" title="매치 생성" :complete="currentStep > 3" />
            <v-divider />
            <v-stepper-item :value="4" title="점수 입력" :complete="currentStep > 4" />
          </v-stepper-header>
        </v-stepper>

        <!-- Step 1: 세션 기본 정보 -->
        <v-card-text v-if="currentStep === 1">
          <v-form ref="createForm" v-model="formValid">
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="sessionForm.date"
                  label="날짜"
                  type="date"
                  variant="outlined"
                  density="compact"
                  :rules="[v => !!v || '날짜를 선택하세요']"
                  required
                />
              </v-col>
              <v-col cols="6">
                <v-text-field
                  v-model="sessionForm.start_time"
                  label="시작 시간"
                  type="time"
                  variant="outlined"
                  density="compact"
                  :rules="[v => !!v || '시작 시간을 입력하세요']"
                  required
                />
              </v-col>
              <v-col cols="6">
                <v-text-field
                  v-model="sessionForm.end_time"
                  label="종료 시간"
                  type="time"
                  variant="outlined"
                  density="compact"
                  :rules="[v => !!v || '종료 시간을 입력하세요']"
                  required
                />
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="sessionForm.location"
                  label="장소"
                  variant="outlined"
                  density="compact"
                  placeholder="예: OO 테니스장"
                />
              </v-col>
              <v-col cols="6">
                <v-text-field
                  v-model.number="sessionForm.num_courts"
                  label="코트 수"
                  type="number"
                  variant="outlined"
                  density="compact"
                  min="1"
                  max="20"
                  :rules="[v => v >= 1 || '1개 이상 필요']"
                  required
                />
              </v-col>
              <v-col cols="6">
                <v-text-field
                  v-model.number="sessionForm.match_duration_minutes"
                  label="경기 시간 (분)"
                  type="number"
                  variant="outlined"
                  density="compact"
                  min="10"
                  max="120"
                />
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="sessionForm.notes"
                  label="메모"
                  variant="outlined"
                  density="compact"
                  rows="2"
                  placeholder="추가 안내사항"
                />
              </v-col>

              <!-- 시즌 없음 경고 -->
              <v-col v-if="showNoSeasonWarning" cols="12">
                <v-alert
                  type="warning"
                  variant="tonal"
                  icon="mdi-alert"
                  density="compact"
                >
                  <div class="d-flex flex-column">
                    <strong>해당 날짜에 활성 시즌이 없습니다</strong>
                    <span class="text-body-2 mt-1">
                      시즌 없이 생성된 세션은 랭킹에 반영되지 않습니다.
                      <router-link :to="{ name: 'season-list' }" class="text-warning font-weight-medium">
                        시즌을 먼저 생성해주세요.
                      </router-link>
                    </span>
                  </div>
                </v-alert>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>

        <!-- Step 2: 참가자 선택 (과거 세션만) -->
        <v-card-text v-if="currentStep === 2">
          <div class="d-flex align-center justify-space-between mb-3">
            <div class="d-flex align-center gap-2">
              <v-btn-toggle v-model="participantGenderFilter" density="compact" variant="outlined" divided>
                <v-btn value="all" size="small">전체</v-btn>
                <v-btn value="male" size="small">남</v-btn>
                <v-btn value="female" size="small">여</v-btn>
              </v-btn-toggle>
            </div>
            <v-chip size="small" color="primary" variant="tonal">
              남 {{ selectedMaleCount }}명, 여 {{ selectedFemaleCount }}명
            </v-chip>
          </div>
          <v-list density="compact" class="member-select-list" style="max-height: 350px; overflow-y: auto;">
            <v-list-item
              v-for="member in filteredClubMembers"
              :key="member.id"
              @click="toggleMemberSelection(member.id)"
              class="member-select-item"
            >
              <template v-slot:prepend>
                <v-checkbox
                  :model-value="selectedMemberIds.includes(member.id)"
                  hide-details
                  density="compact"
                  class="mr-2"
                  @click.stop
                />
              </template>
              <v-list-item-title>{{ member.user_name || '알 수 없음' }}</v-list-item-title>
              <v-list-item-subtitle>
                <v-chip size="x-small" :color="member.gender === 'male' ? 'blue' : 'pink'" variant="tonal">
                  {{ member.gender === 'male' ? '남' : '여' }}
                </v-chip>
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
          <p v-if="filteredClubMembers.length === 0" class="text-grey text-center py-4">
            회원이 없습니다
          </p>
        </v-card-text>

        <!-- Step 3: 매치 생성 (과거 세션만) -->
        <v-card-text v-if="currentStep === 3">
          <div v-if="!generatedMatches.length && !isGeneratingStep">
            <p class="text-body-2 text-grey mb-4">매치 생성 방식을 선택하세요.</p>
            <div class="d-flex flex-column gap-3">
              <v-btn
                color="primary"
                variant="flat"
                prepend-icon="mdi-shuffle-variant"
                :loading="isGeneratingStep"
                @click="generateMatchesStep('auto')"
              >
                자동 생성
              </v-btn>
              <v-btn
                color="secondary"
                variant="flat"
                prepend-icon="mdi-robot"
                :loading="isGeneratingStep"
                @click="generateMatchesStep('ai')"
              >
                AI 생성
              </v-btn>
            </div>
          </div>

          <!-- AI 생성 설정 -->
          <div v-if="showAISettingsStep">
            <v-radio-group v-model="aiModeStep" label="매칭 방식" class="mb-4">
              <v-radio value="balanced">
                <template v-slot:label>
                  <div>
                    <strong>실력 균형</strong>
                    <p class="text-grey text-caption">랭킹/승률 기반으로 팀 밸런스 조정</p>
                  </div>
                </template>
              </v-radio>
              <v-radio value="random">
                <template v-slot:label>
                  <div>
                    <strong>완전 랜덤</strong>
                    <p class="text-grey text-caption">무작위로 팀 구성</p>
                  </div>
                </template>
              </v-radio>
            </v-radio-group>
            <v-btn color="primary" variant="flat" :loading="isGeneratingStep" @click="executeAIGenerate">
              <v-icon start>mdi-creation</v-icon>
              생성하기
            </v-btn>
          </div>

          <!-- 매치 미리보기 -->
          <div v-if="generatedMatches.length > 0">
            <div class="d-flex align-center justify-space-between mb-3">
              <v-chip size="small" color="success" variant="tonal">
                {{ generatedMatches.length }}개 매치 생성됨
              </v-chip>
              <v-btn size="small" variant="text" prepend-icon="mdi-refresh" @click="resetGeneratedMatches">
                다시 생성
              </v-btn>
            </div>
            <div class="match-preview-list">
              <div v-for="(match, index) in generatedMatches" :key="index" class="match-preview-card">
                <v-chip size="x-small" :color="getMatchTypeColor(match.match_type)" variant="tonal" class="mb-1">
                  {{ getMatchTypeLabel(match.match_type) }}
                </v-chip>
                <div class="match-preview-teams">
                  <span class="team-name">{{ getMatchTeamNames(match, 'A') }}</span>
                  <span class="vs-label">vs</span>
                  <span class="team-name">{{ getMatchTeamNames(match, 'B') }}</span>
                </div>
              </div>
            </div>
          </div>

          <v-alert v-if="stepError" type="error" density="compact" class="mt-3">
            {{ stepError }}
          </v-alert>
        </v-card-text>

        <!-- Step 4: 점수 일괄 입력 (과거 세션만) -->
        <v-card-text v-if="currentStep === 4">
          <p class="text-body-2 text-grey mb-3">각 매치의 점수를 입력하세요. 미입력 매치는 건너뜁니다.</p>
          <div class="score-bulk-list">
            <div v-for="(match, index) in generatedMatches" :key="index" class="score-bulk-item">
              <div class="score-bulk-match-info">
                <v-chip size="x-small" :color="getMatchTypeColor(match.match_type)" variant="tonal">
                  {{ getMatchTypeLabel(match.match_type) }}
                </v-chip>
                <span class="text-caption text-grey ml-1">{{ getMatchTeamNames(match, 'A') }} vs {{ getMatchTeamNames(match, 'B') }}</span>
              </div>
              <div class="score-bulk-inputs">
                <v-text-field
                  v-model.number="matchScores[match.id || index].team_a_score"
                  type="number"
                  min="0"
                  variant="outlined"
                  density="compact"
                  class="score-input-small"
                  placeholder="-"
                  hide-details
                />
                <span class="score-colon">:</span>
                <v-text-field
                  v-model.number="matchScores[match.id || index].team_b_score"
                  type="number"
                  min="0"
                  variant="outlined"
                  density="compact"
                  class="score-input-small"
                  placeholder="-"
                  hide-details
                />
              </div>
            </div>
          </div>
        </v-card-text>

        <!-- 액션 버튼 -->
        <v-card-actions>
          <v-btn v-if="currentStep > 1 && isPastDate" variant="text" @click="skipStep">
            건너뛰기
          </v-btn>
          <v-spacer />
          <v-btn variant="text" @click="closeCreateDialog">취소</v-btn>

          <!-- Step 1: 미래 → 생성, 과거 → 다음 -->
          <v-btn
            v-if="currentStep === 1 && !isPastDate"
            color="primary"
            variant="flat"
            :loading="isSaving"
            :disabled="!formValid"
            @click="createSession"
          >
            생성
          </v-btn>
          <v-btn
            v-if="currentStep === 1 && isPastDate"
            color="primary"
            variant="flat"
            :loading="isSaving"
            :disabled="!formValid"
            @click="createSessionAndNext"
          >
            다음
          </v-btn>

          <!-- Step 2: 참가자 추가 후 다음 -->
          <v-btn
            v-if="currentStep === 2"
            color="primary"
            variant="flat"
            :loading="isSaving"
            :disabled="selectedMemberIds.length === 0"
            @click="addParticipantsAndNext"
          >
            다음 ({{ selectedMemberIds.length }}명)
          </v-btn>

          <!-- Step 3: 매치 확정 후 다음 -->
          <v-btn
            v-if="currentStep === 3"
            color="primary"
            variant="flat"
            :disabled="generatedMatches.length === 0"
            @click="confirmMatchesAndNext"
          >
            다음
          </v-btn>

          <!-- Step 4: 점수 저장 -->
          <v-btn
            v-if="currentStep === 4"
            color="primary"
            variant="flat"
            :loading="isSaving"
            @click="saveBulkScoresAndFinish"
          >
            완료
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 로딩 -->
    <v-overlay v-model="isLoading" class="align-center justify-center" contained>
      <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
    </v-overlay>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useClubStore } from '@/stores/club'
import { useMemberStore } from '@/stores/member'
import apiClient from '@/api'
import sessionsApi from '@/api/sessions'
import { getMatchTypeColor, getMatchTypeLabel } from '@/utils/constants'

const router = useRouter()

const clubStore = useClubStore()
const memberStore = useMemberStore()
const selectedClub = computed(() => clubStore.selectedClub)
const isManager = computed(() => clubStore.isManagerOfSelectedClub)

const isLoading = ref(false)
const isSaving = ref(false)
const sessions = ref([])
const seasons = ref([])
const currentDate = ref(new Date())
const selectedDay = ref(null)

// 세션 생성 폼
const showCreateDialog = ref(false)
const createForm = ref(null)
const formValid = ref(false)
const sessionForm = ref({
  date: '',
  start_time: '09:00',
  end_time: '12:00',
  location: '',
  num_courts: 4,
  match_duration_minutes: 30,
  notes: ''
})

// 스테퍼 상태
const currentStep = ref(1)
const createdSessionId = ref(null)
const selectedMemberIds = ref([])
const participantGenderFilter = ref('all')
const generatedMatches = ref([])
const matchScores = ref({})
const isGeneratingStep = ref(false)
const showAISettingsStep = ref(false)
const aiModeStep = ref('balanced')
const stepError = ref('')
const generatedMatchType = ref(null) // 'auto' or 'ai'
const aiPreviewDataStep = ref(null)

// 과거 날짜 감지
const isPastDate = computed(() => {
  if (!sessionForm.value.date) return false
  const selected = new Date(sessionForm.value.date)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  selected.setHours(0, 0, 0, 0)
  return selected < today
})

// 다이얼로그 폭 동적 조절
const dialogMaxWidth = computed(() => isPastDate.value && currentStep.value > 1 ? 800 : 500)

// 클럽 회원 목록 (성별 필터 적용)
const filteredClubMembers = computed(() => {
  const members = memberStore.members || []
  if (participantGenderFilter.value === 'all') return members
  return members.filter(m => m.gender === participantGenderFilter.value)
})

// 선택된 남녀 수
const selectedMaleCount = computed(() => {
  const members = memberStore.members || []
  return selectedMemberIds.value.filter(id => {
    const m = members.find(mem => mem.id === id)
    return m?.gender === 'male'
  }).length
})

const selectedFemaleCount = computed(() => {
  const members = memberStore.members || []
  return selectedMemberIds.value.filter(id => {
    const m = members.find(mem => mem.id === id)
    return m?.gender === 'female'
  }).length
})

const weekdays = ['일', '월', '화', '수', '목', '금', '토']

const currentYear = computed(() => currentDate.value.getFullYear())
const currentMonth = computed(() => currentDate.value.getMonth() + 1)

const calendarDays = computed(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()

  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)

  const days = []
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  // 이전 달 날짜들
  const startDayOfWeek = firstDay.getDay()
  for (let i = startDayOfWeek - 1; i >= 0; i--) {
    const date = new Date(year, month, -i)
    days.push({
      date,
      isCurrentMonth: false,
      isToday: false,
      sessions: getSessionsForDate(date)
    })
  }

  // 현재 달 날짜들
  for (let i = 1; i <= lastDay.getDate(); i++) {
    const date = new Date(year, month, i)
    days.push({
      date,
      isCurrentMonth: true,
      isToday: date.getTime() === today.getTime(),
      sessions: getSessionsForDate(date)
    })
  }

  // 다음 달 날짜들 (6주 채우기)
  const remaining = 42 - days.length
  for (let i = 1; i <= remaining; i++) {
    const date = new Date(year, month + 1, i)
    days.push({
      date,
      isCurrentMonth: false,
      isToday: false,
      sessions: getSessionsForDate(date)
    })
  }

  return days
})

function getSessionsForDate(date) {
  const dateStr = formatDateToISO(date)
  return sessions.value.filter(s => s.date === dateStr)
}

function formatDateToISO(date) {
  // toISOString()은 UTC로 변환되어 날짜가 밀릴 수 있으므로 로컬 날짜 사용
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function formatSelectedDate(date) {
  return `${date.getMonth() + 1}월 ${date.getDate()}일 (${weekdays[date.getDay()]})`
}

function prevMonth() {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() - 1, 1)
}

function nextMonth() {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1, 1)
}

function goToToday() {
  currentDate.value = new Date()
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  selectedDay.value = calendarDays.value.find(d => d.date.getTime() === today.getTime())
}

function selectDay(day) {
  // 세션이 없는 날짜 클릭 시 (매니저만 생성 다이얼로그 열기)
  if (day.sessions.length === 0) {
    if (isManager.value) {
      openCreateDialogForDate(day.date)
    } else {
      selectedDay.value = day
    }
    return
  }

  // 세션이 1개인 날짜 클릭 시 세션 상세로 이동
  if (day.sessions.length === 1) {
    goToSession(day.sessions[0])
    return
  }

  // 세션이 2개 이상인 경우 목록 표시
  selectedDay.value = day
}

function goToSession(session) {
  router.push({ name: 'session-detail', params: { sessionId: session.id } })
}

function getSessionStatusClass(session) {
  const statusClasses = {
    scheduled: 'status-scheduled',
    in_progress: 'status-in-progress',
    completed: 'status-completed',
    cancelled: 'status-cancelled'
  }
  return statusClasses[session.status] || 'status-scheduled'
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

async function loadSessions() {
  if (!selectedClub.value?.id) return

  isLoading.value = true
  try {
    const response = await apiClient.get(`/clubs/${selectedClub.value.id}/sessions`)
    sessions.value = response.data
  } catch (error) {
    console.error('세션 목록 로드 실패:', error)
  } finally {
    isLoading.value = false
  }
}

async function loadSeasons() {
  if (!selectedClub.value?.id) return
  try {
    const response = await apiClient.get(`/clubs/${selectedClub.value.id}/seasons`)
    seasons.value = response.data || []
  } catch (error) {
    console.error('시즌 목록 로드 실패:', error)
    seasons.value = []
  }
}

// 특정 날짜에 해당하는 활성 시즌 찾기
function findSeasonForDate(dateStr) {
  if (!dateStr || !seasons.value.length) return null

  const targetDate = new Date(dateStr)
  targetDate.setHours(0, 0, 0, 0)

  return seasons.value.find(season => {
    if (season.status === 'completed') return false

    const startDate = new Date(season.start_date)
    const endDate = new Date(season.end_date)
    startDate.setHours(0, 0, 0, 0)
    endDate.setHours(23, 59, 59, 999)

    return targetDate >= startDate && targetDate <= endDate
  })
}

// 시즌 없음 경고 표시 여부
const showNoSeasonWarning = computed(() => {
  if (!sessionForm.value.date) return false
  return !findSeasonForDate(sessionForm.value.date)
})

// 세션 생성 관련 함수들
function formatDateForInput(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function initSessionForm(date) {
  // 동호회 설정값으로 초기화
  const club = selectedClub.value
  sessionForm.value = {
    date: formatDateForInput(date),
    start_time: '09:00',
    end_time: '12:00',
    location: club?.location || '',
    num_courts: club?.default_num_courts || 4,
    match_duration_minutes: club?.default_match_duration || 30,
    notes: ''
  }
}

function openCreateDialog() {
  // 기본 날짜: 오늘
  initSessionForm(new Date())
  showCreateDialog.value = true
}

function openCreateDialogForDate(date) {
  initSessionForm(date)
  showCreateDialog.value = true
}

function closeCreateDialog() {
  showCreateDialog.value = false
  initSessionForm(new Date())
  // 스테퍼 상태 리셋
  currentStep.value = 1
  createdSessionId.value = null
  selectedMemberIds.value = []
  generatedMatches.value = []
  matchScores.value = {}
  participantGenderFilter.value = 'all'
  isGeneratingStep.value = false
  showAISettingsStep.value = false
  aiModeStep.value = 'balanced'
  stepError.value = ''
  generatedMatchType.value = null
  aiPreviewDataStep.value = null
}

async function createSession() {
  if (!selectedClub.value?.id || !formValid.value) return

  isSaving.value = true
  try {
    // 세션 날짜에 해당하는 시즌 자동 연결
    const matchingSeason = findSeasonForDate(sessionForm.value.date)

    await apiClient.post(`/clubs/${selectedClub.value.id}/sessions`, {
      date: sessionForm.value.date,
      start_time: sessionForm.value.start_time,
      end_time: sessionForm.value.end_time,
      location: sessionForm.value.location || null,
      num_courts: sessionForm.value.num_courts,
      match_duration_minutes: sessionForm.value.match_duration_minutes,
      season_id: matchingSeason?.id || null
    })
    closeCreateDialog()
    await loadSessions()
    // 생성한 날짜 선택
    const createdDate = new Date(sessionForm.value.date)
    selectedDay.value = calendarDays.value.find(d =>
      d.date.toDateString() === createdDate.toDateString()
    )
  } catch (error) {
    console.error('세션 생성 실패:', error)
    alert(error.response?.data?.detail || '세션 생성에 실패했습니다.')
  } finally {
    isSaving.value = false
  }
}

// === 스테퍼 함수들 ===

// Step 1 → 2: 세션 생성 후 다음 단계
async function createSessionAndNext() {
  if (!selectedClub.value?.id || !formValid.value) return

  isSaving.value = true
  try {
    const matchingSeason = findSeasonForDate(sessionForm.value.date)
    const response = await apiClient.post(`/clubs/${selectedClub.value.id}/sessions`, {
      date: sessionForm.value.date,
      start_time: sessionForm.value.start_time,
      end_time: sessionForm.value.end_time,
      location: sessionForm.value.location || null,
      num_courts: sessionForm.value.num_courts,
      match_duration_minutes: sessionForm.value.match_duration_minutes,
      season_id: matchingSeason?.id || null
    })
    createdSessionId.value = response.data.id
    // 회원 목록 로드
    await memberStore.fetchMembers(selectedClub.value.id)
    currentStep.value = 2
  } catch (error) {
    alert(error.response?.data?.detail || '세션 생성에 실패했습니다.')
  } finally {
    isSaving.value = false
  }
}

// 회원 선택 토글
function toggleMemberSelection(memberId) {
  const idx = selectedMemberIds.value.indexOf(memberId)
  if (idx >= 0) {
    selectedMemberIds.value.splice(idx, 1)
  } else {
    selectedMemberIds.value.push(memberId)
  }
}

// Step 2 → 3: 참가자 일괄 추가 후 매치 생성 단계
async function addParticipantsAndNext() {
  if (!selectedClub.value?.id || !createdSessionId.value) return

  isSaving.value = true
  try {
    await sessionsApi.addParticipantsBulk(
      selectedClub.value.id,
      createdSessionId.value,
      selectedMemberIds.value
    )
    currentStep.value = 3
  } catch (error) {
    alert(error.response?.data?.detail || '참가자 추가에 실패했습니다.')
  } finally {
    isSaving.value = false
  }
}

// Step 3: 매치 생성 방식 선택
async function generateMatchesStep(method) {
  if (method === 'ai') {
    showAISettingsStep.value = true
    return
  }

  // 자동 생성
  isGeneratingStep.value = true
  stepError.value = ''
  try {
    await sessionsApi.generateMatches(selectedClub.value.id, createdSessionId.value)
    // 생성된 매치 목록 조회
    const response = await sessionsApi.getMatches(selectedClub.value.id, createdSessionId.value)
    generatedMatches.value = response.data
    generatedMatchType.value = 'auto'
    initMatchScores()
  } catch (error) {
    stepError.value = error.response?.data?.detail || '매치 생성에 실패했습니다.'
  } finally {
    isGeneratingStep.value = false
  }
}

// AI 생성 실행
async function executeAIGenerate() {
  isGeneratingStep.value = true
  stepError.value = ''
  try {
    const response = await sessionsApi.generateAIMatches(
      selectedClub.value.id,
      createdSessionId.value,
      { mode: aiModeStep.value }
    )
    aiPreviewDataStep.value = response.data
    // AI 미리보기 매치를 generatedMatches에 저장
    generatedMatches.value = response.data.matches || []
    generatedMatchType.value = 'ai'
    showAISettingsStep.value = false
    initMatchScores()
  } catch (error) {
    stepError.value = error.response?.data?.detail || 'AI 매치 생성에 실패했습니다.'
  } finally {
    isGeneratingStep.value = false
  }
}

// 매치 점수 초기화
function initMatchScores() {
  const scores = {}
  generatedMatches.value.forEach((match, index) => {
    const key = match.id || index
    scores[key] = { team_a_score: null, team_b_score: null }
  })
  matchScores.value = scores
}

// 매치 미리보기 리셋
function resetGeneratedMatches() {
  generatedMatches.value = []
  matchScores.value = {}
  showAISettingsStep.value = false
  generatedMatchType.value = null
  aiPreviewDataStep.value = null
  stepError.value = ''
}

// 매치 팀 이름 표시
function getMatchTeamNames(match, team) {
  // 자동 생성 매치 (participants 포함)
  if (match.participants) {
    return match.participants
      .filter(p => p.team === team)
      .map(p => p.member?.user?.name || p.name || '?')
      .join(', ')
  }
  // AI 미리보기 매치
  const teamData = team === 'A' ? match.team_a : match.team_b
  if (teamData?.player_names) {
    return teamData.player_names.join(', ')
  }
  return '-'
}

// Step 3 → 4: 매치 확정 후 점수 입력 단계
async function confirmMatchesAndNext() {
  // AI 생성인 경우 confirm API 호출 필요
  if (generatedMatchType.value === 'ai' && aiPreviewDataStep.value) {
    isSaving.value = true
    try {
      await sessionsApi.confirmAIMatches(
        selectedClub.value.id,
        createdSessionId.value,
        aiPreviewDataStep.value.matches
      )
      // 확정 후 매치 다시 조회 (실제 match ID 획득)
      const response = await sessionsApi.getMatches(selectedClub.value.id, createdSessionId.value)
      generatedMatches.value = response.data
      initMatchScores()
    } catch (error) {
      alert(error.response?.data?.detail || '매치 확정에 실패했습니다.')
      isSaving.value = false
      return
    } finally {
      isSaving.value = false
    }
  }
  currentStep.value = 4
}

// Step 4: 점수 일괄 저장
async function saveBulkScoresAndFinish() {
  if (!selectedClub.value?.id || !createdSessionId.value) return

  const scores = []
  for (const match of generatedMatches.value) {
    const key = match.id
    const score = matchScores.value[key]
    if (score && score.team_a_score != null && score.team_b_score != null
        && score.team_a_score >= 0 && score.team_b_score >= 0) {
      scores.push({
        match_id: match.id,
        team_a_score: score.team_a_score,
        team_b_score: score.team_b_score
      })
    }
  }

  isSaving.value = true
  try {
    if (scores.length > 0) {
      await sessionsApi.updateMatchesBulkScores(
        selectedClub.value.id,
        createdSessionId.value,
        scores
      )
    }
    closeCreateDialog()
    await loadSessions()
    // 세션 상세로 이동
    router.push({ name: 'session-detail', params: { sessionId: createdSessionId.value } })
  } catch (error) {
    alert(error.response?.data?.detail || '점수 저장에 실패했습니다.')
  } finally {
    isSaving.value = false
  }
}

// 건너뛰기 공통 로직
function skipStep() {
  const sessionId = createdSessionId.value
  closeCreateDialog()
  loadSessions()
  if (sessionId) {
    router.push({ name: 'session-detail', params: { sessionId } })
  }
}

watch(selectedClub, () => {
  loadSessions()
  loadSeasons()
})

watch(currentDate, () => {
  // 월 변경 시 오늘 날짜 선택 해제
  selectedDay.value = null
})

onMounted(() => {
  loadSessions()
  loadSeasons()
  goToToday()
})
</script>

<style scoped>
.session-calendar-page {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1E293B;
}

.calendar-card {
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 20px;
}

.calendar-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.calendar-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1E293B;
}

.calendar-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  margin-bottom: 8px;
}

.weekday {
  text-align: center;
  padding: 8px;
  font-size: 0.85rem;
  font-weight: 500;
  color: #64748B;
}

.weekday.sunday {
  color: #EF4444;
}

.weekday.saturday {
  color: #3B82F6;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.calendar-day {
  min-height: 80px;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 4px 2px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.calendar-day:hover {
  background: #F1F5F9;
}

.calendar-day.other-month {
  opacity: 0.3;
}

.calendar-day.today {
  background: #059669;
}

.calendar-day.today .day-number {
  color: white;
  font-weight: 600;
}

.calendar-day.sunday .day-number {
  color: #EF4444;
}

.calendar-day.saturday .day-number {
  color: #3B82F6;
}

.calendar-day.today.sunday .day-number,
.calendar-day.today.saturday .day-number {
  color: white;
}

.day-number {
  font-size: 0.9rem;
  font-weight: 500;
  color: #1E293B;
}

.session-times {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-top: 4px;
  width: 100%;
  align-items: center;
}

.session-time-chip {
  font-size: 0.65rem;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
  background: #D1FAE5;
  color: #059669;
  cursor: pointer;
  transition: all 0.2s;
}

.session-time-chip:hover {
  transform: scale(1.05);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.session-time-chip.status-scheduled {
  background: #DBEAFE;
  color: #2563EB;
}

.session-time-chip.status-in-progress {
  background: #FEF3C7;
  color: #D97706;
}

.session-time-chip.status-completed {
  background: #D1FAE5;
  color: #059669;
}

.session-time-chip.status-cancelled {
  background: #F3F4F6;
  color: #9CA3AF;
}

.more-sessions {
  font-size: 0.6rem;
  color: #64748B;
  font-weight: 500;
}

.sessions-card {
  border: 1px solid #E2E8F0;
  border-radius: 16px;
}

.sessions-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1E293B;
  display: flex;
  align-items: center;
}

.session-item {
  border-bottom: 1px solid #F1F5F9;
}

.session-item:last-child {
  border-bottom: none;
}

.session-time-badge {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #D1FAE5;
  color: #059669;
}

.session-time-badge.status-in-progress {
  background: #FEF3C7;
  color: #D97706;
}

.session-time-badge.status-completed {
  background: #D1FAE5;
  color: #059669;
}

.session-item-title {
  font-weight: 600;
  color: #1E293B;
}

/* 스테퍼 */
.stepper {
  background: transparent;
}

.stepper :deep(.v-stepper-header) {
  box-shadow: none;
}

/* 참가자 선택 */
.member-select-list {
  border: 1px solid #E2E8F0;
  border-radius: 8px;
}

.member-select-item {
  cursor: pointer;
  border-bottom: 1px solid #F1F5F9;
}

.member-select-item:last-child {
  border-bottom: none;
}

/* 매치 미리보기 */
.match-preview-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 300px;
  overflow-y: auto;
}

.match-preview-card {
  border: 1px solid #E2E8F0;
  border-radius: 8px;
  padding: 10px 12px;
}

.match-preview-teams {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
}

.team-name {
  flex: 1;
  color: #1E293B;
}

.team-name:first-child {
  text-align: right;
}

.vs-label {
  color: #94A3B8;
  font-weight: 600;
  font-size: 0.8rem;
}

/* 점수 일괄 입력 */
.score-bulk-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
}

.score-bulk-item {
  border: 1px solid #E2E8F0;
  border-radius: 8px;
  padding: 10px 12px;
}

.score-bulk-match-info {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.score-bulk-inputs {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.score-input-small {
  max-width: 70px;
}

.score-colon {
  font-size: 1.5rem;
  font-weight: 700;
  color: #94A3B8;
}

@media (max-width: 600px) {
  .session-calendar-page {
    padding: 12px;
  }

  .calendar-day {
    min-height: 70px;
    padding: 2px 1px;
  }

  .day-number {
    font-size: 0.75rem;
  }

  .session-time-chip {
    font-size: 0.55rem;
    padding: 1px 4px;
  }

  .more-sessions {
    font-size: 0.5rem;
  }

  .stepper :deep(.v-stepper-item__title) {
    font-size: 0.7rem;
  }

  .score-input-small {
    max-width: 60px;
  }
}
</style>
