<template>
  <div class="fee-management-tab">
    <!-- 회비 설정 섹션 -->
    <v-card class="section-card" variant="flat">
      <v-card-title class="card-title">
        <v-icon class="mr-2">mdi-cog</v-icon>
        회비 설정
        <v-spacer />
        <v-btn color="primary" size="small" prepend-icon="mdi-plus" @click="openSettingDialog">
          회비 추가
        </v-btn>
      </v-card-title>
      <v-card-text>
        <div class="fee-settings-list">
          <v-chip
            v-for="setting in feeSettings"
            :key="setting.id"
            :color="selectedSetting?.id === setting.id ? 'primary' : 'default'"
            :variant="selectedSetting?.id === setting.id ? 'flat' : 'outlined'"
            class="fee-setting-chip"
            closable
            @click="selectSetting(setting)"
            @click:close="deleteSetting(setting.id)"
          >
            {{ setting.name }} ({{ formatAmount(setting.amount) }})
          </v-chip>
          <div v-if="feeSettings.length === 0" class="text-medium-emphasis">
            회비 설정이 없습니다.
          </div>
        </div>
      </v-card-text>
    </v-card>

    <!-- 납부 현황 섹션 -->
    <v-card v-if="selectedSetting" class="section-card" variant="flat">
      <v-card-title class="card-title">
        <v-icon class="mr-2">mdi-cash-multiple</v-icon>
        {{ selectedSetting.name }} 납부 현황
        <v-spacer />
        <v-select
          v-model="selectedYear"
          :items="yearOptions"
          label="년도"
          variant="outlined"
          density="compact"
          hide-details
          style="max-width: 120px"
          class="mr-2"
        />
        <v-select
          v-if="selectedSetting.fee_type === 'monthly'"
          v-model="selectedMonth"
          :items="monthOptions"
          label="월"
          variant="outlined"
          density="compact"
          hide-details
          style="max-width: 100px"
          class="mr-2"
        />
        <v-btn
          color="primary"
          variant="tonal"
          size="small"
          :loading="isGenerating"
          @click="generatePayments"
        >
          납부 기록 생성
        </v-btn>
      </v-card-title>

      <!-- 요약 카드 -->
      <v-card-text v-if="summary">
        <v-row class="summary-row mb-4">
          <v-col cols="6" md="3">
            <div class="summary-card">
              <div class="summary-value">{{ summary.total_members }}</div>
              <div class="summary-label">전체 회원</div>
            </div>
          </v-col>
          <v-col cols="6" md="3">
            <div class="summary-card success">
              <div class="summary-value">{{ summary.paid_count }}</div>
              <div class="summary-label">납부 완료</div>
            </div>
          </v-col>
          <v-col cols="6" md="3">
            <div class="summary-card warning">
              <div class="summary-value">{{ summary.pending_count }}</div>
              <div class="summary-label">미납</div>
            </div>
          </v-col>
          <v-col cols="6" md="3">
            <div class="summary-card info">
              <div class="summary-value">
                {{ formatAmount(summary.total_paid) }} / {{ formatAmount(summary.total_due) }}
              </div>
              <div class="summary-label">납부 금액</div>
            </div>
          </v-col>
        </v-row>

        <!-- 납부 목록 -->
        <v-data-table
          :headers="headers"
          :items="payments"
          :loading="isLoading"
          class="payment-table"
          density="comfortable"
        >
          <template v-slot:item.status="{ item }">
            <v-chip
              :color="getStatusColor(item.status)"
              size="small"
              variant="tonal"
            >
              {{ getStatusLabel(item.status) }}
            </v-chip>
          </template>
          <template v-slot:item.amount="{ item }">
            <span :class="{ 'text-success': item.amount_paid >= item.amount_due }">
              {{ formatAmount(item.amount_paid) }} / {{ formatAmount(item.amount_due) }}
            </span>
          </template>
          <template v-slot:item.actions="{ item }">
            <v-btn
              v-if="item.status !== 'paid'"
              icon
              variant="text"
              size="small"
              color="success"
              @click="markAsPaid(item)"
            >
              <v-icon>mdi-check</v-icon>
              <v-tooltip activator="parent" location="top">납부 처리</v-tooltip>
            </v-btn>
            <v-btn
              icon
              variant="text"
              size="small"
              @click="openPaymentEditDialog(item)"
            >
              <v-icon>mdi-pencil</v-icon>
              <v-tooltip activator="parent" location="top">수정</v-tooltip>
            </v-btn>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <!-- 회비 설정 다이얼로그 -->
    <v-dialog v-model="showSettingDialog" max-width="500" persistent>
      <v-card>
        <v-card-title>회비 설정</v-card-title>
        <v-card-text>
          <v-form ref="settingFormRef" v-model="settingFormValid">
            <v-text-field
              v-model="settingForm.name"
              label="회비 이름"
              :rules="[v => !!v || '이름을 입력하세요']"
              variant="outlined"
              density="comfortable"
              placeholder="예: 2024년 월회비"
              class="mb-3"
            />
            <v-select
              v-model="settingForm.fee_type"
              :items="feeTypeOptions"
              label="회비 유형"
              variant="outlined"
              density="comfortable"
              class="mb-3"
            />
            <v-text-field
              v-model.number="settingForm.amount"
              label="금액 (원)"
              type="number"
              :rules="[v => v > 0 || '금액을 입력하세요']"
              variant="outlined"
              density="comfortable"
              class="mb-3"
            />
            <v-text-field
              v-model.number="settingForm.due_day"
              label="납부 기한일 (매월)"
              type="number"
              min="1"
              max="28"
              variant="outlined"
              density="comfortable"
              class="mb-3"
            />
            <v-textarea
              v-model="settingForm.description"
              label="설명 (선택)"
              variant="outlined"
              rows="2"
            />
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showSettingDialog = false">취소</v-btn>
          <v-btn
            color="primary"
            :loading="isSavingSetting"
            :disabled="!settingFormValid"
            @click="saveSetting"
          >
            저장
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 납부 수정 다이얼로그 -->
    <v-dialog v-model="showPaymentDialog" max-width="400" persistent>
      <v-card>
        <v-card-title>납부 정보 수정</v-card-title>
        <v-card-text v-if="editingPayment">
          <p class="mb-4">
            <strong>{{ editingPayment.member_name }}</strong> 님의 납부 정보
          </p>
          <v-text-field
            v-model.number="paymentForm.amount_paid"
            label="납부 금액"
            type="number"
            variant="outlined"
            density="comfortable"
            class="mb-3"
          />
          <v-select
            v-model="paymentForm.status"
            :items="statusOptions"
            label="납부 상태"
            variant="outlined"
            density="comfortable"
            class="mb-3"
          />
          <v-textarea
            v-model="paymentForm.note"
            label="메모"
            variant="outlined"
            rows="2"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showPaymentDialog = false">취소</v-btn>
          <v-btn color="primary" :loading="isSavingPayment" @click="savePayment">
            저장
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import apiClient from '@/api'

const props = defineProps({
  clubId: {
    type: Number,
    required: true,
  },
})

const feeSettings = ref([])
const selectedSetting = ref(null)
const payments = ref([])
const summary = ref(null)
const isLoading = ref(false)
const isGenerating = ref(false)
const isSavingSetting = ref(false)
const isSavingPayment = ref(false)

const showSettingDialog = ref(false)
const showPaymentDialog = ref(false)
const settingFormRef = ref(null)
const settingFormValid = ref(false)
const editingPayment = ref(null)

const currentYear = new Date().getFullYear()
const currentMonth = new Date().getMonth() + 1

const selectedYear = ref(currentYear)
const selectedMonth = ref(currentMonth)

const settingForm = ref({
  name: '',
  fee_type: 'monthly',
  amount: 30000,
  due_day: 10,
  description: '',
})

const paymentForm = ref({
  amount_paid: 0,
  status: 'pending',
  note: '',
})

const headers = [
  { title: '회원', key: 'member_name', sortable: true },
  { title: '납부 상태', key: 'status', sortable: true },
  { title: '납부 금액', key: 'amount', sortable: false },
  { title: '메모', key: 'note', sortable: false },
  { title: '', key: 'actions', sortable: false, align: 'end' },
]

const feeTypeOptions = [
  { title: '월회비', value: 'monthly' },
  { title: '연회비', value: 'yearly' },
  { title: '세션별', value: 'session' },
  { title: '일회성', value: 'one_time' },
]

const statusOptions = [
  { title: '미납', value: 'pending' },
  { title: '완납', value: 'paid' },
  { title: '일부 납부', value: 'partial' },
  { title: '면제', value: 'exempt' },
]

const yearOptions = computed(() => {
  const years = []
  for (let y = currentYear; y >= currentYear - 2; y--) {
    years.push({ title: `${y}년`, value: y })
  }
  return years
})

const monthOptions = computed(() => {
  return Array.from({ length: 12 }, (_, i) => ({
    title: `${i + 1}월`,
    value: i + 1,
  }))
})

function formatAmount(amount) {
  return new Intl.NumberFormat('ko-KR', {
    style: 'currency',
    currency: 'KRW',
  }).format(amount)
}

function getStatusColor(status) {
  const colors = {
    pending: 'warning',
    paid: 'success',
    partial: 'info',
    exempt: 'grey',
  }
  return colors[status] || 'grey'
}

function getStatusLabel(status) {
  const labels = {
    pending: '미납',
    paid: '완납',
    partial: '일부 납부',
    exempt: '면제',
  }
  return labels[status] || status
}

async function loadSettings() {
  try {
    const response = await apiClient.get(`/clubs/${props.clubId}/fees/settings`)
    feeSettings.value = response.data
    if (feeSettings.value.length > 0 && !selectedSetting.value) {
      selectSetting(feeSettings.value[0])
    }
  } catch (error) {
    console.error('회비 설정 로드 실패:', error)
  }
}

async function loadPayments() {
  if (!selectedSetting.value) return

  isLoading.value = true
  try {
    const params = {
      setting_id: selectedSetting.value.id,
      year: selectedYear.value,
    }
    if (selectedSetting.value.fee_type === 'monthly') {
      params.month = selectedMonth.value
    }

    const [paymentsRes, summaryRes] = await Promise.all([
      apiClient.get(`/clubs/${props.clubId}/fees/payments`, { params }),
      apiClient.get(`/clubs/${props.clubId}/fees/summary`, { params }),
    ])

    payments.value = paymentsRes.data
    summary.value = summaryRes.data
  } catch (error) {
    console.error('납부 기록 로드 실패:', error)
  } finally {
    isLoading.value = false
  }
}

function selectSetting(setting) {
  selectedSetting.value = setting
  loadPayments()
}

function openSettingDialog() {
  settingForm.value = {
    name: '',
    fee_type: 'monthly',
    amount: 30000,
    due_day: 10,
    description: '',
  }
  showSettingDialog.value = true
}

async function saveSetting() {
  if (!settingFormValid.value) return

  isSavingSetting.value = true
  try {
    await apiClient.post(`/clubs/${props.clubId}/fees/settings`, settingForm.value)
    await loadSettings()
    showSettingDialog.value = false
  } catch (error) {
    console.error('저장 실패:', error)
    const errorMessage = error.response?.data?.detail || '저장에 실패했습니다.'
    alert(errorMessage)
  } finally {
    isSavingSetting.value = false
  }
}

async function deleteSetting(id) {
  if (!confirm('이 회비 설정을 삭제하시겠습니까?')) return

  try {
    await apiClient.delete(`/clubs/${props.clubId}/fees/settings/${id}`)
    if (selectedSetting.value?.id === id) {
      selectedSetting.value = null
      payments.value = []
      summary.value = null
    }
    await loadSettings()
  } catch (error) {
    console.error('삭제 실패:', error)
    const errorMessage = error.response?.data?.detail || '삭제에 실패했습니다.'
    alert(errorMessage)
  }
}

async function generatePayments() {
  if (!selectedSetting.value) return

  isGenerating.value = true
  try {
    const params = {
      setting_id: selectedSetting.value.id,
      year: selectedYear.value,
    }
    if (selectedSetting.value.fee_type === 'monthly') {
      params.month = selectedMonth.value
    }

    await apiClient.post(`/clubs/${props.clubId}/fees/payments/generate`, null, { params })
    await loadPayments()
  } catch (error) {
    console.error('생성 실패:', error)
    const errorMessage = error.response?.data?.detail || '납부 기록 생성에 실패했습니다.'
    alert(errorMessage)
  } finally {
    isGenerating.value = false
  }
}

function openPaymentEditDialog(payment) {
  editingPayment.value = payment
  paymentForm.value = {
    amount_paid: payment.amount_paid,
    status: payment.status,
    note: payment.note || '',
  }
  showPaymentDialog.value = true
}

async function markAsPaid(payment) {
  try {
    await apiClient.put(`/clubs/${props.clubId}/fees/payments/${payment.id}`, {
      amount_paid: payment.amount_due,
      status: 'paid',
    })
    await loadPayments()
  } catch (error) {
    console.error('납부 처리 실패:', error)
  }
}

async function savePayment() {
  if (!editingPayment.value) return

  isSavingPayment.value = true
  try {
    await apiClient.put(
      `/clubs/${props.clubId}/fees/payments/${editingPayment.value.id}`,
      paymentForm.value
    )
    await loadPayments()
    showPaymentDialog.value = false
  } catch (error) {
    console.error('저장 실패:', error)
    const errorMessage = error.response?.data?.detail || '저장에 실패했습니다.'
    alert(errorMessage)
  } finally {
    isSavingPayment.value = false
  }
}

watch([selectedYear, selectedMonth], () => {
  if (selectedSetting.value) {
    loadPayments()
  }
})

onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.fee-management-tab {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.section-card {
  border: 1px solid #E2E8F0;
  border-radius: 16px;
}

.card-title {
  display: flex;
  align-items: center;
  font-size: 1.1rem;
  font-weight: 600;
  padding: 20px 24px;
  border-bottom: 1px solid #E2E8F0;
}

.fee-settings-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.fee-setting-chip {
  cursor: pointer;
}

.summary-row {
  margin: 0 -8px;
}

.summary-card {
  background: #F8FAFC;
  border-radius: 12px;
  padding: 16px;
  text-align: center;
}

.summary-card.success {
  background: #ECFDF5;
}

.summary-card.warning {
  background: #FEF3C7;
}

.summary-card.info {
  background: #EFF6FF;
}

.summary-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1E293B;
}

.summary-label {
  font-size: 0.8rem;
  color: #64748B;
  margin-top: 4px;
}

.payment-table {
  border: 1px solid #E2E8F0;
  border-radius: 8px;
}
</style>
