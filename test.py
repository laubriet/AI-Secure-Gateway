from guardrail import build_guardrail_graph, decide_policy


if __name__ == "__main__":
    prompt = "I was charged twice. Please refund the duplicate."
    graph = build_guardrail_graph()
    result = graph.invoke({"prompt": prompt})
    classification = result["classification"]

    print(classification.model_dump_json(indent=2))
    print(f"policy_decision={decide_policy(classification)}")