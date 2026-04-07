/**
 * API 응답 타입 정의 (JSDoc)
 *
 * IDE 자동완성 및 타입 검증을 위한 타입 정의 파일입니다.
 * 사용: @type {import('@/types/api').Club}
 */

// ============================================================
// User / Auth
// ============================================================

/**
 * @typedef {Object} User
 * @property {number} id
 * @property {string} email
 * @property {string} name
 * @property {'male'|'female'|null} gender
 * @property {string|null} birth_date
 * @property {'super_admin'|'user'} role
 * @property {boolean} is_premium
 * @property {string|null} cognito_sub
 * @property {string} created_at
 */

/**
 * @typedef {Object} AuthResponse
 * @property {User} user
 * @property {string} [message]
 */

// ============================================================
// Club
// ============================================================

/**
 * @typedef {Object} Club
 * @property {number} id
 * @property {string} name
 * @property {string|null} description
 * @property {string|null} location
 * @property {number|null} default_num_courts
 * @property {number|null} default_match_duration
 * @property {number|null} default_break_duration
 * @property {'manager'|'member'} [my_role]
 * @property {string} created_at
 */

/**
 * @typedef {Object} ClubMember
 * @property {number} id
 * @property {number} user_id
 * @property {string|null} user_name
 * @property {string|null} nickname
 * @property {'male'|'female'} gender
 * @property {'manager'|'member'} role
 * @property {'active'|'inactive'} status
 */

// ============================================================
// Season
// ============================================================

/**
 * @typedef {Object} Season
 * @property {number} id
 * @property {string} name
 * @property {string|null} description
 * @property {string} start_date
 * @property {string} end_date
 * @property {'upcoming'|'active'|'completed'} status
 * @property {string} created_at
 */

/**
 * @typedef {Object} SeasonRanking
 * @property {number} member_id
 * @property {string} member_name
 * @property {number} rank
 * @property {number} points
 * @property {number} total_matches
 * @property {number} wins
 * @property {number} draws
 * @property {number} losses
 * @property {number|null} win_rate
 */

/**
 * @typedef {Object} SeasonRankingResponse
 * @property {Season} season
 * @property {SeasonRanking[]} rankings
 */

// ============================================================
// Session
// ============================================================

/**
 * @typedef {Object} Session
 * @property {number} id
 * @property {string|null} title
 * @property {string} date
 * @property {string} start_time
 * @property {string} end_time
 * @property {string|null} location
 * @property {'league'|'tournament'} session_type
 * @property {'scheduled'|'in_progress'|'completed'|'cancelled'} status
 * @property {number} num_courts
 * @property {number|null} match_duration_minutes
 * @property {number|null} break_duration_minutes
 * @property {number|null} season_id
 * @property {string|null} season_name
 * @property {number} participant_count
 * @property {Match[]} [matches]
 * @property {string} created_at
 */

/**
 * @typedef {Object} SessionParticipant
 * @property {number} id
 * @property {string|null} name
 * @property {'male'|'female'|null} gender
 * @property {{id: number, user: User}|null} [member]
 * @property {{id: number, name: string, gender: string}|null} [guest]
 */

/**
 * @typedef {Object} MyParticipation
 * @property {boolean} is_participating
 * @property {boolean} is_member
 * @property {number|null} member_id
 * @property {number|null} participant_id
 */

// ============================================================
// Match
// ============================================================

/**
 * @typedef {Object} Match
 * @property {number} id
 * @property {'MENS_DOUBLES'|'WOMENS_DOUBLES'|'MIXED_DOUBLES'|'SINGLES'} match_type
 * @property {number} court_number
 * @property {string|null} scheduled_time
 * @property {'pending'|'in_progress'|'completed'} status
 * @property {number|null} score_a
 * @property {number|null} score_b
 * @property {MatchParticipant[]} [participants]
 * @property {{team_a: number, team_b: number}|null} [score]
 * @property {MatchPlayer[]} [team_a]
 * @property {MatchPlayer[]} [team_b]
 * @property {'A'|'B'|null} [winner_team]
 */

/**
 * @typedef {Object} MatchParticipant
 * @property {number} id
 * @property {'A'|'B'} team
 * @property {string|null} name
 * @property {{id: number, user: {name: string}}|null} [member]
 */

/**
 * @typedef {Object} MatchPlayer
 * @property {string} name
 * @property {number|null} user_id
 */

/**
 * @typedef {Object} AIMatchPreview
 * @property {string} match_type
 * @property {number} court_number
 * @property {string|null} scheduled_time
 * @property {{player_names: string[]}} team_a
 * @property {{player_names: string[]}} team_b
 */

/**
 * @typedef {Object} AIGenerateResponse
 * @property {AIMatchPreview[]} matches
 * @property {{total_matches: number, mens_doubles_matches: number, womens_doubles_matches: number, mixed_doubles_matches: number}} summary
 */

// ============================================================
// Ranking
// ============================================================

/**
 * @typedef {Object} Ranking
 * @property {number} member_id
 * @property {string} member_name
 * @property {number} rank
 * @property {number} points
 * @property {number} total_matches
 * @property {number} wins
 * @property {number} losses
 * @property {number} draws
 * @property {number|null} win_rate
 */

// ============================================================
// OCR
// ============================================================

/**
 * @typedef {Object} OCRMatch
 * @property {string} match_type
 * @property {{players: string[], score: number}} team_a
 * @property {{players: string[], score: number}} team_b
 */

/**
 * @typedef {Object} OCRResult
 * @property {string|null} date
 * @property {string|null} location
 * @property {OCRMatch[]} matches
 */

// ============================================================
// Guest
// ============================================================

/**
 * @typedef {Object} Guest
 * @property {number} id
 * @property {string} name
 * @property {'male'|'female'} gender
 * @property {string|null} phone
 */

export {}
