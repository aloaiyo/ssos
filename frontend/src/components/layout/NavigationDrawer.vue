<template>
  <v-navigation-drawer
    v-model="drawer"
    temporary
    width="280"
  >
    <v-list>
      <!-- 헤더 -->
      <v-list-item class="px-2 py-3">
        <v-list-item-title class="text-h6 font-weight-bold">
          메뉴
        </v-list-item-title>
      </v-list-item>
      <v-divider></v-divider>

      <!-- 메뉴 아이템 -->
      <v-list-item
        v-for="item in menuItems"
        :key="item.title"
        :to="item.to"
        :prepend-icon="item.icon"
        :title="item.title"
        exact
      ></v-list-item>

      <!-- 관리자 메뉴 -->
      <template v-if="isAdmin">
        <v-divider></v-divider>
        <v-list-subheader>관리</v-list-subheader>
        <v-list-item
          v-for="item in adminMenuItems"
          :key="item.title"
          :to="item.to"
          :prepend-icon="item.icon"
          :title="item.title"
        ></v-list-item>
      </template>

      <!-- Phase 2 메뉴 (비활성화) -->
      <v-divider></v-divider>
      <v-list-subheader>Phase 2 (예정)</v-list-subheader>
      <v-list-item
        v-for="item in phase2MenuItems"
        :key="item.title"
        :prepend-icon="item.icon"
        :title="item.title"
        disabled
      ></v-list-item>
    </v-list>
  </v-navigation-drawer>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const { isAdmin } = storeToRefs(authStore)

const drawer = ref(false)

// 기본 메뉴
const menuItems = [
  { title: '홈', icon: 'mdi-home', to: { name: 'home' } },
  { title: '동호회 목록', icon: 'mdi-account-group', to: { name: 'club-list' } },
  { title: '회원 목록', icon: 'mdi-account-multiple', to: { name: 'member-list' } },
]

// 관리자 메뉴
const adminMenuItems = computed(() => [
  { title: '동호회 관리', icon: 'mdi-cog', to: { name: 'club-manage' } },
  { title: '회원 관리', icon: 'mdi-account-cog', to: { name: 'member-manage' } },
])

// Phase 2 메뉴
const phase2MenuItems = [
  { title: '세션 관리', icon: 'mdi-calendar' },
  { title: '매칭 생성', icon: 'mdi-tennis' },
  { title: '결과 입력', icon: 'mdi-clipboard-text' },
  { title: '랭킹', icon: 'mdi-trophy' },
]

// 외부에서 드로어 열기
defineExpose({
  open: () => { drawer.value = true },
  close: () => { drawer.value = false },
  toggle: () => { drawer.value = !drawer.value },
})

// 부모 컴포넌트에서 이벤트 수신
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue'])

watch(() => props.modelValue, (val) => {
  drawer.value = val
})

watch(drawer, (val) => {
  emit('update:modelValue', val)
})
</script>
