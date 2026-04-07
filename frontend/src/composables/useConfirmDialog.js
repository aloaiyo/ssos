import { ref } from 'vue'

// 전역 상태 (앱 전체에서 하나의 스낵바/다이얼로그 공유)
const snackbar = ref(false)
const snackbarMessage = ref('')
const snackbarColor = ref('error')

const confirmDialog = ref(false)
const confirmMessage = ref('')
const confirmTitle = ref('확인')
let confirmResolve = null

/**
 * Vuetify 기반 알림/확인 다이얼로그 composable
 * alert() / confirm() 대체
 */
export function useConfirmDialog() {
  /**
   * 스낵바로 알림 표시 (alert 대체)
   * @param {string} message - 알림 메시지
   * @param {string} color - 스낵바 색상 (기본: error)
   */
  function showAlert(message, color = 'error') {
    snackbarMessage.value = message
    snackbarColor.value = color
    snackbar.value = true
  }

  /**
   * 확인 다이얼로그 표시 (confirm 대체)
   * @param {string} message - 확인 메시지
   * @param {string} title - 다이얼로그 제목
   * @returns {Promise<boolean>} 확인 시 true, 취소 시 false
   */
  function showConfirm(message, title = '확인') {
    confirmMessage.value = message
    confirmTitle.value = title
    confirmDialog.value = true
    return new Promise((resolve) => {
      confirmResolve = resolve
    })
  }

  function handleConfirm() {
    confirmDialog.value = false
    if (confirmResolve) confirmResolve(true)
    confirmResolve = null
  }

  function handleCancel() {
    confirmDialog.value = false
    if (confirmResolve) confirmResolve(false)
    confirmResolve = null
  }

  function closeSnackbar() {
    snackbar.value = false
  }

  return {
    // 스낵바 상태
    snackbar,
    snackbarMessage,
    snackbarColor,
    closeSnackbar,
    // 확인 다이얼로그 상태
    confirmDialog,
    confirmMessage,
    confirmTitle,
    // 메서드
    showAlert,
    showConfirm,
    handleConfirm,
    handleCancel,
  }
}
