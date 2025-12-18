<template>
  <div class="session-calendar-page">
    <!-- 헤더 -->
    <div class="page-header">
      <h1 class="page-title">일정</h1>
      <div class="header-actions">
        <v-btn color="primary" variant="flat" @click="goToToday">
          오늘
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
          <div v-if="day.sessions.length > 0" class="session-dots">
            <span v-for="(session, i) in day.sessions.slice(0, 3)" :key="i" class="session-dot" :class="getSessionStatusClass(session)"></span>
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
      </v-card-text>
    </v-card>

    <!-- 로딩 -->
    <v-overlay v-model="isLoading" class="align-center justify-center" contained>
      <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
    </v-overlay>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useClubStore } from '@/stores/club'
import apiClient from '@/api'

const clubStore = useClubStore()
const selectedClub = computed(() => clubStore.selectedClub)

const isLoading = ref(false)
const sessions = ref([])
const currentDate = ref(new Date())
const selectedDay = ref(null)

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
  return date.toISOString().split('T')[0]
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
  selectedDay.value = day
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

watch(selectedClub, () => {
  loadSessions()
})

watch(currentDate, () => {
  // 월 변경 시 오늘 날짜 선택 해제
  selectedDay.value = null
})

onMounted(() => {
  loadSessions()
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
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
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

.session-dots {
  display: flex;
  gap: 2px;
  margin-top: 4px;
}

.session-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #059669;
}

.session-dot.status-scheduled {
  background: #059669;
}

.session-dot.status-in-progress {
  background: #F59E0B;
}

.session-dot.status-completed {
  background: #10B981;
}

.session-dot.status-cancelled {
  background: #9CA3AF;
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

@media (max-width: 600px) {
  .session-calendar-page {
    padding: 12px;
  }

  .calendar-day {
    padding: 4px;
  }

  .day-number {
    font-size: 0.8rem;
  }

  .session-dot {
    width: 4px;
    height: 4px;
  }
}
</style>
