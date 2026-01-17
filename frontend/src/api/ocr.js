// OCR 관련 API
import apiClient from './index'

export default {
  /**
   * 경기 결과지 이미지에서 결과 추출
   * @param {number} clubId - 동호회 ID
   * @param {File} file - 이미지 파일
   * @returns {Promise} 추출된 경기 결과
   */
  extractMatchResults(clubId, file) {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post(`/clubs/${clubId}/ocr/extract`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  /**
   * 추출된 경기 결과 저장
   * @param {number} clubId - 동호회 ID
   * @param {Object} data - 저장 데이터
   * @param {number} data.season_id - 시즌 ID (선택)
   * @param {number} data.session_id - 세션 ID (create_new_session이 false일 때 필수)
   * @param {boolean} data.create_new_session - 새 세션 생성 여부
   * @param {string} data.session_title - 새 세션 제목
   * @param {string} data.session_date - 새 세션 날짜 (YYYY-MM-DD)
   * @param {string} data.session_start_time - 시작 시간 (HH:MM:SS)
   * @param {string} data.session_end_time - 종료 시간 (HH:MM:SS)
   * @param {string} data.session_location - 장소
   * @param {Array} data.matches - 경기 목록
   * @returns {Promise}
   */
  saveMatchResults(clubId, data) {
    return apiClient.post(`/clubs/${clubId}/ocr/save-matches`, data)
  }
}
