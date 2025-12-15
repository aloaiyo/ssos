<template>
    <v-container>
        <v-row justify="center">
            <v-col cols="12" md="8" lg="7">
                <v-card class="mt-6" rounded="xl">
                    <v-card-title class="text-h5 pa-6">
                        동호회 생성
                    </v-card-title>

                    <v-card-text class="px-6 pb-6">
                        <v-form ref="form" v-model="valid" @submit.prevent="handleSubmit">
                            <!-- 기본 정보 -->
                            <div class="section-title mb-3">기본 정보</div>

                            <v-text-field
                                v-model="name"
                                label="동호회 이름"
                                variant="outlined"
                                :rules="[v => !!v || '동호회 이름을 입력해주세요']"
                                required
                                class="mb-3"
                            />

                            <v-textarea
                                v-model="description"
                                label="동호회 소개"
                                variant="outlined"
                                rows="3"
                                class="mb-4"
                            />

                            <v-row>
                                <v-col cols="12" sm="6">
                                    <v-text-field
                                        v-model="location"
                                        label="활동 장소"
                                        variant="outlined"
                                        placeholder="예: OO테니스장"
                                        prepend-inner-icon="mdi-map-marker"
                                    />
                                </v-col>
                                <v-col cols="6" sm="3">
                                    <v-text-field
                                        v-model.number="defaultNumCourts"
                                        label="코트 수"
                                        type="number"
                                        min="1"
                                        max="20"
                                        variant="outlined"
                                    />
                                </v-col>
                                <v-col cols="6" sm="3">
                                    <v-select
                                        v-model="defaultMatchDuration"
                                        :items="matchDurationOptions"
                                        label="경기 시간"
                                        variant="outlined"
                                    />
                                </v-col>
                            </v-row>

                            <v-divider class="my-4" />

                            <!-- 정기 활동 일정 -->
                            <WeeklySchedulePicker v-model="schedules" class="mb-4" />

                            <v-alert v-if="error" type="error" variant="tonal" class="mb-4" closable
                                @click:close="error = ''">
                                {{ error }}
                            </v-alert>

                            <div class="d-flex gap-4 mt-4">
                                <v-btn variant="text" size="large" @click="router.back()">
                                    취소
                                </v-btn>
                                <v-spacer></v-spacer>
                                <v-btn type="submit" color="primary" size="large" :loading="isLoading"
                                    :disabled="!valid">
                                    생성
                                </v-btn>
                            </div>
                        </v-form>
                    </v-card-text>
                </v-card>
            </v-col>
        </v-row>
    </v-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useClubStore } from '@/stores/club'
import WeeklySchedulePicker from '@/components/common/WeeklySchedulePicker.vue'

const router = useRouter()
const clubStore = useClubStore()

const form = ref(null)
const valid = ref(false)
const error = ref('')
const isLoading = ref(false)

// 기본 정보
const name = ref('')
const description = ref('')
const location = ref('')
const defaultNumCourts = ref(null)
const defaultMatchDuration = ref(30)

// 정기 활동 스케줄
const schedules = ref([])

// 옵션
const matchDurationOptions = [
    { title: '20분', value: 20 },
    { title: '25분', value: 25 },
    { title: '30분', value: 30 },
    { title: '40분', value: 40 },
    { title: '50분', value: 50 },
    { title: '60분', value: 60 },
]

async function handleSubmit() {
    const { valid: isValid } = await form.value.validate()

    if (!isValid) return

    isLoading.value = true
    error.value = ''

    try {
        const clubData = {
            name: name.value,
            description: description.value || null,
            default_num_courts: defaultNumCourts.value || null,
            default_match_duration: defaultMatchDuration.value,
            location: location.value || null,
            schedules: schedules.value.length > 0 ? schedules.value : null,
        }

        const club = await clubStore.createClub(clubData)

        // 생성 성공 시 동호회 설정 페이지로 이동
        router.push({ name: 'club-manage', params: { id: club.id } })
    } catch (e) {
        error.value = e.response?.data?.detail || '동호회 생성에 실패했습니다.'
    } finally {
        isLoading.value = false
    }
}
</script>

<style scoped>
.section-title {
    font-size: 1rem;
    font-weight: 600;
    color: #1E293B;
}
</style>
