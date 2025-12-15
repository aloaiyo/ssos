<template>
  <div class="weekly-schedule-picker">
    <div class="section-header">
      <v-icon class="mr-2" size="20">mdi-calendar-clock</v-icon>
      <span>정기 활동 일정</span>
    </div>

    <!-- 요일 선택 칩 -->
    <div class="day-chips">
      <v-chip
        v-for="day in days"
        :key="day.value"
        :color="isSelected(day.value) ? 'primary' : undefined"
        :variant="isSelected(day.value) ? 'flat' : 'outlined'"
        class="day-chip"
        @click="toggleDay(day.value)"
      >
        {{ day.label }}
      </v-chip>
    </div>

    <!-- 선택된 요일별 시간 설정 -->
    <v-expand-transition>
      <div v-if="selectedDays.length > 0" class="schedule-cards">
        <TransitionGroup name="schedule-list">
          <div
            v-for="dayValue in sortedSelectedDays"
            :key="dayValue"
            class="schedule-card"
          >
            <div class="schedule-card-header">
              <v-chip color="primary" size="small" variant="tonal">
                {{ getDayLabel(dayValue) }}
              </v-chip>
              <v-btn
                icon
                size="x-small"
                variant="text"
                color="error"
                @click="removeDay(dayValue)"
              >
                <v-icon size="18">mdi-close</v-icon>
              </v-btn>
            </div>

            <div class="time-inputs">
              <v-text-field
                :model-value="getStartTime(dayValue)"
                type="time"
                label="시작"
                variant="outlined"
                density="compact"
                hide-details
                class="time-field"
                @update:model-value="updateStartTime(dayValue, $event)"
              />

              <v-icon class="time-separator" size="20" color="grey">mdi-arrow-right</v-icon>

              <v-text-field
                :model-value="getEndTime(dayValue)"
                type="time"
                label="종료"
                variant="outlined"
                density="compact"
                hide-details
                class="time-field"
                @update:model-value="updateEndTime(dayValue, $event)"
              />
            </div>
          </div>
        </TransitionGroup>
      </div>
    </v-expand-transition>

    <!-- 빠른 설정 -->
    <div v-if="selectedDays.length > 1" class="quick-actions">
      <v-btn
        size="small"
        variant="tonal"
        color="secondary"
        prepend-icon="mdi-content-copy"
        @click="applyFirstToAll"
      >
        첫 번째 시간을 모든 요일에 적용
      </v-btn>
    </div>

    <!-- 도움말 -->
    <div v-if="selectedDays.length === 0" class="helper-text">
      <v-icon size="16" color="grey" class="mr-1">mdi-information-outline</v-icon>
      정기 활동 요일을 선택해주세요
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['update:modelValue'])

const days = [
  { value: 0, label: '월' },
  { value: 1, label: '화' },
  { value: 2, label: '수' },
  { value: 3, label: '목' },
  { value: 4, label: '금' },
  { value: 5, label: '토' },
  { value: 6, label: '일' },
]

// 내부 스케줄 상태
const schedules = ref([])

// props에서 초기값 설정
watch(
  () => props.modelValue,
  (newValue) => {
    if (newValue && newValue.length > 0) {
      schedules.value = newValue.map((s) => ({
        day_of_week: s.day_of_week,
        start_time: s.start_time || '09:00',
        end_time: s.end_time || '12:00',
        is_active: s.is_active !== false,
      }))
    }
  },
  { immediate: true }
)

// 선택된 요일 목록
const selectedDays = computed(() => schedules.value.map((s) => s.day_of_week))

// 정렬된 요일 목록
const sortedSelectedDays = computed(() => [...selectedDays.value].sort((a, b) => a - b))

function isSelected(dayValue) {
  return selectedDays.value.includes(dayValue)
}

function getDayLabel(dayValue) {
  return days.find((d) => d.value === dayValue)?.label + '요일'
}

function toggleDay(dayValue) {
  if (isSelected(dayValue)) {
    removeDay(dayValue)
  } else {
    addDay(dayValue)
  }
}

function addDay(dayValue) {
  // 기본 시간 또는 마지막 추가된 요일의 시간 사용
  const lastSchedule = schedules.value[schedules.value.length - 1]
  schedules.value.push({
    day_of_week: dayValue,
    start_time: lastSchedule?.start_time || '09:00',
    end_time: lastSchedule?.end_time || '12:00',
    is_active: true,
  })
  emitUpdate()
}

function removeDay(dayValue) {
  schedules.value = schedules.value.filter((s) => s.day_of_week !== dayValue)
  emitUpdate()
}

function getStartTime(dayValue) {
  return schedules.value.find((s) => s.day_of_week === dayValue)?.start_time || '09:00'
}

function getEndTime(dayValue) {
  return schedules.value.find((s) => s.day_of_week === dayValue)?.end_time || '12:00'
}

function updateStartTime(dayValue, value) {
  const schedule = schedules.value.find((s) => s.day_of_week === dayValue)
  if (schedule) {
    schedule.start_time = value
    emitUpdate()
  }
}

function updateEndTime(dayValue, value) {
  const schedule = schedules.value.find((s) => s.day_of_week === dayValue)
  if (schedule) {
    schedule.end_time = value
    emitUpdate()
  }
}

function applyFirstToAll() {
  if (schedules.value.length === 0) return
  const first = schedules.value[0]
  schedules.value.forEach((s) => {
    s.start_time = first.start_time
    s.end_time = first.end_time
  })
  emitUpdate()
}

function emitUpdate() {
  emit('update:modelValue', [...schedules.value])
}
</script>

<style scoped>
.weekly-schedule-picker {
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.section-header {
  display: flex;
  align-items: center;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 16px;
}

.day-chips {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.day-chip {
  cursor: pointer;
  min-width: 44px;
  justify-content: center;
  transition: all 0.2s ease;
}

.day-chip:hover {
  transform: scale(1.05);
}

.schedule-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.schedule-card {
  background: white;
  border-radius: 10px;
  padding: 12px 16px;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
}

.schedule-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.schedule-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.time-inputs {
  display: flex;
  align-items: center;
  gap: 12px;
}

.time-field {
  flex: 1;
  min-width: 0;
}

.time-separator {
  flex-shrink: 0;
}

.quick-actions {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px dashed #e2e8f0;
}

.helper-text {
  display: flex;
  align-items: center;
  color: #94a3b8;
  font-size: 0.875rem;
}

/* 리스트 트랜지션 */
.schedule-list-enter-active,
.schedule-list-leave-active {
  transition: all 0.3s ease;
}

.schedule-list-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.schedule-list-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

.schedule-list-move {
  transition: transform 0.3s ease;
}

/* 반응형 */
@media (max-width: 600px) {
  .time-inputs {
    flex-wrap: wrap;
  }

  .time-field {
    min-width: 120px;
  }

  .time-separator {
    display: none;
  }
}
</style>
