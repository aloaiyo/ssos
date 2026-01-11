<template>
  <div class="season-list-page">
    <!-- 헤더 -->
    <div class="page-header">
      <h1 class="page-title">시즌 관리</h1>
      <v-btn color="primary" variant="flat" @click="showCreateDialog = true">
        <v-icon left>mdi-plus</v-icon>
        시즌 생성
      </v-btn>
    </div>

    <!-- 시즌 목록 -->
    <div v-if="isLoading" class="loading-container">
      <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
    </div>

    <div v-else-if="seasons.length === 0" class="empty-state">
      <v-icon size="64" color="grey-lighten-1">mdi-calendar-blank</v-icon>
      <p class="text-grey mt-4">등록된 시즌이 없습니다</p>
      <v-btn color="primary" variant="flat" class="mt-4" @click="showCreateDialog = true">
        첫 시즌 생성하기
      </v-btn>
    </div>

    <div v-else class="season-list">
      <v-card
        v-for="season in seasons"
        :key="season.id"
        class="season-card"
        variant="flat"
        @click="goToSeasonDetail(season)"
      >
        <div class="season-card-content">
          <div class="season-info">
            <div class="season-header">
              <h3 class="season-name">{{ season.name }}</h3>
              <v-chip :color="getStatusColor(season.status)" size="small" variant="tonal">
                {{ getStatusLabel(season.status) }}
              </v-chip>
            </div>
            <p v-if="season.description" class="season-description">{{ season.description }}</p>
            <div class="season-dates">
              <v-icon size="16">mdi-calendar-range</v-icon>
              {{ formatDate(season.start_date) }} ~ {{ formatDate(season.end_date) }}
            </div>
            <div class="season-stats">
              <span><v-icon size="14">mdi-calendar-check</v-icon> {{ season.session_count || 0 }}개 세션</span>
              <span class="ml-4"><v-icon size="14">mdi-tennis</v-icon> {{ season.match_count || 0 }}개 경기</span>
            </div>
          </div>
          <v-btn icon variant="text" @click.stop="openEditDialog(season)">
            <v-icon>mdi-pencil</v-icon>
          </v-btn>
        </div>
      </v-card>
    </div>

    <!-- 시즌 생성/수정 다이얼로그 -->
    <v-dialog v-model="showCreateDialog" max-width="500">
      <v-card>
        <v-card-title>{{ isEditing ? '시즌 수정' : '시즌 생성' }}</v-card-title>
        <v-card-text>
          <v-form ref="formRef" v-model="formValid">
            <v-text-field
              v-model="form.name"
              label="시즌 이름"
              :rules="[v => !!v || '시즌 이름을 입력해주세요']"
              placeholder="예: 2024 상반기 리그"
              required
            ></v-text-field>
            <v-textarea
              v-model="form.description"
              label="설명 (선택)"
              rows="2"
              placeholder="시즌에 대한 설명을 입력하세요"
            ></v-textarea>
            <v-row>
              <v-col cols="6">
                <v-text-field
                  v-model="form.start_date"
                  label="시작일"
                  type="date"
                  :rules="[v => !!v || '시작일을 선택해주세요']"
                  required
                ></v-text-field>
              </v-col>
              <v-col cols="6">
                <v-text-field
                  v-model="form.end_date"
                  label="종료일"
                  type="date"
                  :rules="[
                    v => !!v || '종료일을 선택해주세요',
                    v => !form.start_date || v > form.start_date || '종료일은 시작일 이후여야 합니다'
                  ]"
                  required
                ></v-text-field>
              </v-col>
            </v-row>
            <v-select
              v-if="isEditing"
              v-model="form.status"
              label="상태"
              :items="statusOptions"
              item-title="label"
              item-value="value"
            ></v-select>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="closeDialog">취소</v-btn>
          <v-btn
            color="primary"
            variant="flat"
            :loading="isSaving"
            :disabled="!formValid"
            @click="saveSeason"
          >
            {{ isEditing ? '수정' : '생성' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 삭제 확인 다이얼로그 -->
    <v-dialog v-model="showDeleteDialog" max-width="400">
      <v-card>
        <v-card-title>시즌 삭제</v-card-title>
        <v-card-text>
          "{{ seasonToDelete?.name }}" 시즌을 삭제하시겠습니까?
          <br />
          <span class="text-error">이 작업은 되돌릴 수 없습니다.</span>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="showDeleteDialog = false">취소</v-btn>
          <v-btn color="error" variant="flat" :loading="isDeleting" @click="deleteSeason">
            삭제
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useClubStore } from '@/stores/club'
import { useSeasonStore } from '@/stores/season'

const router = useRouter()
const clubStore = useClubStore()
const seasonStore = useSeasonStore()

const selectedClub = computed(() => clubStore.selectedClub)
const seasons = computed(() => seasonStore.seasons)
const isLoading = computed(() => seasonStore.isLoading)

const showCreateDialog = ref(false)
const showDeleteDialog = ref(false)
const isEditing = ref(false)
const isSaving = ref(false)
const isDeleting = ref(false)
const formValid = ref(false)
const formRef = ref(null)
const editingSeasonId = ref(null)
const seasonToDelete = ref(null)

const form = ref({
  name: '',
  description: '',
  start_date: '',
  end_date: '',
  status: 'upcoming'
})

const statusOptions = [
  { value: 'upcoming', label: '예정' },
  { value: 'active', label: '진행 중' },
  { value: 'completed', label: '완료' }
]

function getStatusColor(status) {
  const colors = {
    upcoming: 'info',
    active: 'success',
    completed: 'grey'
  }
  return colors[status] || 'grey'
}

function getStatusLabel(status) {
  const labels = {
    upcoming: '예정',
    active: '진행 중',
    completed: '완료'
  }
  return labels[status] || status
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}`
}

function goToSeasonDetail(season) {
  router.push({ name: 'season-detail', params: { seasonId: season.id } })
}

function openEditDialog(season) {
  isEditing.value = true
  editingSeasonId.value = season.id
  form.value = {
    name: season.name,
    description: season.description || '',
    start_date: season.start_date,
    end_date: season.end_date,
    status: season.status
  }
  showCreateDialog.value = true
}

function closeDialog() {
  showCreateDialog.value = false
  isEditing.value = false
  editingSeasonId.value = null
  form.value = {
    name: '',
    description: '',
    start_date: '',
    end_date: '',
    status: 'upcoming'
  }
}

async function saveSeason() {
  if (!selectedClub.value?.id) return

  isSaving.value = true
  try {
    if (isEditing.value && editingSeasonId.value) {
      await seasonStore.updateSeason(selectedClub.value.id, editingSeasonId.value, form.value)
    } else {
      await seasonStore.createSeason(selectedClub.value.id, form.value)
    }
    closeDialog()
  } catch (error) {
    console.error('시즌 저장 실패:', error)
  } finally {
    isSaving.value = false
  }
}

function confirmDelete(season) {
  seasonToDelete.value = season
  showDeleteDialog.value = true
}

async function deleteSeason() {
  if (!selectedClub.value?.id || !seasonToDelete.value) return

  isDeleting.value = true
  try {
    await seasonStore.deleteSeason(selectedClub.value.id, seasonToDelete.value.id)
    showDeleteDialog.value = false
    seasonToDelete.value = null
  } catch (error) {
    console.error('시즌 삭제 실패:', error)
  } finally {
    isDeleting.value = false
  }
}

async function loadSeasons() {
  if (!selectedClub.value?.id) return
  await seasonStore.fetchSeasons(selectedClub.value.id)
}

watch(selectedClub, () => {
  loadSeasons()
})

onMounted(() => {
  loadSeasons()
})
</script>

<style scoped>
.season-list-page {
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

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  text-align: center;
}

.season-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.season-card {
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.season-card:hover {
  border-color: #059669;
  box-shadow: 0 4px 12px rgba(5, 150, 105, 0.1);
}

.season-card-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.season-info {
  flex: 1;
}

.season-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.season-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1E293B;
}

.season-description {
  font-size: 0.9rem;
  color: #64748B;
  margin-bottom: 8px;
}

.season-dates {
  font-size: 0.85rem;
  color: #64748B;
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 8px;
}

.season-stats {
  font-size: 0.8rem;
  color: #94A3B8;
  display: flex;
  align-items: center;
}

.season-stats span {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
