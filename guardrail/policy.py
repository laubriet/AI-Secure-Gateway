from enum import StrEnum

from .schema import Category, Classification, ClassificationStatus


class PolicyDecision(StrEnum):
    ALLOW = "allow"
    BLOCK = "block"
    REVIEW = "review"


def decide_policy(
    classification: Classification,
    block_threshold: float = 0.85,
    review_threshold: float = 0.50,
) -> PolicyDecision:
    if classification.status is ClassificationStatus.ERROR:
        return PolicyDecision.REVIEW
    if classification.category is Category.UNKNOWN:
        return PolicyDecision.REVIEW
    if classification.is_dangerous:
        if classification.confidence >= block_threshold:
            return PolicyDecision.BLOCK
        return PolicyDecision.REVIEW
    if classification.confidence < review_threshold:
        return PolicyDecision.REVIEW
    return PolicyDecision.ALLOW
