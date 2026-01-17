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
        <v-stepper-item :value="3" title="결과 확인" :complete="currentStep > 3"></v-stepper-item>
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
          @click="currentStep = 3"
        >
          다음
        </v-btn>
      </div>
    </div>

    <!-- Step 3: 결과 확인 및 저장 -->
    <div v-if="currentStep === 3" class="step-content">
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
        <v-btn variant="text" @click="currentStep = 2">이전</v-btn>
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

const timeOptions = [
  '06:00', '07:00', '08:00', '09:00', '10:00', '11:00', '12:00',
  '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00',
  '20:00', '21:00', '22:00'
]

// Step 3: 저장
const isSaving = ref(false)

// 스낵바
const showSnackbar = ref(false)
const snackbarMessage = ref('')
const snackbarColor = ref('success')

const isStep2Valid = computed(() => {
  if (sessionOption.value === 'new') {
    return !!newSession.value.date
  } else {
    return !!selectedSessionId.value
  }
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

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`
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

    if (seasonOption.value === 'existing' && selectedSeasonId.value) {
      data.season_id = selectedSeasonId.value
    }

    if (sessionOption.value === 'new') {
      data.session_title = newSession.value.title
      data.session_date = newSession.value.date
      data.session_start_time = newSession.value.start_time + ':00'
      data.session_end_time = newSession.value.end_time + ':00'
      data.session_location = newSession.value.location
      if (seasonOption.value === 'existing' && selectedSeasonId.value) {
        data.season_id = selectedSeasonId.value
      }
    } else {
      data.session_id = selectedSessionId.value
    }

    const response = await ocrApi.saveMatchResults(selectedClub.value.id, data)

    snackbarMessage.value = response.data.message || '경기 결과가 저장되었습니다'
    snackbarColor.value = 'success'
    showSnackbar.value = true

    // 매칭되지 않은 선수가 있으면 알림
    if (response.data.unmatched_players?.length > 0) {
      setTimeout(() => {
        snackbarMessage.value = `일부 선수를 찾지 못했습니다: ${response.data.unmatched_players.join(', ')}`
        snackbarColor.value = 'warning'
        showSnackbar.value = true
      }, 2000)
    }

    // 세션 상세로 이동
    setTimeout(() => {
      router.push({ name: 'session-detail', params: { sessionId: response.data.session_id } })
    }, 1500)
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
</style>
