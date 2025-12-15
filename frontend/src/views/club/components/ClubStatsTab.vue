<template>
  <div class="club-stats-tab">
    <!-- 요약 카드들 -->
    <v-row>
      <v-col cols="12" sm="6" md="3">
        <v-card class="stat-card" variant="flat">
          <v-card-text>
            <div class="stat-icon primary">
              <v-icon>mdi-account-group</v-icon>
            </div>
            <div class="stat-value">{{ stats.totalMembers }}</div>
            <div class="stat-label">총 회원 수</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card class="stat-card" variant="flat">
          <v-card-text>
            <div class="stat-icon success">
              <v-icon>mdi-calendar-check</v-icon>
            </div>
            <div class="stat-value">{{ stats.totalSessions }}</div>
            <div class="stat-label">총 세션 수</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card class="stat-card" variant="flat">
          <v-card-text>
            <div class="stat-icon warning">
              <v-icon>mdi-tennis</v-icon>
            </div>
            <div class="stat-value">{{ stats.totalMatches }}</div>
            <div class="stat-label">총 경기 수</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card class="stat-card" variant="flat">
          <v-card-text>
            <div class="stat-icon info">
              <v-icon>mdi-trophy</v-icon>
            </div>
            <div class="stat-value">{{ stats.averageWinRate }}%</div>
            <div class="stat-label">평균 승률</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 회원 분포 -->
    <v-row>
      <v-col cols="12" md="6">
        <v-card class="section-card" variant="flat">
          <v-card-title class="card-title">
            <v-icon class="mr-2">mdi-chart-pie</v-icon>
            회원 성별 분포
          </v-card-title>
          <v-card-text>
            <div class="distribution-bars">
              <div class="distribution-item">
                <div class="distribution-label">
                  <v-icon size="18" color="blue" class="mr-2">mdi-gender-male</v-icon>
                  남성
                </div>
                <div class="distribution-bar-wrapper">
                  <div
                    class="distribution-bar male"
                    :style="{ width: genderDistribution.malePercent + '%' }"
                  ></div>
                </div>
                <div class="distribution-value">
                  {{ genderDistribution.male }}명 ({{ genderDistribution.malePercent }}%)
                </div>
              </div>
              <div class="distribution-item">
                <div class="distribution-label">
                  <v-icon size="18" color="pink" class="mr-2">mdi-gender-female</v-icon>
                  여성
                </div>
                <div class="distribution-bar-wrapper">
                  <div
                    class="distribution-bar female"
                    :style="{ width: genderDistribution.femalePercent + '%' }"
                  ></div>
                </div>
                <div class="distribution-value">
                  {{ genderDistribution.female }}명 ({{ genderDistribution.femalePercent }}%)
                </div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6">
        <v-card class="section-card" variant="flat">
          <v-card-title class="card-title">
            <v-icon class="mr-2">mdi-chart-bar</v-icon>
            역할 분포
          </v-card-title>
          <v-card-text>
            <div class="distribution-bars">
              <div class="distribution-item">
                <div class="distribution-label">매니저</div>
                <div class="distribution-bar-wrapper">
                  <div
                    class="distribution-bar primary"
                    :style="{ width: roleDistribution.managerPercent + '%' }"
                  ></div>
                </div>
                <div class="distribution-value">{{ roleDistribution.manager }}명</div>
              </div>
              <div class="distribution-item">
                <div class="distribution-label">일반 회원</div>
                <div class="distribution-bar-wrapper">
                  <div
                    class="distribution-bar grey"
                    :style="{ width: roleDistribution.memberPercent + '%' }"
                  ></div>
                </div>
                <div class="distribution-value">{{ roleDistribution.member }}명</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 최근 활동 회원 -->
    <v-card class="section-card" variant="flat">
      <v-card-title class="card-title">
        <v-icon class="mr-2">mdi-trophy-outline</v-icon>
        랭킹 Top 10
      </v-card-title>
      <v-card-text>
        <v-data-table
          :headers="rankingHeaders"
          :items="rankings"
          :loading="isLoading"
          density="comfortable"
          class="ranking-table"
        >
          <template v-slot:item.rank="{ index }">
            <div class="rank-badge" :class="`rank-${index + 1}`">
              {{ index + 1 }}
            </div>
          </template>
          <template v-slot:item.win_rate="{ item }">
            <v-progress-linear
              :model-value="item.win_rate"
              :color="getWinRateColor(item.win_rate)"
              height="20"
              rounded
            >
              <template v-slot:default>
                <span class="text-caption font-weight-bold">{{ item.win_rate }}%</span>
              </template>
            </v-progress-linear>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <!-- 최근 활동 -->
    <v-card class="section-card" variant="flat">
      <v-card-title class="card-title">
        <v-icon class="mr-2">mdi-history</v-icon>
        최근 활동
      </v-card-title>
      <v-card-text>
        <v-timeline density="compact" side="end">
          <v-timeline-item
            v-for="activity in recentActivities"
            :key="activity.id"
            :dot-color="activity.color"
            size="small"
          >
            <div class="activity-item">
              <div class="activity-title">{{ activity.title }}</div>
              <div class="activity-date">{{ activity.date }}</div>
            </div>
          </v-timeline-item>
        </v-timeline>
        <div v-if="recentActivities.length === 0" class="text-center text-medium-emphasis py-4">
          최근 활동이 없습니다.
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import apiClient from '@/api'

const props = defineProps({
  clubId: {
    type: Number,
    required: true,
  },
})

const isLoading = ref(false)
const members = ref([])
const rankings = ref([])
const sessions = ref([])

const stats = ref({
  totalMembers: 0,
  totalSessions: 0,
  totalMatches: 0,
  averageWinRate: 0,
})

const genderDistribution = computed(() => {
  const male = members.value.filter(m => m.gender === 'male').length
  const female = members.value.filter(m => m.gender === 'female').length
  const total = male + female || 1

  return {
    male,
    female,
    malePercent: Math.round((male / total) * 100),
    femalePercent: Math.round((female / total) * 100),
  }
})

const roleDistribution = computed(() => {
  const manager = members.value.filter(m => m.role === 'manager').length
  const member = members.value.filter(m => m.role === 'member').length
  const total = manager + member || 1

  return {
    manager,
    member,
    managerPercent: Math.round((manager / total) * 100),
    memberPercent: Math.round((member / total) * 100),
  }
})

const recentActivities = computed(() => {
  const activities = []

  // 최근 세션들을 활동으로 변환
  sessions.value.slice(0, 5).forEach(session => {
    activities.push({
      id: `session-${session.id}`,
      title: `세션 진행: ${session.date}`,
      date: formatDate(session.created_at),
      color: 'primary',
    })
  })

  return activities
})

const rankingHeaders = [
  { title: '순위', key: 'rank', sortable: false, width: '80px' },
  { title: '이름', key: 'member_name', sortable: false },
  { title: '경기 수', key: 'total_matches', sortable: true },
  { title: '승', key: 'wins', sortable: true },
  { title: '패', key: 'losses', sortable: true },
  { title: '승률', key: 'win_rate', sortable: true, width: '150px' },
  { title: '점수', key: 'points', sortable: true },
]

function formatDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

function getWinRateColor(rate) {
  if (rate >= 70) return 'success'
  if (rate >= 50) return 'info'
  if (rate >= 30) return 'warning'
  return 'error'
}

async function loadData() {
  isLoading.value = true
  try {
    const [membersRes, rankingsRes, sessionsRes] = await Promise.all([
      apiClient.get(`/clubs/${props.clubId}/members`),
      apiClient.get(`/clubs/${props.clubId}/rankings`),
      apiClient.get(`/clubs/${props.clubId}/sessions`),
    ])

    members.value = membersRes.data
    rankings.value = rankingsRes.data.slice(0, 10).map(r => ({
      ...r,
      win_rate: r.total_matches > 0 ? Math.round((r.wins / r.total_matches) * 100) : 0,
    }))
    sessions.value = sessionsRes.data

    // 통계 계산
    stats.value.totalMembers = members.value.length
    stats.value.totalSessions = sessions.value.length
    stats.value.totalMatches = rankings.value.reduce((sum, r) => sum + (r.total_matches || 0), 0)

    const totalWinRate = rankings.value.reduce((sum, r) => sum + (r.win_rate || 0), 0)
    stats.value.averageWinRate = rankings.value.length > 0
      ? Math.round(totalWinRate / rankings.value.length)
      : 0
  } catch (error) {
    console.error('데이터 로드 실패:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.club-stats-tab {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.stat-card {
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  text-align: center;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
  color: white;
}

.stat-icon.primary {
  background: linear-gradient(135deg, #10B981 0%, #059669 100%);
}

.stat-icon.success {
  background: linear-gradient(135deg, #22C55E 0%, #16A34A 100%);
}

.stat-icon.warning {
  background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
}

.stat-icon.info {
  background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #1E293B;
}

.stat-label {
  font-size: 0.85rem;
  color: #64748B;
}

.section-card {
  border: 1px solid #E2E8F0;
  border-radius: 16px;
}

.card-title {
  display: flex;
  align-items: center;
  font-size: 1rem;
  font-weight: 600;
  padding: 16px 20px;
  border-bottom: 1px solid #E2E8F0;
}

.distribution-bars {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.distribution-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.distribution-label {
  width: 100px;
  font-size: 0.9rem;
  color: #64748B;
  display: flex;
  align-items: center;
}

.distribution-bar-wrapper {
  flex: 1;
  height: 24px;
  background: #F1F5F9;
  border-radius: 12px;
  overflow: hidden;
}

.distribution-bar {
  height: 100%;
  border-radius: 12px;
  transition: width 0.5s ease;
}

.distribution-bar.male {
  background: linear-gradient(90deg, #3B82F6 0%, #60A5FA 100%);
}

.distribution-bar.female {
  background: linear-gradient(90deg, #EC4899 0%, #F472B6 100%);
}

.distribution-bar.primary {
  background: linear-gradient(90deg, #10B981 0%, #34D399 100%);
}

.distribution-bar.secondary {
  background: linear-gradient(90deg, #6366F1 0%, #818CF8 100%);
}

.distribution-bar.grey {
  background: linear-gradient(90deg, #94A3B8 0%, #CBD5E1 100%);
}

.distribution-value {
  width: 120px;
  text-align: right;
  font-size: 0.85rem;
  font-weight: 500;
  color: #1E293B;
}

.rank-badge {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 700;
  background: #E2E8F0;
  color: #64748B;
}

.rank-badge.rank-1 {
  background: linear-gradient(135deg, #FCD34D 0%, #F59E0B 100%);
  color: white;
}

.rank-badge.rank-2 {
  background: linear-gradient(135deg, #E2E8F0 0%, #CBD5E1 100%);
  color: #475569;
}

.rank-badge.rank-3 {
  background: linear-gradient(135deg, #FDBA74 0%, #F97316 100%);
  color: white;
}

.activity-item {
  padding: 8px 0;
}

.activity-title {
  font-size: 0.9rem;
  color: #1E293B;
}

.activity-date {
  font-size: 0.75rem;
  color: #94A3B8;
}

.ranking-table {
  border: 1px solid #E2E8F0;
  border-radius: 8px;
}
</style>
