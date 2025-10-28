<template>
  <v-overlay :model-value="true" class="align-center justify-center">
    <v-progress-circular
      :size="70"
      :width="7"
      color="primary"
      indeterminate
    >
    </v-progress-circular>
    <div class="text-h6 text-white mt-4">로딩 중...</div>
  </v-overlay>
</template>

<script setup>
// 전역 로딩 스피너 컴포넌트
</script>

<style scoped>
.v-overlay {
  z-index: 9999;
}
</style>
