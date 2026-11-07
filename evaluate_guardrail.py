import argparse
import json
from collections import Counter
from pathlib import Path

from guardrail import build_guardrail_graph


def load_examples(path: Path, split: str) -> list[dict]:
    with path.open(encoding="utf-8") as file:
        return [
            example
            for line in file
            if (example := json.loads(line)).get("split") == split
        ]


def evaluate(path: Path, split: str) -> dict:
    graph = build_guardrail_graph()
    rows = []
    for example in load_examples(path, split):
        result = graph.invoke({"prompt": example["text"]})["classification"]
        rows.append(
            {
                "id": example["id"],
                "expected": example["expected_is_dangerous"],
                "predicted": result.is_dangerous,
                "expected_category": example["expected_category"],
                "predicted_category": result.category.value,
                "confidence": result.confidence,
            }
        )

    true_positive = sum(row["expected"] and row["predicted"] for row in rows)
    true_negative = sum(not row["expected"] and not row["predicted"] for row in rows)
    false_positive = sum(not row["expected"] and row["predicted"] for row in rows)
    false_negative = sum(row["expected"] and not row["predicted"] for row in rows)
    total = len(rows)
    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    accuracy = (true_positive + true_negative) / total if total else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

    return {
        "examples": total,
        "accuracy": accuracy,
        "precision_dangerous": precision,
        "recall_dangerous": recall,
        "f1_dangerous": f1,
        "false_positive_rate": false_positive / (false_positive + true_negative)
        if false_positive + true_negative
        else 0.0,
        "false_negative_rate": false_negative / (false_negative + true_positive)
        if false_negative + true_positive
        else 0.0,
        "confusion_matrix": {
            "true_positive": true_positive,
            "true_negative": true_negative,
            "false_positive": false_positive,
            "false_negative": false_negative,
        },
        "category_counts": dict(
            Counter(row["predicted_category"] for row in rows)
        ),
        "errors": [row for row in rows if row["expected"] != row["predicted"]],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset", type=Path, default=Path("data/prompt_safety.jsonl")
    )
    parser.add_argument("--split", default="test")
    args = parser.parse_args()
    print(json.dumps(evaluate(args.dataset, args.split), indent=2))
