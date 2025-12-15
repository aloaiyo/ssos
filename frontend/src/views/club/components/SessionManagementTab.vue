<template>
  <div class="session-management-tab">
    <!-- 헤더 -->
    <div class="tab-header">
      <h2 class="tab-title">일정 관리</h2>
      <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreateDialog">
        세션 추가
      </v-btn>
    </div>

    <!-- 달력 뷰 또는 리스트 뷰 토글 -->
    <v-card class="view-toggle-card" variant="flat">
      <v-card-text class="pa-3">
        <v-btn-toggle v-model="viewMode" mandatory color="primary" density="compact">
          <v-btn value="calendar" prepend-icon="mdi-calendar-month">
            달력
          </v-btn>
          <v-btn value="list" prepend-icon="mdi-format-list-bulleted">
            목록
          </v-btn>
        </v-btn-toggle>
      </v-card-text>
    </v-card>

    <!-- 달력 뷰 -->
    <v-card v-if="viewMode === 'calendar'" class="calendar-card" variant="flat">
      <v-card-text>
        <!-- 월 네비게이션 -->
        <div class="calendar-header">
          <v-btn icon variant="text" @click="prevMonth">
            <v-icon>mdi-chevron-left</v-icon>
          </v-btn>
          <h3 class="calendar-title">{{ currentYear }}년 {{ currentMonth + 1 }}월</h3>
          <v-btn icon variant="text" @click="nextMonth">
            <v-icon>mdi-chevron-right</v-icon>
          </v-btn>
        </div>

        <!-- 요일 헤더 -->
        <div class="calendar-weekdays">
          <div v-for="day in weekDays" :key="day" class="weekday">{{ day }}</div>
        </div>

        <!-- 달력 그리드 -->
        <div class="calendar-grid">
          <div
            v-for="(day, index) in calendarDays"
            :key="index"
            class="calendar-day"
            :class="{
              'other-month': day.otherMonth,
              'today': day.isToday,
              'has-session': day.sessions.length > 0,
            }"
            @click="day.sessions.length > 0 && selectDaySessions(day)"
          >
            <span class="day-number">{{ day.date }}</span>
            <div v-if="day.sessions.length > 0" class="session-dots">
              <div
                v-for="session in day.sessions.slice(0, 3)"
                :key="session.id"
                class="session-dot"
                :class="getSessionStatusClass(session)"
              ></div>
            </div>
          </div>
        </div>
      </v-card-text>
    </v-card>

    <!-- 리스트 뷰 -->
    <v-card v-else class="sessions-list-card" variant="flat">
      <v-card-text class="pa-0">
        <div v-if="sessions.length === 0" class="empty-state">
          <v-icon size="64" color="grey-lighten-1">mdi-calendar-blank</v-icon>
          <p>등록된 세션이 없습니다.</p>
          <v-btn color="primary" variant="tonal" @click="openCreateDialog">
            첫 세션 만들기
          </v-btn>
        </div>

        <v-list v-else class="session-list">
          <template v-for="(group, date) in groupedSessions" :key="date">
            <v-list-subheader class="session-date-header">
              {{ formatDateHeader(date) }}
            </v-list-subheader>
            <v-list-item
              v-for="session in group"
              :key="session.id"
              class="session-item"
              :class="{ 'selected': selectedSessionId === session.id }"
              @click="selectSession(session.id)"
            >
              <template v-slot:prepend>
                <div class="session-time-badge">
                  <v-icon size="16">mdi-clock-outline</v-icon>
                  <span>{{ session.start_time?.substring(0, 5) }}</span>
                </div>
              </template>
              <v-list-item-title class="session-title">
                {{ session.start_time?.substring(0, 5) }} - {{ session.end_time?.substring(0, 5) }}
              </v-list-item-title>
              <v-list-item-subtitle class="session-subtitle">
                <v-chip size="x-small" color="primary" variant="tonal" class="mr-2">
                  <v-icon start size="12">mdi-account-multiple</v-icon>
                  {{ session.participant_count || 0 }}명
                </v-chip>
                <v-chip size="x-small" color="secondary" variant="tonal">
                  <v-icon start size="12">mdi-tennis</v-icon>
                  {{ session.num_courts }}코트
                </v-chip>
              </v-list-item-subtitle>
              <template v-slot:append>
                <v-chip
                  :color="getSessionStatusColor(session)"
                  size="x-small"
                  variant="flat"
                >
                  {{ getSessionStatusLabel(session) }}
                </v-chip>
              </template>
            </v-list-item>
          </template>
        </v-list>
      </v-card-text>
    </v-card>

    <!-- 세션 상세 패널 -->
    <v-card v-if="selectedSession" class="session-detail-card" variant="flat">
      <v-card-title class="card-title">
        <div class="d-flex align-center justify-space-between w-100">
          <div class="d-flex align-center">
            <v-icon class="mr-2">mdi-calendar-check</v-icon>
            {{ formatDate(selectedSession.date) }}
            <v-chip class="ml-3" size="small" color="primary" variant="tonal">
              {{ selectedSession.start_time?.substring(0, 5) }} - {{ selectedSession.end_time?.substring(0, 5) }}
            </v-chip>
          </div>
          <div>
            <v-btn
              icon
              variant="text"
              size="small"
              color="error"
              @click="confirmDeleteSession"
            >
              <v-icon>mdi-delete</v-icon>
            </v-btn>
            <v-btn
              icon
              variant="text"
              size="small"
              @click="selectedSession = null; selectedSessionId = null"
            >
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </div>
        </div>
      </v-card-title>

      <v-card-text>
        <!-- 참가자 섹션 -->
        <div class="detail-section">
          <div class="section-header">
            <h4 class="section-title">
              <v-icon size="20" class="mr-2">mdi-account-multiple</v-icon>
              참가자
              <v-chip size="x-small" color="primary" class="ml-2">
                {{ selectedSession.participants?.length || 0 }}명
              </v-chip>
            </h4>
          </div>

          <div class="participants-grid">
            <v-chip
              v-for="participant in selectedSession.participants"
              :key="participant.id"
              :color="getParticipantColor(participant)"
              variant="tonal"
              closable
              @click:close="removeParticipant(participant.id)"
            >
              <v-avatar start size="24" :color="getParticipantColor(participant)">
                <span class="text-white text-caption">{{ getInitial(participant.name) }}</span>
              </v-avatar>
              {{ participant.name }}
              <span v-if="participant.category === 'guest'" class="text-caption ml-1">(게스트)</span>
              <span v-if="participant.category === 'associate'" class="text-caption ml-1">(준회원)</span>
            </v-chip>
          </div>

          <!-- 참가자 추가 탭 -->
          <v-tabs v-model="participantTab" density="compact" class="mt-4">
            <v-tab value="member">회원</v-tab>
            <v-tab value="guest">게스트</v-tab>
          </v-tabs>

          <v-window v-model="participantTab" class="mt-2">
            <!-- 회원 추가 -->
            <v-window-item value="member">
              <v-autocomplete
                v-model="selectedMemberId"
                :items="availableMembers"
                item-title="user_name"
                item-value="id"
                label="회원 추가"
                variant="outlined"
                density="compact"
                prepend-inner-icon="mdi-account-plus"
                hide-details
                clearable
                @update:model-value="addMemberParticipant"
              >
                <template v-slot:item="{ props, item }">
                  <v-list-item v-bind="props">
                    <template v-slot:prepend>
                      <v-avatar :color="item.raw.gender === 'male' ? 'blue' : 'pink'" size="32">
                        <span class="text-white text-caption">{{ getInitial(item.raw.user_name) }}</span>
                      </v-avatar>
                    </template>
                  </v-list-item>
                </template>
              </v-autocomplete>
            </v-window-item>

            <!-- 게스트 추가 -->
            <v-window-item value="guest">
              <div class="d-flex gap-2 align-center">
                <v-autocomplete
                  v-model="selectedGuestId"
                  :items="guests"
                  item-title="name"
                  item-value="id"
                  label="게스트 선택"
                  variant="outlined"
                  density="compact"
                  prepend-inner-icon="mdi-account-outline"
                  hide-details
                  clearable
                  class="flex-grow-1"
                  @update:model-value="addGuestParticipant"
                >
                  <template v-slot:item="{ props, item }">
                    <v-list-item v-bind="props">
                      <template v-slot:prepend>
                        <v-avatar :color="item.raw.gender === 'male' ? 'blue' : 'pink'" size="32">
                          <span class="text-white text-caption">{{ getInitial(item.raw.name) }}</span>
                        </v-avatar>
                      </template>
                    </v-list-item>
                  </template>
                </v-autocomplete>
                <v-btn color="primary" variant="tonal" @click="showGuestDialog = true">
                  <v-icon>mdi-plus</v-icon>
                  새 게스트
                </v-btn>
              </div>
            </v-window-item>
          </v-window>
        </div>

        <v-divider class="my-4" />

        <!-- 경기 섹션 -->
        <div class="detail-section">
          <div class="section-header">
            <h4 class="section-title">
              <v-icon size="20" class="mr-2">mdi-tennis</v-icon>
              경기
              <v-chip size="x-small" color="warning" class="ml-2">
                {{ selectedSession.matches?.length || 0 }}경기
              </v-chip>
            </h4>
            <div class="section-actions">
              <v-btn
                color="success"
                variant="tonal"
                size="small"
                prepend-icon="mdi-auto-fix"
                class="mr-2"
                :disabled="!selectedSession.participants?.length"
                @click="autoGenerateMatches"
              >
                자동 생성
              </v-btn>
              <v-btn
                color="primary"
                variant="tonal"
                size="small"
                prepend-icon="mdi-plus"
                @click="showMatchDialog = true"
              >
                수동 추가
              </v-btn>
            </div>
          </div>

          <!-- 경기 목록 -->
          <div v-if="selectedSession.matches?.length > 0" class="matches-grid">
            <v-card
              v-for="match in selectedSession.matches"
              :key="match.id"
              class="match-card"
              variant="outlined"
            >
              <v-card-text class="pa-3">
                <div class="match-header">
                  <div class="match-info">
                    <v-chip size="x-small" color="grey" variant="flat">
                      코트 {{ match.court_number }}
                    </v-chip>
                    <v-chip
                      size="x-small"
                      :color="getMatchTypeColor(match.match_type)"
                      variant="tonal"
                      class="ml-1"
                    >
                      {{ getMatchTypeLabel(match.match_type) }}
                    </v-chip>
                  </div>
                  <v-chip
                    :color="match.status === 'completed' ? 'success' : 'grey'"
                    size="x-small"
                    variant="flat"
                  >
                    {{ match.status === 'completed' ? '완료' : '대기' }}
                  </v-chip>
                </div>

                <div class="match-teams">
                  <div class="team team-a">
                    <div class="team-label">A팀</div>
                    <div class="team-players">
                      <template v-if="match.team_a?.length > 0">
                        <v-chip
                          v-for="player in match.team_a"
                          :key="player.id"
                          :color="getParticipantColor(player)"
                          variant="tonal"
                          size="x-small"
                        >
                          {{ player.name }}
                        </v-chip>
                      </template>
                      <span v-else class="text-grey text-caption">미배정</span>
                    </div>
                  </div>

                  <div class="match-score">
                    <v-text-field
                      :model-value="match.score?.team_a ?? 0"
                      type="number"
                      variant="outlined"
                      density="compact"
                      hide-details
                      class="score-input"
                      min="0"
                      @blur="updateScore(match.id, $event.target.value, match.score?.team_b ?? 0)"
                    />
                    <span class="score-divider">:</span>
                    <v-text-field
                      :model-value="match.score?.team_b ?? 0"
                      type="number"
                      variant="outlined"
                      density="compact"
                      hide-details
                      class="score-input"
                      min="0"
                      @blur="updateScore(match.id, match.score?.team_a ?? 0, $event.target.value)"
                    />
                  </div>

                  <div class="team team-b">
                    <div class="team-label">B팀</div>
                    <div class="team-players">
                      <template v-if="match.team_b?.length > 0">
                        <v-chip
                          v-for="player in match.team_b"
                          :key="player.id"
                          :color="getParticipantColor(player)"
                          variant="tonal"
                          size="x-small"
                        >
                          {{ player.name }}
                        </v-chip>
                      </template>
                      <span v-else class="text-grey text-caption">미배정</span>
                    </div>
                  </div>
                </div>

                <div class="match-actions">
                  <v-btn
                    icon
                    variant="text"
                    size="x-small"
                    color="error"
                    @click="deleteMatch(match.id)"
                  >
                    <v-icon size="16">mdi-delete</v-icon>
                  </v-btn>
                </div>
              </v-card-text>
            </v-card>
          </div>

          <div v-else class="no-matches">
            <v-icon size="48" color="grey-lighten-1">mdi-tennis</v-icon>
            <p class="text-medium-emphasis mt-2">등록된 경기가 없습니다.</p>
            <p class="text-caption text-grey">참가자를 추가한 후 자동 생성하거나 수동으로 추가하세요.</p>
          </div>
        </div>
      </v-card-text>
    </v-card>

    <!-- 세션 생성/수정 다이얼로그 -->
    <v-dialog v-model="showCreateDialog" max-width="500" persistent>
      <v-card>
        <v-card-title>
          {{ editingSession ? '세션 수정' : '새 세션 만들기' }}
        </v-card-title>
        <v-card-text>
          <v-form ref="sessionFormRef" v-model="sessionFormValid">
            <v-text-field
              v-model="sessionForm.date"
              label="날짜"
              type="date"
              variant="outlined"
              :rules="[v => !!v || '날짜를 선택하세요']"
              class="mb-3"
            />
            <v-row>
              <v-col cols="6">
                <v-text-field
                  v-model="sessionForm.start_time"
                  label="시작 시간"
                  type="time"
                  variant="outlined"
                  :rules="[v => !!v || '시작 시간을 입력하세요']"
                />
              </v-col>
              <v-col cols="6">
                <v-text-field
                  v-model="sessionForm.end_time"
                  label="종료 시간"
                  type="time"
                  variant="outlined"
                  :rules="[v => !!v || '종료 시간을 입력하세요']"
                />
              </v-col>
            </v-row>
            <v-text-field
              v-model.number="sessionForm.num_courts"
              label="코트 수"
              type="number"
              variant="outlined"
              min="1"
              max="20"
              :rules="[v => v >= 1 || '최소 1개 이상의 코트가 필요합니다']"
              class="mb-3"
            />
            <v-textarea
              v-model="sessionForm.notes"
              label="메모 (선택)"
              variant="outlined"
              rows="2"
              hide-details
            />
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="closeCreateDialog">취소</v-btn>
          <v-btn
            color="primary"
            :disabled="!sessionFormValid"
            :loading="isSaving"
            @click="saveSession"
          >
            {{ editingSession ? '수정' : '생성' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 경기 추가 다이얼로그 -->
    <v-dialog v-model="showMatchDialog" max-width="600">
      <v-card>
        <v-card-title>경기 추가</v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="6">
              <v-text-field
                v-model.number="newMatch.court_number"
                label="코트 번호"
                type="number"
                variant="outlined"
                min="1"
                density="compact"
              />
            </v-col>
            <v-col cols="6">
              <v-select
                v-model="newMatch.match_type"
                :items="matchTypes"
                label="경기 타입"
                variant="outlined"
                density="compact"
              />
            </v-col>
          </v-row>

          <v-divider class="my-3" />

          <v-row>
            <v-col cols="6">
              <div class="text-subtitle-2 mb-2">A팀</div>
              <v-select
                v-model="newMatch.team_a"
                :items="sessionParticipantsForMatch"
                item-title="name"
                item-value="id"
                label="A팀 선수 선택"
                variant="outlined"
                density="compact"
                multiple
                chips
                closable-chips
              >
                <template v-slot:chip="{ props, item }">
                  <v-chip
                    v-bind="props"
                    :color="item.raw.gender === 'male' ? 'blue' : 'pink'"
                    size="small"
                  >
                    {{ item.raw.name }}
                  </v-chip>
                </template>
                <template v-slot:item="{ props, item }">
                  <v-list-item v-bind="props" :disabled="newMatch.team_b?.includes(item.raw.id)">
                    <template v-slot:prepend>
                      <v-avatar :color="item.raw.gender === 'male' ? 'blue' : 'pink'" size="28">
                        <span class="text-white text-caption">{{ getInitial(item.raw.name) }}</span>
                      </v-avatar>
                    </template>
                  </v-list-item>
                </template>
              </v-select>
            </v-col>
            <v-col cols="6">
              <div class="text-subtitle-2 mb-2">B팀</div>
              <v-select
                v-model="newMatch.team_b"
                :items="sessionParticipantsForMatch"
                item-title="name"
                item-value="id"
                label="B팀 선수 선택"
                variant="outlined"
                density="compact"
                multiple
                chips
                closable-chips
              >
                <template v-slot:chip="{ props, item }">
                  <v-chip
                    v-bind="props"
                    :color="item.raw.gender === 'male' ? 'blue' : 'pink'"
                    size="small"
                  >
                    {{ item.raw.name }}
                  </v-chip>
                </template>
                <template v-slot:item="{ props, item }">
                  <v-list-item v-bind="props" :disabled="newMatch.team_a?.includes(item.raw.id)">
                    <template v-slot:prepend>
                      <v-avatar :color="item.raw.gender === 'male' ? 'blue' : 'pink'" size="28">
                        <span class="text-white text-caption">{{ getInitial(item.raw.name) }}</span>
                      </v-avatar>
                    </template>
                  </v-list-item>
                </template>
              </v-select>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="closeMatchDialog">취소</v-btn>
          <v-btn color="primary" @click="createMatch">생성</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 게스트 생성 다이얼로그 -->
    <v-dialog v-model="showGuestDialog" max-width="400" persistent>
      <v-card>
        <v-card-title>새 게스트 등록</v-card-title>
        <v-card-text>
          <v-form ref="guestFormRef" v-model="guestFormValid">
            <v-text-field
              v-model="guestForm.name"
              label="이름"
              variant="outlined"
              :rules="[v => !!v || '이름을 입력하세요']"
              class="mb-3"
            />
            <v-btn-toggle
              v-model="guestForm.gender"
              mandatory
              color="primary"
              class="mb-3"
            >
              <v-btn value="male">남성</v-btn>
              <v-btn value="female">여성</v-btn>
            </v-btn-toggle>
            <v-text-field
              v-model="guestForm.phone"
              label="연락처 (선택)"
              variant="outlined"
              hide-details
            />
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="closeGuestDialog">취소</v-btn>
          <v-btn
            color="primary"
            :disabled="!guestFormValid"
            :loading="isSavingGuest"
            @click="saveGuest"
          >
            등록
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import apiClient from '@/api'

const props = defineProps({
  clubId: {
    type: Number,
    required: true,
  },
  club: {
    type: Object,
    default: null,
  },
})

// 뷰 모드
const viewMode = ref('list')
const weekDays = ['일', '월', '화', '수', '목', '금', '토']

// 달력 상태
const currentDate = ref(new Date())
const currentYear = computed(() => currentDate.value.getFullYear())
const currentMonth = computed(() => currentDate.value.getMonth())

// 세션 데이터
const sessions = ref([])
const selectedSessionId = ref(null)
const selectedSession = ref(null)
const isLoading = ref(false)
const isSaving = ref(false)

// 회원 데이터
const availableMembers = ref([])
const selectedMemberId = ref(null)

// 게스트 데이터
const guests = ref([])
const selectedGuestId = ref(null)
const participantTab = ref('member')

// 다이얼로그 상태
const showCreateDialog = ref(false)
const showMatchDialog = ref(false)
const showGuestDialog = ref(false)
const sessionFormRef = ref(null)
const sessionFormValid = ref(false)
const editingSession = ref(null)
const guestFormRef = ref(null)
const guestFormValid = ref(false)
const isSavingGuest = ref(false)

// 게스트 폼
const guestForm = ref({
  name: '',
  gender: 'male',
  phone: '',
})

// 세션 폼
const sessionForm = ref({
  date: getTomorrowDate(),
  start_time: '10:00',
  end_time: '12:00',
  num_courts: 2,
  notes: '',
})

// 새 경기 폼
const newMatch = ref({
  court_number: 1,
  match_type: 'mixed_doubles',
  team_a: [],
  team_b: [],
})

// 경기 생성용 세션 참가자 목록
const sessionParticipantsForMatch = computed(() => {
  if (!selectedSession.value?.participants) return []
  return selectedSession.value.participants.map(p => ({
    id: p.id,
    name: p.name,
    gender: p.gender,
    category: p.category,
    member_id: p.member_id,
    guest_id: p.guest_id,
    user_id: p.user_id,
  }))
})

const matchTypes = [
  { value: 'mens_doubles', title: '남자 복식' },
  { value: 'mixed_doubles', title: '혼합 복식' },
  { value: 'singles', title: '단식' },
]

// 날짜 그룹화된 세션
const groupedSessions = computed(() => {
  const groups = {}
  const sortedSessions = [...sessions.value].sort((a, b) => {
    const dateA = new Date(a.date)
    const dateB = new Date(b.date)
    return dateB - dateA // 최신 날짜순
  })

  sortedSessions.forEach(session => {
    if (!groups[session.date]) {
      groups[session.date] = []
    }
    groups[session.date].push(session)
  })
  return groups
})

// 달력 일자 계산
const calendarDays = computed(() => {
  const year = currentYear.value
  const month = currentMonth.value
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  const days = []

  // 이전 달의 날짜들
  const firstDayOfWeek = firstDay.getDay()
  const prevMonthLastDay = new Date(year, month, 0).getDate()
  for (let i = firstDayOfWeek - 1; i >= 0; i--) {
    days.push({
      date: prevMonthLastDay - i,
      otherMonth: true,
      sessions: [],
    })
  }

  // 현재 달의 날짜들
  const today = new Date()
  for (let d = 1; d <= lastDay.getDate(); d++) {
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    const isToday = today.getFullYear() === year && today.getMonth() === month && today.getDate() === d
    const daySessions = sessions.value.filter(s => s.date === dateStr)

    days.push({
      date: d,
      fullDate: dateStr,
      otherMonth: false,
      isToday,
      sessions: daySessions,
    })
  }

  // 다음 달의 날짜들 (6주 채우기)
  const remainingDays = 42 - days.length
  for (let d = 1; d <= remainingDays; d++) {
    days.push({
      date: d,
      otherMonth: true,
      sessions: [],
    })
  }

  return days
})

// 유틸리티 함수
function getTomorrowDate() {
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  return tomorrow.toISOString().split('T')[0]
}

function getInitial(name) {
  if (!name) return '?'
  return name.charAt(0).toUpperCase()
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'short',
  })
}

function formatDateHeader(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const today = new Date()
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)

  if (date.toDateString() === today.toDateString()) {
    return '오늘'
  } else if (date.toDateString() === tomorrow.toDateString()) {
    return '내일'
  }

  return date.toLocaleDateString('ko-KR', {
    month: 'long',
    day: 'numeric',
    weekday: 'short',
  })
}

function getSessionStatusColor(session) {
  const sessionDate = new Date(session.date)
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  if (sessionDate < today) return 'grey'
  if (sessionDate.toDateString() === today.toDateString()) return 'success'
  return 'primary'
}

function getSessionStatusLabel(session) {
  const sessionDate = new Date(session.date)
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  if (sessionDate < today) return '종료'
  if (sessionDate.toDateString() === today.toDateString()) return '진행중'
  return '예정'
}

function getSessionStatusClass(session) {
  const sessionDate = new Date(session.date)
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  if (sessionDate < today) return 'past'
  if (sessionDate.toDateString() === today.toDateString()) return 'today'
  return 'upcoming'
}

function getMatchTypeColor(type) {
  const colors = {
    mens_doubles: 'blue',
    mixed_doubles: 'purple',
    singles: 'orange',
  }
  return colors[type] || 'grey'
}

function getMatchTypeLabel(type) {
  const labels = {
    mens_doubles: '남복',
    mixed_doubles: '혼복',
    singles: '단식',
  }
  return labels[type] || type
}

function getParticipantColor(participant) {
  // 게스트는 주황색, 준회원은 보라색, 일반 회원은 성별에 따라
  if (participant.category === 'guest') {
    return participant.gender === 'male' ? 'teal' : 'orange'
  }
  if (participant.category === 'associate') {
    return participant.gender === 'male' ? 'indigo' : 'purple'
  }
  return participant.gender === 'male' ? 'blue' : 'pink'
}

// 달력 네비게이션
function prevMonth() {
  currentDate.value = new Date(currentYear.value, currentMonth.value - 1, 1)
}

function nextMonth() {
  currentDate.value = new Date(currentYear.value, currentMonth.value + 1, 1)
}

function selectDaySessions(day) {
  if (day.sessions.length === 1) {
    selectSession(day.sessions[0].id)
  } else if (day.sessions.length > 1) {
    // 여러 세션이 있으면 리스트 뷰로 전환
    viewMode.value = 'list'
  }
}

// API 호출
async function loadSessions() {
  isLoading.value = true
  try {
    const response = await apiClient.get(`/clubs/${props.clubId}/sessions`)
    sessions.value = response.data
  } catch (error) {
    console.error('세션 목록 로드 실패:', error)
  } finally {
    isLoading.value = false
  }
}

async function loadMembers() {
  try {
    const response = await apiClient.get(`/clubs/${props.clubId}/members`, {
      params: { status_filter: 'active' }
    })
    availableMembers.value = response.data
  } catch (error) {
    console.error('회원 목록 로드 실패:', error)
  }
}

async function loadGuests() {
  try {
    const response = await apiClient.get(`/clubs/${props.clubId}/guests`)
    guests.value = response.data
  } catch (error) {
    console.error('게스트 목록 로드 실패:', error)
  }
}

async function selectSession(sessionId) {
  selectedSessionId.value = sessionId
  try {
    const response = await apiClient.get(`/clubs/${props.clubId}/sessions/${sessionId}`)
    selectedSession.value = response.data
  } catch (error) {
    console.error('세션 상세 로드 실패:', error)
  }
}

// 이미 세션이 있는 날짜인지 확인
function hasSessionOnDate(dateStr) {
  return sessions.value.some(s => s.date === dateStr)
}

// 가장 가까운 스케줄 날짜 계산 (이미 세션이 있는 날짜 제외)
function getNextScheduledDate() {
  const schedules = props.club?.schedules
  if (!schedules || schedules.length === 0) {
    return {
      date: getTomorrowDate(),
      start_time: '10:00',
      end_time: '12:00',
    }
  }

  const today = new Date()
  today.setHours(0, 0, 0, 0)

  // 오늘부터 60일 동안 스케줄에 맞는 날짜 찾기
  for (let i = 0; i <= 60; i++) {
    const checkDate = new Date(today)
    checkDate.setDate(today.getDate() + i)
    const jsDay = checkDate.getDay() // 0=일, 1=월, ..., 6=토

    // 스케줄의 day_of_week (0=월, 1=화, ..., 6=일)을 JS 요일로 변환
    // 스케줄 0(월) → JS 1, 스케줄 6(일) → JS 0
    for (const schedule of schedules) {
      const scheduleJsDay = (schedule.day_of_week + 1) % 7

      if (jsDay === scheduleJsDay) {
        const year = checkDate.getFullYear()
        const month = String(checkDate.getMonth() + 1).padStart(2, '0')
        const day = String(checkDate.getDate()).padStart(2, '0')
        const dateStr = `${year}-${month}-${day}`

        // 이미 세션이 있는 날짜면 건너뛰기
        if (hasSessionOnDate(dateStr)) {
          continue
        }

        // 오늘인 경우 현재 시간 이후인지 확인
        if (i === 0) {
          const now = new Date()
          const [hours, minutes] = (schedule.start_time || '10:00').split(':').map(Number)
          const scheduleTime = new Date(today)
          scheduleTime.setHours(hours, minutes, 0, 0)
          if (now > scheduleTime) {
            continue // 이미 지난 시간이면 다음 날짜 확인
          }
        }

        return {
          date: dateStr,
          start_time: formatTimeValue(schedule.start_time) || '10:00',
          end_time: formatTimeValue(schedule.end_time) || '12:00',
        }
      }
    }
  }

  // 스케줄에 맞는 날짜가 없으면 기본값
  return {
    date: getTomorrowDate(),
    start_time: '10:00',
    end_time: '12:00',
  }
}

// 시간 값 포맷 (HH:MM:SS → HH:MM)
function formatTimeValue(timeValue) {
  if (!timeValue) return null
  if (typeof timeValue === 'string') {
    return timeValue.substring(0, 5)
  }
  return timeValue
}

// 세션 CRUD
function openCreateDialog() {
  editingSession.value = null

  const nextSchedule = getNextScheduledDate()
  const defaultCourts = props.club?.default_num_courts || 2

  sessionForm.value = {
    date: nextSchedule.date,
    start_time: nextSchedule.start_time,
    end_time: nextSchedule.end_time,
    num_courts: defaultCourts,
    notes: '',
  }
  showCreateDialog.value = true
}

function closeCreateDialog() {
  showCreateDialog.value = false
  editingSession.value = null
}

async function saveSession() {
  if (!sessionFormValid.value) return

  isSaving.value = true
  try {
    if (editingSession.value) {
      await apiClient.put(
        `/clubs/${props.clubId}/sessions/${editingSession.value.id}`,
        sessionForm.value
      )
    } else {
      await apiClient.post(`/clubs/${props.clubId}/sessions`, sessionForm.value)
    }
    await loadSessions()
    closeCreateDialog()
  } catch (error) {
    console.error('세션 저장 실패:', error)
    alert('세션 저장에 실패했습니다.')
  } finally {
    isSaving.value = false
  }
}

async function confirmDeleteSession() {
  if (!selectedSession.value) return
  if (!confirm('이 세션을 삭제하시겠습니까? 모든 경기 정보도 함께 삭제됩니다.')) return

  try {
    await apiClient.delete(`/clubs/${props.clubId}/sessions/${selectedSession.value.id}`)
    selectedSession.value = null
    selectedSessionId.value = null
    await loadSessions()
  } catch (error) {
    console.error('세션 삭제 실패:', error)
    alert('세션 삭제에 실패했습니다.')
  }
}

// 참가자 관리
async function addMemberParticipant(memberId) {
  if (!memberId || !selectedSessionId.value) return

  try {
    await apiClient.post(`/clubs/${props.clubId}/sessions/${selectedSessionId.value}/participants`, {
      category: 'member',
      member_id: memberId
    })
    await selectSession(selectedSessionId.value)
    selectedMemberId.value = null
  } catch (error) {
    console.error('회원 참가자 추가 실패:', error)
    alert('참가자 추가에 실패했습니다.')
  }
}

async function addGuestParticipant(guestId) {
  if (!guestId || !selectedSessionId.value) return

  try {
    await apiClient.post(`/clubs/${props.clubId}/sessions/${selectedSessionId.value}/participants`, {
      category: 'guest',
      guest_id: guestId
    })
    await selectSession(selectedSessionId.value)
    selectedGuestId.value = null
  } catch (error) {
    console.error('게스트 참가자 추가 실패:', error)
    alert('참가자 추가에 실패했습니다.')
  }
}

async function removeParticipant(participantId) {
  if (!selectedSessionId.value) return

  try {
    await apiClient.delete(`/clubs/${props.clubId}/sessions/${selectedSessionId.value}/participants/${participantId}`)
    await selectSession(selectedSessionId.value)
  } catch (error) {
    console.error('참가자 제거 실패:', error)
    alert('참가자 제거에 실패했습니다.')
  }
}

// 게스트 관리
function closeGuestDialog() {
  showGuestDialog.value = false
  guestForm.value = { name: '', gender: 'male', phone: '' }
}

async function saveGuest() {
  if (!guestFormValid.value) return

  isSavingGuest.value = true
  try {
    const response = await apiClient.post(`/clubs/${props.clubId}/guests`, guestForm.value)
    await loadGuests()

    // 생성된 게스트를 자동으로 참가자에 추가
    if (selectedSessionId.value && response.data.id) {
      await addGuestParticipant(response.data.id)
    }

    closeGuestDialog()
  } catch (error) {
    console.error('게스트 저장 실패:', error)
    alert('게스트 등록에 실패했습니다.')
  } finally {
    isSavingGuest.value = false
  }
}

// 경기 관리
async function autoGenerateMatches() {
  if (!selectedSessionId.value) return

  try {
    await apiClient.post(`/clubs/${props.clubId}/sessions/${selectedSessionId.value}/matches/generate`)
    await selectSession(selectedSessionId.value)
    await loadSessions()
  } catch (error) {
    console.error('경기 자동 생성 실패:', error)
    alert('경기 자동 생성에 실패했습니다.')
  }
}

function closeMatchDialog() {
  showMatchDialog.value = false
  newMatch.value = { court_number: 1, match_type: 'mixed_doubles', team_a: [], team_b: [] }
}

async function createMatch() {
  if (!selectedSessionId.value) return

  try {
    // 선택된 참가자를 API 형식으로 변환
    const teamAData = newMatch.value.team_a.map(participantId => {
      const participant = sessionParticipantsForMatch.value.find(p => p.id === participantId)
      if (!participant) return null
      return {
        category: participant.category || 'member',
        member_id: participant.member_id,
        guest_id: participant.guest_id,
        user_id: participant.user_id,
      }
    }).filter(Boolean)

    const teamBData = newMatch.value.team_b.map(participantId => {
      const participant = sessionParticipantsForMatch.value.find(p => p.id === participantId)
      if (!participant) return null
      return {
        category: participant.category || 'member',
        member_id: participant.member_id,
        guest_id: participant.guest_id,
        user_id: participant.user_id,
      }
    }).filter(Boolean)

    await apiClient.post(`/clubs/${props.clubId}/sessions/${selectedSessionId.value}/matches`, {
      court_number: newMatch.value.court_number,
      match_type: newMatch.value.match_type,
      team_a: teamAData,
      team_b: teamBData,
    })
    await selectSession(selectedSessionId.value)
    closeMatchDialog()
  } catch (error) {
    console.error('경기 생성 실패:', error)
    alert('경기 생성에 실패했습니다.')
  }
}

async function deleteMatch(matchId) {
  if (!confirm('이 경기를 삭제하시겠습니까?')) return

  try {
    await apiClient.delete(`/clubs/${props.clubId}/sessions/${selectedSessionId.value}/matches/${matchId}`)
    await selectSession(selectedSessionId.value)
  } catch (error) {
    console.error('경기 삭제 실패:', error)
    alert('경기 삭제에 실패했습니다.')
  }
}

async function updateScore(matchId, teamAScore, teamBScore) {
  if (!selectedSessionId.value || teamAScore === '' || teamBScore === '') return

  try {
    await apiClient.put(`/clubs/${props.clubId}/sessions/${selectedSessionId.value}/matches/${matchId}`, {
      team_a_score: parseInt(teamAScore),
      team_b_score: parseInt(teamBScore)
    })
  } catch (error) {
    console.error('점수 저장 실패:', error)
  }
}

onMounted(() => {
  loadSessions()
  loadMembers()
  loadGuests()
})
</script>

<style scoped>
.session-management-tab {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.tab-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tab-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1E293B;
}

.view-toggle-card,
.calendar-card,
.sessions-list-card,
.session-detail-card {
  border: 1px solid #E2E8F0;
  border-radius: 16px;
}

/* 달력 스타일 */
.calendar-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 20px;
}

.calendar-title {
  font-size: 1.1rem;
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
  font-size: 0.85rem;
  font-weight: 500;
  color: #64748B;
  padding: 8px 0;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.calendar-day {
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4px;
  border-radius: 8px;
  cursor: default;
  transition: all 0.2s;
}

.calendar-day.has-session {
  cursor: pointer;
  background: #F0FDF4;
}

.calendar-day.has-session:hover {
  background: #DCFCE7;
}

.calendar-day.other-month {
  opacity: 0.3;
}

.calendar-day.today {
  background: #10B981;
  color: white;
}

.calendar-day.today .day-number {
  color: white;
}

.day-number {
  font-size: 0.9rem;
  font-weight: 500;
  color: #1E293B;
}

.session-dots {
  display: flex;
  gap: 3px;
  margin-top: 4px;
}

.session-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.session-dot.past {
  background: #94A3B8;
}

.session-dot.today {
  background: #10B981;
}

.session-dot.upcoming {
  background: #3B82F6;
}

/* 리스트 뷰 스타일 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px 24px;
  text-align: center;
  color: #94A3B8;
}

.empty-state p {
  margin: 16px 0;
}

.session-list {
  padding: 0;
}

.session-date-header {
  background: #F8FAFC;
  font-weight: 600;
  color: #1E293B;
}

.session-item {
  border-bottom: 1px solid #E2E8F0;
  padding: 16px 20px;
}

.session-item.selected {
  background: #F0FDF4;
  border-left: 3px solid #10B981;
}

.session-time-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #64748B;
  font-size: 0.85rem;
}

.session-title {
  font-weight: 600;
  color: #1E293B;
}

.session-subtitle {
  margin-top: 4px;
}

/* 세션 상세 스타일 */
.card-title {
  display: flex;
  align-items: center;
  font-size: 1rem;
  font-weight: 600;
  padding: 16px 20px;
  border-bottom: 1px solid #E2E8F0;
}

.detail-section {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title {
  display: flex;
  align-items: center;
  font-size: 1rem;
  font-weight: 600;
  color: #1E293B;
}

.participants-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

/* 경기 카드 스타일 */
.matches-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.match-card {
  border-radius: 12px;
  position: relative;
}

.match-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.match-info {
  display: flex;
  gap: 4px;
}

.match-teams {
  display: flex;
  align-items: center;
  gap: 12px;
}

.team {
  flex: 1;
}

.team-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748B;
  margin-bottom: 6px;
}

.team-players {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.match-score {
  display: flex;
  align-items: center;
  gap: 4px;
}

.score-input {
  width: 50px;
}

.score-input :deep(input) {
  text-align: center;
  font-weight: 700;
}

.score-divider {
  font-size: 1.25rem;
  font-weight: 700;
  color: #64748B;
}

.match-actions {
  position: absolute;
  top: 8px;
  right: 8px;
}

.no-matches {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  text-align: center;
}
</style>
