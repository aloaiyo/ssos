<template>
  <div class="dashboard">
    <!-- 헤더 영역 -->
    <header class="dashboard-header">
      <div class="greeting">
        <h1 class="greeting-title">
          안녕하세요, <span class="text-primary">{{ user?.name || '회원' }}</span>님
        </h1>
        <p class="greeting-subtitle">오늘도 즐거운 테니스 되세요!</p>
      </div>
      <div class="header-actions">
        <v-btn
          v-if="!selectedClub"
          color="primary"
          size="large"
          prepend-icon="mdi-plus"
          @click="router.push({ name: 'club-create' })"
        >
          동호회 만들기
        </v-btn>
      </div>
    </header>

    <!-- 동호회가 없는 경우: 온보딩 -->
    <div v-if="!selectedClub" class="onboarding">
      <div class="bento-grid onboarding-grid">
        <!-- 동호회 생성 카드 -->
        <div class="bento-item bento-large glass-card hover-lift" @click="router.push({ name: 'club-create' })">
          <div class="card-icon-wrapper gradient-primary">
            <v-icon size="40">mdi-plus-circle-outline</v-icon>
          </div>
          <h3 class="card-title">새 동호회 만들기</h3>
          <p class="card-description">나만의 테니스 동호회를 만들고 회원들과 함께 운영해보세요</p>
          <div class="card-arrow">
            <v-icon>mdi-arrow-right</v-icon>
          </div>
        </div>

        <!-- 동호회 찾기 카드 -->
        <div class="bento-item bento-medium glass-card hover-lift" @click="router.push({ name: 'club-list' })">
          <div class="card-icon-wrapper gradient-secondary">
            <v-icon size="32">mdi-magnify</v-icon>
          </div>
          <h3 class="card-title">동호회 찾기</h3>
          <p class="card-description">활동 중인 동호회를 찾아 가입하세요</p>
        </div>

        <!-- 기능 소개 카드들 -->
        <div class="bento-item bento-small glass-card">
          <v-icon size="28" color="primary">mdi-shuffle-variant</v-icon>
          <span class="feature-label">자동 매칭</span>
        </div>

        <div class="bento-item bento-small glass-card">
          <v-icon size="28" color="secondary">mdi-trophy</v-icon>
          <span class="feature-label">랭킹 시스템</span>
        </div>

        <div class="bento-item bento-small glass-card">
          <v-icon size="28" color="accent">mdi-calendar-check</v-icon>
          <span class="feature-label">일정 관리</span>
        </div>
      </div>
    </div>

    <!-- 동호회가 있는 경우: 대시보드 -->
    <div v-else class="dashboard-content">
      <!-- Bento Grid 레이아웃 -->
      <div class="bento-grid">
        <!-- 클럽 정보 카드 (Large) -->
        <div class="bento-item bento-hero glass-card-primary">
          <div class="hero-content">
            <div class="club-badge">
              <v-icon size="24">mdi-tennis</v-icon>
            </div>
            <h2 class="club-name">{{ selectedClub.name }}</h2>
            <p class="club-description">{{ selectedClub.description || '우리 동호회에 오신 것을 환영합니다!' }}</p>
          </div>
          <div class="hero-stats">
            <div class="hero-stat">
              <span class="stat-value">{{ stats.totalMembers }}</span>
              <span class="stat-label">회원</span>
            </div>
            <div class="hero-stat">
              <span class="stat-value">{{ stats.totalSessions }}</span>
              <span class="stat-label">세션</span>
            </div>
            <div class="hero-stat">
              <span class="stat-value">{{ stats.totalMatches }}</span>
              <span class="stat-label">경기</span>
            </div>
          </div>
        </div>

        <!-- 내 순위 카드 -->
        <div class="bento-item bento-tall glass-card hover-lift">
          <div class="card-header">
            <span class="card-label">내 순위</span>
            <v-icon size="20" color="primary">mdi-trophy</v-icon>
          </div>
          <div class="rank-display">
            <span class="rank-number">{{ stats.myRanking || '-' }}</span>
            <span class="rank-suffix">위</span>
          </div>
          <div class="rank-details">
            <div class="rank-detail">
              <span class="detail-value text-success">{{ myStats?.wins || 0 }}승</span>
            </div>
            <div class="rank-detail">
              <span class="detail-value text-error">{{ myStats?.losses || 0 }}패</span>
            </div>
          </div>
          <v-btn
            variant="tonal"
            color="primary"
            size="small"
            block
            class="mt-auto"
            :to="{ name: 'ranking-list' }"
          >
            전체 순위 보기
          </v-btn>
        </div>

        <!-- 다가오는 일정 카드 -->
        <div class="bento-item bento-wide glass-card">
          <div class="card-header">
            <span class="card-label">다가오는 일정</span>
            <v-btn
              variant="text"
              size="small"
              color="primary"
              append-icon="mdi-chevron-right"
              @click="router.push({ name: 'session-list' })"
            >
              전체보기
            </v-btn>
          </div>
          <div v-if="upcomingSessions.length > 0" class="schedule-list">
            <div
              v-for="session in upcomingSessions.slice(0, 3)"
              :key="session.id"
              class="schedule-item"
            >
              <div class="schedule-date">
                <span class="date-day">{{ formatDay(session.date) }}</span>
                <span class="date-month">{{ formatMonth(session.date) }}</span>
              </div>
              <div class="schedule-info">
                <span class="schedule-time">{{ session.start_time }} - {{ session.end_time }}</span>
                <span class="schedule-meta">
                  <v-icon size="14">mdi-account-group</v-icon>
                  {{ session.participant_count }}명
                  <v-icon size="14" class="ml-2">mdi-tennis-ball</v-icon>
                  {{ session.num_courts }}코트
                </span>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">
            <v-icon size="48" color="grey-light">mdi-calendar-blank</v-icon>
            <p>예정된 일정이 없습니다</p>
          </div>
        </div>

        <!-- 빠른 액션 카드들 -->
        <div
          class="bento-item bento-action glass-card hover-lift"
          @click="router.push({ name: 'club-manage' })"
        >
          <div class="action-icon gradient-primary">
            <v-icon>mdi-cog</v-icon>
          </div>
          <span class="action-label">동호회 관리</span>
        </div>

        <div
          class="bento-item bento-action glass-card hover-lift"
          @click="router.push({ name: 'member-list' })"
        >
          <div class="action-icon gradient-secondary">
            <v-icon>mdi-account-group</v-icon>
          </div>
          <span class="action-label">회원 목록</span>
        </div>

        <div
          v-if="isAdmin"
          class="bento-item bento-action glass-card hover-lift"
          @click="router.push({ name: 'member-manage' })"
        >
          <div class="action-icon gradient-accent">
            <v-icon>mdi-account-cog</v-icon>
          </div>
          <span class="action-label">회원 관리</span>
        </div>

        <!-- Top 5 랭킹 카드 -->
        <div class="bento-item bento-ranking glass-card">
          <div class="card-header">
            <span class="card-label">Top 5</span>
            <v-icon size="20" color="warning">mdi-podium</v-icon>
          </div>
          <div v-if="rankings.length > 0" class="ranking-list">
            <div
              v-for="(rank, index) in rankings.slice(0, 5)"
              :key="rank.id"
              class="ranking-item"
            >
              <div class="ranking-position" :class="`position-${index + 1}`">
                {{ index + 1 }}
              </div>
              <div class="ranking-name">{{ rank.member_name }}</div>
              <div class="ranking-points">{{ rank.points }}점</div>
            </div>
          </div>
          <div v-else class="empty-state small">
            <p>아직 순위 데이터가 없습니다</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 신규 동호회 생성 안내 팝업 -->
    <v-dialog v-model="showWelcomeDialog" max-width="500" persistent>
      <v-card class="welcome-dialog" rounded="xl">
        <div class="welcome-header">
          <div class="welcome-icon">
            <v-icon size="48" color="white">mdi-party-popper</v-icon>
          </div>
          <h2 class="welcome-title">동호회가 생성되었습니다!</h2>
          <p class="welcome-club-name">{{ newClubName }}</p>
        </div>

        <v-card-text class="welcome-content">
          <h3 class="guide-title">시작하기 가이드</h3>
          <div class="guide-steps">
            <div class="guide-step">
              <div class="step-number">1</div>
              <div class="step-content">
                <strong>기본 정보 설정</strong>
                <p>동호회 관리에서 정기 활동 요일, 시간, 장소를 설정하세요</p>
              </div>
            </div>
            <div class="guide-step">
              <div class="step-number">2</div>
              <div class="step-content">
                <strong>회원 초대</strong>
                <p>동호회 회원들에게 가입 링크를 공유하세요</p>
              </div>
            </div>
            <div class="guide-step">
              <div class="step-number">3</div>
              <div class="step-content">
                <strong>일정 생성</strong>
                <p>첫 번째 활동 일정을 만들고 참가자를 모집하세요</p>
              </div>
            </div>
            <div class="guide-step">
              <div class="step-number">4</div>
              <div class="step-content">
                <strong>경기 매칭</strong>
                <p>참가자가 모이면 자동 매칭으로 공정한 경기를 진행하세요</p>
              </div>
            </div>
          </div>
        </v-card-text>

        <v-card-actions class="welcome-actions">
          <v-btn
            variant="tonal"
            @click="goToClubManage"
          >
            동호회 설정하기
          </v-btn>
          <v-spacer />
          <v-btn
            color="primary"
            @click="closeWelcomeDialog"
          >
            시작하기
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useClubStore } from '@/stores/club'
import { useMemberStore } from '@/stores/member'
import apiClient from '@/api'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const clubStore = useClubStore()
const memberStore = useMemberStore()

const { user, isAdmin } = storeToRefs(authStore)
const { selectedClub } = storeToRefs(clubStore)

// 신규 동호회 환영 팝업
const showWelcomeDialog = ref(false)
const newClubId = ref(null)
const newClubName = ref('')

function closeWelcomeDialog() {
  showWelcomeDialog.value = false
  // URL에서 쿼리 파라미터 제거
  router.replace({ name: 'home' })
}

function goToClubManage() {
  showWelcomeDialog.value = false
  router.push({ name: 'club-manage', params: { id: newClubId.value } })
}

// 통계 데이터
const stats = ref({
  totalMembers: 0,
  totalSessions: 0,
  totalMatches: 0,
  myRanking: null,
})

const myStats = ref(null)
const upcomingSessions = ref([])
const rankings = ref([])

// 날짜 포맷팅
function formatDay(dateString) {
  return new Date(dateString).getDate()
}

function formatMonth(dateString) {
  const months = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월']
  return months[new Date(dateString).getMonth()]
}

// 다가오는 일정 로드
async function loadUpcomingSessions() {
  if (!selectedClub.value) return

  try {
    const response = await apiClient.get(`/clubs/${selectedClub.value.id}/sessions`)
    upcomingSessions.value = response.data.slice(0, 5)
    stats.value.totalSessions = response.data.length
  } catch (error) {
    console.error('일정 로드 실패:', error)
  }
}

// 순위 로드
async function loadRankings() {
  if (!selectedClub.value) return

  try {
    const response = await apiClient.get(`/clubs/${selectedClub.value.id}/rankings`)
    rankings.value = response.data

    // 내 순위 찾기
    if (user.value) {
      const myRank = response.data.findIndex(r => r.user_id === user.value.id)
      if (myRank !== -1) {
        stats.value.myRanking = myRank + 1
        myStats.value = response.data[myRank]
      }
    }
  } catch (error) {
    console.error('순위 로드 실패:', error)
  }
}

// 사용자의 동호회 로드
async function loadUserClubs() {
  try {
    const response = await apiClient.get('/users/me/clubs')
    const userClubs = response.data

    if (userClubs.length > 0) {
      clubStore.clubs = userClubs

      const savedClubId = localStorage.getItem('selectedClubId')
      if (savedClubId && userClubs.find(c => c.id === parseInt(savedClubId))) {
        clubStore.selectClub(parseInt(savedClubId))
      } else {
        clubStore.selectClub(userClubs[0].id)
      }
    }
  } catch (error) {
    console.error('사용자 동호회 로드 실패:', error)
  }
}

// 컴포넌트 마운트 시 데이터 로드
onMounted(async () => {
  // 신규 동호회 생성 확인
  if (route.query.newClub) {
    newClubId.value = route.query.newClub
    newClubName.value = route.query.clubName || '새 동호회'
    showWelcomeDialog.value = true
  }

  await loadUserClubs()

  if (selectedClub.value) {
    try {
      await memberStore.fetchMembers(selectedClub.value.id)
      stats.value.totalMembers = memberStore.members.length

      await Promise.all([
        loadUpcomingSessions(),
        loadRankings()
      ])
    } catch (error) {
      console.error('데이터 로드 실패:', error)
    }
  }
})
</script>

<style scoped>
.dashboard {
  padding: 8px 16px 32px;
  max-width: 1400px;
  margin: 0 auto;
}

/* 헤더 */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  padding-top: 8px;
}

.greeting-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1E293B;
  margin-bottom: 4px;
}

.greeting-subtitle {
  font-size: 0.95rem;
  color: #64748B;
}

/* Bento Grid */
.bento-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.onboarding-grid {
  grid-template-columns: repeat(3, 1fr);
  max-width: 900px;
  margin: 0 auto;
}

/* Glass Card */
.glass-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 20px;
  padding: 24px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: default;
}

.glass-card-primary {
  background: linear-gradient(135deg, #10B981 0%, #059669 100%);
  border: none;
  color: white;
  border-radius: 24px;
  padding: 32px;
}

.hover-lift {
  cursor: pointer;
}

.hover-lift:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

/* Bento Item Sizes */
.bento-hero {
  grid-column: span 2;
  grid-row: span 2;
}

.bento-large {
  grid-column: span 2;
  grid-row: span 2;
}

.bento-tall {
  grid-column: span 1;
  grid-row: span 2;
  display: flex;
  flex-direction: column;
}

.bento-wide {
  grid-column: span 2;
  grid-row: span 1;
}

.bento-medium {
  grid-column: span 1;
  grid-row: span 1;
}

.bento-small {
  grid-column: span 1;
  grid-row: span 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 20px;
}

.bento-action {
  grid-column: span 1;
  grid-row: span 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 24px;
}

.bento-ranking {
  grid-column: span 1;
  grid-row: span 2;
}

/* Card Elements */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #64748B;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.card-icon-wrapper {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  color: white;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1E293B;
  margin-bottom: 8px;
}

.card-description {
  font-size: 0.9rem;
  color: #64748B;
  line-height: 1.5;
}

.card-arrow {
  position: absolute;
  bottom: 24px;
  right: 24px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(16, 185, 129, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #10B981;
}

.bento-large {
  position: relative;
}

/* Gradients */
.gradient-primary {
  background: linear-gradient(135deg, #10B981 0%, #059669 100%);
}

.gradient-secondary {
  background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
}

.gradient-accent {
  background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
}

/* Hero Card */
.hero-content {
  margin-bottom: 32px;
}

.club-badge {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.club-name {
  font-size: 1.75rem;
  font-weight: 700;
  margin-bottom: 8px;
}

.club-description {
  font-size: 0.95rem;
  opacity: 0.9;
}

.hero-stats {
  display: flex;
  gap: 32px;
}

.hero-stat {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 2rem;
  font-weight: 800;
}

.stat-label {
  font-size: 0.8rem;
  opacity: 0.8;
  text-transform: uppercase;
}

/* Rank Card */
.rank-display {
  text-align: center;
  margin: 24px 0;
}

.rank-number {
  font-size: 4rem;
  font-weight: 800;
  color: #10B981;
  line-height: 1;
}

.rank-suffix {
  font-size: 1.5rem;
  font-weight: 600;
  color: #64748B;
}

.rank-details {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-bottom: 16px;
}

.detail-value {
  font-size: 1rem;
  font-weight: 600;
}

/* Schedule List */
.schedule-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.schedule-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  background: #F8FAFC;
  border-radius: 12px;
}

.schedule-date {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 48px;
}

.date-day {
  font-size: 1.5rem;
  font-weight: 700;
  color: #10B981;
  line-height: 1;
}

.date-month {
  font-size: 0.75rem;
  color: #64748B;
}

.schedule-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.schedule-time {
  font-size: 0.95rem;
  font-weight: 600;
  color: #1E293B;
}

.schedule-meta {
  font-size: 0.8rem;
  color: #64748B;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* Action Card */
.action-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.action-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #1E293B;
}

/* Ranking List */
.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: #F8FAFC;
  border-radius: 10px;
}

.ranking-position {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  font-weight: 700;
  background: #E2E8F0;
  color: #64748B;
}

.ranking-position.position-1 {
  background: linear-gradient(135deg, #FCD34D 0%, #F59E0B 100%);
  color: white;
}

.ranking-position.position-2 {
  background: linear-gradient(135deg, #E2E8F0 0%, #CBD5E1 100%);
  color: #475569;
}

.ranking-position.position-3 {
  background: linear-gradient(135deg, #FDBA74 0%, #F97316 100%);
  color: white;
}

.ranking-name {
  flex: 1;
  font-size: 0.9rem;
  font-weight: 500;
  color: #1E293B;
}

.ranking-points {
  font-size: 0.85rem;
  font-weight: 600;
  color: #10B981;
}

/* Feature Label */
.feature-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #64748B;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px;
  color: #94A3B8;
  text-align: center;
}

.empty-state.small {
  padding: 16px;
}

.empty-state p {
  margin-top: 8px;
  font-size: 0.9rem;
}

/* Responsive */
@media (max-width: 1200px) {
  .bento-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .bento-hero {
    grid-column: span 2;
  }
}

@media (max-width: 900px) {
  .bento-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .bento-hero,
  .bento-wide {
    grid-column: span 2;
  }

  .bento-tall,
  .bento-ranking {
    grid-column: span 1;
    grid-row: span 1;
  }
}

@media (max-width: 600px) {
  .dashboard {
    padding: 8px 12px 24px;
  }

  .dashboard-header {
    flex-direction: column;
    gap: 16px;
  }

  .greeting-title {
    font-size: 1.5rem;
  }

  .bento-grid {
    grid-template-columns: 1fr;
  }

  .bento-hero,
  .bento-large,
  .bento-wide,
  .bento-tall,
  .bento-ranking {
    grid-column: span 1;
    grid-row: span 1;
  }

  .onboarding-grid {
    grid-template-columns: 1fr;
  }

  .hero-stats {
    flex-wrap: wrap;
    gap: 16px;
  }
}

/* Welcome Dialog */
.welcome-dialog {
  overflow: hidden;
}

.welcome-header {
  background: linear-gradient(135deg, #10B981 0%, #059669 100%);
  padding: 32px 24px;
  text-align: center;
  color: white;
}

.welcome-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}

.welcome-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 8px;
}

.welcome-club-name {
  font-size: 1.1rem;
  opacity: 0.9;
}

.welcome-content {
  padding: 24px !important;
}

.guide-title {
  font-size: 1rem;
  font-weight: 600;
  color: #1E293B;
  margin-bottom: 16px;
}

.guide-steps {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.guide-step {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.step-number {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, #10B981 0%, #059669 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  font-weight: 700;
  flex-shrink: 0;
}

.step-content strong {
  display: block;
  font-size: 0.95rem;
  color: #1E293B;
  margin-bottom: 2px;
}

.step-content p {
  font-size: 0.85rem;
  color: #64748B;
  margin: 0;
  line-height: 1.4;
}

.welcome-actions {
  padding: 16px 24px 24px !important;
}
</style>
