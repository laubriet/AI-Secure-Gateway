from guardrail import build_guardrail_graph
from guardrail.schema import to_gate_decision
from guardrail.simulator import LocalLLMSimulator


if __name__ == "__main__":
    prompt = "I was charged twice. Please refund the duplicate."
    graph = build_guardrail_graph()
    result = graph.invoke({"prompt": prompt})
    classification = result["classification"]
    decision = to_gate_decision(classification)
    print(decision.value)
    if decision.value == "go":
        print(LocalLLMSimulator().respond(prompt))