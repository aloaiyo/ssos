<template>
  <v-navigation-drawer
    v-model="drawer"
    :permanent="!isMobile"
    :temporary="isMobile"
    width="260"
    class="nav-drawer"
  >
    <!-- 로고 헤더 -->
    <div class="drawer-header">
      <router-link to="/" class="logo-link">
        <div class="logo-icon">
          <v-icon size="24">mdi-tennis</v-icon>
        </div>
        <span class="logo-text">{{ selectedClubName }}</span>
      </router-link>
    </div>

    <v-divider class="mx-4 mb-2"></v-divider>

    <!-- 메인 메뉴 -->
    <v-list nav density="comfortable" class="px-2">
      <v-list-item
        v-for="item in menuItems"
        :key="item.title"
        :to="item.to"
        :prepend-icon="item.icon"
        rounded="lg"
        class="nav-item mb-1"
        exact
      >
        <v-list-item-title class="nav-item-title">{{ item.title }}</v-list-item-title>
      </v-list-item>
    </v-list>

    <!-- 일정 & 경기 메뉴 -->
    <div class="section-label">일정 & 경기</div>
    <v-list nav density="comfortable" class="px-2">
      <v-list-item
        v-for="item in scheduleMenuItems"
        :key="item.title"
        :to="item.to"
        :prepend-icon="item.icon"
        rounded="lg"
        class="nav-item mb-1"
      >
        <v-list-item-title class="nav-item-title">{{ item.title }}</v-list-item-title>
      </v-list-item>
    </v-list>

    <!-- 하단 영역 -->
    <template v-slot:append>
      <v-divider class="mx-4 mb-2"></v-divider>
      <v-list nav density="comfortable" class="px-2 pb-4">
        <v-list-item
          prepend-icon="mdi-cog-outline"
          rounded="lg"
          class="nav-item"
          @click="goToSettings"
        >
          <v-list-item-title class="nav-item-title">설정</v-list-item-title>
        </v-list-item>
      </v-list>
    </template>
  </v-navigation-drawer>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useClubStore } from '@/stores/club'

const clubStore = useClubStore()
const { clubs, selectedClubId } = storeToRefs(clubStore)

const drawer = ref(true) // 기본 열림
const isMobile = ref(false)

// 선택된 클럽 이름
const selectedClubName = computed(() => {
  if (!selectedClubId.value) return '동호회'
  const club = clubs.value.find(c => c.id === parseInt(selectedClubId.value))
  return club?.name || '동호회'
})

// 반응형 체크
function checkMobile() {
  isMobile.value = window.innerWidth < 1024
  // 모바일에서는 기본 닫힘
  if (isMobile.value) {
    drawer.value = false
  } else {
    drawer.value = true
  }
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})

// 기본 메뉴
const menuItems = [
  { title: '홈', icon: 'mdi-home-outline', to: { name: 'home' } },
  { title: '회원 목록', icon: 'mdi-account-multiple-outline', to: { name: 'member-list' } },
]

// 일정 & 경기 메뉴
const scheduleMenuItems = [
  { title: '시즌', icon: 'mdi-calendar-star', to: { name: 'season-list' } },
  { title: '세션', icon: 'mdi-calendar-outline', to: { name: 'session-list' } },
  { title: '경기 기록', icon: 'mdi-tennis', to: { name: 'match-list' } },
  { title: '랭킹', icon: 'mdi-trophy-outline', to: { name: 'ranking-list' } },
]

function goToSettings() {
  console.log('설정 페이지')
}

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
    default: true,
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

<style scoped>
.nav-drawer {
  background: #FFFFFF !important;
  border-right: 1px solid #F1F5F9 !important;
}

.drawer-header {
  padding: 20px 16px;
}

.logo-link {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
}

.logo-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: linear-gradient(135deg, #10B981 0%, #059669 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1E293B;
}

.section-label {
  padding: 16px 20px 8px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #94A3B8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.nav-item {
  margin-bottom: 2px;
}

.nav-item :deep(.v-list-item__prepend) {
  color: #64748B;
}

.nav-item :deep(.v-list-item-title) {
  font-size: 0.9rem;
  font-weight: 500;
  color: #475569;
}

.nav-item:hover {
  background: #F8FAFC;
}

.nav-item:hover :deep(.v-list-item__prepend) {
  color: #10B981;
}

.nav-item.v-list-item--active {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%);
}

.nav-item.v-list-item--active :deep(.v-list-item__prepend) {
  color: #10B981;
}

.nav-item.v-list-item--active :deep(.v-list-item-title) {
  color: #10B981;
  font-weight: 600;
}
</style>
