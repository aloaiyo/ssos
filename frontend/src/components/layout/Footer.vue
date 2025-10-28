<template>
  <v-footer
    app
    color="grey-lighten-4"
    elevation="4"
    class="px-4 py-3"
  >
    <v-row>
      <v-col cols="12" md="6" class="text-center text-md-left">
        <span class="text-body-2">
          &copy; {{ currentYear }} 테니스 동호회 관리 시스템
        </span>
      </v-col>
      <v-col cols="12" md="6" class="text-center text-md-right">
        <span class="text-body-2 text-grey">
          Version 1.0.0 (Phase 1)
        </span>
      </v-col>
    </v-row>
  </v-footer>
</template>

<script setup>
import { computed } from 'vue'

const currentYear = computed(() => new Date().getFullYear())
</script>

<style scoped>
.v-footer {
  border-top: 1px solid rgba(0, 0, 0, 0.12);
}
</style>
