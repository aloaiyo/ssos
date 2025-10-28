<template>
  <v-container class="fill-height">
    <v-row align="center" justify="center">
      <v-col cols="12" class="text-center">
        <v-icon
          icon="mdi-alert-circle-outline"
          size="120"
          color="grey"
        ></v-icon>
        <h1 class="text-h2 font-weight-bold mt-4">404</h1>
        <p class="text-h5 mt-4">페이지를 찾을 수 없습니다</p>
        <p class="text-body-1 text-grey mt-2">
          요청하신 페이지가 존재하지 않거나 이동되었습니다.
        </p>
        <v-btn
          :to="{ name: 'home' }"
          color="primary"
          size="large"
          class="mt-6"
        >
          홈으로 돌아가기
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
// 404 페이지
</script>

<style scoped>
.fill-height {
  min-height: 70vh;
}
</style>
