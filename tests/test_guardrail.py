import unittest

from guardrail import Category, Classification, ClassificationStatus, decide_policy
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


if __name__ == "__main__":
    unittest.main()
