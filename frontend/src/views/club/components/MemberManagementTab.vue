<template>
  <div class="member-management-tab">
    <!-- 헤더 -->
    <div class="tab-header">
      <h2 class="tab-title">회원 관리</h2>
      <div class="header-stats">
        <v-chip color="primary" variant="tonal" size="small">
          전체 {{ allMembers.length }}명
        </v-chip>
        <v-chip v-if="pendingMembers.length > 0" color="warning" variant="tonal" size="small">
          승인 대기 {{ pendingMembers.length }}명
        </v-chip>
      </div>
    </div>

    <!-- 가입 요청 섹션 -->
    <v-card v-if="pendingMembers.length > 0" class="pending-card" variant="flat">
      <v-card-title class="card-title warning">
        <v-icon class="mr-2">mdi-account-clock</v-icon>
        가입 요청
        <v-chip color="warning" size="x-small" class="ml-2">{{ pendingMembers.length }}</v-chip>
      </v-card-title>
      <v-card-text class="pa-0">
        <v-list>
          <v-list-item
            v-for="member in pendingMembers"
            :key="member.id"
            class="pending-item"
          >
            <template v-slot:prepend>
              <v-avatar :color="member.gender === 'male' ? 'blue' : 'pink'" size="40">
                <span class="text-white font-weight-bold">
                  {{ getInitial(member.user_name) }}
                </span>
              </v-avatar>
            </template>
            <v-list-item-title class="font-weight-medium">
              {{ member.user_name }}
            </v-list-item-title>
            <v-list-item-subtitle>
              {{ member.user_email }}
            </v-list-item-subtitle>
            <template v-slot:append>
              <v-btn
                color="error"
                variant="text"
                size="small"
                class="mr-2"
                @click="rejectMember(member.id)"
              >
                거절
              </v-btn>
              <v-btn
                color="success"
                variant="flat"
                size="small"
                @click="approveMember(member.id)"
              >
                승인
              </v-btn>
            </template>
          </v-list-item>
        </v-list>
      </v-card-text>
    </v-card>

    <!-- 검색 및 필터 -->
    <v-card class="filter-card" variant="flat">
      <v-card-text>
        <v-row align="center">
          <v-col cols="12" md="4">
            <v-text-field
              v-model="searchQuery"
              prepend-inner-icon="mdi-magnify"
              label="회원 검색"
              variant="outlined"
              density="compact"
              hide-details
              clearable
            />
          </v-col>
          <v-col cols="6" md="2">
            <v-select
              v-model="filterRole"
              :items="roleOptions"
              label="역할"
              variant="outlined"
              density="compact"
              hide-details
            />
          </v-col>
          <v-col cols="6" md="2">
            <v-select
              v-model="filterGender"
              :items="genderOptions"
              label="성별"
              variant="outlined"
              density="compact"
              hide-details
            />
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- 회원 목록 -->
    <v-card class="members-card" variant="flat">
      <v-card-text class="pa-0">
        <v-data-table
          :headers="headers"
          :items="filteredMembers"
          :search="searchQuery"
          :loading="isLoading"
          density="comfortable"
          class="members-table"
          hover
        >
          <template v-slot:item.name="{ item }">
            <div class="member-info">
              <v-avatar
                :color="item.gender === 'male' ? 'blue' : 'pink'"
                size="36"
                class="mr-3"
              >
                <span class="text-white font-weight-bold text-caption">
                  {{ getInitial(item.user_name) }}
                </span>
              </v-avatar>
              <div>
                <div class="member-name">{{ item.user_name || item.nickname }}</div>
                <div class="member-email">{{ item.user_email }}</div>
              </div>
            </div>
          </template>

          <template v-slot:item.gender="{ item }">
            <v-icon :color="item.gender === 'male' ? 'blue' : 'pink'" size="20">
              {{ item.gender === 'male' ? 'mdi-gender-male' : 'mdi-gender-female' }}
            </v-icon>
          </template>

          <template v-slot:item.role="{ item }">
            <v-chip
              :color="getRoleColor(item.role)"
              size="small"
              variant="tonal"
            >
              {{ getRoleLabel(item.role) }}
            </v-chip>
          </template>

          <template v-slot:item.stats="{ item }">
            <div class="member-stats">
              <span class="text-success">{{ item.wins || 0 }}승</span>
              <span class="text-error">{{ item.losses || 0 }}패</span>
            </div>
          </template>

          <template v-slot:item.joined_at="{ item }">
            {{ formatDate(item.joined_at || item.created_at) }}
          </template>

          <template v-slot:item.actions="{ item }">
            <v-menu>
              <template v-slot:activator="{ props }">
                <v-btn icon variant="text" size="small" v-bind="props">
                  <v-icon>mdi-dots-vertical</v-icon>
                </v-btn>
              </template>
              <v-list density="compact">
                <v-list-item @click="openRoleDialog(item)">
                  <v-list-item-title>역할 변경</v-list-item-title>
                </v-list-item>
                <v-list-item
                  class="text-error"
                  @click="confirmRemove(item)"
                >
                  <v-list-item-title>내보내기</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <!-- 역할 변경 다이얼로그 -->
    <v-dialog v-model="showRoleDialog" max-width="400">
      <v-card>
        <v-card-title>역할 변경</v-card-title>
        <v-card-text>
          <p class="mb-4">
            <strong>{{ editingMember?.user_name }}</strong> 님의 역할을 변경합니다.
          </p>
          <v-select
            v-model="newRole"
            :items="availableRoles"
            label="새로운 역할"
            variant="outlined"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showRoleDialog = false">취소</v-btn>
          <v-btn color="primary" @click="changeRole">변경</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

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

const allMembers = ref([])
const isLoading = ref(false)
const searchQuery = ref('')
const filterRole = ref('all')
const filterGender = ref('all')

const showRoleDialog = ref(false)
const editingMember = ref(null)
const newRole = ref('')

const headers = [
  { title: '회원', key: 'name', sortable: true },
  { title: '성별', key: 'gender', sortable: true, width: '80px' },
  { title: '역할', key: 'role', sortable: true, width: '120px' },
  { title: '전적', key: 'stats', sortable: false, width: '120px' },
  { title: '가입일', key: 'joined_at', sortable: true, width: '120px' },
  { title: '', key: 'actions', sortable: false, width: '60px' },
]

const roleOptions = [
  { title: '전체', value: 'all' },
  { title: '매니저', value: 'manager' },
  { title: '회원', value: 'member' },
  { title: '지인', value: 'friend' },
  { title: '졸업자', value: 'alumni' },
]

const genderOptions = [
  { title: '전체', value: 'all' },
  { title: '남성', value: 'male' },
  { title: '여성', value: 'female' },
]

const availableRoles = [
  { title: '매니저', value: 'manager' },
  { title: '회원', value: 'member' },
  { title: '지인', value: 'friend' },
  { title: '졸업자', value: 'alumni' },
]

const pendingMembers = computed(() =>
  allMembers.value.filter(m => m.status === 'pending')
)

const activeMembers = computed(() =>
  allMembers.value.filter(m => m.status === 'active')
)

const filteredMembers = computed(() => {
  let result = activeMembers.value

  if (filterRole.value !== 'all') {
    result = result.filter(m => m.role === filterRole.value)
  }

  if (filterGender.value !== 'all') {
    result = result.filter(m => m.gender === filterGender.value)
  }

  return result
})

function getInitial(name) {
  if (!name) return '?'
  return name.charAt(0).toUpperCase()
}

function getRoleColor(role) {
  const colors = {
    manager: 'primary',
    member: 'grey',
    friend: 'teal',
    alumni: 'purple',
  }
  return colors[role] || 'grey'
}

function getRoleLabel(role) {
  const labels = {
    manager: '매니저',
    member: '회원',
    friend: '지인',
    alumni: '졸업자',
  }
  return labels[role] || role
}

function formatDate(dateString) {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('ko-KR')
}

async function loadMembers() {
  isLoading.value = true
  try {
    const response = await apiClient.get(`/clubs/${props.clubId}/members`)
    allMembers.value = response.data
  } catch (error) {
    console.error('회원 목록 로드 실패:', error)
  } finally {
    isLoading.value = false
  }
}

async function approveMember(memberId) {
  try {
    await apiClient.post(`/clubs/${props.clubId}/members/${memberId}/approve`)
    await loadMembers()
  } catch (error) {
    console.error('승인 실패:', error)
    alert('승인에 실패했습니다.')
  }
}

async function rejectMember(memberId) {
  if (!confirm('정말 거절하시겠습니까?')) return

  try {
    await apiClient.delete(`/clubs/${props.clubId}/members/${memberId}`)
    await loadMembers()
  } catch (error) {
    console.error('거절 실패:', error)
    alert('거절에 실패했습니다.')
  }
}

function openRoleDialog(member) {
  editingMember.value = member
  newRole.value = member.role
  showRoleDialog.value = true
}

async function changeRole() {
  if (!editingMember.value || !newRole.value) return

  try {
    await apiClient.put(
      `/clubs/${props.clubId}/members/${editingMember.value.id}`,
      { role: newRole.value }
    )
    await loadMembers()
    showRoleDialog.value = false
  } catch (error) {
    console.error('역할 변경 실패:', error)
    alert('역할 변경에 실패했습니다.')
  }
}

async function confirmRemove(member) {
  if (!confirm(`${member.user_name} 님을 동호회에서 내보내시겠습니까?`)) return

  try {
    await apiClient.delete(`/clubs/${props.clubId}/members/${member.id}`)
    await loadMembers()
  } catch (error) {
    console.error('내보내기 실패:', error)
    alert('내보내기에 실패했습니다.')
  }
}

onMounted(() => {
  loadMembers()
})
</script>

<style scoped>
.member-management-tab {
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

.header-stats {
  display: flex;
  gap: 8px;
}

.pending-card {
  border: 1px solid #FEF3C7;
  border-radius: 16px;
  background: #FFFBEB;
}

.pending-card .card-title {
  font-size: 1rem;
  font-weight: 600;
  padding: 16px 20px;
  border-bottom: 1px solid #FEF3C7;
}

.pending-item {
  border-bottom: 1px solid #FEF3C7;
}

.pending-item:last-child {
  border-bottom: none;
}

.filter-card,
.members-card {
  border: 1px solid #E2E8F0;
  border-radius: 16px;
}

.members-table {
  border-radius: 0 0 16px 16px;
}

.member-info {
  display: flex;
  align-items: center;
}

.member-name {
  font-weight: 500;
  color: #1E293B;
}

.member-email {
  font-size: 0.75rem;
  color: #94A3B8;
}

.member-stats {
  display: flex;
  gap: 8px;
  font-size: 0.85rem;
  font-weight: 500;
}
</style>
