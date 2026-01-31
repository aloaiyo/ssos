"""
Gemini API를 사용한 경기 결과지 OCR 서비스

google-genai SDK 사용 (pip install google-genai)
https://ai.google.dev/gemini-api/docs
"""
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Lazy import to avoid import errors when API key is not set
_client = None


def _get_client():
    """Lazy initialization of Gemini client"""
    global _client
    if _client is None:
        from app.config import settings
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다")

        from google import genai
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


class OCRService:
    """경기 결과지 이미지에서 데이터를 추출하는 서비스"""

    def __init__(self):
        pass  # Lazy initialization - client created on first use

    async def extract_match_results(self, image_data: bytes, mime_type: str = "image/jpeg") -> Dict[str, Any]:
        """
        이미지에서 경기 결과를 추출합니다.

        Args:
            image_data: 이미지 바이너리 데이터
            mime_type: 이미지 MIME 타입

        Returns:
            추출된 경기 결과 데이터
        """
        from google.genai import types

        client = _get_client()

        prompt = """
이 이미지는 테니스/배드민턴 경기 결과지입니다. 이미지에서 경기 결과 정보를 추출해주세요.

다음 JSON 형식으로 결과를 반환해주세요:
{
    "date": "YYYY-MM-DD 형식의 경기 날짜 (없으면 null)",
    "location": "경기 장소 (없으면 null)",
    "matches": [
        {
            "match_type": "mens_doubles | mixed_doubles | singles 중 하나",
            "court_number": 코트 번호 (숫자, 없으면 1),
            "team_a": {
                "players": ["선수1 이름", "선수2 이름"],
                "score": 점수 (숫자)
            },
            "team_b": {
                "players": ["선수1 이름", "선수2 이름"],
                "score": 점수 (숫자)
            }
        }
    ]
}

추출 규칙:
1. 복식 경기는 각 팀에 2명의 선수가 있습니다
2. 단식 경기는 각 팀에 1명의 선수가 있습니다
3. 남복(남자복식)은 "mens_doubles", 혼복(혼합복식)은 "mixed_doubles", 단식은 "singles"입니다
4. 점수가 더 높은 팀이 승자입니다
5. 이름은 가능한 정확하게 추출하되, 읽기 어려우면 최선의 추측을 해주세요
6. 코트 번호가 명시되어 있으면 추출하고, 없으면 순서대로 1, 2, 3...으로 지정하세요

JSON만 반환하고 다른 텍스트는 포함하지 마세요.
"""

        result_text = ""
        try:
            # google-genai SDK 사용 (최신 API 문서 기반)
            # https://ai.google.dev/gemini-api/docs/image-understanding
            response = client.models.generate_content(
                model='gemini-2.5-flash',  # 이미지 처리 지원, 저렴한 모델
                contents=[
                    types.Part.from_bytes(data=image_data, mime_type=mime_type),
                    prompt
                ]
            )

            # 응답에서 JSON 추출
            result_text = response.text.strip()

            # JSON 블록 추출 (```json ... ``` 형식 처리)
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            # JSON 파싱
            result = json.loads(result_text)

            # 결과 검증 및 정규화
            return self._normalize_results(result)

        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 실패: {e}, 원본: {result_text}")
            raise ValueError(f"결과 파싱 실패: {str(e)}")
        except Exception as e:
            logger.error(f"OCR 처리 실패: {e}")
            raise ValueError(f"이미지 분석 실패: {str(e)}")

    def _normalize_results(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """추출된 결과를 정규화합니다"""
        normalized = {
            "date": result.get("date"),
            "location": result.get("location"),
            "matches": []
        }

        for match in result.get("matches", []):
            match_type = match.get("match_type", "mens_doubles")
            if match_type not in ["mens_doubles", "mixed_doubles", "singles"]:
                match_type = "mens_doubles"

            team_a = match.get("team_a", {})
            team_b = match.get("team_b", {})

            normalized_match = {
                "match_type": match_type,
                "court_number": int(match.get("court_number", 1)),
                "team_a": {
                    "players": team_a.get("players", []),
                    "score": int(team_a.get("score", 0))
                },
                "team_b": {
                    "players": team_b.get("players", []),
                    "score": int(team_b.get("score", 0))
                }
            }
            normalized["matches"].append(normalized_match)

        return normalized


# 싱글톤 인스턴스
ocr_service = OCRService()
