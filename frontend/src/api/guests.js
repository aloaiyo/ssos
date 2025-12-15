import api from './index'

/**
 * 게스트 목록 조회
 */
export const getGuests = (clubId) => {
  return api.get(`/clubs/${clubId}/guests`)
}

/**
 * 게스트 생성
 */
export const createGuest = (clubId, guestData) => {
  return api.post(`/clubs/${clubId}/guests`, guestData)
}

/**
 * 게스트 상세 조회
 */
export const getGuest = (clubId, guestId) => {
  return api.get(`/clubs/${clubId}/guests/${guestId}`)
}

/**
 * 게스트 수정
 */
export const updateGuest = (clubId, guestId, guestData) => {
  return api.put(`/clubs/${clubId}/guests/${guestId}`, guestData)
}

/**
 * 게스트 삭제
 */
export const deleteGuest = (clubId, guestId) => {
  return api.delete(`/clubs/${clubId}/guests/${guestId}`)
}
