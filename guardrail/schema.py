from enum import StrEnum

from pydantic import BaseModel, Field


class Category(StrEnum):
    BENIGN = "benign"
    PROMPT_INJECTION = "prompt_injection"
    CREDENTIAL_EXFILTRATION = "credential_exfiltration"
    MALWARE_OR_EXPLOITATION = "malware_or_exploitation"
    SELF_HARM_OR_VIOLENCE = "self_harm_or_violence"
    PRIVACY_ABUSE = "privacy_abuse"
    UNKNOWN = "unknown"


class ClassificationStatus(StrEnum):
    OK = "ok"
    ERROR = "error"


class Classification(BaseModel):
    is_dangerous: bool
    category: Category
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str = Field(min_length=1, max_length=500)
    status: ClassificationStatus = ClassificationStatus.OK
    model: str = "unknown"
    policy_version: str = "v1"

    @classmethod
    def error(cls, model: str, reason: str) -> "Classification":
        return cls(
            is_dangerous=False,
            category=Category.UNKNOWN,
            confidence=0.0,
            reason=reason[:500],
            status=ClassificationStatus.ERROR,
            model=model,
        )
