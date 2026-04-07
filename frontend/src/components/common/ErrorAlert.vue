<template>
  <v-snackbar
    v-model="show"
    :timeout="timeout"
    color="error"
    location="top"
    multi-line
  >
    <div class="d-flex align-center">
      <v-icon start>mdi-alert-circle</v-icon>
      {{ message }}
    </div>
    <template v-slot:actions>
      <v-btn
        color="white"
        variant="text"
        @click="close"
      >
        닫기
      </v-btn>
    </template>
  </v-snackbar>
</template>

<script setup>
import { ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { useClubStore } from '@/stores/club'
import { useMemberStore } from '@/stores/member'
import { useSessionStore } from '@/stores/session'
import { useMatchStore } from '@/stores/match'
import { useSeasonStore } from '@/stores/season'
import { useRankingStore } from '@/stores/ranking'

const show = ref(false)
const message = ref('')
const timeout = ref(5000)

// 모든 스토어의 에러 감시
const authStore = useAuthStore()
const clubStore = useClubStore()
const memberStore = useMemberStore()
const sessionStore = useSessionStore()
const matchStore = useMatchStore()
const seasonStore = useSeasonStore()
const rankingStore = useRankingStore()

const { error: authError } = storeToRefs(authStore)
const { error: clubError } = storeToRefs(clubStore)
const { error: memberError } = storeToRefs(memberStore)
const { error: sessionError } = storeToRefs(sessionStore)
const { error: matchError } = storeToRefs(matchStore)
const { error: seasonError } = storeToRefs(seasonStore)
const { error: rankingError } = storeToRefs(rankingStore)

// 에러 메시지 표시
watch(
  [authError, clubError, memberError, sessionError, matchError, seasonError, rankingError],
  ([auth, club, member, session, match, season, ranking]) => {
    const error = auth || club || member || session || match || season || ranking
    if (error) {
      message.value = error
      show.value = true
    }
  }
)

// 닫기 — 모든 스토어 에러를 일관되게 초기화
function close() {
  show.value = false
  authStore.clearError()
  clubStore.clearError()
  memberStore.clearError()
  sessionStore.clearError()
  matchStore.clearError()
  seasonStore.clearError()
  rankingStore.clearError()
}
</script>
