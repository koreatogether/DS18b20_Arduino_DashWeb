"""UI 모드(Enum) 정의 및 헬퍼.

Raw 문자열 'v1', 'v2' 사용을 피하고 중앙집중식 관리로 오타 / 조건 분기 실수를 줄입니다.
"""

from __future__ import annotations

from enum import Enum
from typing import Union


class UIMode(str, Enum):
    """Dash UI 모드 식별자.

    값은 기존 dcc.Store 에 저장되던 문자열과 동일하게 유지하여 역호환 보장.
    """

    DAY = "v1"
    NIGHT = "v2"

    @classmethod
    def normalize(cls, value: Union[str, "UIMode", None]) -> "UIMode":
        """임의 입력을 표준 UIMode 로 변환 (알 수 없는 값은 DAY 로 fallback)."""
        if isinstance(value, cls):
            return value
        if value in (cls.DAY.value, "day", "Day", "DAY"):
            return cls.DAY
        if value in (cls.NIGHT.value, "night", "Night", "NIGHT"):
            return cls.NIGHT
        return cls.DAY

    @classmethod
    def is_night(cls, value: Union[str, "UIMode", None]) -> bool:
        return cls.normalize(value) == cls.NIGHT
