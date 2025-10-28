<template>
  <v-container>
    <!-- 헤더 -->
    <v-row>
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center mb-4">
          <h1 class="text-h4 font-weight-bold">동호회 관리</h1>
          <v-btn
            :to="{ name: 'club-list' }"
            variant="outlined"
          >
            목록으로
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <v-row>
      <!-- 동호회 생성 폼 -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="text-h6">동호회 생성</v-card-title>
          <v-divider></v-divider>
          <v-card-text>
            <v-form ref="createForm" v-model="createValid" @submit.prevent="handleCreate">
              <v-text-field
                v-model="newClub.name"
                :rules="[required]"
                label="동호회명 *"
                variant="outlined"
                required
              ></v-text-field>

              <v-textarea
                v-model="newClub.description"
                label="설명"
                variant="outlined"
                rows="3"
              ></v-textarea>

              <v-text-field
                v-model="newClub.location"
                label="위치"
                variant="outlined"
                prepend-inner-icon="mdi-map-marker"
              ></v-text-field>

              <v-btn
                :loading="isLoading"
                :disabled="!createValid"
                type="submit"
                color="primary"
                block
              >
                생성
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- 동호회 목록 및 관리 -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="text-h6">등록된 동호회</v-card-title>
          <v-divider></v-divider>
          <v-card-text>
            <v-list v-if="clubs.length > 0">
              <v-list-item
                v-for="club in clubs"
                :key="club.id"
                class="mb-2"
              >
                <template v-slot:prepend>
                  <v-icon icon="mdi-account-group"></v-icon>
                </template>

                <v-list-item-title>{{ club.name }}</v-list-item-title>
                <v-list-item-subtitle>{{ club.location || '위치 정보 없음' }}</v-list-item-subtitle>

                <template v-slot:append>
                  <v-btn
                    icon="mdi-pencil"
                    size="small"
                    variant="text"
                    @click="editClub(club)"
                  ></v-btn>
                  <v-btn
                    icon="mdi-delete"
                    size="small"
                    variant="text"
                    color="error"
                    @click="confirmDelete(club)"
                  ></v-btn>
                </template>
              </v-list-item>
            </v-list>
            <div v-else class="text-center pa-4 text-grey">
              등록된 동호회가 없습니다.
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 수정 다이얼로그 -->
    <v-dialog v-model="editDialog" max-width="600">
      <v-card>
        <v-card-title class="text-h6">동호회 수정</v-card-title>
        <v-divider></v-divider>
        <v-card-text>
          <v-form ref="editForm" v-model="editValid">
            <v-text-field
              v-model="editingClub.name"
              :rules="[required]"
              label="동호회명 *"
              variant="outlined"
              required
            ></v-text-field>

            <v-textarea
              v-model="editingClub.description"
              label="설명"
              variant="outlined"
              rows="3"
            ></v-textarea>

            <v-text-field
              v-model="editingClub.location"
              label="위치"
              variant="outlined"
              prepend-inner-icon="mdi-map-marker"
            ></v-text-field>
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
        <v-card-title class="text-h6">동호회 삭제</v-card-title>
        <v-card-text>
          <p>정말로 <strong>{{ deletingClub?.name }}</strong>을(를) 삭제하시겠습니까?</p>
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
import { required } from '@/utils/validators'

const clubStore = useClubStore()
const { clubs, isLoading } = storeToRefs(clubStore)

const createForm = ref(null)
const editForm = ref(null)
const createValid = ref(false)
const editValid = ref(false)

const newClub = ref({
  name: '',
  description: '',
  location: '',
})

const editDialog = ref(false)
const editingClub = ref({
  id: null,
  name: '',
  description: '',
  location: '',
})

const deleteDialog = ref(false)
const deletingClub = ref(null)

// 동호회 생성
async function handleCreate() {
  if (!createValid.value) return

  try {
    await clubStore.createClub(newClub.value)
    // 폼 초기화
    newClub.value = {
      name: '',
      description: '',
      location: '',
    }
    createForm.value?.reset()
  } catch (error) {
    console.error('동호회 생성 실패:', error)
  }
}

// 수정 다이얼로그 열기
function editClub(club) {
  editingClub.value = {
    id: club.id,
    name: club.name,
    description: club.description || '',
    location: club.location || '',
  }
  editDialog.value = true
}

// 동호회 수정
async function handleUpdate() {
  if (!editValid.value) return

  try {
    await clubStore.updateClub(editingClub.value.id, {
      name: editingClub.value.name,
      description: editingClub.value.description,
      location: editingClub.value.location,
    })
    editDialog.value = false
  } catch (error) {
    console.error('동호회 수정 실패:', error)
  }
}

// 삭제 확인 다이얼로그 열기
function confirmDelete(club) {
  deletingClub.value = club
  deleteDialog.value = true
}

// 동호회 삭제
async function handleDelete() {
  if (!deletingClub.value) return

  try {
    await clubStore.deleteClub(deletingClub.value.id)
    deleteDialog.value = false
    deletingClub.value = null
  } catch (error) {
    console.error('동호회 삭제 실패:', error)
  }
}

// 컴포넌트 마운트 시 동호회 목록 로드
onMounted(async () => {
  await clubStore.fetchClubs()
})
</script>
