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

const show = ref(false)
const message = ref('')
const timeout = ref(5000)

// 모든 스토어의 에러 감시
const authStore = useAuthStore()
const clubStore = useClubStore()
const memberStore = useMemberStore()

const { error: authError } = storeToRefs(authStore)
const { error: clubError } = storeToRefs(clubStore)
const { error: memberError } = storeToRefs(memberStore)

// 에러 메시지 표시
watch([authError, clubError, memberError], ([auth, club, member]) => {
  const error = auth || club || member
  if (error) {
    message.value = error
    show.value = true
  }
})

// 닫기
function close() {
  show.value = false
  authStore.error = null
  clubStore.error = null
  memberStore.error = null
}
</script>
