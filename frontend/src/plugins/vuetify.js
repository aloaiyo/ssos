// Vuetify 설정 - 2024-2025 Modern UI Trends
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import '@mdi/font/css/materialdesignicons.css'

const vuetify = createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          // 모던 그린 팔레트 (더 세련된 톤)
          primary: '#10B981',           // Emerald 500 (메인)
          'primary-darken-1': '#059669', // Emerald 600
          'primary-lighten-1': '#34D399', // Emerald 400
          secondary: '#6366F1',          // Indigo 500 (포인트)
          'secondary-darken-1': '#4F46E5',
          accent: '#F59E0B',             // Amber 500
          success: '#22C55E',            // Green 500
          warning: '#F59E0B',            // Amber 500
          error: '#EF4444',              // Red 500
          info: '#3B82F6',               // Blue 500

          // 배경 & 서피스 (더 밝고 깔끔)
          background: '#F8FAFC',         // Slate 50
          surface: '#FFFFFF',
          'surface-variant': '#F1F5F9',  // Slate 100
          'surface-light': '#FFFFFF',

          // 텍스트
          'on-surface': '#1E293B',       // Slate 800
          'on-surface-variant': '#64748B', // Slate 500
          'on-primary': '#FFFFFF',
          'on-secondary': '#FFFFFF',

          // 추가 컬러
          'grey-light': '#E2E8F0',       // Slate 200
          'grey-medium': '#94A3B8',      // Slate 400
        },
      },
      dark: {
        colors: {
          primary: '#34D399',
          'primary-darken-1': '#10B981',
          'primary-lighten-1': '#6EE7B7',
          secondary: '#818CF8',
          accent: '#FBBF24',
          success: '#4ADE80',
          warning: '#FBBF24',
          error: '#F87171',
          info: '#60A5FA',
          background: '#0F172A',          // Slate 900
          surface: '#1E293B',             // Slate 800
          'surface-variant': '#334155',   // Slate 700
          'on-surface': '#F1F5F9',
          'on-surface-variant': '#94A3B8',
          'on-primary': '#0F172A',
          'on-secondary': '#0F172A',
        },
      },
    },
  },
  defaults: {
    VBtn: {
      rounded: 'lg',
      fontWeight: '600',
      elevation: 0,
    },
    VTextField: {
      variant: 'outlined',
      density: 'comfortable',
      rounded: 'lg',
    },
    VSelect: {
      variant: 'outlined',
      density: 'comfortable',
      rounded: 'lg',
    },
    VCard: {
      rounded: 'xl',
      elevation: 0,
    },
    VChip: {
      rounded: 'lg',
    },
    VAlert: {
      rounded: 'lg',
    },
    VList: {
      rounded: 'lg',
    },
  },
})

export default vuetify
