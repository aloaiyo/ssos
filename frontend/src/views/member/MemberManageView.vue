<template>
  <v-container>
    <!-- 헤더 -->
    <v-row>
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center mb-4">
          <div>
            <h1 class="text-h4 font-weight-bold">회원 관리</h1>
            <p class="text-subtitle-1 text-grey">
              {{ selectedClub?.name || '동호회를 선택해주세요' }}
            </p>
          </div>
          <v-btn
            :to="{ name: 'member-list' }"
            variant="outlined"
          >
            목록으로
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

    <!-- 회원 관리 -->
    <v-row v-else>
      <!-- 회원 추가 폼 -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="text-h6">회원 추가</v-card-title>
          <v-divider></v-divider>
          <v-card-text>
            <v-form ref="createForm" v-model="createValid" @submit.prevent="handleCreate">
              <v-text-field
                v-model="newMember.user_id"
                :rules="[required]"
                label="사용자 ID *"
                variant="outlined"
                type="number"
                hint="시스템에 등록된 사용자 ID"
                persistent-hint
                required
              ></v-text-field>

              <v-select
                v-model="newMember.gender"
                :rules="[required]"
                :items="genderOptions"
                label="성별 *"
                variant="outlined"
                required
              ></v-select>

              <v-select
                v-model="newMember.preferred_type"
                :rules="[required]"
                :items="typeOptions"
                label="선호 타입 *"
                variant="outlined"
                required
              ></v-select>

              <v-btn
                :loading="isLoading"
                :disabled="!createValid"
                type="submit"
                color="primary"
                block
              >
                추가
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- 회원 목록 -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="text-h6">등록된 회원</v-card-title>
          <v-divider></v-divider>
          <v-card-text>
            <v-list v-if="members.length > 0" class="overflow-y-auto" style="max-height: 500px;">
              <v-list-item
                v-for="member in members"
                :key="member.id"
                class="mb-2"
              >
                <template v-slot:prepend>
                  <v-avatar color="primary" size="40">
                    <span class="text-white">
                      {{ member.user?.full_name?.[0] || member.user?.username?.[0] }}
                    </span>
                  </v-avatar>
                </template>

                <v-list-item-title>
                  {{ member.user?.full_name || member.user?.username }}
                </v-list-item-title>
                <v-list-item-subtitle>
                  {{ member.gender === 'male' ? '남성' : '여성' }} |
                  {{ getPreferredTypeLabel(member.preferred_type) }}
                </v-list-item-subtitle>

                <template v-slot:append>
                  <v-btn
                    icon="mdi-pencil"
                    size="small"
                    variant="text"
                    @click="editMember(member)"
                  ></v-btn>
                  <v-btn
                    icon="mdi-delete"
                    size="small"
                    variant="text"
                    color="error"
                    @click="confirmDelete(member)"
                  ></v-btn>
                </template>
              </v-list-item>
            </v-list>
            <div v-else class="text-center pa-4 text-grey">
              등록된 회원이 없습니다.
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 수정 다이얼로그 -->
    <v-dialog v-model="editDialog" max-width="600">
      <v-card>
        <v-card-title class="text-h6">회원 수정</v-card-title>
        <v-divider></v-divider>
        <v-card-text>
          <v-form ref="editForm" v-model="editValid">
            <v-text-field
              v-model="editingMember.user_id"
              label="사용자 ID"
              variant="outlined"
              type="number"
              disabled
            ></v-text-field>

            <v-select
              v-model="editingMember.gender"
              :rules="[required]"
              :items="genderOptions"
              label="성별 *"
              variant="outlined"
              required
            ></v-select>

            <v-select
              v-model="editingMember.preferred_type"
              :rules="[required]"
              :items="typeOptions"
              label="선호 타입 *"
              variant="outlined"
              required
            ></v-select>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            variant="text"
            @click="editDialog = false"
          >
            취소
          </v-btn>
          <v-btn
            :loading="isLoading"
            :disabled="!editValid"
            color="primary"
            @click="handleUpdate"
          >
            저장
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 삭제 확인 다이얼로그 -->
    <v-dialog v-model="deleteDialog" max-width="400">
      <v-card>
        <v-card-title class="text-h6">회원 삭제</v-card-title>
        <v-card-text>
          <p>
            정말로 <strong>{{ deletingMember?.user?.full_name || deletingMember?.user?.username }}</strong>을(를) 삭제하시겠습니까?
          </p>
          <p class="text-error mt-2">이 작업은 되돌릴 수 없습니다.</p>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            variant="text"
            @click="deleteDialog = false"
          >
            취소
          </v-btn>
          <v-btn
            :loading="isLoading"
            color="error"
            @click="handleDelete"
          >
            삭제
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useClubStore } from '@/stores/club'
import { useMemberStore } from '@/stores/member'
import { required } from '@/utils/validators'

const clubStore = useClubStore()
const memberStore = useMemberStore()

const { selectedClub } = storeToRefs(clubStore)
const { members, isLoading } = storeToRefs(memberStore)

const createForm = ref(null)
const editForm = ref(null)
const createValid = ref(false)
const editValid = ref(false)

const genderOptions = [
  { title: '남성', value: 'male' },
  { title: '여성', value: 'female' },
]

const typeOptions = [
  { title: '단식', value: 'singles' },
  { title: '복식', value: 'doubles' },
  { title: '무관', value: 'both' },
]

const newMember = ref({
  user_id: null,
  gender: null,
  preferred_type: null,
})

const editDialog = ref(false)
const editingMember = ref({
  id: null,
  user_id: null,
  gender: null,
  preferred_type: null,
})

const deleteDialog = ref(false)
const deletingMember = ref(null)

// 선호 타입 라벨
function getPreferredTypeLabel(type) {
  const labels = {
    singles: '단식',
    doubles: '복식',
    both: '무관',
  }
  return labels[type] || type
}

// 회원 추가
async function handleCreate() {
  if (!createValid.value || !selectedClub.value) return

  try {
    await memberStore.createMember(selectedClub.value.id, newMember.value)
    // 폼 초기화
    newMember.value = {
      user_id: null,
      gender: null,
      preferred_type: null,
    }
    createForm.value?.reset()
  } catch (error) {
    console.error('회원 추가 실패:', error)
  }
}

// 수정 다이얼로그 열기
function editMember(member) {
  editingMember.value = {
    id: member.id,
    user_id: member.user_id,
    gender: member.gender,
    preferred_type: member.preferred_type,
  }
  editDialog.value = true
}

// 회원 수정
async function handleUpdate() {
  if (!editValid.value || !selectedClub.value) return

  try {
    await memberStore.updateMember(
      selectedClub.value.id,
      editingMember.value.id,
      {
        gender: editingMember.value.gender,
        preferred_type: editingMember.value.preferred_type,
      }
    )
    editDialog.value = false
  } catch (error) {
    console.error('회원 수정 실패:', error)
  }
}

// 삭제 확인 다이얼로그 열기
function confirmDelete(member) {
  deletingMember.value = member
  deleteDialog.value = true
}

// 회원 삭제
async function handleDelete() {
  if (!deletingMember.value || !selectedClub.value) return

  try {
    await memberStore.deleteMember(selectedClub.value.id, deletingMember.value.id)
    deleteDialog.value = false
    deletingMember.value = null
  } catch (error) {
    console.error('회원 삭제 실패:', error)
  }
}

// 컴포넌트 마운트 시 회원 목록 로드
onMounted(async () => {
  if (selectedClub.value) {
    await memberStore.fetchMembers(selectedClub.value.id)
  }
})
</script>
