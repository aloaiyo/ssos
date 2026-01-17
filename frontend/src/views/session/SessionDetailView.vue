<template>
  <div class="session-detail-page">
    <!-- 로딩 -->
    <div v-if="isLoading" class="loading-container">
      <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
    </div>

    <template v-else-if="session">
      <!-- 세션 정보 헤더 -->
      <div class="session-header">
        <div class="header-content">
          <v-btn icon variant="text" @click="goBack" class="back-btn">
            <v-icon>mdi-arrow-left</v-icon>
          </v-btn>
          <div class="session-info">
            <div class="session-title-row">
              <h1 class="session-title">{{ session.title || `세션 #${session.id}` }}</h1>
              <v-chip :color="getSessionTypeColor(session.session_type)" size="small" variant="tonal">
                {{ getSessionTypeLabel(session.session_type) }}
              </v-chip>
            </div>
            <div class="session-meta">
              <span v-if="session.date" class="meta-item">
                <v-icon size="16">mdi-calendar</v-icon>
                {{ formatDateTime(session.date, session.start_time) }}
              </span>
              <span v-if="session.location" class="meta-item">
                <v-icon size="16">mdi-map-marker</v-icon>
                {{ session.location }}
              </span>
            </div>
          </div>
          <v-btn icon variant="text" @click="showEditDialog = true">
            <v-icon>mdi-pencil</v-icon>
          </v-btn>
        </div>

        <!-- 참가/불참 토글 버튼 -->
        <div class="participation-section" v-if="myParticipation?.is_member">
          <v-btn
            :color="myParticipation?.is_participating ? 'error' : 'primary'"
            :variant="myParticipation?.is_participating ? 'outlined' : 'flat'"
            :loading="isTogglingParticipation"
            @click="toggleParticipation"
            block
            class="mt-4"
          >
            <v-icon start>{{ myParticipation?.is_participating ? 'mdi-account-minus' : 'mdi-account-plus' }}</v-icon>
            {{ myParticipation?.is_participating ? '참가 취소' : '참가하기' }}
          </v-btn>
          <p v-if="myParticipation?.is_participating" class="participation-status text-success mt-2">
            <v-icon size="16">mdi-check-circle</v-icon>
            참가 중입니다
          </p>
        </div>
      </div>

      <!-- 탭 메뉴 -->
      <v-tabs v-model="activeTab" color="primary" class="session-tabs">
        <v-tab value="participants">참가자</v-tab>
        <v-tab value="matches">경기</v-tab>
      </v-tabs>

      <v-window v-model="activeTab" class="tab-content">
        <!-- 참가자 탭 -->
        <v-window-item value="participants">
          <div class="tab-header">
            <h2 class="section-title">참가자 ({{ participants.length }}명)</h2>
            <v-btn color="primary" variant="flat" size="small" @click="showAddParticipantDialog = true">
              <v-icon start size="18">mdi-account-plus</v-icon>
              참가자 추가
            </v-btn>
          </div>

          <div v-if="participants.length === 0" class="empty-state">
            <v-icon size="48" color="grey-lighten-1">mdi-account-group</v-icon>
            <p class="text-grey mt-3">참가자가 없습니다</p>
            <v-btn color="primary" variant="flat" class="mt-3" @click="showAddParticipantDialog = true">
              참가자 추가하기
            </v-btn>
          </div>

          <div v-else class="participant-list">
            <v-card
              v-for="participant in participants"
              :key="participant.id"
              class="participant-card"
              variant="flat"
            >
              <div class="participant-content">
                <v-avatar size="40" color="primary">
                  <span class="text-white">{{ getInitials(getParticipantName(participant)) }}</span>
                </v-avatar>
                <div class="participant-info">
                  <span class="participant-name">{{ getParticipantName(participant) }}</span>
                  <span class="participant-gender">{{ getGenderLabel(getParticipantGender(participant)) }}</span>
                </div>
                <v-btn
                  icon
                  variant="text"
                  size="small"
                  color="error"
                  @click="removeParticipant(participant)"
                >
                  <v-icon size="18">mdi-close</v-icon>
                </v-btn>
              </div>
            </v-card>
          </div>
        </v-window-item>

        <!-- 경기 탭 -->
        <v-window-item value="matches">
          <div class="tab-header">
            <h2 class="section-title">경기 ({{ matches.length }}개)</h2>
            <v-btn
              color="primary"
              variant="flat"
              size="small"
              @click="showAIGenerateDialog = true"
              :disabled="participants.length < 4"
            >
              <v-icon start size="18">mdi-robot</v-icon>
              AI 경기생성
            </v-btn>
          </div>

          <div v-if="matches.length === 0" class="empty-state">
            <v-icon size="48" color="grey-lighten-1">mdi-tennis</v-icon>
            <p class="text-grey mt-3">등록된 경기가 없습니다</p>
            <v-btn
              color="primary"
              variant="flat"
              class="mt-3"
              @click="showAIGenerateDialog = true"
              :disabled="participants.length < 4"
            >
              <v-icon start>mdi-robot</v-icon>
              AI 경기생성
            </v-btn>
          </div>

          <div v-else class="match-list">
            <v-card
              v-for="match in matches"
              :key="match.id"
              class="match-card"
              variant="flat"
            >
              <div class="match-content">
                <div class="match-info">
                  <v-chip size="x-small" :color="getMatchTypeColor(match.match_type)" variant="tonal" class="mb-2">
                    {{ getMatchTypeLabel(match.match_type) }}
                  </v-chip>
                  <div class="match-teams">
                    <div class="team team-a">
                      <span v-for="(player, idx) in getTeamA(match)" :key="idx">
                        {{ player }}
                      </span>
                    </div>
                    <div class="match-score">
                      <span class="score">{{ match.score_a || 0 }}</span>
                      <span class="divider">:</span>
                      <span class="score">{{ match.score_b || 0 }}</span>
                    </div>
                    <div class="team team-b">
                      <span v-for="(player, idx) in getTeamB(match)" :key="idx">
                        {{ player }}
                      </span>
                    </div>
                  </div>
                </div>
                <v-btn icon variant="text" size="small" @click="openScoreDialog(match)">
                  <v-icon size="18">mdi-pencil</v-icon>
                </v-btn>
              </div>
            </v-card>
          </div>
        </v-window-item>
      </v-window>
    </template>

    <!-- 세션 수정 다이얼로그 -->
    <v-dialog v-model="showEditDialog" max-width="500">
      <v-card>
        <v-card-title>세션 수정</v-card-title>
        <v-card-text>
          <v-form ref="editFormRef" v-model="editFormValid">
            <v-text-field
              v-model="editForm.title"
              label="세션 제목"
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
                  :model-value="formatDateDisplay(editForm.date)"
                  label="날짜"
                  prepend-inner-icon="mdi-calendar"
                  readonly
                ></v-text-field>
              </template>
              <v-date-picker
                v-model="editForm.date"
                @update:model-value="showDatePicker = false"
                color="primary"
              ></v-date-picker>
            </v-menu>

            <!-- 시작 시간 선택 -->
            <div class="time-section">
              <label class="time-label">시작 시간</label>
              <v-chip-group
                v-model="editForm.start_time"
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
                v-model="editForm.end_time"
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
              v-model="editForm.location"
              label="장소"
              prepend-inner-icon="mdi-map-marker"
              class="mt-2"
            ></v-text-field>

            <v-select
              v-model="editForm.session_type"
              label="유형"
              :items="sessionTypeOptions"
              item-title="label"
              item-value="value"
            ></v-select>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-btn color="error" variant="text" @click="confirmDeleteSession">삭제</v-btn>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="showEditDialog = false">취소</v-btn>
          <v-btn color="primary" variant="flat" :loading="isSaving" @click="saveSession">저장</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 참가자 추가 다이얼로그 -->
    <v-dialog v-model="showAddParticipantDialog" max-width="400">
      <v-card>
        <v-card-title>참가자 추가</v-card-title>
        <v-card-text>
          <v-list density="compact" class="member-select-list">
            <v-list-item
              v-for="member in availableMembers"
              :key="member.id"
              @click="addParticipant(member)"
              class="member-select-item"
            >
              <template v-slot:prepend>
                <v-avatar size="32" color="primary">
                  <span class="text-white">{{ getInitials(member.user_name) }}</span>
                </v-avatar>
              </template>
              <v-list-item-title>{{ member.user_name || '알 수 없음' }}</v-list-item-title>
              <v-list-item-subtitle>{{ getGenderLabel(member.gender) }}</v-list-item-subtitle>
            </v-list-item>
          </v-list>
          <p v-if="availableMembers.length === 0" class="text-grey text-center py-4">
            추가할 수 있는 회원이 없습니다
          </p>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="showAddParticipantDialog = false">닫기</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 점수 입력 다이얼로그 -->
    <v-dialog v-model="showScoreDialog" max-width="350">
      <v-card>
        <v-card-title>점수 입력</v-card-title>
        <v-card-text>
          <div class="score-input-container">
            <div class="team-score">
              <p class="team-label">팀 A</p>
              <v-text-field
                v-model.number="scoreForm.score_a"
                type="number"
                min="0"
                variant="outlined"
                density="compact"
                class="score-input"
              ></v-text-field>
            </div>
            <span class="score-divider">:</span>
            <div class="team-score">
              <p class="team-label">팀 B</p>
              <v-text-field
                v-model.number="scoreForm.score_b"
                type="number"
                min="0"
                variant="outlined"
                density="compact"
                class="score-input"
              ></v-text-field>
            </div>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="showScoreDialog = false">취소</v-btn>
          <v-btn color="primary" variant="flat" :loading="isSavingScore" @click="saveScore">저장</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 삭제 확인 다이얼로그 -->
    <v-dialog v-model="showDeleteDialog" max-width="400">
      <v-card>
        <v-card-title>세션 삭제</v-card-title>
        <v-card-text>
          이 세션을 삭제하시겠습니까?
          <br />
          <span class="text-error">이 작업은 되돌릴 수 없습니다.</span>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="showDeleteDialog = false">취소</v-btn>
          <v-btn color="error" variant="flat" :loading="isDeleting" @click="deleteSession">삭제</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- AI 경기 생성 설정 다이얼로그 -->
    <v-dialog v-model="showAIGenerateDialog" max-width="450">
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon color="primary" class="mr-2">mdi-robot</v-icon>
          AI 경기 생성
        </v-card-title>
        <v-card-text>
          <p class="text-grey mb-4">참가자: {{ participants.length }}명</p>

          <v-radio-group v-model="aiGenerateForm.mode" label="매칭 방식" class="mb-4">
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

          <v-divider class="mb-4"></v-divider>

          <div class="d-flex gap-3">
            <v-text-field
              v-model.number="aiGenerateForm.match_duration_minutes"
              label="경기 시간 (분)"
              type="number"
              min="10"
              max="60"
              density="compact"
              variant="outlined"
            ></v-text-field>
            <v-text-field
              v-model.number="aiGenerateForm.break_duration_minutes"
              label="휴식 시간 (분)"
              type="number"
              min="0"
              max="30"
              density="compact"
              variant="outlined"
            ></v-text-field>
          </div>

          <v-alert v-if="aiGenerateError" type="error" density="compact" class="mt-3">
            {{ aiGenerateError }}
          </v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="showAIGenerateDialog = false">취소</v-btn>
          <v-btn
            color="primary"
            variant="flat"
            :loading="isAIGenerating"
            @click="generateAIMatches"
          >
            <v-icon start>mdi-creation</v-icon>
            생성하기
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- AI 경기 미리보기 다이얼로그 -->
    <v-dialog v-model="showAIPreviewDialog" max-width="600" scrollable>
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon color="success" class="mr-2">mdi-check-circle</v-icon>
          경기 미리보기
        </v-card-title>
        <v-card-subtitle v-if="aiPreviewData?.summary">
          총 {{ aiPreviewData.summary.total_matches }}경기
          (남복 {{ aiPreviewData.summary.mens_doubles_matches || 0 }},
          여복 {{ aiPreviewData.summary.womens_doubles_matches || 0 }},
          혼복 {{ aiPreviewData.summary.mixed_doubles_matches || 0 }})
        </v-card-subtitle>
        <v-card-text class="pa-0" style="max-height: 400px;">
          <v-list density="compact">
            <v-list-item
              v-for="(match, index) in aiPreviewData?.matches || []"
              :key="index"
              class="ai-preview-match"
            >
              <template v-slot:prepend>
                <v-chip
                  :color="getMatchTypeColor(match.match_type)"
                  size="x-small"
                  variant="tonal"
                  class="mr-2"
                >
                  {{ getMatchTypeLabel(match.match_type) }}
                </v-chip>
              </template>
              <v-list-item-title class="d-flex align-center justify-space-between">
                <span class="team-names">{{ match.team_a?.player_names?.join(', ') || '-' }}</span>
                <span class="vs-text mx-2">vs</span>
                <span class="team-names">{{ match.team_b?.player_names?.join(', ') || '-' }}</span>
              </v-list-item-title>
              <v-list-item-subtitle>
                {{ match.scheduled_time }} | 코트 {{ match.court_number }}
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-card-text>
        <v-card-actions>
          <v-btn variant="text" @click="showAIPreviewDialog = false">취소</v-btn>
          <v-btn variant="outlined" @click="regenerateAIMatches">
            <v-icon start>mdi-refresh</v-icon>
            다시 생성
          </v-btn>
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            variant="flat"
            :loading="isConfirmingAI"
            @click="confirmAIMatches"
          >
            <v-icon start>mdi-check</v-icon>
            확정하기
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useClubStore } from '@/stores/club'
import sessionsApi from '@/api/sessions'
import clubsApi from '@/api/clubs'

const route = useRoute()
const router = useRouter()
const clubStore = useClubStore()

const selectedClub = computed(() => clubStore.selectedClub)

const isLoading = ref(true)
const session = ref(null)
const participants = ref([])
const matches = ref([])
const clubMembers = ref([])
const myParticipation = ref(null)

const activeTab = ref('participants')
const isGenerating = ref(false)
const isSaving = ref(false)
const isDeleting = ref(false)
const isSavingScore = ref(false)
const isTogglingParticipation = ref(false)

// AI 경기 생성
const showAIGenerateDialog = ref(false)
const showAIPreviewDialog = ref(false)
const isAIGenerating = ref(false)
const isConfirmingAI = ref(false)
const aiGenerateError = ref('')
const aiPreviewData = ref(null)
const aiGenerateForm = ref({
  mode: 'balanced',
  match_duration_minutes: 30,
  break_duration_minutes: 5
})

// 세션 수정
const showEditDialog = ref(false)
const showDatePicker = ref(false)
const editFormRef = ref(null)
const editFormValid = ref(true)
const editForm = ref({
  title: '',
  date: new Date(),
  start_time: '09:00',
  end_time: '12:00',
  location: '',
  session_type: 'league'
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
  const startIdx = timeOptions.findIndex(t => t.value === editForm.value.start_time)
  return timeOptions.slice(startIdx + 1)
})

// 참가자 추가
const showAddParticipantDialog = ref(false)

// 점수 입력
const showScoreDialog = ref(false)
const selectedMatch = ref(null)
const scoreForm = ref({
  score_a: 0,
  score_b: 0
})

// 삭제 확인
const showDeleteDialog = ref(false)

const sessionTypeOptions = [
  { value: 'league', label: '리그전' },
  { value: 'tournament', label: '토너먼트' }
]

const availableMembers = computed(() => {
  const participantIds = participants.value.map(p => p.member?.id)
  return clubMembers.value.filter(m => !participantIds.includes(m.id))
})

function getSessionTypeColor(type) {
  return type === 'tournament' ? 'warning' : 'primary'
}

function getSessionTypeLabel(type) {
  return type === 'tournament' ? '토너먼트' : '리그'
}

function getMatchTypeColor(type) {
  const colors = {
    mens_doubles: 'blue',
    womens_doubles: 'pink',
    mixed_doubles: 'purple',
    singles: 'green'
  }
  return colors[type] || 'grey'
}

function getMatchTypeLabel(type) {
  const labels = {
    mens_doubles: '남복',
    womens_doubles: '여복',
    mixed_doubles: '혼복',
    singles: '단식'
  }
  return labels[type] || type
}

function getGenderLabel(gender) {
  return gender === 'male' ? '남성' : gender === 'female' ? '여성' : ''
}

function getInitials(name) {
  if (!name) return '?'
  return name.charAt(0)
}

function formatDateTime(dateStr, timeStr) {
  if (!dateStr) return ''
  const y = dateStr.slice(0, 4)
  const m = dateStr.slice(5, 7)
  const d = dateStr.slice(8, 10)
  if (timeStr) {
    return `${y}.${m}.${d} ${timeStr.slice(0, 5)}`
  }
  return `${y}.${m}.${d}`
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

function getParticipantName(p) {
  if (p.member?.user?.name) return p.member.user.name
  if (p.guest?.name) return p.guest.name
  if (p.user?.name) return p.user.name
  // 단순 구조 (get_session API 응답)
  if (p.name) return p.name
  return '알 수 없음'
}

function getParticipantGender(p) {
  if (p.member?.user?.gender) return p.member.user.gender
  if (p.guest?.gender) return p.guest.gender
  if (p.user?.gender) return p.user.gender
  // 단순 구조 (get_session API 응답)
  if (p.gender) return p.gender
  return null
}

function getTeamA(match) {
  if (!match.participants) return []
  return match.participants
    .filter(p => p.team === 'A')
    .map(p => getParticipantName(p))
}

function getTeamB(match) {
  if (!match.participants) return []
  return match.participants
    .filter(p => p.team === 'B')
    .map(p => getParticipantName(p))
}

function goBack() {
  if (session.value?.season_id) {
    router.push({ name: 'season-detail', params: { seasonId: session.value.season_id } })
  } else {
    router.push({ name: 'session-list' })
  }
}

async function loadSession() {
  if (!selectedClub.value?.id) return
  const sessionId = route.params.sessionId

  isLoading.value = true
  try {
    const response = await sessionsApi.getSession(selectedClub.value.id, sessionId)
    session.value = response.data

    // 폼 초기화 (새 구조)
    editForm.value = {
      title: session.value.title || '',
      date: session.value.date ? new Date(session.value.date) : new Date(),
      start_time: session.value.start_time?.slice(0, 5) || '09:00',
      end_time: session.value.end_time?.slice(0, 5) || '12:00',
      location: session.value.location || '',
      session_type: session.value.session_type || 'league'
    }

    await Promise.all([
      loadParticipants(),
      loadMatches(),
      loadClubMembers(),
      loadMyParticipation()
    ])
  } catch (error) {
    console.error('세션 조회 실패:', error)
  } finally {
    isLoading.value = false
  }
}

async function loadParticipants() {
  if (!selectedClub.value?.id || !session.value?.id) return
  try {
    const response = await sessionsApi.getSessionParticipants(selectedClub.value.id, session.value.id)
    participants.value = Array.isArray(response.data) ? response.data : []
  } catch (error) {
    console.error('참가자 조회 실패:', error)
    participants.value = []
  }
}

async function loadMatches() {
  if (!selectedClub.value?.id || !session.value?.id) return
  try {
    const response = await sessionsApi.getMatches(selectedClub.value.id, session.value.id)
    matches.value = Array.isArray(response.data) ? response.data : []
  } catch (error) {
    console.error('경기 조회 실패:', error)
    matches.value = []
  }
}

async function loadClubMembers() {
  if (!selectedClub.value?.id) return
  try {
    const response = await clubsApi.getClubMembers(selectedClub.value.id)
    clubMembers.value = Array.isArray(response.data) ? response.data : []
  } catch (error) {
    console.error('회원 목록 조회 실패:', error)
    clubMembers.value = []
  }
}

async function loadMyParticipation() {
  if (!selectedClub.value?.id || !session.value?.id) return
  try {
    const response = await sessionsApi.getMyParticipation(selectedClub.value.id, session.value.id)
    myParticipation.value = response.data
  } catch (error) {
    console.error('참가 여부 조회 실패:', error)
    myParticipation.value = null
  }
}

async function toggleParticipation() {
  if (!selectedClub.value?.id || !session.value?.id) return

  isTogglingParticipation.value = true
  try {
    if (myParticipation.value?.is_participating) {
      // 참가 취소
      await sessionsApi.leaveSession(selectedClub.value.id, session.value.id)
      myParticipation.value = { ...myParticipation.value, is_participating: false }
    } else {
      // 참가
      await sessionsApi.joinSession(selectedClub.value.id, session.value.id)
      myParticipation.value = { ...myParticipation.value, is_participating: true }
    }
    // 참가자 목록 새로고침
    await loadParticipants()
  } catch (error) {
    console.error('참가 상태 변경 실패:', error)
    alert(error.response?.data?.detail || '참가 상태 변경에 실패했습니다')
  } finally {
    isTogglingParticipation.value = false
  }
}

async function saveSession() {
  if (!selectedClub.value?.id || !session.value?.id) return

  isSaving.value = true
  try {
    // Date 객체에서 YYYY-MM-DD 형식 추출
    const d = new Date(editForm.value.date)
    const datePart = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`

    await sessionsApi.updateSession(selectedClub.value.id, session.value.id, {
      title: editForm.value.title,
      date: datePart,
      start_time: editForm.value.start_time + ':00',
      end_time: editForm.value.end_time + ':00',
      location: editForm.value.location,
      session_type: editForm.value.session_type
    })
    // 로컬 상태 업데이트
    session.value = {
      ...session.value,
      title: editForm.value.title,
      date: datePart,
      start_time: editForm.value.start_time + ':00',
      end_time: editForm.value.end_time + ':00',
      location: editForm.value.location,
      session_type: editForm.value.session_type
    }
    showEditDialog.value = false
  } catch (error) {
    console.error('세션 수정 실패:', error)
  } finally {
    isSaving.value = false
  }
}

function confirmDeleteSession() {
  showEditDialog.value = false
  showDeleteDialog.value = true
}

async function deleteSession() {
  if (!selectedClub.value?.id || !session.value?.id) return

  isDeleting.value = true
  try {
    await sessionsApi.deleteSession(selectedClub.value.id, session.value.id)
    showDeleteDialog.value = false
    goBack()
  } catch (error) {
    console.error('세션 삭제 실패:', error)
  } finally {
    isDeleting.value = false
  }
}

async function addParticipant(member) {
  if (!selectedClub.value?.id || !session.value?.id) return

  try {
    await sessionsApi.addParticipant(selectedClub.value.id, session.value.id, member.id)
    await loadParticipants()
  } catch (error) {
    console.error('참가자 추가 실패:', error)
  }
}

async function removeParticipant(participant) {
  if (!selectedClub.value?.id || !session.value?.id) return

  try {
    // participant.id를 먼저 사용하고, 없으면 member_id 사용 (백엔드가 둘 다 처리 가능)
    const participantId = participant.id || participant.member?.id || participant.guest?.id || participant.user?.id
    if (!participantId) {
      console.error('참가자 ID를 찾을 수 없습니다')
      return
    }
    await sessionsApi.removeParticipant(selectedClub.value.id, session.value.id, participantId)
    await loadParticipants()
  } catch (error) {
    console.error('참가자 제거 실패:', error)
  }
}

async function generateMatches() {
  if (!selectedClub.value?.id || !session.value?.id) return

  isGenerating.value = true
  try {
    await sessionsApi.generateMatches(selectedClub.value.id, session.value.id)
    await loadMatches()
    activeTab.value = 'matches'
  } catch (error) {
    console.error('경기 생성 실패:', error)
  } finally {
    isGenerating.value = false
  }
}

async function generateAIMatches() {
  if (!selectedClub.value?.id || !session.value?.id) return

  isAIGenerating.value = true
  aiGenerateError.value = ''

  try {
    const response = await sessionsApi.generateAIMatches(
      selectedClub.value.id,
      session.value.id,
      {
        mode: aiGenerateForm.value.mode,
        match_duration_minutes: aiGenerateForm.value.match_duration_minutes,
        break_duration_minutes: aiGenerateForm.value.break_duration_minutes
      }
    )
    aiPreviewData.value = response.data
    showAIGenerateDialog.value = false
    showAIPreviewDialog.value = true
  } catch (error) {
    console.error('AI 경기 생성 실패:', error)
    aiGenerateError.value = error.response?.data?.detail || 'AI 경기 생성에 실패했습니다'
  } finally {
    isAIGenerating.value = false
  }
}

async function regenerateAIMatches() {
  showAIPreviewDialog.value = false
  showAIGenerateDialog.value = true
}

async function confirmAIMatches() {
  if (!selectedClub.value?.id || !session.value?.id || !aiPreviewData.value?.matches) return

  isConfirmingAI.value = true
  try {
    await sessionsApi.confirmAIMatches(
      selectedClub.value.id,
      session.value.id,
      aiPreviewData.value.matches
    )
    showAIPreviewDialog.value = false
    aiPreviewData.value = null
    await loadMatches()
    activeTab.value = 'matches'
  } catch (error) {
    console.error('경기 확정 실패:', error)
    alert(error.response?.data?.detail || '경기 확정에 실패했습니다')
  } finally {
    isConfirmingAI.value = false
  }
}

function openScoreDialog(match) {
  selectedMatch.value = match
  scoreForm.value = {
    score_a: match.score_a || 0,
    score_b: match.score_b || 0
  }
  showScoreDialog.value = true
}

async function saveScore() {
  if (!selectedClub.value?.id || !session.value?.id || !selectedMatch.value?.id) return

  isSavingScore.value = true
  try {
    // 백엔드는 /clubs/{club_id}/sessions/{session_id}/matches/{match_id} 엔드포인트 사용
    await sessionsApi.updateMatch(
      selectedClub.value.id,
      session.value.id,
      selectedMatch.value.id,
      {
        team_a_score: scoreForm.value.score_a,
        team_b_score: scoreForm.value.score_b
      }
    )
    await loadMatches()
    showScoreDialog.value = false
  } catch (error) {
    console.error('점수 저장 실패:', error)
  } finally {
    isSavingScore.value = false
  }
}

onMounted(() => {
  loadSession()
})
</script>

<style scoped>
.session-detail-page {
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

.session-header {
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

.session-info {
  flex: 1;
}

.session-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.session-title {
  font-size: 1.4rem;
  font-weight: 600;
  color: #1E293B;
}

.session-meta {
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

.session-tabs {
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

.participant-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.participant-card {
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 12px;
}

.participant-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.participant-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.participant-name {
  font-weight: 500;
  color: #1E293B;
}

.participant-gender {
  font-size: 0.8rem;
  color: #64748B;
}

.match-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.match-card {
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 16px;
}

.match-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.match-info {
  flex: 1;
}

.match-teams {
  display: flex;
  align-items: center;
  gap: 16px;
}

.team {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.team-a {
  text-align: right;
}

.team-b {
  text-align: left;
}

.team span {
  font-size: 0.9rem;
  color: #1E293B;
}

.match-score {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.5rem;
  font-weight: 700;
  color: #059669;
}

.match-score .divider {
  color: #94A3B8;
}

.member-select-list {
  max-height: 300px;
  overflow-y: auto;
}

.member-select-item {
  cursor: pointer;
  border-radius: 8px;
}

.member-select-item:hover {
  background: #F1F5F9;
}

.score-input-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.team-score {
  text-align: center;
}

.team-label {
  font-size: 0.85rem;
  color: #64748B;
  margin-bottom: 8px;
}

.score-input {
  width: 80px;
}

.score-divider {
  font-size: 2rem;
  font-weight: 700;
  color: #94A3B8;
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

/* 참가 섹션 */
.participation-section {
  border-top: 1px solid #E2E8F0;
  margin-top: 16px;
  padding-top: 16px;
}

.participation-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 0.9rem;
}

/* AI 미리보기 스타일 */
.ai-preview-match {
  border-bottom: 1px solid #E2E8F0;
}

.ai-preview-match:last-child {
  border-bottom: none;
}

.team-names {
  font-size: 0.9rem;
  flex: 1;
}

.vs-text {
  color: #94A3B8;
  font-weight: 600;
  font-size: 0.8rem;
}

.gap-3 {
  gap: 12px;
}
</style>
