<template>
  <v-container>
    <!-- 헤더 -->
    <v-row>
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center mb-4">
          <div>
            <h1 class="text-h4 font-weight-bold">회원 목록</h1>
            <p class="text-subtitle-1 text-grey">
              {{ selectedClub?.name || '동호회를 선택해주세요' }}
            </p>
          </div>
          <v-btn
            v-if="isAdmin && selectedClub"
            :to="{ name: 'member-manage' }"
            color="primary"
            prepend-icon="mdi-plus"
          >
            회원 추가
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <!-- 동호회 미선택 -->
    <v-row v-if="!selectedClub">
      <v-col cols="12">
        <v-card>
          <v-card-text class="text-center pa-8">
            <v-icon icon="mdi-alert-circle" size="64" color="warning"></v-icon>
            <p class="text-h6 mt-4">동호회를 먼저 선택해주세요.</p>
            <v-btn
              :to="{ name: 'club-list' }"
              color="primary"
              class="mt-4"
            >
              동호회 선택하기
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 회원 목록 -->
    <v-row v-else>
      <v-col cols="12">
        <!-- 필터 -->
        <v-card class="mb-4">
          <v-card-text>
            <v-row>
              <v-col cols="12" sm="6" md="3">
                <v-text-field
                  v-model="search"
                  label="검색"
                  prepend-inner-icon="mdi-magnify"
                  variant="outlined"
                  density="compact"
                  hide-details
                  clearable
                ></v-text-field>
              </v-col>
              <v-col cols="12" sm="6" md="3">
                <v-select
                  v-model="genderFilter"
                  :items="genderOptions"
                  label="성별"
                  variant="outlined"
                  density="compact"
                  hide-details
                  clearable
                ></v-select>
              </v-col>

            </v-row>
          </v-card-text>
        </v-card>

        <!-- 테이블 -->
        <v-card>
          <v-data-table
            :headers="headers"
            :items="filteredMembers"
            :search="search"
            :loading="isLoading"
            items-per-page="10"
            class="elevation-1"
          >
            <!-- 이름 -->
            <template v-slot:item.user_name="{ item }">
              <div class="d-flex align-center">
                <v-avatar color="primary" size="32" class="mr-2">
                  <span class="text-white text-caption">
                    {{ item.user_name?.[0] || '?' }}
                  </span>
                </v-avatar>
                <div>
                  <div :class="{'text-blue': item.gender === 'male', 'text-pink': item.gender === 'female'}">
                    {{ item.user_name }}
                  </div>
                  <div class="text-caption text-grey">{{ item.user_email }}</div>
                </div>
              </div>
            </template>



            <!-- 가입일 -->
            <template v-slot:item.created_at="{ item }">
              {{ formatDate(item.created_at) }}
            </template>

            <!-- 액션 -->
            <template v-slot:item.actions="{ item }">
              <v-btn
                icon="mdi-eye"
                size="small"
                variant="text"
                @click="viewMember(item)"
              ></v-btn>
              <v-btn
                v-if="isAdmin"
                icon="mdi-pencil"
                size="small"
                variant="text"
                @click="editMember(item)"
              ></v-btn>
            </template>

            <!-- 데이터 없음 -->
            <template v-slot:no-data>
              <div class="text-center pa-4">
                <v-icon icon="mdi-account-off" size="64" color="grey"></v-icon>
                <p class="text-h6 mt-4">등록된 회원이 없습니다.</p>
              </div>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>

    <!-- 회원 상세 다이얼로그 -->
    <v-dialog v-model="detailDialog" max-width="600">
      <v-card v-if="selectedMember">
        <v-card-title class="text-h6">회원 상세 정보</v-card-title>
        <v-divider></v-divider>
        <v-card-text>
          <v-list>
            <v-list-item>
              <template v-slot:prepend>
                <v-avatar color="primary" size="48">
                  <span class="text-white text-h6">
                    {{ selectedMember.user_name?.[0] || '?' }}
                  </span>
                </v-avatar>
              </template>
              <v-list-item-title class="text-h6">
                {{ selectedMember.user_name }}
              </v-list-item-title>
              <v-list-item-subtitle>
                {{ selectedMember.user_email }}
              </v-list-item-subtitle>
            </v-list-item>

            <v-divider></v-divider>

            <v-list-item>
              <v-list-item-title>성별</v-list-item-title>
              <v-list-item-subtitle>
                {{ selectedMember.gender === 'male' ? '남성' : '여성' }}
              </v-list-item-subtitle>
            </v-list-item>



            <v-list-item>
              <v-list-item-title>가입일</v-list-item-title>
              <v-list-item-subtitle>
                {{ formatDate(selectedMember.created_at) }}
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            variant="text"
            @click="detailDialog = false"
          >
            닫기
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { useClubStore } from '@/stores/club'
import { useMemberStore } from '@/stores/member'
import { formatDate } from '@/utils/date'

const router = useRouter()
const authStore = useAuthStore()
const clubStore = useClubStore()
const memberStore = useMemberStore()

const { isAdmin } = storeToRefs(authStore)
const { selectedClub } = storeToRefs(clubStore)
const { members, isLoading } = storeToRefs(memberStore)

// 필터
const search = ref('')
const genderFilter = ref(null)
const typeFilter = ref(null)

const genderOptions = [
  { title: '남성', value: 'male' },
  { title: '여성', value: 'female' },
]



// 테이블 헤더
const headers = [
  { title: '이름', key: 'user_name', sortable: true },
  { title: '가입일', key: 'created_at', sortable: true },
  { title: '액션', key: 'actions', sortable: false, align: 'center' },
]

// 필터링된 회원 목록
const filteredMembers = computed(() => {
  let filtered = members.value

  if (genderFilter.value) {
    filtered = filtered.filter(m => m.gender === genderFilter.value)
  }



  return filtered
})

// 회원 상세 다이얼로그
const detailDialog = ref(false)
const selectedMember = ref(null)



// 회원 상세 보기
function viewMember(member) {
  selectedMember.value = member
  detailDialog.value = true
}

// 회원 수정
function editMember(member) {
  router.push({
    name: 'member-manage',
    query: { memberId: member.id },
  })
}

// 컴포넌트 마운트 시 회원 목록 로드
onMounted(async () => {
  if (selectedClub.value) {
    await memberStore.fetchMembers(selectedClub.value.id)
  }
})
</script>

<style scoped>
.v-data-table {
  border-radius: 8px;
}
</style>
