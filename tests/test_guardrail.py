import unittest

from guardrail import (
    Category,
    Classification,
    ClassificationStatus,
    decide_policy,
    to_gate_decision,
)
from guardrail.graph import build_guardrail_graph, normalize_input


class GuardrailTests(unittest.TestCase):
    def test_normalization_trims_and_limits_input(self):
        result = normalize_input({"prompt": "  hello  "})
        self.assertEqual(result["prompt"], "hello")

    def test_graph_accepts_injected_classifier(self):
        def classify(prompt: str) -> Classification:
            return Classification(
                is_dangerous=True,
                category=Category.PROMPT_INJECTION,
                confidence=0.91,
                reason=f"classified: {prompt}",
            )

        result = build_guardrail_graph(classify).invoke({"prompt": "ignore rules"})
        self.assertEqual(result["classification"].category, Category.PROMPT_INJECTION)

    def test_policy_blocks_high_confidence_danger(self):
        classification = Classification(
            is_dangerous=True,
            category=Category.CREDENTIAL_EXFILTRATION,
            confidence=0.90,
            reason="requests a secret",
        )
        self.assertEqual(decide_policy(classification).value, "block")

    def test_policy_reviews_model_errors(self):
        classification = Classification.error("test", "offline")
        self.assertIs(classification.status, ClassificationStatus.ERROR)
        self.assertEqual(decide_policy(classification).value, "review")

    def test_public_output_is_binary(self):
        safe = Classification(
            is_dangerous=False,
            category=Category.BENIGN,
            confidence=0.95,
            reason="internal",
        )
        dangerous = Classification(
            is_dangerous=True,
            category=Category.PROMPT_INJECTION,
            confidence=0.95,
            reason="internal",
        )
        self.assertEqual(to_gate_decision(safe).value, "go")
        self.assertEqual(to_gate_decision(dangerous).value, "no-go")

    def test_public_output_fails_closed_when_unknown(self):
        unknown = Classification(
            is_dangerous=False,
            category=Category.UNKNOWN,
            confidence=0.0,
            reason="internal",
        )
        self.assertEqual(to_gate_decision(unknown).value, "no-go")


if __name__ == "__main__":
    unittest.main()
