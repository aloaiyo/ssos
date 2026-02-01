<template>
  <div class="match-upload-page">
    <!-- 헤더 -->
    <div class="page-header">
      <v-btn icon variant="text" @click="goBack" class="back-btn">
        <v-icon>mdi-arrow-left</v-icon>
      </v-btn>
      <h1 class="page-title">경기 결과 업로드</h1>
    </div>

    <!-- 스텝 인디케이터 -->
    <v-stepper v-model="currentStep" alt-labels class="stepper">
      <v-stepper-header>
        <v-stepper-item :value="1" title="이미지 업로드" :complete="currentStep > 1"></v-stepper-item>
        <v-divider></v-divider>
        <v-stepper-item :value="2" title="시즌/세션 선택" :complete="currentStep > 2"></v-stepper-item>
        <v-divider></v-divider>
        <v-stepper-item :value="3" title="선수 매핑" :complete="currentStep > 3"></v-stepper-item>
        <v-divider></v-divider>
        <v-stepper-item :value="4" title="결과 확인" :complete="currentStep > 4"></v-stepper-item>
      </v-stepper-header>
    </v-stepper>

    <!-- Step 1: 이미지 업로드 -->
    <div v-if="currentStep === 1" class="step-content">
      <v-card class="upload-card" variant="flat">
        <div
          class="upload-area"
          :class="{ 'dragging': isDragging }"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="handleDrop"
          @click="triggerFileInput"
        >
          <input
            ref="fileInput"
            type="file"
            accept="image/*"
            style="display: none"
            @change="handleFileSelect"
          />

          <template v-if="!selectedFile">
            <v-icon size="64" color="grey-lighten-1">mdi-cloud-upload-outline</v-icon>
            <p class="upload-text mt-4">이미지를 드래그하거나 클릭하여 업로드</p>
            <p class="upload-hint">JPEG, PNG, GIF, WebP (최대 10MB)</p>
          </template>

          <template v-else>
            <img :src="previewUrl" class="preview-image" />
            <p class="file-name mt-2">{{ selectedFile.name }}</p>
            <v-btn variant="text" color="error" size="small" @click.stop="clearFile">
              <v-icon start>mdi-close</v-icon>
              삭제
            </v-btn>
          </template>
        </div>
      </v-card>

      <div class="step-actions">
        <v-btn
          color="primary"
          size="large"
          :loading="isExtracting"
          :disabled="!selectedFile"
          @click="extractResults"
        >
          <v-icon start>mdi-text-recognition</v-icon>
          결과 추출하기
        </v-btn>
      </div>
    </div>

    <!-- Step 2: 시즌/세션 선택 -->
    <div v-if="currentStep === 2" class="step-content">
      <!-- 시즌 선택 -->
      <v-card class="selection-card" variant="flat">
        <v-card-title>시즌 선택</v-card-title>
        <v-card-text>
          <v-radio-group v-model="seasonOption" hide-details>
            <v-radio label="시즌 없이 저장" value="none"></v-radio>
            <v-radio label="기존 시즌 선택" value="existing"></v-radio>
            <v-radio label="새 시즌 생성" value="new"></v-radio>
          </v-radio-group>

          <v-select
            v-if="seasonOption === 'existing'"
            v-model="selectedSeasonId"
            :items="seasons"
            item-title="name"
            item-value="id"
            label="시즌 선택"
            variant="outlined"
            density="compact"
            class="mt-3"
            :loading="isLoadingSeasons"
          >
            <template v-slot:item="{ item, props }">
              <v-list-item v-bind="props">
                <template v-slot:subtitle>
                  {{ formatDate(item.raw.start_date) }} ~ {{ formatDate(item.raw.end_date) }}
                </template>
              </v-list-item>
            </template>
          </v-select>

          <!-- 새 시즌 생성 폼 -->
          <div v-if="seasonOption === 'new'" class="new-season-form mt-4">
            <v-text-field
              v-model="newSeason.name"
              label="시즌 이름"
              variant="outlined"
              density="compact"
              placeholder="예: 2026년 상반기 시즌"
              :rules="[v => !!v || '시즌 이름을 입력해주세요']"
            ></v-text-field>

            <v-row>
              <v-col cols="6">
                <v-text-field
                  v-model="newSeason.start_date"
                  label="시작일"
                  type="date"
                  variant="outlined"
                  density="compact"
                  :rules="[v => !!v || '시작일을 선택해주세요']"
                ></v-text-field>
              </v-col>
              <v-col cols="6">
                <v-text-field
                  v-model="newSeason.end_date"
                  label="종료일"
                  type="date"
                  variant="outlined"
                  density="compact"
                  :rules="[v => !!v || '종료일을 선택해주세요']"
                ></v-text-field>
              </v-col>
            </v-row>

            <v-textarea
              v-model="newSeason.description"
              label="설명 (선택)"
              variant="outlined"
              density="compact"
              rows="2"
            ></v-textarea>
          </div>
        </v-card-text>
      </v-card>

      <!-- 세션 선택 -->
      <v-card class="selection-card mt-4" variant="flat">
        <v-card-title>세션 선택</v-card-title>
        <v-card-text>
          <v-radio-group v-model="sessionOption" hide-details>
            <v-radio label="새 세션 생성" value="new"></v-radio>
            <v-radio label="기존 세션에 추가" value="existing"></v-radio>
          </v-radio-group>

          <!-- 새 세션 생성 폼 -->
          <div v-if="sessionOption === 'new'" class="new-session-form mt-4">
            <v-text-field
              v-model="newSession.title"
              label="세션 제목"
              variant="outlined"
              density="compact"
              placeholder="예: 1주차 리그전"
            ></v-text-field>

            <v-row>
              <v-col cols="6">
                <v-text-field
                  v-model="newSession.date"
                  label="날짜"
                  type="date"
                  variant="outlined"
                  density="compact"
                  :rules="[v => !!v || '날짜를 선택해주세요']"
                ></v-text-field>
              </v-col>
              <v-col cols="6">
                <v-text-field
                  v-model="newSession.location"
                  label="장소"
                  variant="outlined"
                  density="compact"
                ></v-text-field>
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="6">
                <v-select
                  v-model="newSession.start_time"
                  :items="timeOptions"
                  label="시작 시간"
                  variant="outlined"
                  density="compact"
                ></v-select>
              </v-col>
              <v-col cols="6">
                <v-select
                  v-model="newSession.end_time"
                  :items="timeOptions"
                  label="종료 시간"
                  variant="outlined"
                  density="compact"
                ></v-select>
              </v-col>
            </v-row>
          </div>

          <!-- 기존 세션 선택 -->
          <v-select
            v-if="sessionOption === 'existing'"
            v-model="selectedSessionId"
            :items="sessions"
            item-title="displayName"
            item-value="id"
            label="세션 선택"
            variant="outlined"
            density="compact"
            class="mt-3"
            :loading="isLoadingSessions"
          >
            <template v-slot:item="{ item, props }">
              <v-list-item v-bind="props">
                <template v-slot:subtitle>
                  {{ formatDate(item.raw.date) }} | {{ item.raw.location || '장소 미정' }}
                </template>
              </v-list-item>
            </template>
          </v-select>
        </v-card-text>
      </v-card>

      <div class="step-actions">
        <v-btn variant="text" @click="currentStep = 1">이전</v-btn>
        <v-btn
          color="primary"
          size="large"
          :disabled="!isStep2Valid"
          @click="goToPlayerMapping"
        >
          다음
        </v-btn>
      </div>
    </div>

    <!-- Step 3: 선수 매핑 확인 -->
    <div v-if="currentStep === 3" class="step-content">
      <v-card class="mapping-card" variant="flat">
        <v-card-title>
          <v-icon class="mr-2">mdi-account-check</v-icon>
          선수 매핑 확인
        </v-card-title>
        <v-card-subtitle>
          추출된 선수 이름을 클럽 회원 또는 게스트와 매핑합니다
        </v-card-subtitle>
        <v-card-text>
          <v-list>
            <v-list-item
              v-for="(mapping, idx) in playerMappings"
              :key="idx"
              class="mapping-item"
            >
              <template v-slot:prepend>
                <v-avatar
                  :color="mapping.matched ? 'success' : 'warning'"
                  size="40"
                >
                  <v-icon color="white">
                    {{ mapping.matched ? 'mdi-check' : 'mdi-account-question' }}
                  </v-icon>
                </v-avatar>
              </template>

              <v-list-item-title class="font-weight-medium">
                {{ mapping.extractedName }}
              </v-list-item-title>

              <template v-slot:append>
                <div class="mapping-select">
                  <v-autocomplete
                    v-model="mapping.selectedId"
                    :items="mappingOptions"
                    item-title="displayName"
                    item-value="id"
                    label="매핑 대상"
                    variant="outlined"
                    density="compact"
                    hide-details
                    clearable
                    style="min-width: 250px;"
                    @update:model-value="updateMapping(idx, $event)"
                  >
                    <template v-slot:item="{ item, props }">
                      <v-list-item v-bind="props">
                        <template v-slot:prepend>
                          <v-chip size="x-small" :color="item.raw.type === 'member' ? 'primary' : 'teal'" class="mr-2">
                            {{ item.raw.type === 'member' ? '회원' : '게스트' }}
                          </v-chip>
                        </template>
                      </v-list-item>
                    </template>
                    <template v-slot:no-data>
                      <v-list-item>
                        <v-list-item-title>매핑할 대상이 없습니다</v-list-item-title>
                      </v-list-item>
                      <v-divider class="my-2"></v-divider>
                      <v-list-item @click="openGuestDialog(mapping)">
                        <template v-slot:prepend>
                          <v-icon color="primary">mdi-plus</v-icon>
                        </template>
                        <v-list-item-title class="text-primary">새 게스트 추가</v-list-item-title>
                      </v-list-item>
                    </template>
                    <template v-slot:append-item>
                      <v-divider class="my-2"></v-divider>
                      <v-list-item @click="openGuestDialog(mapping)">
                        <template v-slot:prepend>
                          <v-icon color="primary">mdi-plus</v-icon>
                        </template>
                        <v-list-item-title class="text-primary">새 게스트 추가</v-list-item-title>
                      </v-list-item>
                    </template>
                  </v-autocomplete>
                </div>
              </template>
            </v-list-item>
          </v-list>

          <v-alert
            v-if="unmappedCount > 0"
            type="warning"
            variant="tonal"
            class="mt-4"
          >
            {{ unmappedCount }}명의 선수가 아직 매핑되지 않았습니다.
            매핑하지 않으면 해당 선수는 경기 기록에서 제외됩니다.
          </v-alert>
        </v-card-text>
      </v-card>

      <div class="step-actions">
        <v-btn variant="text" @click="currentStep = 2">이전</v-btn>
        <v-btn
          color="primary"
          size="large"
          @click="currentStep = 4"
        >
          다음
        </v-btn>
      </div>
    </div>

    <!-- Step 4: 결과 확인 및 저장 -->
    <div v-if="currentStep === 4" class="step-content">
      <v-card class="result-card" variant="flat">
        <v-card-title>추출된 경기 결과</v-card-title>
        <v-card-subtitle v-if="extractedResult?.date || extractedResult?.location">
          {{ extractedResult.date ? formatDate(extractedResult.date) : '' }}
          {{ extractedResult.location ? `| ${extractedResult.location}` : '' }}
        </v-card-subtitle>
        <v-card-text>
          <div v-if="extractedResult?.matches?.length === 0" class="empty-state">
            <p>추출된 경기가 없습니다</p>
          </div>

          <div v-else class="match-list">
            <v-card
              v-for="(match, idx) in extractedResult.matches"
              :key="idx"
              class="match-item"
              variant="outlined"
            >
              <div class="match-header">
                <v-chip size="small" :color="getMatchTypeColor(match.match_type)">
                  {{ getMatchTypeLabel(match.match_type) }}
                </v-chip>
                <span class="court-info">코트 {{ match.court_number }}</span>
                <v-btn icon size="x-small" variant="text" @click="removeMatch(idx)">
                  <v-icon size="16">mdi-close</v-icon>
                </v-btn>
              </div>

              <div class="match-teams">
                <div class="team team-a">
                  <div class="team-players">
                    <v-text-field
                      v-for="(player, pIdx) in match.team_a.players"
                      :key="pIdx"
                      v-model="match.team_a.players[pIdx]"
                      density="compact"
                      variant="underlined"
                      hide-details
                      class="player-input"
                    ></v-text-field>
                  </div>
                  <v-text-field
                    v-model.number="match.team_a.score"
                    type="number"
                    min="0"
                    density="compact"
                    variant="outlined"
                    hide-details
                    class="score-input"
                  ></v-text-field>
                </div>

                <span class="vs">VS</span>

                <div class="team team-b">
                  <v-text-field
                    v-model.number="match.team_b.score"
                    type="number"
                    min="0"
                    density="compact"
                    variant="outlined"
                    hide-details
                    class="score-input"
                  ></v-text-field>
                  <div class="team-players">
                    <v-text-field
                      v-for="(player, pIdx) in match.team_b.players"
                      :key="pIdx"
                      v-model="match.team_b.players[pIdx]"
                      density="compact"
                      variant="underlined"
                      hide-details
                      class="player-input"
                    ></v-text-field>
                  </div>
                </div>
              </div>
            </v-card>
          </div>

          <v-btn variant="outlined" color="primary" class="mt-4" @click="addMatch">
            <v-icon start>mdi-plus</v-icon>
            경기 추가
          </v-btn>
        </v-card-text>
      </v-card>

      <div class="step-actions">
        <v-btn variant="text" @click="currentStep = 3">이전</v-btn>
        <v-btn
          color="primary"
          size="large"
          :loading="isSaving"
          :disabled="extractedResult?.matches?.length === 0"
          @click="saveResults"
        >
          <v-icon start>mdi-content-save</v-icon>
          저장하기
        </v-btn>
      </div>
    </div>

    <!-- 게스트 생성 다이얼로그 -->
    <v-dialog v-model="showGuestDialog" max-width="400">
      <v-card>
        <v-card-title>새 게스트 추가</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="newGuest.name"
            label="이름"
            variant="outlined"
            density="compact"
            class="mb-3"
          ></v-text-field>

          <v-radio-group v-model="newGuest.gender" inline hide-details class="mb-3">
            <v-radio label="남성" value="male"></v-radio>
            <v-radio label="여성" value="female"></v-radio>
          </v-radio-group>

          <v-text-field
            v-model="newGuest.phone"
            label="연락처 (선택)"
            variant="outlined"
            density="compact"
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="showGuestDialog = false">취소</v-btn>
          <v-btn
            color="primary"
            :loading="isCreatingGuest"
            :disabled="!newGuest.name || !newGuest.gender"
            @click="createGuest"
          >
            추가
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 에러/성공 스낵바 -->
    <v-snackbar v-model="showSnackbar" :color="snackbarColor" timeout="5000">
      {{ snackbarMessage }}
    </v-snackbar>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useClubStore } from '@/stores/club'
import ocrApi from '@/api/ocr'
import seasonsApi from '@/api/seasons'
import sessionsApi from '@/api/sessions'
import membersApi from '@/api/members'
import * as guestsApi from '@/api/guests'
import { getMatchTypeColor, getMatchTypeLabel } from '@/utils/constants'

const router = useRouter()
const clubStore = useClubStore()

const selectedClub = computed(() => clubStore.selectedClub)

// 스텝 관리
const currentStep = ref(1)

// Step 1: 이미지 업로드
const fileInput = ref(null)
const selectedFile = ref(null)
const previewUrl = ref('')
const isDragging = ref(false)
const isExtracting = ref(false)
const extractedResult = ref(null)

// Step 2: 시즌/세션 선택
const seasonOption = ref('none')
const selectedSeasonId = ref(null)
const seasons = ref([])
const isLoadingSeasons = ref(false)

const sessionOption = ref('new')
const selectedSessionId = ref(null)
const sessions = ref([])
const isLoadingSessions = ref(false)

const newSession = ref({
  title: '',
  date: new Date().toISOString().split('T')[0],
  location: '',
  start_time: '09:00',
  end_time: '12:00'
})

// 새 시즌 생성
const newSeason = ref({
  name: getDefaultSeasonName(),
  start_date: getDefaultSeasonDates().start,
  end_date: getDefaultSeasonDates().end,
  description: ''
})

function getDefaultSeasonName() {
  const now = new Date()
  const year = now.getFullYear()
  const half = now.getMonth() < 6 ? '상반기' : '하반기'
  return `${year}년 ${half} 시즌`
}

function getDefaultSeasonDates() {
  const now = new Date()
  const year = now.getFullYear()
  if (now.getMonth() < 6) {
    return {
      start: `${year}-01-01`,
      end: `${year}-06-30`
    }
  } else {
    return {
      start: `${year}-07-01`,
      end: `${year}-12-31`
    }
  }
}

const timeOptions = [
  '06:00', '07:00', '08:00', '09:00', '10:00', '11:00', '12:00',
  '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00',
  '20:00', '21:00', '22:00'
]

// Step 3: 선수 매핑
const members = ref([])
const guests = ref([])
const playerMappings = ref([])
const isLoadingMembers = ref(false)

// 게스트 생성
const showGuestDialog = ref(false)
const isCreatingGuest = ref(false)
const currentMappingForGuest = ref(null)
const newGuest = ref({
  name: '',
  gender: '',
  phone: ''
})

// Step 4: 저장
const isSaving = ref(false)

// 스낵바
const showSnackbar = ref(false)
const snackbarMessage = ref('')
const snackbarColor = ref('success')

const isStep2Valid = computed(() => {
  // 시즌 유효성 검사
  if (seasonOption.value === 'new') {
    if (!newSeason.value.name || !newSeason.value.start_date || !newSeason.value.end_date) {
      return false
    }
  } else if (seasonOption.value === 'existing') {
    if (!selectedSeasonId.value) {
      return false
    }
  }

  // 세션 유효성 검사
  if (sessionOption.value === 'new') {
    return !!newSession.value.date
  } else {
    return !!selectedSessionId.value
  }
})

const mappingOptions = computed(() => {
  const options = []

  // 회원 목록
  members.value.forEach(member => {
    options.push({
      id: `member_${member.id}`,
      displayName: member.user_name || member.nickname || `회원 #${member.id}`,
      type: 'member',
      memberId: member.id
    })
  })

  // 게스트 목록
  guests.value.forEach(guest => {
    options.push({
      id: `guest_${guest.id}`,
      displayName: `${guest.name} (게스트)`,
      type: 'guest',
      guestId: guest.id
    })
  })

  return options
})

const unmappedCount = computed(() => {
  return playerMappings.value.filter(m => !m.matched).length
})

function goBack() {
  router.back()
}

function triggerFileInput() {
  fileInput.value?.click()
}

function handleFileSelect(event) {
  const file = event.target.files?.[0]
  if (file) {
    setFile(file)
  }
}

function handleDrop(event) {
  isDragging.value = false
  const file = event.dataTransfer.files?.[0]
  if (file && file.type.startsWith('image/')) {
    setFile(file)
  }
}

function setFile(file) {
  selectedFile.value = file
  previewUrl.value = URL.createObjectURL(file)
}

function clearFile() {
  selectedFile.value = null
  previewUrl.value = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

async function extractResults() {
  if (!selectedClub.value?.id || !selectedFile.value) return

  isExtracting.value = true
  try {
    const response = await ocrApi.extractMatchResults(selectedClub.value.id, selectedFile.value)
    extractedResult.value = response.data

    // 추출된 날짜가 있으면 새 세션 날짜에 설정
    if (extractedResult.value.date) {
      newSession.value.date = extractedResult.value.date
    }
    if (extractedResult.value.location) {
      newSession.value.location = extractedResult.value.location
    }

    currentStep.value = 2
  } catch (error) {
    console.error('OCR 추출 실패:', error)
    snackbarMessage.value = error.response?.data?.detail || '이미지 분석에 실패했습니다'
    snackbarColor.value = 'error'
    showSnackbar.value = true
  } finally {
    isExtracting.value = false
  }
}

async function loadSeasons() {
  if (!selectedClub.value?.id) return

  isLoadingSeasons.value = true
  try {
    const response = await seasonsApi.getSeasons(selectedClub.value.id)
    seasons.value = response.data || []
  } catch (error) {
    console.error('시즌 목록 조회 실패:', error)
  } finally {
    isLoadingSeasons.value = false
  }
}

async function loadSessions() {
  if (!selectedClub.value?.id) return

  isLoadingSessions.value = true
  try {
    const params = {}
    if (seasonOption.value === 'existing' && selectedSeasonId.value) {
      params.season_id = selectedSeasonId.value
    }
    const response = await sessionsApi.getSessions(selectedClub.value.id, params)
    sessions.value = (response.data || []).map(s => ({
      ...s,
      displayName: s.title || `세션 #${s.id} (${formatDate(s.date)})`
    }))
  } catch (error) {
    console.error('세션 목록 조회 실패:', error)
  } finally {
    isLoadingSessions.value = false
  }
}

async function loadMembers() {
  if (!selectedClub.value?.id) return

  isLoadingMembers.value = true
  try {
    const response = await membersApi.getMembers(selectedClub.value.id)
    members.value = (response.data || []).filter(m => m.status === 'active')
  } catch (error) {
    console.error('회원 목록 조회 실패:', error)
  } finally {
    isLoadingMembers.value = false
  }
}

async function loadGuests() {
  if (!selectedClub.value?.id) return

  try {
    const response = await guestsApi.getGuests(selectedClub.value.id)
    guests.value = response.data || []
  } catch (error) {
    console.error('게스트 목록 조회 실패:', error)
  }
}

function extractUniquePlayerNames() {
  const names = new Set()
  if (!extractedResult.value?.matches) return []

  extractedResult.value.matches.forEach(match => {
    match.team_a.players.forEach(p => {
      if (p && p.trim()) names.add(p.trim())
    })
    match.team_b.players.forEach(p => {
      if (p && p.trim()) names.add(p.trim())
    })
  })

  return Array.from(names)
}

function findBestMatch(playerName) {
  if (!playerName) return null

  const normalizedName = playerName.replace(/\s/g, '').toLowerCase()

  // 회원에서 찾기
  for (const member of members.value) {
    const memberName = (member.user_name || member.nickname || '').replace(/\s/g, '').toLowerCase()
    if (memberName === normalizedName || memberName.includes(normalizedName) || normalizedName.includes(memberName)) {
      return {
        id: `member_${member.id}`,
        type: 'member',
        memberId: member.id
      }
    }
  }

  // 게스트에서 찾기
  for (const guest of guests.value) {
    const guestName = guest.name.replace(/\s/g, '').toLowerCase()
    if (guestName === normalizedName || guestName.includes(normalizedName) || normalizedName.includes(guestName)) {
      return {
        id: `guest_${guest.id}`,
        type: 'guest',
        guestId: guest.id
      }
    }
  }

  return null
}

function initializePlayerMappings() {
  const uniqueNames = extractUniquePlayerNames()
  playerMappings.value = uniqueNames.map(name => {
    const match = findBestMatch(name)
    return {
      extractedName: name,
      selectedId: match?.id || null,
      memberId: match?.memberId || null,
      guestId: match?.guestId || null,
      matched: !!match
    }
  })
}

async function goToPlayerMapping() {
  await Promise.all([loadMembers(), loadGuests()])
  initializePlayerMappings()
  currentStep.value = 3
}

function updateMapping(idx, selectedId) {
  if (!selectedId) {
    playerMappings.value[idx].memberId = null
    playerMappings.value[idx].guestId = null
    playerMappings.value[idx].matched = false
    return
  }

  const option = mappingOptions.value.find(o => o.id === selectedId)
  if (option) {
    playerMappings.value[idx].memberId = option.memberId || null
    playerMappings.value[idx].guestId = option.guestId || null
    playerMappings.value[idx].matched = true
  }
}

function openGuestDialog(mapping) {
  currentMappingForGuest.value = mapping
  newGuest.value = {
    name: mapping.extractedName,
    gender: '',
    phone: ''
  }
  showGuestDialog.value = true
}

async function createGuest() {
  if (!selectedClub.value?.id || !newGuest.value.name || !newGuest.value.gender) return

  isCreatingGuest.value = true
  try {
    const response = await guestsApi.createGuest(selectedClub.value.id, {
      name: newGuest.value.name,
      gender: newGuest.value.gender,
      phone: newGuest.value.phone || null
    })

    const createdGuest = response.data
    guests.value.push(createdGuest)

    // 현재 매핑 업데이트
    if (currentMappingForGuest.value) {
      const idx = playerMappings.value.findIndex(
        m => m.extractedName === currentMappingForGuest.value.extractedName
      )
      if (idx >= 0) {
        playerMappings.value[idx].selectedId = `guest_${createdGuest.id}`
        playerMappings.value[idx].guestId = createdGuest.id
        playerMappings.value[idx].memberId = null
        playerMappings.value[idx].matched = true
      }
    }

    showGuestDialog.value = false
    snackbarMessage.value = '게스트가 추가되었습니다'
    snackbarColor.value = 'success'
    showSnackbar.value = true
  } catch (error) {
    console.error('게스트 생성 실패:', error)
    snackbarMessage.value = error.response?.data?.detail || '게스트 생성에 실패했습니다'
    snackbarColor.value = 'error'
    showSnackbar.value = true
  } finally {
    isCreatingGuest.value = false
  }
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`
}

// getMatchTypeColor, getMatchTypeLabel → imported from @/utils/constants

function removeMatch(index) {
  extractedResult.value.matches.splice(index, 1)
}

function addMatch() {
  extractedResult.value.matches.push({
    match_type: 'mens_doubles',
    court_number: extractedResult.value.matches.length + 1,
    team_a: { players: ['', ''], score: 0 },
    team_b: { players: ['', ''], score: 0 }
  })
}

async function saveResults() {
  if (!selectedClub.value?.id) return

  isSaving.value = true
  try {
    const data = {
      matches: extractedResult.value.matches,
      create_new_session: sessionOption.value === 'new'
    }

    // 시즌 관련 데이터
    if (seasonOption.value === 'new') {
      data.create_new_season = true
      data.new_season_name = newSeason.value.name
      data.new_season_start_date = newSeason.value.start_date
      data.new_season_end_date = newSeason.value.end_date
      data.new_season_description = newSeason.value.description
    } else if (seasonOption.value === 'existing' && selectedSeasonId.value) {
      data.season_id = selectedSeasonId.value
    }

    // 세션 관련 데이터
    if (sessionOption.value === 'new') {
      data.session_title = newSession.value.title
      data.session_date = newSession.value.date
      data.session_start_time = newSession.value.start_time + ':00'
      data.session_end_time = newSession.value.end_time + ':00'
      data.session_location = newSession.value.location
    } else {
      data.session_id = selectedSessionId.value
    }

    // 플레이어 매핑 데이터
    data.player_mappings = playerMappings.value.map(m => ({
      extracted_name: m.extractedName,
      member_id: m.memberId,
      guest_id: m.guestId
    }))

    const response = await ocrApi.saveMatchResults(selectedClub.value.id, data)

    snackbarMessage.value = response.data.message || '경기 결과가 저장되었습니다'
    snackbarColor.value = 'success'
    showSnackbar.value = true

    // 새 시즌이 생성되었으면 알림
    if (response.data.created_season_id) {
      setTimeout(() => {
        snackbarMessage.value = '새 시즌이 생성되었습니다'
        snackbarColor.value = 'info'
        showSnackbar.value = true
      }, 1500)
    }

    // 매칭되지 않은 선수가 있으면 알림
    if (response.data.unmatched_players?.length > 0) {
      setTimeout(() => {
        snackbarMessage.value = `일부 선수를 찾지 못했습니다: ${response.data.unmatched_players.join(', ')}`
        snackbarColor.value = 'warning'
        showSnackbar.value = true
      }, 2500)
    }

    // 세션 상세로 이동
    setTimeout(() => {
      router.push({ name: 'session-detail', params: { sessionId: response.data.session_id } })
    }, 2000)
  } catch (error) {
    console.error('저장 실패:', error)
    snackbarMessage.value = error.response?.data?.detail || '저장에 실패했습니다'
    snackbarColor.value = 'error'
    showSnackbar.value = true
  } finally {
    isSaving.value = false
  }
}

// 시즌 선택 변경 시 세션 목록 다시 로드
watch(selectedSeasonId, () => {
  if (sessionOption.value === 'existing') {
    loadSessions()
  }
})

watch(seasonOption, () => {
  if (seasonOption.value === 'existing') {
    loadSessions()
  }
})

onMounted(() => {
  loadSeasons()
  loadSessions()
})
</script>

<style scoped>
.match-upload-page {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
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

.stepper {
  background: transparent;
  margin-bottom: 24px;
}

/* 모바일에서 스텝 인디케이터 반응형 처리 */
@media (max-width: 600px) {
  .stepper :deep(.v-stepper-header) {
    flex-wrap: nowrap;
    overflow-x: auto;
    padding: 8px 0;
  }

  .stepper :deep(.v-stepper-item) {
    flex: 0 0 auto;
    min-width: 70px;
    padding: 0 4px;
  }

  .stepper :deep(.v-stepper-item__title) {
    font-size: 0.65rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 60px;
  }

  .stepper :deep(.v-divider) {
    min-width: 12px;
    flex: 0 0 12px;
  }
}

.step-content {
  min-height: 400px;
}

.upload-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  border: 1px solid #E2E8F0;
}

.upload-area {
  border: 2px dashed #CBD5E1;
  border-radius: 12px;
  padding: 48px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.upload-area:hover {
  border-color: #10B981;
  background: rgba(16, 185, 129, 0.05);
}

.upload-area.dragging {
  border-color: #10B981;
  background: rgba(16, 185, 129, 0.1);
}

.upload-text {
  font-size: 1rem;
  color: #475569;
}

.upload-hint {
  font-size: 0.85rem;
  color: #94A3B8;
  margin-top: 8px;
}

.preview-image {
  max-width: 100%;
  max-height: 300px;
  border-radius: 8px;
}

.file-name {
  font-size: 0.9rem;
  color: #64748B;
}

.step-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 24px;
}

.selection-card {
  background: white;
  border-radius: 16px;
  border: 1px solid #E2E8F0;
}

.new-session-form {
  padding-top: 8px;
}

.result-card {
  background: white;
  border-radius: 16px;
  border: 1px solid #E2E8F0;
}

.match-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.match-item {
  padding: 16px;
  border-radius: 12px;
}

.match-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.court-info {
  flex: 1;
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

.team-players {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.team-a .team-players {
  text-align: right;
}

.player-input {
  max-width: 120px;
}

.score-input {
  width: 60px;
}

.vs {
  font-size: 0.8rem;
  font-weight: 600;
  color: #94A3B8;
  padding: 0 8px;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #64748B;
}

.new-season-form {
  padding-top: 8px;
}

.mapping-card {
  background: white;
  border-radius: 16px;
  border: 1px solid #E2E8F0;
}

.mapping-item {
  border-bottom: 1px solid #E2E8F0;
  padding: 16px;
}

.mapping-item:last-child {
  border-bottom: none;
}

.mapping-select {
  display: flex;
  align-items: center;
}
</style>
