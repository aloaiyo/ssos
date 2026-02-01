import js from '@eslint/js'
import pluginVue from 'eslint-plugin-vue'

export default [
  js.configs.recommended,
  ...pluginVue.configs['flat/recommended'],
  {
    files: ['**/*.{js,vue}'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: {
        // Browser globals
        window: 'readonly',
        document: 'readonly',
        navigator: 'readonly',
        localStorage: 'readonly',
        sessionStorage: 'readonly',
        fetch: 'readonly',
        console: 'readonly',
        setTimeout: 'readonly',
        setInterval: 'readonly',
        clearTimeout: 'readonly',
        clearInterval: 'readonly',
        Promise: 'readonly',
        FormData: 'readonly',
        File: 'readonly',
        Blob: 'readonly',
        URL: 'readonly',
        URLSearchParams: 'readonly',
        alert: 'readonly',
        confirm: 'readonly',
        // Node.js globals (for config files)
        process: 'readonly',
        __dirname: 'readonly',
      },
    },
    rules: {
      // console.log 경고 (production에서는 vite가 제거)
      'no-console': ['warn', { allow: ['warn', 'error'] }],
      // 미사용 변수 경고
      'no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      // Vue 규칙 완화
      'vue/multi-word-component-names': 'off',
      'vue/no-v-html': 'warn', // v-html 사용 시 경고
      'vue/require-default-prop': 'off',
      'vue/max-attributes-per-line': 'off',
      'vue/singleline-html-element-content-newline': 'off',
      'vue/html-self-closing': 'off',
      'vue/valid-v-slot': ['error', { allowModifiers: true }], // Vuetify scoped slots
    },
  },
  {
    // 설정 파일에서는 console 허용
    files: ['vite.config.js', 'eslint.config.js'],
    rules: {
      'no-console': 'off',
    },
  },
]
