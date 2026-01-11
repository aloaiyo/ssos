<template>
  <div class="club-info-tab">
    <v-card class="info-card" variant="flat">
      <v-card-title class="card-title d-flex align-center">
        <v-icon class="mr-2">mdi-information-outline</v-icon>
        동호회 기본 정보
        <v-spacer />
        <v-btn
          v-if="!isEditing"
          variant="tonal"
          color="primary"
          size="small"
          prepend-icon="mdi-pencil"
          @click="startEditing"
        >
          편집
        </v-btn>
        <template v-else>
          <v-btn
            variant="text"
            size="small"
            class="mr-2"
            @click="cancelEditing"
          >
            취소
          </v-btn>
          <v-btn
            variant="tonal"
            color="primary"
            size="small"
            prepend-icon="mdi-content-save"
            :loading="isLoading"
            @click="handleSubmit"
          >
            저장
          </v-btn>
        </template>
      </v-card-title>

      <v-card-text>
        <!-- 읽기 모드 -->
        <div v-if="!isEditing" class="view-mode">
          <div class="info-grid">
            <div class="info-item">
              <div class="info-label">
                <v-icon size="18" class="mr-1">mdi-tennis</v-icon>
                동호회 이름
              </div>
              <div class="info-value">{{ club?.name || '-' }}</div>
            </div>

            <div class="info-item">
              <div class="info-label">
                <v-icon size="18" class="mr-1">mdi-map-marker</v-icon>
                활동 장소
              </div>
              <div class="info-value">{{ club?.location || '-' }}</div>
            </div>

            <div class="info-item full-width">
              <div class="info-label">
                <v-icon size="18" class="mr-1">mdi-text</v-icon>
                동호회 소개
              </div>
              <div class="info-value description">{{ club?.description || '-' }}</div>
            </div>

            <div class="info-item">
              <div class="info-label">
                <v-icon size="18" class="mr-1">mdi-tennis-ball</v-icon>
                기본 코트 수
              </div>
              <div class="info-value">{{ club?.default_num_courts ? `${club.default_num_courts}면` : '-' }}</div>
            </div>

            <div class="info-item">
              <div class="info-label">
                <v-icon size="18" class="mr-1">mdi-timer-outline</v-icon>
                경기 시간
              </div>
              <div class="info-value">{{ club?.default_match_duration ? `${club.default_match_duration}분` : '-' }}</div>
            </div>
          </div>

          <!-- 가입 설정 (읽기 모드) -->
          <v-divider class="my-6" />
          <div class="join-settings-view">
            <div class="info-label mb-3">
              <v-icon size="18" class="mr-1">mdi-account-plus</v-icon>
              가입 설정
            </div>
            <div class="d-flex flex-wrap gap-3">
              <v-chip
                :color="club?.is_join_allowed ? 'success' : 'error'"
                variant="tonal"
              >
                <v-icon start size="16">{{ club?.is_join_allowed ? 'mdi-check-circle' : 'mdi-close-circle' }}</v-icon>
                {{ club?.is_join_allowed ? '가입 가능' : '가입 불가' }}
              </v-chip>
              <v-chip
                v-if="club?.is_join_allowed"
                :color="club?.requires_approval ? 'warning' : 'info'"
                variant="tonal"
              >
                <v-icon start size="16">{{ club?.requires_approval ? 'mdi-account-clock' : 'mdi-account-check' }}</v-icon>
                {{ club?.requires_approval ? '승인 필요' : '바로 가입' }}
              </v-chip>
            </div>
          </div>

          <!-- 정기 활동 일정 (읽기 모드) -->
          <v-divider class="my-6" />
          <div class="schedule-view">
            <div class="info-label mb-3">
              <v-icon size="18" class="mr-1">mdi-calendar-clock</v-icon>
              정기 활동 일정
            </div>
            <div v-if="club?.schedules?.length > 0" class="schedule-chips">
              <v-chip
                v-for="schedule in sortedSchedules"
                :key="schedule.day_of_week"
                color="primary"
                variant="tonal"
                class="schedule-chip"
              >
                <span class="day-label">{{ getDayLabel(schedule.day_of_week) }}</span>
                <span class="time-label">{{ formatTime(schedule.start_time) }} - {{ formatTime(schedule.end_time) }}</span>
              </v-chip>
            </div>
            <div v-else class="text-medium-emphasis">
              등록된 정기 활동 일정이 없습니다.
            </div>
          </div>
        </div>

        <!-- 편집 모드 -->
        <v-form v-else ref="formRef" v-model="valid" @submit.prevent="handleSubmit">
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="form.name"
                label="동호회 이름"
                :rules="[rules.required]"
                variant="outlined"
                density="comfortable"
                prepend-inner-icon="mdi-tennis"
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="form.location"
                label="활동 장소"
                variant="outlined"
                density="comfortable"
                prepend-inner-icon="mdi-map-marker"
                placeholder="예: OO테니스장"
              />
            </v-col>
            <v-col cols="12">
              <v-textarea
                v-model="form.description"
                label="동호회 소개"
                variant="outlined"
                density="comfortable"
                rows="3"
                placeholder="동호회를 소개해주세요"
              />
            </v-col>
            <v-col cols="6" md="3">
              <v-text-field
                v-model.number="form.default_num_courts"
                label="기본 코트 수"
                type="number"
                min="1"
                max="20"
                variant="outlined"
                density="comfortable"
                prepend-inner-icon="mdi-tennis-ball"
              />
            </v-col>
            <v-col cols="6" md="3">
              <v-select
                v-model="form.default_match_duration"
                :items="matchDurationOptions"
                label="경기 시간"
                variant="outlined"
                density="comfortable"
              />
            </v-col>
          </v-row>

          <!-- 가입 설정 (편집 모드) -->
          <v-divider class="my-6" />
          <div class="join-settings-edit">
            <div class="info-label mb-4">
              <v-icon size="18" class="mr-1">mdi-account-plus</v-icon>
              가입 설정
            </div>
            <v-row>
              <v-col cols="12" md="6">
                <v-switch
                  v-model="form.is_join_allowed"
                  color="success"
                  hide-details
                  inset
                >
                  <template v-slot:label>
                    <div class="switch-label">
                      <v-icon size="20" class="mr-2">
                        {{ form.is_join_allowed ? 'mdi-account-plus' : 'mdi-account-off' }}
                      </v-icon>
                      <div>
                        <div class="font-weight-medium">가입 허용</div>
                        <div class="text-caption text-medium-emphasis">
                          {{ form.is_join_allowed ? '새로운 회원이 가입할 수 있습니다' : '신규 가입이 차단됩니다' }}
                        </div>
                      </div>
                    </div>
                  </template>
                </v-switch>
              </v-col>
              <v-col cols="12" md="6">
                <v-switch
                  v-model="form.requires_approval"
                  :disabled="!form.is_join_allowed"
                  color="warning"
                  hide-details
                  inset
                >
                  <template v-slot:label>
                    <div class="switch-label" :class="{ 'text-disabled': !form.is_join_allowed }">
                      <v-icon size="20" class="mr-2">
                        {{ form.requires_approval ? 'mdi-account-clock' : 'mdi-account-check' }}
                      </v-icon>
                      <div>
                        <div class="font-weight-medium">관리자 승인 필요</div>
                        <div class="text-caption text-medium-emphasis">
                          {{ form.requires_approval ? '관리자가 승인해야 가입됩니다' : '신청 즉시 가입됩니다' }}
                        </div>
                      </div>
                    </div>
                  </template>
                </v-switch>
              </v-col>
            </v-row>
          </div>

          <v-divider class="my-6" />

          <!-- 정기 활동 일정 (편집 모드) -->
          <WeeklySchedulePicker v-model="form.schedules" />
        </v-form>
      </v-card-text>
    </v-card>

    <!-- 위험 구역 -->
    <v-card class="danger-zone" variant="flat">
      <v-card-title class="card-title text-error">
        <v-icon class="mr-2" color="error">mdi-alert-outline</v-icon>
        위험 구역
      </v-card-title>
      <v-card-text>
        <div class="danger-item">
          <div>
            <h4>동호회 삭제</h4>
            <p class="text-medium-emphasis">
              동호회를 삭제하면 모든 회원, 일정, 경기 기록이 영구적으로 삭제됩니다.
            </p>
          </div>
          <v-btn
            color="error"
            variant="outlined"
            @click="showDeleteDialog = true"
          >
            동호회 삭제
          </v-btn>
        </div>
      </v-card-text>
    </v-card>

    <!-- 삭제 확인 다이얼로그 -->
    <v-dialog v-model="showDeleteDialog" max-width="400">
      <v-card>
        <v-card-title class="text-error">동호회 삭제</v-card-title>
        <v-card-text>
          <p class="mb-4">
            정말로 <strong>{{ club?.name }}</strong> 동호회를 삭제하시겠습니까?
          </p>
          <p class="text-error text-caption">
            이 작업은 되돌릴 수 없습니다. 모든 데이터가 영구적으로 삭제됩니다.
          </p>
          <v-text-field
            v-model="deleteConfirmText"
            label="동호회 이름을 입력하여 확인"
            variant="outlined"
            density="comfortable"
            class="mt-4"
            :placeholder="club?.name"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showDeleteDialog = false">취소</v-btn>
          <v-btn
            color="error"
            :disabled="deleteConfirmText !== club?.name"
            :loading="isDeleting"
            @click="handleDelete"
          >
            삭제
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useClubStore } from '@/stores/club'
import apiClient from '@/api'
import WeeklySchedulePicker from '@/components/common/WeeklySchedulePicker.vue'

const props = defineProps({
  club: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['update'])

const router = useRouter()
const clubStore = useClubStore()

const formRef = ref(null)
const valid = ref(false)
const isLoading = ref(false)
const isDeleting = ref(false)
const isEditing = ref(false)
const showDeleteDialog = ref(false)
const deleteConfirmText = ref('')

const form = ref({
  name: '',
  description: '',
  location: '',
  default_num_courts: null,
  default_match_duration: 30,
  is_join_allowed: true,
  requires_approval: false,
  schedules: [],
})

const rules = {
  required: (v) => !!v || '필수 입력 항목입니다',
}

const matchDurationOptions = [
  { title: '20분', value: 20 },
  { title: '25분', value: 25 },
  { title: '30분', value: 30 },
  { title: '40분', value: 40 },
  { title: '50분', value: 50 },
  { title: '60분', value: 60 },
]

const days = ['월', '화', '수', '목', '금', '토', '일']

const sortedSchedules = computed(() => {
  if (!props.club?.schedules) return []
  return [...props.club.schedules].sort((a, b) => a.day_of_week - b.day_of_week)
})

function getDayLabel(dayValue) {
  return days[dayValue] + '요일'
}

function formatTime(timeValue) {
  if (!timeValue) return ''
  if (typeof timeValue === 'string') {
    return timeValue.substring(0, 5)
  }
  return timeValue
}

function syncFormFromClub() {
  if (props.club) {
    form.value = {
      name: props.club.name || '',
      description: props.club.description || '',
      location: props.club.location || '',
      default_num_courts: props.club.default_num_courts,
      default_match_duration: props.club.default_match_duration || 30,
      is_join_allowed: props.club.is_join_allowed ?? true,
      requires_approval: props.club.requires_approval ?? false,
      schedules: (props.club.schedules || []).map(s => ({
        day_of_week: s.day_of_week,
        start_time: formatTime(s.start_time),
        end_time: formatTime(s.end_time),
        is_active: s.is_active,
      })),
    }
  }
}

watch(() => props.club, () => {
  syncFormFromClub()
}, { immediate: true })

function startEditing() {
  syncFormFromClub()
  isEditing.value = true
}

function cancelEditing() {
  syncFormFromClub()
  isEditing.value = false
}

async function handleSubmit() {
  if (!valid.value || !props.club) return

  isLoading.value = true
  try {
    const response = await apiClient.put(`/clubs/${props.club.id}`, form.value)
    emit('update', response.data)
    isEditing.value = false
  } catch (error) {
    console.error('저장 실패:', error)
    alert('저장에 실패했습니다.')
  } finally {
    isLoading.value = false
  }
}

async function handleDelete() {
  if (deleteConfirmText.value !== props.club?.name) return

  isDeleting.value = true
  try {
    await clubStore.deleteClub(props.club.id)
    showDeleteDialog.value = false
    router.push({ name: 'home' })
  } catch (error) {
    console.error('삭제 실패:', error)
    alert('삭제에 실패했습니다.')
  } finally {
    isDeleting.value = false
  }
}
</script>

<style scoped>
.club-info-tab {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.info-card,
.danger-zone {
  border-radius: 16px;
  border: 1px solid #E2E8F0;
}

.card-title {
  font-size: 1.1rem;
  font-weight: 600;
  padding: 20px 24px;
  border-bottom: 1px solid #E2E8F0;
}

/* 읽기 모드 스타일 */
.view-mode {
  padding: 8px 0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.info-label {
  display: flex;
  align-items: center;
  font-size: 0.85rem;
  font-weight: 500;
  color: #64748B;
}

.info-value {
  font-size: 1rem;
  font-weight: 500;
  color: #1E293B;
  padding-left: 26px;
}

.info-value.description {
  white-space: pre-wrap;
  line-height: 1.6;
}

/* 스케줄 읽기 모드 */
.schedule-view {
  padding-top: 8px;
}

.schedule-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.schedule-chip {
  height: auto !important;
  padding: 8px 14px !important;
}

.schedule-chip .day-label {
  font-weight: 600;
  margin-right: 8px;
}

.schedule-chip .time-label {
  font-weight: 400;
  opacity: 0.9;
}

/* 위험 구역 */
.danger-zone {
  border-color: #FEE2E2;
  background: #FEF2F2;
}

.danger-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
}

.danger-item h4 {
  font-size: 0.95rem;
  font-weight: 600;
  color: #1E293B;
  margin-bottom: 4px;
}

.danger-item p {
  font-size: 0.85rem;
  margin: 0;
}

/* 가입 설정 스위치 */
.switch-label {
  display: flex;
  align-items: flex-start;
}

.switch-label.text-disabled {
  opacity: 0.5;
}

.gap-3 {
  gap: 12px;
}

/* 반응형 */
@media (max-width: 600px) {
  .info-grid {
    grid-template-columns: 1fr;
  }

  .danger-item {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
