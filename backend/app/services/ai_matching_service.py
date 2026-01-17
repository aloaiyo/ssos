"""
Gemini AI를 사용한 경기 매칭 서비스
"""
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import time, datetime, timedelta
from google import genai
from google.genai import types
from app.config import settings

logger = logging.getLogger(__name__)


class AIMatchingService:
    """AI 기반 경기 매칭 서비스"""

    def __init__(self):
        self.client = None
        if settings.GEMINI_API_KEY:
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        else:
            logger.warning("GEMINI_API_KEY가 설정되지 않았습니다")

    async def generate_matches(
        self,
        participants: List[Dict[str, Any]],
        session_config: Dict[str, Any],
        mode: str = "balanced"  # "balanced" or "random"
    ) -> Dict[str, Any]:
        """
        세션 참가자를 기반으로 경기 매칭을 생성합니다.

        Args:
            participants: 참가자 목록 (id, name, gender, match_type, ranking_info)
            session_config: 세션 설정 (start_time, end_time, match_duration, break_duration, num_courts)
            mode: 매칭 모드 ("balanced" - 실력 기반, "random" - 완전 랜덤)

        Returns:
            생성된 매치 목록
        """
        if not self.client:
            raise ValueError("Gemini API가 설정되지 않았습니다. GEMINI_API_KEY를 확인하세요.")

        # 참가자를 경기 유형별로 분류
        mens_doubles = [p for p in participants if p.get("match_type") == "mens_doubles"]
        womens_doubles = [p for p in participants if p.get("match_type") == "womens_doubles"]
        mixed_doubles = [p for p in participants if p.get("match_type") == "mixed_doubles"]

        prompt = self._build_prompt(
            mens_doubles=mens_doubles,
            womens_doubles=womens_doubles,
            mixed_doubles=mixed_doubles,
            session_config=session_config,
            mode=mode
        )

        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-lite',
                contents=[types.Content(parts=[types.Part(text=prompt)])]
            )

            result_text = response.text.strip()

            # JSON 블록 추출
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            result = json.loads(result_text)
            return self._validate_and_normalize(result, session_config)

        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 실패: {e}, 원본: {result_text}")
            raise ValueError(f"결과 파싱 실패: {str(e)}")
        except Exception as e:
            logger.error(f"매칭 생성 실패: {e}")
            raise ValueError(f"매칭 생성 실패: {str(e)}")

    def _build_prompt(
        self,
        mens_doubles: List[Dict],
        womens_doubles: List[Dict],
        mixed_doubles: List[Dict],
        session_config: Dict[str, Any],
        mode: str
    ) -> str:
        """Gemini 프롬프트 생성"""

        mode_instruction = ""
        if mode == "balanced":
            mode_instruction = """
매칭 규칙 (실력 균형 모드):
- 각 팀의 총 포인트가 비슷하도록 매칭합니다
- 승률이 높은 선수와 낮은 선수를 같은 팀에 배치하여 균형을 맞춥니다
- 경기별로 두 팀의 실력 차이를 최소화합니다
"""
        else:
            mode_instruction = """
매칭 규칙 (랜덤 모드):
- 완전히 무작위로 매칭합니다
- 실력은 고려하지 않습니다
"""

        # 참가자 정보를 문자열로 변환
        def format_participants(participants: List[Dict], label: str) -> str:
            if not participants:
                return f"{label}: 없음"

            lines = [f"{label} ({len(participants)}명):"]
            for p in participants:
                ranking = p.get("ranking", {})
                points = ranking.get("points", 0)
                wins = ranking.get("wins", 0)
                losses = ranking.get("losses", 0)
                win_rate = ranking.get("win_rate", 0)
                lines.append(f"  - ID: {p['id']}, 이름: {p['name']}, 성별: {p['gender']}, "
                           f"포인트: {points}, 승: {wins}, 패: {losses}, 승률: {win_rate:.1f}%")
            return "\n".join(lines)

        participants_info = "\n\n".join([
            format_participants(mens_doubles, "남자 복식 참가자"),
            format_participants(womens_doubles, "여자 복식 참가자"),
            format_participants(mixed_doubles, "혼합 복식 참가자")
        ])

        prompt = f"""테니스 동호회 경기 매칭을 생성해주세요.

## 세션 정보
- 시작 시간: {session_config['start_time']}
- 종료 시간: {session_config['end_time']}
- 경기 시간: {session_config['match_duration']}분
- 휴식 시간: {session_config['break_duration']}분
- 코트 수: {session_config['num_courts']}개

## 참가자 정보
{participants_info}

{mode_instruction}

## 중요한 규칙
1. 남자 복식은 남자 복식끼리만 경기합니다 (4명이 한 경기)
2. 여자 복식은 여자 복식끼리만 경기합니다 (4명이 한 경기)
3. 혼합 복식은 혼합 복식끼리만 경기합니다 (남1+여1 vs 남1+여1)
4. 복식은 한 팀에 2명이 필요합니다
5. 혼합 복식 팀은 반드시 남자 1명 + 여자 1명으로 구성합니다
6. 시간 내에 가능한 많은 경기를 배치합니다
7. 한 선수가 연속으로 경기하지 않도록 가능한 휴식을 줍니다
8. 코트를 효율적으로 사용합니다

## 응답 형식 (JSON만 반환)
{{
    "matches": [
        {{
            "match_number": 1,
            "match_type": "mens_doubles | womens_doubles | mixed_doubles",
            "court_number": 1,
            "scheduled_time": "HH:MM",
            "team_a": {{
                "player_ids": [참가자ID1, 참가자ID2],
                "player_names": ["이름1", "이름2"]
            }},
            "team_b": {{
                "player_ids": [참가자ID3, 참가자ID4],
                "player_names": ["이름3", "이름4"]
            }},
            "balance_score": 0.95
        }}
    ],
    "summary": {{
        "total_matches": 10,
        "mens_doubles_matches": 4,
        "womens_doubles_matches": 2,
        "mixed_doubles_matches": 4,
        "estimated_end_time": "HH:MM"
    }}
}}

JSON만 반환하고 다른 텍스트는 포함하지 마세요.
"""
        return prompt

    def _validate_and_normalize(
        self,
        result: Dict[str, Any],
        session_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """결과 검증 및 정규화"""
        matches = result.get("matches", [])
        normalized_matches = []

        for match in matches:
            match_type = match.get("match_type", "mens_doubles")
            if match_type not in ["mens_doubles", "womens_doubles", "mixed_doubles"]:
                match_type = "mens_doubles"

            normalized_match = {
                "match_number": int(match.get("match_number", 1)),
                "match_type": match_type,
                "court_number": int(match.get("court_number", 1)),
                "scheduled_time": match.get("scheduled_time", session_config["start_time"]),
                "team_a": {
                    "player_ids": match.get("team_a", {}).get("player_ids", []),
                    "player_names": match.get("team_a", {}).get("player_names", [])
                },
                "team_b": {
                    "player_ids": match.get("team_b", {}).get("player_ids", []),
                    "player_names": match.get("team_b", {}).get("player_names", [])
                },
                "balance_score": float(match.get("balance_score", 0.5))
            }
            normalized_matches.append(normalized_match)

        return {
            "matches": normalized_matches,
            "summary": result.get("summary", {
                "total_matches": len(normalized_matches),
                "mens_doubles_matches": sum(1 for m in normalized_matches if m["match_type"] == "mens_doubles"),
                "womens_doubles_matches": sum(1 for m in normalized_matches if m["match_type"] == "womens_doubles"),
                "mixed_doubles_matches": sum(1 for m in normalized_matches if m["match_type"] == "mixed_doubles"),
            })
        }


# 싱글톤 인스턴스
ai_matching_service = AIMatchingService()
