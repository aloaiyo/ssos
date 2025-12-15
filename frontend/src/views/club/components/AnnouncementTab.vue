<template>
  <div class="announcement-tab">
    <!-- 헤더 -->
    <div class="tab-header">
      <h2 class="tab-title">공지사항</h2>
      <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreateDialog">
        공지 작성
      </v-btn>
    </div>

    <!-- 공지사항 목록 -->
    <div class="announcement-list">
      <v-card
        v-for="announcement in announcements"
        :key="announcement.id"
        class="announcement-card"
        variant="flat"
        @click="openDetailDialog(announcement)"
      >
        <v-card-text class="pa-4">
          <div class="announcement-header">
            <div class="announcement-badges">
              <v-chip
                v-if="announcement.is_pinned"
                size="x-small"
                color="error"
                variant="flat"
              >
                <v-icon start size="12">mdi-pin</v-icon>
                고정
              </v-chip>
              <v-chip
                :color="getTypeColor(announcement.announcement_type)"
                size="x-small"
                variant="tonal"
              >
                {{ getTypeLabel(announcement.announcement_type) }}
              </v-chip>
            </div>
            <span class="announcement-date">
              {{ formatDate(announcement.created_at) }}
            </span>
          </div>
          <h3 class="announcement-title">{{ announcement.title }}</h3>
          <p class="announcement-preview">{{ getPreview(announcement.content) }}</p>
          <div class="announcement-footer">
            <span class="announcement-author">
              <v-icon size="14" class="mr-1">mdi-account</v-icon>
              {{ announcement.author_name || '관리자' }}
            </span>
            <span class="announcement-views">
              <v-icon size="14" class="mr-1">mdi-eye</v-icon>
              {{ announcement.views }}
            </span>
          </div>
        </v-card-text>
      </v-card>

      <!-- 빈 상태 -->
      <div v-if="announcements.length === 0 && !isLoading" class="empty-state">
        <v-icon size="64" color="grey-lighten-1">mdi-bullhorn-outline</v-icon>
        <p>등록된 공지사항이 없습니다.</p>
        <v-btn color="primary" variant="tonal" @click="openCreateDialog">
          첫 공지 작성하기
        </v-btn>
      </div>
    </div>

    <!-- 작성/수정 다이얼로그 -->
    <v-dialog v-model="showFormDialog" max-width="600" persistent>
      <v-card>
        <v-card-title>
          {{ editingAnnouncement ? '공지 수정' : '공지 작성' }}
        </v-card-title>
        <v-card-text>
          <v-form ref="formRef" v-model="formValid">
            <v-text-field
              v-model="form.title"
              label="제목"
              :rules="[v => !!v || '제목을 입력하세요']"
              variant="outlined"
              density="comfortable"
              class="mb-3"
            />
            <v-select
              v-model="form.announcement_type"
              :items="typeOptions"
              label="공지 유형"
              variant="outlined"
              density="comfortable"
              class="mb-3"
            />
            <v-textarea
              v-model="form.content"
              label="내용"
              :rules="[v => !!v || '내용을 입력하세요']"
              variant="outlined"
              rows="6"
              class="mb-3"
            />
            <v-checkbox
              v-model="form.is_pinned"
              label="상단 고정"
              color="primary"
              density="comfortable"
            />
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="closeFormDialog">취소</v-btn>
          <v-btn
            color="primary"
            :loading="isSaving"
            :disabled="!formValid"
            @click="saveAnnouncement"
          >
            {{ editingAnnouncement ? '수정' : '등록' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 상세 다이얼로그 -->
    <v-dialog v-model="showDetailDialog" max-width="600">
      <v-card v-if="selectedAnnouncement">
        <v-card-title class="d-flex align-center">
          <div class="flex-grow-1">
            <v-chip
              v-if="selectedAnnouncement.is_pinned"
              size="x-small"
              color="error"
              variant="flat"
              class="mr-2"
            >
              고정
            </v-chip>
            <v-chip
              :color="getTypeColor(selectedAnnouncement.announcement_type)"
              size="x-small"
              variant="tonal"
            >
              {{ getTypeLabel(selectedAnnouncement.announcement_type) }}
            </v-chip>
          </div>
          <v-btn icon variant="text" size="small" @click="showDetailDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text>
          <h2 class="text-h6 mb-4">{{ selectedAnnouncement.title }}</h2>
          <div class="detail-meta mb-4">
            <span>
              <v-icon size="14" class="mr-1">mdi-account</v-icon>
              {{ selectedAnnouncement.author_name || '관리자' }}
            </span>
            <span>
              <v-icon size="14" class="mr-1">mdi-calendar</v-icon>
              {{ formatDate(selectedAnnouncement.created_at) }}
            </span>
            <span>
              <v-icon size="14" class="mr-1">mdi-eye</v-icon>
              조회 {{ selectedAnnouncement.views }}
            </span>
          </div>
          <v-divider class="mb-4" />
          <div class="detail-content" v-html="formatContent(selectedAnnouncement.content)"></div>
        </v-card-text>
        <v-card-actions>
          <v-btn
            color="error"
            variant="text"
            @click="deleteAnnouncement(selectedAnnouncement.id)"
          >
            삭제
          </v-btn>
          <v-spacer />
          <v-btn
            color="primary"
            variant="tonal"
            @click="openEditDialog(selectedAnnouncement)"
          >
            수정
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import apiClient from '@/api'

const props = defineProps({
  clubId: {
    type: Number,
    required: true,
  },
})

const announcements = ref([])
const isLoading = ref(false)
const isSaving = ref(false)
const showFormDialog = ref(false)
const showDetailDialog = ref(false)
const formRef = ref(null)
const formValid = ref(false)
const editingAnnouncement = ref(null)
const selectedAnnouncement = ref(null)

const form = ref({
  title: '',
  content: '',
  announcement_type: 'general',
  is_pinned: false,
})

const typeOptions = [
  { title: '일반 공지', value: 'general' },
  { title: '중요 공지', value: 'important' },
  { title: '이벤트', value: 'event' },
]

function getTypeColor(type) {
  const colors = {
    general: 'grey',
    important: 'error',
    event: 'success',
  }
  return colors[type] || 'grey'
}

function getTypeLabel(type) {
  const labels = {
    general: '일반',
    important: '중요',
    event: '이벤트',
  }
  return labels[type] || type
}

function formatDate(dateString) {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) {
    return '오늘'
  } else if (days === 1) {
    return '어제'
  } else if (days < 7) {
    return `${days}일 전`
  } else {
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }
}

function getPreview(content) {
  if (!content) return ''
  return content.length > 100 ? content.substring(0, 100) + '...' : content
}

function formatContent(content) {
  if (!content) return ''
  return content.replace(/\n/g, '<br>')
}

async function loadAnnouncements() {
  isLoading.value = true
  try {
    const response = await apiClient.get(`/clubs/${props.clubId}/announcements`)
    announcements.value = response.data
  } catch (error) {
    console.error('공지사항 로드 실패:', error)
  } finally {
    isLoading.value = false
  }
}

function openCreateDialog() {
  editingAnnouncement.value = null
  form.value = {
    title: '',
    content: '',
    announcement_type: 'general',
    is_pinned: false,
  }
  showFormDialog.value = true
}

function openEditDialog(announcement) {
  editingAnnouncement.value = announcement
  form.value = {
    title: announcement.title,
    content: announcement.content,
    announcement_type: announcement.announcement_type,
    is_pinned: announcement.is_pinned,
  }
  showDetailDialog.value = false
  showFormDialog.value = true
}

function openDetailDialog(announcement) {
  selectedAnnouncement.value = announcement
  showDetailDialog.value = true
}

function closeFormDialog() {
  showFormDialog.value = false
  editingAnnouncement.value = null
}

async function saveAnnouncement() {
  if (!formValid.value) return

  isSaving.value = true
  try {
    if (editingAnnouncement.value) {
      await apiClient.put(
        `/clubs/${props.clubId}/announcements/${editingAnnouncement.value.id}`,
        form.value
      )
    } else {
      await apiClient.post(`/clubs/${props.clubId}/announcements`, form.value)
    }
    await loadAnnouncements()
    closeFormDialog()
  } catch (error) {
    console.error('저장 실패:', error)
    alert('저장에 실패했습니다.')
  } finally {
    isSaving.value = false
  }
}

async function deleteAnnouncement(id) {
  if (!confirm('정말 삭제하시겠습니까?')) return

  try {
    await apiClient.delete(`/clubs/${props.clubId}/announcements/${id}`)
    await loadAnnouncements()
    showDetailDialog.value = false
  } catch (error) {
    console.error('삭제 실패:', error)
    alert('삭제에 실패했습니다.')
  }
}

onMounted(() => {
  loadAnnouncements()
})
</script>

<style scoped>
.announcement-tab {
  display: flex;
  flex-direction: column;
  gap: 24px;
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

.announcement-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.announcement-card {
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.announcement-card:hover {
  border-color: #10B981;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.1);
}

.announcement-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.announcement-badges {
  display: flex;
  gap: 6px;
}

.announcement-date {
  font-size: 0.75rem;
  color: #94A3B8;
}

.announcement-title {
  font-size: 1rem;
  font-weight: 600;
  color: #1E293B;
  margin-bottom: 8px;
}

.announcement-preview {
  font-size: 0.875rem;
  color: #64748B;
  line-height: 1.5;
  margin-bottom: 12px;
}

.announcement-footer {
  display: flex;
  gap: 16px;
  font-size: 0.75rem;
  color: #94A3B8;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px 24px;
  text-align: center;
  color: #94A3B8;
}

.empty-state p {
  margin: 16px 0;
}

.detail-meta {
  display: flex;
  gap: 16px;
  font-size: 0.85rem;
  color: #64748B;
}

.detail-content {
  font-size: 0.95rem;
  line-height: 1.7;
  color: #1E293B;
}
</style>
